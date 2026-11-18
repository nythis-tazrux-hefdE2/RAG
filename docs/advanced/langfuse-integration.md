# 可选 Langfuse

Langfuse 默认关闭，核心问答、知识库、评测和 Dashboard 使用本地状态即可运行。显式设置 `RAG_LANGFUSE_ENABLED=true` 并填写现有 Langfuse 连接参数后，API/worker 才使用远端追踪。

Turn 根与 Run observation 保留执行归属；远端不可用不会成为本地执行的第二份权威状态。只有超级管理员可访问受控 trace 链接，链接必须匹配已配置的安全 HTTP 来源。

未配置可用远端时，启用验证记为 `Not run`。本地关闭验证和 mock callback 不能替代真实远端追踪。
