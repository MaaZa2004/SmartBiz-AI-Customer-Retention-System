import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.db import engine
from app.core.limiter import limiter
from app.models.base import Base

# Automatically create tables for SQLite/MySQL if they do not exist
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database auto-creation warning: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Customer Retention & Decision Intelligence System",
    version="1.0.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root Endpoint
@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Welcome to SmartBiz AI Decision Intelligence System API",
        "docs_url": "/docs"
    }

# Include routers
from app.api.auth import router as auth_router
from app.api.predictions import router as predictions_router
from app.api.decision_engine import router as decision_engine_router
from app.api.customers import router as customers_router
from app.api.reports import router as reports_router

app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(predictions_router, prefix=settings.API_V1_STR)
app.include_router(decision_engine_router, prefix=settings.API_V1_STR)
app.include_router(customers_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
