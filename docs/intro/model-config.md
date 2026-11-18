# 模型配置

设置页拥有模型供应商连接与可用模型。默认聊天、快速响应、图谱抽取及 Judge 为 `deepseek:deepseek-flash`；Embedding 为 `siliconflow-cn:Pro/BAAI/bge-m3`；Rerank 为 `siliconflow-cn:Pro/BAAI/bge-reranker-v2-m3`。

供应商配置保存在本应用私有配置及 PG，不能提交密钥。连接探测只证明对应接口可用；真实问答、图谱抽取和 Judge 要分别执行。修改向量模型须按知识库现有索引约束处理，不能把旧向量直接视为新模型结果。

重排失败和模型 usage 缺失沿用现有可观察降级；Dashboard 不把缺失 Token 伪造为零。
