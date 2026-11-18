"""业务 PostgreSQL 映射。"""

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKeyConstraint,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from rag.infrastructure.postgres.base import BusinessBase as Base
from rag.shared.datetime import utc_now

UNVIEWED_RUN_MARKER = "__unviewed__"


class Session(Base):
    """保存与 Thread 一对一的长期交互会话。"""

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="Primary key")
    thread_id = Column(String(64), nullable=False, comment="Thread ID (UUID)")
    config_snapshot = Column(JSON, nullable=True)
    creation_request_id = Column(String(64), nullable=True, comment="新建 Session 幂等请求 ID")
    uid = Column(String(128), index=True, nullable=False, comment="UID")
    app_id = Column(String(64), nullable=True, comment="Public API 可信 APP 归属")
    # 保存 Agent.slug 值；列名与契约字段 agent_id 一致。
    agent_id = Column(String(64), index=True, nullable=False, comment="Agent slug (agent_id)")
    title = Column(String(255), nullable=True, comment="Session title")
    status = Column(String(20), default="active", comment="Status: active/archived/deleted")
    queue_paused = Column(Boolean, nullable=False, default=False, server_default="false")
    is_pinned = Column(Boolean, default=False, nullable=False, index=True, comment="Is pinned to top")
    last_viewed_run_id = Column(String(64), nullable=True, comment="Latest top-level run id viewed by user")
    project_id = Column(String(64), nullable=False, index=True, comment="Session 绑定的 Project ID")
    created_at = Column(DateTime(timezone=True), default=utc_now, comment="Creation time")
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, comment="Update time")
    extra_metadata = Column(JSON, nullable=True, comment="Additional metadata")

    # Relationships
    messages = relationship("Message", back_populates="agent_session", cascade="all, delete-orphan")
    project = relationship("Project", back_populates="sessions")

    __table_args__ = (
        UniqueConstraint("thread_id", name="uq_sessions_thread_id"),
        ForeignKeyConstraint(
            ["project_id", "uid"],
            ["projects.id", "projects.uid"],
            name="fk_sessions_project_uid",
        ),
        UniqueConstraint("uid", "creation_request_id", name="uq_sessions_uid_creation_request_id"),
        UniqueConstraint("id", "thread_id", name="uq_sessions_id_thread"),
    )
