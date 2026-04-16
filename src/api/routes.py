"""FastAPI routes for Benford analysis."""
import os
from typing import Literal, List, Optional
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.core import analyze_text

# External services configuration from environment
EXTERNAL_URL_TIMEOUT = int(os.getenv("EXTERNAL_URL_TIMEOUT", "10"))
MAX_URL_SIZE = int(os.getenv("MAX_URL_SIZE", "5242880"))  # 5MB

router = APIRouter(prefix="/api/v1", tags=["analyze"])


class AnalyzeRequest(BaseModel):
    """Request body for /analyze endpoint."""
    content: str = Field(..., description="Text content or URL to analyze")
    source: Literal["article", "url"] = Field(default="article", description="Content type")
    digits: List[int] = Field(default=[1, 2], description="Digit positions to analyze")


class AnalysisResult(BaseModel):
    """Result of Benford analysis."""
    numbers_found: int
    digits_analyzed: List[int]
    results: dict
    source_used: str
    content_preview: Optional[str] = None


async def fetch_url_content(url: str) -> str:
    """Fetch and extract visible text from a URL."""
    try:
        parsed = urlparse(url)
        if not parsed.scheme:
            url = f"https://{url}"
        
        async with httpx.AsyncClient(timeout=float(EXTERNAL_URL_TIMEOUT), follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove script and style elements
        for tag in soup(["script", "style"]):
            tag.decompose()
        
        text = soup.get_text(separator=" ", strip=True)
        return text[:MAX_URL_SIZE]  # Limit to configured max size
    
    except httpx.HTTPError as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse content: {str(e)}")


@router.post("/analyze", response_model=AnalysisResult)
async def analyze(request: AnalyzeRequest) -> AnalysisResult:
    """
    Analyze text or URL for Benford's Law compliance.
    
    Accepts either raw text or a URL to fetch and analyze.
    Returns full Benford statistics and verdict.
    """
    # Fetch URL content if needed
    if request.source == "url":
        content = await fetch_url_content(request.content)
    else:
        content = request.content
    
    # Validate digits
    for d in request.digits:
        if d not in [1, 2]:
            raise HTTPException(
                status_code=422,
                detail="Only digit positions 1 and 2 are supported"
            )
    
    # Run analysis
    result = analyze_text(content, request.digits)
    
    if "error" in result:
        raise HTTPException(status_code=422, detail=result["error"])
    
    return AnalysisResult(
        numbers_found=result["numbers_found"],
        digits_analyzed=result["digits_analyzed"],
        results=result["results"],
        source_used=request.source,
        content_preview=content[:500]
    )
