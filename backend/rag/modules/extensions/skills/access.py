"""共享与专属 Skill 的权限、依赖及带锁读取契约。"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from rag.infrastructure.observability.logging import logger
from rag.infrastructure.runtime_settings import get_skill_data_dir
from rag.modules.extensions.skills.models import Skill
from rag.modules.extensions.skills.package import normalize_string_list, validated_shared_skill_parts
from rag.modules.extensions.skills.repository import SkillRepository
from rag.modules.extensions.skills.resolved import ResolvedSkill
from rag.modules.identity.models import User
from rag.modules.identity.permissions import ResourcePermission, normalize_permission_config, resolve_skill_permission

BUILTIN_SKILL_SHARE_CONFIG = {
    "version": 2,
    "read_scope": {"access_level": "global", "department_ids": [], "user_uids": []},
    "manage_scope": None,
}


async def lock_accessible_shared_skill_for_file(db: AsyncSession, user: User, slug: str) -> Skill | None:
    """在读取共享源文件期间锁定一行并重新检查权限。"""
    repo = SkillRepository(db)
    item = await repo.get_by_slug_for_read(slug)
    return item if item is not None and user_can_access_skill(user, item) else None


async def lock_accessible_shared_skills_for_runtime(
    db: AsyncSession,
    user: User,
    selected: list[str],
) -> list[Skill]:
    """只锁定已选共享 Skill 及其依赖，锁后重新检查权限。"""
    repo = SkillRepository(db)
    visible = {item.slug for item in await repo.list_enabled_readable(user)}
    pending = list(selected)
    locked: dict[str, Skill] = {}
    while pending:
        slug = pending.pop(0)
        if slug not in visible or slug in locked:
            continue
        item = await repo.get_by_slug_for_read(slug)
        if item is None or not user_can_access_skill(user, item):
            continue
        locked[slug] = item
        pending.extend(item.skill_dependencies or [])
    return list(locked.values())


def resolved_shared_skill(item: Skill) -> ResolvedSkill:
    """将数据库 Skill 适配为统一的有效 Skill 描述。"""
    source_scope = "builtin"
    try:
        share_config = normalize_permission_config(item.share_config)
    except (TypeError, ValueError) as exc:
        # 可见性仍由 repository/resolver 校验；保留坏配置供管理者修复。
        share_config = item.share_config
        logger.warning("Invalid skill share config exposed for repair: slug={}, error={}", item.slug, str(exc))
    return ResolvedSkill(
        id=item.id,
        slug=item.slug,
        name=item.name,
        description=item.description,
        source_type=item.source_type,
        source_scope=source_scope,
        source_dir=_resolve_skill_dir(item),
        enabled=bool(item.enabled),
        created_by=item.created_by,
        share_config=share_config,
        tool_dependencies=normalize_string_list(item.tool_dependencies),
        mcp_dependencies=normalize_string_list(item.mcp_dependencies),
        skill_dependencies=normalize_string_list(item.skill_dependencies),
        version=item.version,
        content_hash=item.content_hash,
    )


def user_can_access_skill(user: User, skill: Skill) -> bool:
    """检查用户是否可使用已启用的共享 Skill。"""
    if not skill.enabled:
        return False
    return resolve_skill_permission(user, skill) != ResourcePermission.NONE


def is_builtin_skill(item: Skill | ResolvedSkill) -> bool:
    """判断共享 Skill 是否为内置来源。"""
    return item.source_type == "builtin"


def get_skills_root_dir() -> Path:
    """返回共享与内置 Skill 的持久源目录。"""
    root = get_skill_data_dir() / "shared"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _resolve_skill_dir(item: Skill) -> Path:
    """将共享 Skill 数据库路径解析到持久根下。"""
    return get_skill_data_dir().joinpath(*validated_shared_skill_parts(item.slug, item.dir_path))
