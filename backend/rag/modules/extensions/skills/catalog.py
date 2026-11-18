"""查询知识问答所需的内置 Skill。"""

from sqlalchemy.ext.asyncio import AsyncSession

from rag.modules.extensions.skills.access import resolved_shared_skill
from rag.modules.extensions.skills.repository import SkillRepository
from rag.modules.extensions.skills.resolved import ResolvedSkill
from rag.modules.identity.models import User


async def list_accessible_skills(db: AsyncSession, user: User) -> list[ResolvedSkill]:
    """按当前用户授权返回内置知识 Skill。"""
    items = await SkillRepository(db).list_enabled_readable(user)
    return [resolved_shared_skill(item) for item in items if item.slug == "knowledge-base"]


async def list_builtin_skill_definitions(db: AsyncSession) -> list:
    """返回启动同步使用的内置定义。"""
    return await SkillRepository(db).list_builtin()
