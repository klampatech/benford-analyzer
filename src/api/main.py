"""Main FastAPI application."""
import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router as analyze_router

# Environment configuration with defaults
APP_NAME = os.getenv("APP_NAME", "BenfordFingerprint")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
MAX_CONTENT_SIZE = int(os.getenv("MAX_CONTENT_SIZE", "10485760"))  # 10MB

# CORS configuration
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "*")
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "")

# External services
EXTERNAL_URL_TIMEOUT = int(os.getenv("EXTERNAL_URL_TIMEOUT", "10"))
MAX_URL_SIZE = int(os.getenv("MAX_URL_SIZE", "5242880"))  # 5MB

# Rate limiting
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true"
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))


app = FastAPI(
    title=f"{APP_NAME} API",
    description="API for analyzing numerical data compliance with Benford's Law",
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
cors_origins = CORS_ALLOWED_ORIGINS.split(",") if CORS_ALLOWED_ORIGINS != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analyze_router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": APP_VERSION,
        "app_name": APP_NAME,
        "debug": DEBUG
    }


@app.get("/api/v1/info")
async def info():
    """API information endpoint."""
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "description": "Analyzes numerical data for Benford's Law compliance",
        "debug": DEBUG,
        "endpoints": [
            {"path": "/api/v1/analyze", "method": "POST", "description": "Analyze text or URL"},
            {"path": "/health", "method": "GET", "description": "Health check"},
            {"path": "/api/v1/info", "method": "GET", "description": "API information"}
        ],
        "web_ui": "/docs",
        "documentation": "/redoc"
    }
