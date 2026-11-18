# RAG

A document knowledge base with source-linked answers, graph-assisted retrieval and evaluation.

## Install and run

Install Docker Engine, Docker Compose v2 and Python 3.10 or later. Network access is required for the first build and for configured model or OCR providers.

Run from the repository root:

```bash
bash scripts/init.sh
```

Configure provider credentials in the generated private `.env` file, then start the services:

```bash
docker compose up -d --build
docker compose ps
curl --fail http://localhost:25050/api/system/ready
```

Open `http://localhost:25173`, create the administrator account, configure and test model connections, then create a knowledge base and upload documents. Wait for indexing to finish before asking questions, and check the returned sources.

The sandbox is intended for single-tenant, trusted-code execution. Keep environment files and runtime data private and back them up. See the [deployment guide](docs/advanced/deployment.md) for production setup, ports, configuration changes and backups.

## Usage guides

- [Getting started](docs/intro/quick-start.md)
- [Knowledge bases and graphs](docs/intro/knowledge-base.md)
- [Model configuration](docs/intro/model-config.md)
- [Evaluation](docs/intro/evaluation.md)
- [Document processing](docs/advanced/document-processing.md)
- [Optional Langfuse integration](docs/advanced/langfuse-integration.md)

## License and origin

See the [MIT license](LICENSE) and [upstream and third-party notices](UPSTREAM.md).
