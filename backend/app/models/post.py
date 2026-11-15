from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin
from app.database.vector_type import VectorType
from app.core.config import settings

class Post(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "posts"

    author_agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    tags = Column(JSON, default=list, nullable=False)
    post_embedding = Column(VectorType(settings.EMBEDDING_DIMENSION), nullable=True)
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    author_agent = relationship("Agent", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="post", cascade="all, delete-orphan")
    routing_logs = relationship("RoutingLog", back_populates="post", cascade="all, delete-orphan")
    feedback = relationship("AgentFeedback", back_populates="post", cascade="all, delete-orphan")
