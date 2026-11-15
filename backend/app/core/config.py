import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "AgentConnect"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql+psycopg2://postgres@localhost:5432/agentconnect",
        description="PostgreSQL connection string. Fallback to sqlite if needed."
    )
    SQL_ECHO: bool = False
    
    # Redis & Event Bus
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for async workers. In-memory fallback if unreachable."
    )
    USE_IN_MEMORY_REDIS_FALLBACK: bool = True
    
    # Security & Auth
    JWT_SECRET: str = "agentconnect-enterprise-grade-secret-key-super-secure-32chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # AI Providers
    # "deterministic", "gemini", "openai"
    LLM_PROVIDER: str = "deterministic"
    EMBEDDING_PROVIDER: str = "deterministic"
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None
    
    # Vector & Routing Configuration
    EMBEDDING_DIMENSION: int = 384
    RELEVANCE_THRESHOLD: float = 0.75
    TOP_K_CANDIDATES: int = 50
    
    # Reranking Weights
    WEIGHT_SEMANTIC: float = 0.45
    WEIGHT_KEYWORD: float = 0.20
    WEIGHT_INDUSTRY: float = 0.25
    WEIGHT_FEEDBACK: float = 0.10
    
    # Webhooks & Retries
    WEBHOOK_TIMEOUT: int = 10
    MAX_WEBHOOK_RETRIES: int = 3
    WEBHOOK_SIGNING_SECRET: str = "agentconnect-hmac-webhook-secret-key-2026"
    ALLOW_PRIVATE_IPS: bool = True  # Allowed in local development, blocked in strict production mode
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 120

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()
