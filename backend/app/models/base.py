import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from app.database.session import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class UUIDPrimaryKeyMixin:
    id = Column(
        String(36),
        primary_key=True,
        default=generate_uuid,
        index=True
    )

class TimestampMixin:
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
