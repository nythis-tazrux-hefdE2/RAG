"""系统管理员转移共享资源所有权。"""

from sqlalchemy import select

from rag.modules.identity.models import User
from rag.modules.identity.repositories.users import UserRepository
from rag.modules.knowledge.cache import delete_cached_kb_config
from rag.modules.knowledge.models import KnowledgeBase


async def transfer_shared_resource(db, *, kind: str, resource_id: str, owner_uid: str, actor: User) -> None:
    """锁定共享对象与有效接收者，保持私有与内置定义边界。"""
    if actor.role != "superadmin" or actor.is_deleted:
        raise PermissionError("只有系统管理员可以转移所有权")
    if kind != "knowledge":
        raise ValueError("未知资源类型")
    model, key = KnowledgeBase, KnowledgeBase.kb_id
    resource = await db.scalar(select(model).where(key == resource_id).with_for_update(of=model))
    if resource is None:
        raise LookupError("资源不存在")
    actor = await UserRepository(db).lock_active_human(actor.uid)
    if actor is None or actor.role != "superadmin":
        raise PermissionError("只有系统管理员可以转移所有权")
    owner = await db.scalar(
        select(User)
        .where(
            User.uid == owner_uid,
            User.is_deleted == 0,
            User.role.in_(("admin", "superadmin")),
            User.user_kind == "human",
        )
        .with_for_update(read=True)
    )
    if owner is None:
        raise ValueError("接收者必须是有效管理员")
    resource.created_by = owner.uid
    await delete_cached_kb_config(resource_id)
    await db.commit()
