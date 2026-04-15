"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router as analyze_router

app = FastAPI(
    title="BenfordFingerprint API",
    description="API for analyzing numerical data compliance with Benford's Law",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analyze_router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "1.0.0"}


@app.get("/api/v1/info")
async def info():
    """API information endpoint."""
    return {
        "name": "BenfordFingerprint",
        "version": "1.0.0",
        "description": "Analyzes numerical data for Benford's Law compliance",
        "endpoints": [
            {"path": "/api/v1/analyze", "method": "POST", "description": "Analyze text or URL"},
            {"path": "/health", "method": "GET", "description": "Health check"},
            {"path": "/api/v1/info", "method": "GET", "description": "API information"}
        ],
        "web_ui": "/docs",
        "documentation": "/redoc"
    }
