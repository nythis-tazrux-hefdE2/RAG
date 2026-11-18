"""装配唯一的 container 执行客户端并验证连接配置。"""

import asyncio
import os

from rag.modules.agents.runtime.sandbox.container import ContainerSandboxProvider

_sandbox_provider: ContainerSandboxProvider | None = None


def get_sandbox_provider() -> ContainerSandboxProvider:
    """返回本进程共享的无长期连接执行客户端。"""
    global _sandbox_provider
    if _sandbox_provider is None:
        validate_sandbox_configuration()
        _sandbox_provider = ContainerSandboxProvider()
    return _sandbox_provider


async def check_sandbox_provider() -> None:
    """核对所选执行节点真实就绪；镜像和资源限制由节点自身校验。"""
    await asyncio.to_thread(get_sandbox_provider().health)


def validate_sandbox_configuration() -> str:
    """拒绝错误后端和未配置的 runner 认证。"""
    if os.environ.get("RAG_SANDBOX_BACKEND", "container").strip().lower() != "container":
        raise RuntimeError("RAG_SANDBOX_BACKEND 必须是 container")
    if len(os.environ.get("RAG_SANDBOX_RUNNER_TOKEN", "").strip()) < 16:
        raise RuntimeError("container 执行需要至少 16 个字符的 RAG_SANDBOX_RUNNER_TOKEN")
    return "container"
