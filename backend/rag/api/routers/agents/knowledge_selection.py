"""Web 问答会话的知识库选择。"""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, StringConstraints
from sqlalchemy.ext.asyncio import AsyncSession

from rag.api.dependencies.auth import get_db, get_required_user
from rag.modules.agents.scope import ActorScope
from rag.modules.agents.services.knowledge_selection import read_knowledge_selection, update_knowledge_selection
from rag.modules.identity.models import User

knowledge_selection_router = APIRouter(prefix="/agent/threads", tags=["agent"], include_in_schema=False)


class KnowledgeSelectionUpdate(BaseModel):
    """全部当前可见知识库，或明确选择的一组知识库。"""

    model_config = ConfigDict(extra="forbid")
    selection: Literal["all"] | list[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]]


async def require_web_knowledge_scope(request: Request, user: User = Depends(get_required_user)) -> ActorScope:
    """产品会话设置只接受 Web 登录身份。"""
    if getattr(request.state, "api_key", None) is not None:
        raise HTTPException(status_code=403, detail="会话知识选择仅支持 Web 登录用户")
    return ActorScope(uid=str(user.uid), app_id=None)


@knowledge_selection_router.get("/{thread_id}/knowledge-selection")
async def get_selection(
    thread_id: str,
    scope: ActorScope = Depends(require_web_knowledge_scope),
    db: AsyncSession = Depends(get_db),
):
    """读取当前产品会话的知识范围。"""
    return await read_knowledge_selection(db=db, scope=scope, thread_id=thread_id)


@knowledge_selection_router.put("/{thread_id}/knowledge-selection")
async def put_selection(
    thread_id: str,
    payload: KnowledgeSelectionUpdate,
    scope: ActorScope = Depends(require_web_knowledge_scope),
    db: AsyncSession = Depends(get_db),
):
    """设置后续提交使用的知识库范围。"""
    return await update_knowledge_selection(db=db, scope=scope, thread_id=thread_id, selection=payload.selection)
