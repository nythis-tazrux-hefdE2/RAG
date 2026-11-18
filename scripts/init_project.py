"""生成独立部署配置；保留已有非空配置的原始 dotenv 表达。"""

import base64
import os
import re
import secrets
import tempfile
import uuid
from pathlib import Path


_ASSIGNMENT = re.compile(
    r"^\s*(?:export\s+)?(?P<quote>'?)(?P<key>[A-Za-z_][A-Za-z0-9_]*)(?P=quote)\s*=(?P<value>.*)$"
)


def main(root: Path | None = None) -> None:
    """仅补齐空项和缺项，不重新编码已有凭据或内联注释。"""
    root = root or Path(__file__).resolve().parents[1]
    env_path = root / ".env"
    source = env_path if env_path.exists() else root / ".env.template"
    lines = source.read_text().splitlines()
    assignments = {}
    for index, line in enumerate(lines):
        match = _ASSIGNMENT.fullmatch(line)
        if match:
            assignments[match["key"]] = (index, match["value"])

    generated = {}

    def fill(key: str, factory) -> None:
        """只为最终赋值为空的配置生成新值。"""
        existing = assignments.get(key)
        if existing is None or not _has_value(existing[1]):
            generated[key] = factory()

    for key in ("RAG_JWT_SECRET_KEY", "RAG_API_KEY_DERIVATION_SECRET", "RAG_SANDBOX_RUNNER_TOKEN",
                "RAG_POSTGRES_PASSWORD", "RAG_MINIO_SECRET_KEY", "RAG_NEO4J_PASSWORD"):
        fill(key, lambda: secrets.token_hex(32))
    fill("RAG_INSTANCE_ID", lambda: str(uuid.uuid4()))
    fill("RAG_MINIO_ACCESS_KEY", lambda: "rag" + secrets.token_hex(8))
    fill("RAG_ENCRYPTION_KEY", lambda: base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())
    defaults = {
        "COMPOSE_PROJECT_NAME": "rag", "RAG_SANDBOX_BACKEND": "container",
        "RAG_PUBLIC_URL": "http://localhost:25173",
        "RAG_CORS_ORIGINS": "http://localhost:25173,http://127.0.0.1:25173",
        "RAG_POSTGRES_DB": "rag", "RAG_LANGFUSE_ENABLED": "false", "RAG_ARQ_MAX_JOBS": "10",
    }
    for prefix in ("API", "WORKER"):
        defaults.update({f"RAG_{prefix}_POSTGRES_POOL_SIZE": "10", f"RAG_{prefix}_POSTGRES_MAX_OVERFLOW": "5",
                         f"RAG_{prefix}_LANGGRAPH_POSTGRES_POOL_SIZE": "10"})
    for key, value in defaults.items():
        fill(key, lambda value=value: value)

    output = list(lines)
    for key, value in generated.items():
        encoded = _env_line(key, value)
        if key in assignments:
            output[assignments[key][0]] = encoded
        else:
            output.append(encoded)
    descriptor, temporary = tempfile.mkstemp(prefix=".env-", dir=root)
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write("\n".join(output).rstrip() + "\n")
        os.replace(temporary, env_path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print("RAG 私有配置已准备；现有值已保留，未显示凭据。")


def _has_value(raw: str) -> bool:
    """只识别空赋值，不解析或展开用户的非空配置。"""
    value = raw.strip()
    return bool(value and not value.startswith("#") and not re.fullmatch(r"(?:''|\"\")\s*(?:#.*)?", value))


def _env_line(key: str, value: str) -> str:
    """按 Compose dotenv 语义编码一个单行新值。"""
    if "\n" in value or "\r" in value or "\x00" in value:
        raise ValueError(f"{key} 必须是单行配置")
    return key + "='" + value.replace("'", "\\'") + "'"


if __name__ == "__main__":
    main()
