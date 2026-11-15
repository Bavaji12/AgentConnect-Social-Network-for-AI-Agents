from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin
from app.database.vector_type import VectorType
from app.core.config import settings

class Agent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "agents"

    company_name = Column(String(255), nullable=False, index=True)
    agent_name = Column(String(255), nullable=False)
    industry_category = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    interest_manifesto = Column(Text, nullable=False)
    interest_embedding = Column(VectorType(settings.EMBEDDING_DIMENSION), nullable=True)
    webhook_url = Column(String(500), nullable=False)
    api_key_hash = Column(String(255), nullable=False, index=True)
    trust_score = Column(Float, default=1.0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    response_mode = Column(String(50), default="auto", nullable=False)  # "auto", "human_approval", "ignore"
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    posts = relationship("Post", back_populates="author_agent", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author_agent", cascade="all, delete-orphan")
    sent_notifications = relationship(
        "Notification",
        foreign_keys="Notification.source_agent_id",
        back_populates="source_agent"
    )
    received_notifications = relationship(
        "Notification",
        foreign_keys="Notification.target_agent_id",
        back_populates="target_agent"
    )
    routing_logs = relationship("RoutingLog", back_populates="target_agent")
    feedback = relationship("AgentFeedback", back_populates="agent")
