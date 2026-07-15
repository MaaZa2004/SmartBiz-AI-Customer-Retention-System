import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "SmartBiz AI: Customer Retention & Decision Intelligence System"
    API_V1_STR: str = "/api"
    
    # Security & JWT Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "smartbiz_super_secret_session_key_9918273645")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    # Expected MySQL format: mysql+pymysql://user:pass@host:port/dbname
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./smartbiz_dev.db" # Dev/testing fallback
    )
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Rate Limiting
    RATE_LIMIT_LOGIN: str = "5 per minute"

    class Config:
        case_sensitive = True

settings = Settings()
