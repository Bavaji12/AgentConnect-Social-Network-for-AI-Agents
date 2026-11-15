from sqlalchemy import Column, String, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin

class RoutingLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "routing_logs"

    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    target_agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    semantic_score = Column(Float, nullable=False)
    keyword_score = Column(Float, nullable=False)
    industry_score = Column(Float, nullable=False)
    final_score = Column(Float, nullable=False)
    routing_decision = Column(String(50), nullable=False, index=True)  # NOTIFIED, FILTERED_OUT, THRESHOLD_NOT_MET
    relevance_explanation = Column(Text, nullable=True)

    # Relationships
    post = relationship("Post", back_populates="routing_logs")
    target_agent = relationship("Agent", back_populates="routing_logs")
