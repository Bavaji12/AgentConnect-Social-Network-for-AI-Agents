from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin

class AgentFeedback(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "agent_feedback"

    agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    feedback_type = Column(String(50), nullable=False)  # ENGAGED, IGNORED, IRRELEVANT, HELPFUL
    relevance_rating = Column(Float, default=1.0, nullable=False)  # Rating e.g. 0.0 - 1.0 or 1-5

    # Relationships
    agent = relationship("Agent", back_populates="feedback")
    post = relationship("Post", back_populates="feedback")
