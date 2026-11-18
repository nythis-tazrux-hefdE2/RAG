# 部署与运行

读者：部署和维护 RAG 的管理员。Compose 项目名为 `rag`，数据存放仓库自己的 `docker/volumes/`。

## 配置与启动

```bash
bash scripts/init.sh
docker compose up -d --build
docker compose ps
curl --fail http://localhost:25050/api/system/ready
```

初始化生成独立的 PG、MinIO、Neo4j、JWT、API 派生、runner 和加密密钥。`.env` 必须私有且备份，不能提交；运行中不要重置密钥。模型连接可在设置中配置。Compose 默认包含执行镜像准备和 sandbox-runner，无需选择后端或 profile。

| 服务 | 主机端口 |
|---|---|
| Web / API | 25173 / 25050 |
| PostgreSQL / Redis | 25432 / 26379 |
| MinIO API / 控制台 | 29000 / 29001 |
| Milvus / 健康 | 29530 / 29091 |
| Neo4j HTTP / Bolt | 27474 / 27687 |

启动前使用 `ss -lnt` 检查冲突。内部服务名称和容器端口由 Compose 拥有，不能把主机 URL 用作容器内连接。沙盒适用于单租户、可信代码执行；网络公开范围、TLS 和备份策略由实际部署环境决定。

## 生产部署

在独立部署目录中初始化配置；首次创建 `.env.prod` 时保留已有文件：

```bash
bash scripts/init.sh
cp -n .env .env.prod
chmod 600 .env.prod
```

编辑私有 `.env.prod`，将 `RAG_ENV` 设为 `production`，填写模型供应商凭据并核对外部访问地址。生产环境与其他实例同时运行时，为每套实例设置独立的 `COMPOSE_PROJECT_NAME`、`RAG_STATE_DIR` 和主机端口；同一数据目录只允许一套 API、worker 和 app-init 写入。

生产拓扑要求预先构建沙盒镜像并固定其标识。以下命令使用当前默认镜像名；自定义 `RAG_SANDBOX_CONTAINER_IMAGE` 时同步替换构建标签和检查目标：

```bash
docker build -f docker/sandbox.Dockerfile -t rag-sandbox:0.8.0.beta4 .
docker image inspect --format '{{.Id}}' rag-sandbox:0.8.0.beta4
```

将检查得到的 `sha256:...` 写入 `.env.prod` 的 `RAG_SANDBOX_CONTAINER_IMAGE_DIGEST`。runner 会核对实际镜像 ID 或仓库 digest；重新构建镜像后须核对并更新该值。

显式选择生产配置文件及容器环境文件：

```bash
RAG_ENV_FILE=.env.prod docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
RAG_ENV_FILE=.env.prod docker compose --env-file .env.prod -f docker-compose.prod.yml ps
curl --fail http://localhost:25050/api/system/ready
```

Web 默认地址为 `http://localhost:25173`。修改端口时同步修改检查地址。首次部署需创建管理员并分别检查模型连接、文档索引和带来源问答；ready 通过不能代替这些业务结果。

## 关闭本地知识库

与默认部署配置叠加，关闭知识库运行能力和本地图谱、向量服务：

```bash
docker compose -f docker-compose.yml -f docker-compose.no-knowledge.yml up -d --build
```

生产部署使用相同叠加文件，并继续显式指定生产环境文件：

```bash
RAG_ENV_FILE=.env.prod docker compose --env-file .env.prod -f docker-compose.prod.yml -f docker-compose.no-knowledge.yml up -d --build
```

该操作保留代码和已有数据。恢复时去掉叠加文件，确认环境配置中的 `RAG_KNOWLEDGE_ENABLED=true` 后重新启动。

## 环境接口

本应用拥有的配置使用 `RAG_` 前缀，包括服务连接、身份安全、沙盒、运行限额和 MinerU 设置。完整变量及默认值由根目录 `.env.template` 和 Compose 维护，不在文档复制完整清单。

模型供应商及 SDK 的原生变量，例如 `DEEPSEEK_API_KEY`、`SILICONFLOW_API_KEY`、`LANGFUSE_PUBLIC_KEY`，保持原名。Compose 将应用配置映射为第三方容器需要的原生变量，例如 Neo4j 的 `NEO4J_AUTH`。`COMPOSE_PROJECT_NAME` 和 `TZ` 继续采用工具原生约定。

## 更新配置与备份

开发部署的环境文件更改后执行 `docker compose up -d --no-deps --force-recreate api worker`。生产部署继续使用生产配置：

```bash
RAG_ENV_FILE=.env.prod docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --no-deps --force-recreate api worker sandbox-runner
```

修改了中间件配置时，按受影响服务重新创建对应容器。数据库、对象、向量、图、工作目录、Skill 投影和密钥必须作为同一部署备份；备份正确性需要单独恢复演练。停止开发部署使用 `docker compose stop`；生产部署使用相同的生产参数执行 `stop`。运行中保持持久密钥稳定。

Langfuse 默认关闭；可选方式见 [Langfuse](langfuse-integration.md)。文档解析见 [解析参考](document-processing.md)。
