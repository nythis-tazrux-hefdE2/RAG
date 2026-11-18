"""知识库运行时装配：导入期注册执行器类型并构建进程级单例。

KnowledgeBaseFactory 不依赖任何具体实现，本模块是其唯一注册点；
消费者拿到 knowledge_base 时注册已全部完成，工厂首次使用前即就绪。
"""

import os

from rag.infrastructure.runtime_settings import get_runtime_dir
from rag.modules.knowledge.factory import KnowledgeBaseFactory
from rag.modules.knowledge.implementations.milvus import MilvusKB
from rag.modules.knowledge.manager import KnowledgeBaseManager

# 注册顺序决定 get_available_types 的类型展示顺序（注册表按字典插入序遍历）。
KnowledgeBaseFactory.register(MilvusKB)

knowledge_base = KnowledgeBaseManager(os.path.join(get_runtime_dir(), "knowledge_base_data"))
