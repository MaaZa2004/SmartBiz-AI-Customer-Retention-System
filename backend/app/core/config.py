import os
from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import List, Union

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "SmartBiz AI: Customer Retention & Decision Intelligence System"
    API_V1_STR: str = "/api"
    
    # Security & JWT Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
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
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return v
    
    # Rate Limiting
    RATE_LIMIT_LOGIN: str = "5 per minute"

    class Config:
        case_sensitive = True

settings = Settings()

import sys
if not settings.SECRET_KEY and "pytest" not in sys.modules:
    raise RuntimeError(
        "SECRET_KEY environment variable is not set. Generate one with "
        "`python -c \"import secrets; print(secrets.token_hex(32))\"` "
        "and set it as an environment variable before starting the app."
    )
