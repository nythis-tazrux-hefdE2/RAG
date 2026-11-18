# 快速开始

读者：首次部署和使用本应用的管理员。前置条件为 Docker Compose、可用的模型供应商连接及足够的内存和磁盘空间。

## 初始化并登录

在仓库根执行：

```bash
bash scripts/init.sh
docker compose up -d --build
```

打开 `http://localhost:25173`，创建本应用管理员。初始化生成独立密钥；重复运行保留已有值。ready 成功只说明依赖满足接流量条件。

## 配置模型

在设置中配置 DeepSeek 与 SiliconFlow 连接，分别测试 Chat、Embedding 和 Rerank。默认聊天、快速响应、图谱抽取及 Judge 使用 `deepseek:deepseek-flash`。向量与重排模型见 [模型配置](model-config.md)。密钥不得放入仓库或聊天记录。

## 上传并提问

进入知识库，新建本地 Milvus 知识库，上传 Markdown 或 TXT，等待文件显示已索引。进入对话，选择可访问知识库，询问文档中特有的事实，并打开来源核对正文和行范围。刷新页面后再次读取历史，再发送依赖上一轮的问题。

PDF、Office、表格和图片的解析条件见 [文档解析](../advanced/document-processing.md)。上传成功和任务入队都不能代替已索引结果。
