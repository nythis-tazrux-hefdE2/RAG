"""用户环境查询与跨进程生命周期锁。"""

import os

import psycopg
from psycopg.rows import dict_row

from rag.infrastructure.postgres.connection import postgres_conninfo


class SandboxRepository:
    """同步 executor 使用真实 PostgreSQL，不保存进程内业务状态。"""

    def connect(self):
        """取得独立短连接，凭据不进入日志。"""
        url = postgres_conninfo(os.environ.get("RAG_POSTGRES_URL", ""))
        if not url:
            raise RuntimeError("RAG_POSTGRES_URL is required for user environments")
        return psycopg.connect(url, autocommit=True, row_factory=dict_row, connect_timeout=5)

    def run_owner(self, run_id: str):
        """只读 Run 的执行归属与清理责任，不取得生命周期行锁。"""
        with self.connect() as connection:
            return connection.execute(
                "SELECT uid,status,worker_id,lease_expires_at,runtime_cleanup_pending FROM agent_runs WHERE id=%s",
                (run_id,),
            ).fetchone()

    def active_runs(self, connection, uid: str) -> list[dict]:
        """取消收尾和 runtime cleanup 同样占用环境。"""
        return connection.execute(
            "SELECT id,thread_id,turn_id,status,worker_id,lease_expires_at FROM agent_runs "
            "WHERE uid=%s AND (status IN ('running','cancel_requested') OR runtime_cleanup_pending) ORDER BY created_at",
            (uid,),
        ).fetchall()
