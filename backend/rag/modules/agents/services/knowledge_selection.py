"""Web 会话的知识选择，已接收的 Input 继续使用冻结配置。"""

from copy import deepcopy
from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from rag.modules.agents.scope import ActorScope
from rag.modules.agents.services.thread_access import require_thread
from rag.modules.knowledge.services.access import visible_knowledge_bases
from rag.shared.datetime import utc_now
from rag.shared.errors import PermissionDeniedError, StateConflictError

type KnowledgeSelection = Literal["all"] | list[str]


async def read_knowledge_selection(*, db: AsyncSession, scope: ActorScope, thread_id: str) -> dict:
    """只读取本人产品会话的当前选择。"""
    session = await require_thread(db=db, scope=scope, thread_id=thread_id)
    if session.config_snapshot is None:
        raise StateConflictError("会话缺少配置快照")
    return {"selection": session.config_snapshot.get("knowledges", "all")}


async def update_knowledge_selection(*, db: AsyncSession, scope: ActorScope, thread_id: str, selection: KnowledgeSelection) -> dict:
    """与输入接收共用 Thread 锁，只更新后续提交的配置。"""
    selected = selection
    session = await require_thread(db=db, scope=scope, thread_id=thread_id, lock=True)
    if session.status != "active" or session.config_snapshot is None:
        raise StateConflictError("只有具备配置快照的活跃会话可以修改知识库选择")
    if selected != "all":
        available = {item["kb_id"] for item in await visible_knowledge_bases(scope.uid)}
        if set(selected) - available:
            raise PermissionDeniedError("知识库不存在或无权选择")
    snapshot = deepcopy(session.config_snapshot)
    snapshot["knowledges"] = selected
    session.config_snapshot = snapshot
    session.updated_at = utc_now()
    await db.commit()
    return {"selection": selected}
