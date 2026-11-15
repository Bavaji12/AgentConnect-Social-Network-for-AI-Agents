from sqlalchemy import Column, String, Text, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin

class Notification(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "notifications"

    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    source_agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    target_agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    relevance_score = Column(Float, nullable=False)
    relevance_explanation = Column(Text, nullable=False)
    delivery_status = Column(String(50), default="PENDING", nullable=False, index=True)  # PENDING, DELIVERED, FAILED, VIEWED, ENGAGED, IGNORED
    retry_count = Column(Integer, default=0, nullable=False)
    delivered_at = Column(DateTime, nullable=True)

    # Relationships
    post = relationship("Post", back_populates="notifications")
    source_agent = relationship("Agent", foreign_keys=[source_agent_id], back_populates="sent_notifications")
    target_agent = relationship("Agent", foreign_keys=[target_agent_id], back_populates="received_notifications")
