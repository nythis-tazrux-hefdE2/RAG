"""显式注册业务和知识 ORM 映射，供 Schema 初始化与测试独立装配。"""

from importlib import import_module

from rag.infrastructure.postgres.base import BusinessBase, KnowledgeBase

MODEL_MODULES = (
    "rag.modules.agents.models.definitions",
    "rag.modules.agents.models.sessions",
    "rag.modules.agents.models.inputs",
    "rag.modules.agents.models.attachments",
    "rag.modules.agents.models.turns",
    "rag.modules.agents.models.runs",
    "rag.modules.agents.models.messages",
    "rag.modules.agents.models.feedback",
    "rag.modules.workspace.models",
    "rag.modules.identity.models",
    "rag.modules.extensions.skills.models",
    "rag.modules.extensions.mcp.models",
    "rag.modules.models.tables",
    "rag.modules.system.models",
    "rag.modules.background_jobs.models",
    "rag.modules.knowledge.models",
)


def load_models() -> tuple:
    """加载全部映射并返回两个独立 metadata。"""
    for module in MODEL_MODULES:
        import_module(module)
    return BusinessBase.metadata, KnowledgeBase.metadata
