"""MCP 服务配置的 PostgreSQL 查询和写入。"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rag.modules.extensions.mcp.models import MCPServer


async def get_mcp_server(db: AsyncSession, slug: str) -> MCPServer | None:
    """Get single server configuration by slug."""
    result = await db.execute(select(MCPServer).filter(MCPServer.slug == slug).execution_options(populate_existing=True))
    return result.scalar_one_or_none()


async def list_enabled_mcp_servers(db: AsyncSession, *, names: list[str] | None = None) -> list[MCPServer]:
    """按服务开关和受支持传输读取配置目录。"""
    from rag.modules.extensions.mcp.runtime import SUPPORTED_TRANSPORTS

    stmt = select(MCPServer).where(MCPServer.slug == "knowledge", MCPServer.enabled == 1, MCPServer.transport.in_(SUPPORTED_TRANSPORTS))
    if names is not None:
        stmt = stmt.where(MCPServer.slug.in_(names))
    return list((await db.scalars(stmt)).all())


async def active_mcp_user(db, *, user_id=None, uid=None):
    """运行用户必须由可信 ID 或 uid 解析，停用账号不能读取凭据。"""
    from rag.modules.identity.models import User
    from rag.shared.errors import PermissionDeniedError

    query = select(User).where(User.is_deleted == 0)
    query = query.where(User.id == user_id) if user_id is not None else query.where(User.uid == uid)
    user = await db.scalar(query.execution_options(populate_existing=True))
    if user is None:
        raise PermissionDeniedError("MCP 用户不可用")
    return user


async def runtime_mcp_policy(db, slug, uid):
    """同一语句读取有效调用者和最新服务策略，不读取个人凭据。"""
    from rag.modules.identity.models import User

    return (
        await db.execute(
            select(User, MCPServer)
            .select_from(User)
            .outerjoin(MCPServer, MCPServer.slug == slug)
            .where(User.uid == uid, User.is_deleted == 0)
            .execution_options(populate_existing=True)
        )
    ).first()
