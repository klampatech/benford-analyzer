"""Tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Tests for GET /health."""
    
    def test_health_returns_ok(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestInfoEndpoint:
    """Tests for GET /api/v1/info."""
    
    def test_info_returns_metadata(self):
        response = client.get("/api/v1/info")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "BenfordFingerprint"
        assert data["version"] == "1.0.0"
        assert "endpoints" in data


class TestAnalyzeEndpoint:
    """Tests for POST /api/v1/analyze."""
    
    def test_analyze_with_article_text(self):
        """Test analysis with article content."""
        text = """
        The company reported revenue of 125000 dollars in Q1.
        Q2 saw an increase to 187000 dollars.
        Q3 and Q4 brought 234000 and 456000 respectively.
        Total for the year exceeded 1 million dollars.
        Marketing spend was 45000, 67000, 89000, and 123000 across quarters.
        """
        response = client.post("/api/v1/analyze", json={
            "content": text,
            "source": "article",
            "digits": [1]
        })
        assert response.status_code == 200
        data = response.json()
        assert "numbers_found" in data
        assert data["source_used"] == "article"
    
    def test_analyze_requires_content(self):
        """Test that content is required."""
        response = client.post("/api/v1/analyze", json={
            "source": "article"
        })
        assert response.status_code == 422
    
    def test_analyze_invalid_digits(self):
        """Test with invalid digit position."""
        response = client.post("/api/v1/analyze", json={
            "content": "Some text with numbers 12345 and 67890",
            "source": "article",
            "digits": [3]
        })
        assert response.status_code == 422
    
    def test_analyze_insufficient_data(self):
        """Test with too few numbers."""
        response = client.post("/api/v1/analyze", json={
            "content": "Only 1 number here",
            "source": "article",
            "digits": [1]
        })
        # Should return 422 for insufficient data
        assert response.status_code == 422
