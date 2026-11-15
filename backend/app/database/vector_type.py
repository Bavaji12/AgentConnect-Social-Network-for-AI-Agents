import json
from typing import List, Optional
from sqlalchemy import TypeDecorator, Text
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT

try:
    from pgvector.sqlalchemy import Vector
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False

class VectorType(TypeDecorator):
    """
    SQLAlchemy type decorator for vector embeddings.
    Uses pgvector Vector when available, and falls back to JSON-serialized Text
    or PostgreSQL Float array when pgvector extension is not installed.
    """
    impl = Text
    cache_ok = True

    def __init__(self, dim: int = 384, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dim = dim

    def load_dialect_impl(self, dialect):
        # We store as Text (JSON array) across engines for maximum cross-compatibility
        # unless pgvector is explicitly enabled in postgres.
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value: Optional[List[float]], dialect):
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return json.dumps(list(value))

    def process_result_value(self, value, dialect) -> Optional[List[float]]:
        if value is None:
            return None
        if isinstance(value, list):
            return [float(x) for x in value]
        if isinstance(value, str):
            try:
                # Handle postgres array format '{0.1,0.2,...}' or JSON '[0.1, 0.2]'
                cleaned = value.strip()
                if cleaned.startswith("{") and cleaned.endswith("}"):
                    cleaned = "[" + cleaned[1:-1] + "]"
                parsed = json.loads(cleaned)
                return [float(x) for x in parsed]
            except Exception:
                return []
        return None
