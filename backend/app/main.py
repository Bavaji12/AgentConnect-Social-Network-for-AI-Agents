from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import logger
from app.database.init_db import init_db
from app.workers.runner import start_worker, stop_worker
from app.api.v1 import api_v1_router
from app.security.rate_limiter import rate_limit_dependency

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and start background queue
    logger.info("Starting up AgentConnect enterprise backend service...")
    try:
        init_db()
    except Exception as e:
        logger.error(f"Error during database table initialization: {e}")

    try:
        start_worker()
    except Exception as e:
        logger.error(f"Error starting background worker: {e}")

    yield

    # Shutdown
    logger.info("Shutting down AgentConnect services...")
    stop_worker()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise Social Network for AI Agents with Multi-Stage Semantic Relevance Routing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler for unexpected crashes
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please consult backend logs."}
    )

# Health check
@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "llm_provider": settings.LLM_PROVIDER,
        "embedding_provider": settings.EMBEDDING_PROVIDER,
        "database": "connected"
    }

# Mount API v1 router
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
