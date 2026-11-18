"""内部 Knowledge MCP 工具入口，按当前可信运行用户装配。"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rag.infrastructure.observability.logging import logger
from rag.modules.extensions.mcp.builtin import BUILTIN_MCP_DEFAULTS, BUILTIN_MCP_MANIFEST, builtin_mcp_available
from rag.modules.extensions.mcp.config import normalize_mcp_manifest_entry
from rag.modules.extensions.mcp.models import MCPServer
from rag.modules.extensions.mcp.repository import active_mcp_user, list_enabled_mcp_servers
from rag.modules.extensions.mcp.runtime import (
    SharedMCPAuth,
)
from rag.modules.extensions.mcp.runtime import (
    get_mcp_tools as load_mcp_tools,
)

BUILTIN_MCP_SERVERS = BUILTIN_MCP_MANIFEST["mcpServers"]

_SYNCED_MCP_FIELDS = (
    "name",
    "description",
    "transport",
    "url",
    "headers",
    "timeout",
    "sse_read_timeout",
    "auth_mode",
)


# =============================================================================
# === 内置同步与配置读取 ===
# =============================================================================


async def ensure_builtin_mcp_servers_in_db() -> None:
    """同步代码拥有的连接字段，保留管理员启停和工具开关。"""
    from rag.infrastructure.postgres.manager import pg_manager

    async with pg_manager.get_async_session_context() as session:
        any_changed = False

        for slug, entry in BUILTIN_MCP_SERVERS.items():
            config = {
                **normalize_mcp_manifest_entry(slug, entry),
                **BUILTIN_MCP_DEFAULTS.get(slug, {"auth_mode": "headers", "enabled": False}),
            }
            result = await session.execute(select(MCPServer).filter(MCPServer.slug == slug))
            existing = result.scalar_one_or_none()
            if not existing:
                session.add(
                    MCPServer(
                        slug=slug,
                        name=config.get("name", slug),
                        description=config.get("description"),
                        transport=config["transport"],
                        url=config.get("url"),
                        headers=config.get("headers"),
                        timeout=config.get("timeout"),
                        sse_read_timeout=config.get("sse_read_timeout"),
                        # delegation 表示凭据由 Agent 运行时按当前用户签发；enabled 表达清单声明的默认启停。
                        auth_mode=config.get("auth_mode", "headers"),
                        enabled=1 if config.get("enabled") else 0,
                        created_by="system",
                        updated_by="system",
                    )
                )
                any_changed = True
                logger.info(f"Added built-in MCP server '{slug}' to database")
                continue

            if existing.created_by != "system":
                raise ValueError(f"内置 MCP slug 冲突：{slug} 已由用户服务占用，请先显式处理")

            server_changed = False
            for field in _SYNCED_MCP_FIELDS:
                next_value = config.get(field)
                if getattr(existing, field) != next_value:
                    setattr(existing, field, next_value)
                    server_changed = True
            if server_changed:
                existing.updated_by = "system"
                any_changed = True

        if any_changed:
            await session.commit()


async def get_enabled_mcp_server_config(server_slug: str, *, db: AsyncSession | None = None) -> dict[str, Any] | None:
    """Get the latest enabled MCP server config from the database."""
    servers = await get_enabled_mcp_servers(names=[server_slug], db=db)
    return _to_runtime_mcp_config(servers[0]) if servers else None


async def get_enabled_mcp_server_slugs(*, db: AsyncSession | None = None) -> list[str]:
    """读取受支持且已启用的服务标识，供配置选择与 Skill 依赖校验。"""
    return [server.slug for server in await get_enabled_mcp_servers(db=db)]


async def get_enabled_mcp_servers(*, names: list[str] | None = None, db: AsyncSession | None = None) -> list[MCPServer]:
    """读取本部署启用的内部知识服务。"""
    if db is None:
        from rag.infrastructure.postgres.manager import pg_manager

        async with pg_manager.get_async_session_context() as session:
            return await get_enabled_mcp_servers(names=names, db=session)

    return [server for server in await list_enabled_mcp_servers(db, names=names) if builtin_mcp_available(server.slug)]


# =============================================================================
# === Server Config CRUD ===
# =============================================================================


# =============================================================================
# === Tool Management ===
# =============================================================================


# =============================================================================
# === 按调用身份装配工具 ===
# =============================================================================


async def resolve_runtime_mcp_tools(
    server_slugs: list[str],
    *,
    uid: str | None,
    run_tools: dict[str, list] | None = None,
    unavailable: dict[str, str] | None = None,
    context=None,
) -> dict[str, list]:
    """按本人当前权限读取工具，本 Run 的目录由调用方独占持有，不跨运行或用户复用。"""
    import asyncio

    from rag.infrastructure.postgres.manager import pg_manager

    if not server_slugs:
        return {}
    async with pg_manager.get_async_session_context() as db:
        user = await active_mcp_user(db, uid=uid)
        servers = await available_mcp_servers(db, server_slugs, user_id=user.id)

    if run_tools is None:
        run_tools = {}

    if unavailable is None:
        unavailable = {}
    for slug in server_slugs:
        if slug not in servers:
            unavailable[slug] = "知识库能力不可用，请联系管理员检查服务"

    async def load(server):
        """隔离单服务发现故障，日志和提示只包含安全原因。"""
        try:
            config = _to_runtime_mcp_config(server)
            config.pop("headers", None)
            config.update(_delegation_connection(server, uid=uid, context=context))
            return await load_mcp_tools(server.slug, config, disabled_tools=[])
        except Exception as exc:
            unavailable[server.slug] = runtime_mcp_failure_message(exc)
            logger.warning(
                "MCP discovery unavailable: server={}, uid={}, error_type={}, reason={}",
                server.slug,
                uid,
                type(exc).__name__,
                unavailable[server.slug],
            )
            return None

    pending = {slug: server for slug, server in servers.items() if slug not in run_tools and slug not in unavailable}
    loaded = await asyncio.gather(*(load(server) for server in pending.values()))
    run_tools.update({slug: tools for slug, tools in zip(pending, loaded, strict=True) if tools is not None})
    return {
        slug: [tool for tool in run_tools[slug] if tool.name not in (server.disabled_tools or [])]
        for slug, server in servers.items()
        if slug in run_tools and slug not in unavailable
    }


def runtime_mcp_failure_message(exc: Exception) -> str:
    """展开任务组和异常链，仅将已知业务原因转换为可公开提示。"""
    if isinstance(exc, ExceptionGroup):
        reasons = dict.fromkeys(runtime_mcp_failure_message(child) for child in exc.exceptions)
        return "；".join(reasons)
    if exc.__cause__ is not None and isinstance(exc.__cause__, Exception):
        return runtime_mcp_failure_message(exc.__cause__)
    return "服务连接或调用失败，请检查 MCP 服务后重试"


async def available_mcp_servers(db: AsyncSession, server_slugs, *, user_id: int) -> dict[str, MCPServer]:
    """按当前有效用户与内部服务开关返回可用目录。"""

    if not server_slugs:
        return {}
    await active_mcp_user(db, user_id=user_id)
    servers = await get_enabled_mcp_servers(names=list(server_slugs), db=db)
    available = {server.slug: server for server in servers}
    return {slug: available[slug] for slug in dict.fromkeys(server_slugs) if slug in available}


def _delegation_connection(server, *, uid, context=None):
    """内部服务直接提供 SDK 认证，执行请求复用通用出站策略。"""
    from rag.modules.knowledge.mcp.client import knowledge_mcp_connection

    policy = SharedMCPAuth(server.slug, server.to_mcp_config(), uid=uid, auth_mode=server.auth_mode)
    return knowledge_mcp_connection(
        server.slug,
        uid=uid,
        context=context,
        before_request=policy.validate_request,
    )


def _to_runtime_mcp_config(server: MCPServer) -> dict[str, Any]:
    """生成运行时 MCP 配置，内置连接字段始终以代码定义为准。"""
    builtin = normalize_mcp_manifest_entry(server.slug, BUILTIN_MCP_SERVERS[server.slug])
    config = {key: builtin[key] for key in ("transport", "url", "headers", "timeout", "sse_read_timeout") if builtin.get(key) is not None}
    if server.disabled_tools:
        config["disabled_tools"] = server.disabled_tools
    return config
