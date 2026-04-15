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
        # Generate text with at least 30 numbers for meaningful analysis
        numbers = [125000, 187000, 234000, 456000, 45000, 67000, 89000, 123000,
                   234000, 567000, 890000, 1230000, 2345000, 3456000, 4567000,
                   5678000, 6789000, 7890000, 8901000, 9012000, 1013000, 1124000,
                   1235000, 2346000, 3457000, 4568000, 5679000, 6780000, 7891000,
                   8902000, 9013000, 123400, 234500, 345600, 456700, 567800]
        text = "The company reported: " + ", ".join(str(n) for n in numbers)
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
