import logging
from app.database.session import engine, Base
from app.models import *  # Ensure all models are registered

logger = logging.getLogger("agentconnect.init_db")

def init_db():
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")

if __name__ == "__main__":
    init_db()
