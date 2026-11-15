import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from app.core.config import settings

logger = logging.getLogger("agentconnect.database")

Base = declarative_base()

def get_engine():
    db_url = settings.DATABASE_URL
    connect_args = {}
    
    if db_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        return create_engine(
            db_url,
            connect_args=connect_args,
            echo=settings.SQL_ECHO
        )
    else:
        try:
            # PostgreSQL engine with robust connection pooling
            engine = create_engine(
                db_url,
                pool_size=20,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=settings.SQL_ECHO
            )
            # Test connection
            with engine.connect() as conn:
                pass
            return engine
        except Exception as e:
            logger.warning(f"Could not connect to PostgreSQL at {db_url}: {e}. Falling back to SQLite.")
            return create_engine(
                "sqlite:///./agentconnect.db",
                connect_args={"check_same_thread": False},
                echo=settings.SQL_ECHO
            )

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
