"""内置智能体定义与后端信息路由。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from rag.api.dependencies.auth import get_db, get_required_user
from rag.modules.agents.permissions import user_can_access_agent
from rag.modules.agents.runtime.agent_backends import (
    AgentBackendNotFoundError,
)
from rag.modules.agents.services.definitions import (
    ensure_default_agent_definition,
    get_visible_agent_definition,
    list_visible_agent_definitions,
    serialize_agent_definition,
)
from rag.modules.identity.models import User

agent_router = APIRouter(prefix="/agent", tags=["agent"])


@agent_router.get("")
async def list_agents(
    current_user: User = Depends(get_required_user),
    db: AsyncSession = Depends(get_db),
):
    items = await list_visible_agent_definitions(db, user=current_user)
    backend_info_cache: dict[tuple[str, bool, str], dict] = {}
    agents = [await _serialize_agent(db, item, current_user, backend_info_cache=backend_info_cache) for item in items]
    return {"agents": agents}


@agent_router.get("/default")
async def get_default_agent(current_user: User = Depends(get_required_user), db: AsyncSession = Depends(get_db)):
    item = await ensure_default_agent_definition(db)
    if not item or not user_can_access_agent(current_user, item):
        raise HTTPException(status_code=404, detail="默认智能体不可访问")
    return {"agent": await _serialize_agent(db, item, current_user, include_configurable_items=True)}


@agent_router.get("/{agent_id}")
async def get_agent(agent_id: str, current_user: User = Depends(get_required_user), db: AsyncSession = Depends(get_db)):
    agent_slug = agent_id  # 兼容既有路径参数名；这里实际是 Agent.slug。
    item = await get_visible_agent_definition(db, user=current_user, slug=agent_slug)
    if not item:
        raise HTTPException(status_code=404, detail="智能体不存在")
    return {"agent": await _serialize_agent(db, item, current_user, include_configurable_items=True)}


async def _serialize_agent(
    db,
    item,
    user: User,
    *,
    include_configurable_items: bool = False,
    backend_info_cache: dict[tuple[str, bool, str], dict] | None = None,
) -> dict:
    """序列化智能体定义，后端缺失时返回 404。"""
    try:
        data = await serialize_agent_definition(
            db,
            item,
            user=user,
            include_configurable_items=include_configurable_items,
            backend_info_cache=backend_info_cache,
        )
    except AgentBackendNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return data
