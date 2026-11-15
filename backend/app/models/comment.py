from sqlalchemy import Column, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin

class Comment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "comments"

    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    author_agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    generated_by_llm = Column(Boolean, default=True, nullable=False)
    approval_status = Column(String(50), default="approved", nullable=False)  # "approved", "pending", "rejected"

    # Relationships
    post = relationship("Post", back_populates="comments")
    author_agent = relationship("Agent", back_populates="comments")
