# Benford Analyzer

A statistical analysis tool that detects anomalies in numerical datasets by testing compliance with Benford's Law — the mathematical phenomenon where leading digits in naturally occurring data follow a predictable distribution.

## Overview

Benford's Law predicts that the number `1` appears as the leading digit about **30.1%** of the time, while `9` appears only about **4.6%** of the time. This counterintuitive规律 applies to many real-world datasets: river lengths, stock prices, population numbers, street addresses, etc.

**benford-analyzer** provides:
- **First and second digit distribution analysis**
- **Chi-squared statistical testing** with p-values
- **Mean Absolute Deviation (MAD)** computation
- **Human-readable verdicts** explaining findings
- **REST API** for integration with other systems
- **URL scraping** for analyzing web content

### Use Cases

| Application | What It Detects |
|-------------|-----------------|
| **Fraud Detection** | Fabricated financial data, manipulated statistics |
| **Financial Auditing** | Anomalous expense reports, revenue figures |
| **Scientific Integrity** | Questionable datasets, p-hacked results |
| **Journalism** | Data quality in reported statistics |
| **Data Quality** | Import errors, systematic rounding |

## Installation

### Prerequisites

- **Python 3.9+** (for API and analysis engine)
- **Go 1.21+** (for simple HTTP server)
- **Docker & Docker Compose** (for containerized deployment)

### Option 1: Python API

```bash
# Clone the repository
git clone https://github.com/klampatech/benford-analyzer.git
cd benford-analyzer

# Install dependencies
pip install -e .

# Or install dev dependencies
pip install -e ".[dev]"
```

### Option 2: Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Option 3: Pre-built Binary

```bash
# Download the latest release
curl -fsSL https://github.com/klampatech/benford-analyzer/releases/latest/download/benford-analyzer-linux-amd64 -o benford-analyzer
chmod +x benford-analyzer
./benford-analyzer
```

## Usage

### REST API

Start the API server:

```bash
# Python API (recommended)
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Go server (lightweight)
go run main.go
```

#### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/analyze` | Analyze text or URL for Benford compliance |
| `GET` | `/health` | Health check |
| `GET` | `/api/v1/info` | API information |
| `GET` | `/docs` | Swagger UI documentation |

#### Analyze Text

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Sample text containing numbers 123, 456, 789...",
    "source": "article",
    "digits": [1, 2]
  }'
```

#### Analyze URL

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "content": "https://example.com/article-with-numbers",
    "source": "url",
    "digits": [1, 2]
  }'
```

#### Response Format

```json
{
  "numbers_found": 847,
  "digits_analyzed": [1, 2],
  "results": {
    "1": {
      "sample_size": 847,
      "chi_squared": 12.45,
      "p_value": 0.13,
      "mad": 0.015,
      "is_suspicious": false,
      "verdict": "NORMAL",
      "digit_breakdown": [
        {"digit": 1, "expected": 0.301, "actual": 0.312, "deviation": 0.011},
        ...
      ]
    },
    "2": { ... }
  },
  "source_used": "article",
  "content_preview": "Sample text containing..."
}
```

### Python Library

```python
from src.core import analyze_benford, analyze_text

# Analyze a list of numbers
numbers = [123, 456, 789, 100, 200, 300, 1234, 5678, 9012, 3456]
results = analyze_benford(numbers, positions=[1, 2])

# Print first-digit results
first_digit = results[1]
print(f"Chi-squared: {first_digit.chi_squared}")
print(f"Verdict: {first_digit.verdict}")

# Analyze text (extracts numbers automatically)
text = "The 2019 revenue was $1,234,567 with 45,000 units sold..."
result = analyze_text(text)
print(f"Numbers found: {result['numbers_found']}")
```

### Go HTTP Server

```bash
# Run the Go server
go run main.go

# Access health endpoint
curl http://localhost:8080/health

# Access info endpoint  
curl http://localhost:8080/info
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `BenfordFingerprint` | Application name |
| `APP_VERSION` | `1.0.0` | Application version |
| `DEBUG` | `false` | Enable debug mode |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `API_TIMEOUT` | `30` | API request timeout (seconds) |
| `MAX_CONTENT_SIZE` | `10485760` | Max content size (10MB) |
| `LOG_LEVEL` | `INFO` | Logging level |
| `LOG_FORMAT` | `json` | Log format (`json` or `text`) |
| `CORS_ALLOWED_ORIGINS` | `*` | CORS allowed origins |
| `RATE_LIMIT_ENABLED` | `false` | Enable rate limiting |
| `RATE_LIMIT_PER_MINUTE` | `60` | Rate limit threshold |
| `SECRET_KEY` | - | Secret key for production |
| `EXTERNAL_URL_TIMEOUT` | `10` | URL fetch timeout (seconds) |
| `MAX_URL_SIZE` | `5242880` | Max URL content size (5MB) |

### Example: Production Configuration

```bash
export APP_NAME="BenfordAnalyzer"
export DEBUG="false"
export LOG_LEVEL="INFO"
export RATE_LIMIT_ENABLED="true"
export RATE_LIMIT_PER_MINUTE="120"
export SECRET_KEY="your-secret-key-here"
```

## Development

### Project Structure

```
benford-analyzer/
├── src/
│   ├── api/           # FastAPI REST endpoints
│   │   ├── main.py    # FastAPI application
│   │   └── routes.py  # API routes
│   ├── core/          # Core Benford analysis
│   │   └── __init__.py
│   └── engine/         # Analysis engine
│       ├── analyzer.py # Statistical analysis
│       └── verdict.py  # Verdict generation
├── tests/             # Python test suite
├── main.go           # Go HTTP server
├── main_test.go      # Go tests
└── docker-compose.yml
```

### Running Locally

```bash
# Install dependencies
pip install -e .

# Start the API server
uvicorn src.api.main:app --reload

# Or use the npm script
npm run dev
```

### Code Style

```bash
# Lint Python code
ruff check src/

# Format Python code
ruff format src/

# Lint Go code
go fmt ./...
go vet ./...
```

## Testing

### Python Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_analyzer.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Go Tests

```bash
# Run all Go tests
go test ./...

# Run with verbose output
go test -v ./...

# Run benchmarks
go test -bench=. ./...
```

### Test Categories

| Test Suite | Purpose |
|------------|---------|
| `test_core.py` | Core Benford analysis algorithms |
| `test_analyzer.py` | Statistical calculations |
| `test_verdict.py` | Verdict generation logic |
| `test_api.py` | REST API endpoints |
| `main_test.go` | Go server handlers |

## Deployment

### Docker Deployment

```yaml
# docker-compose.yml
version: '3.8'
services:
  benford-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - LOG_LEVEL=INFO
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

```bash
# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f benford-api

# Scale for load
docker-compose up -d --scale benford-api=3
```

### Manual Deployment

```bash
# Build the Go binary
go build -o benford-analyzer main.go

# Build Docker image
docker build -t benford-analyzer:latest .

# Run with environment file
cp .env.example .env
# Edit .env with production values
docker run -d \
  --name benford-api \
  -p 8000:8000 \
  --env-file .env \
  benford-analyzer:latest
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: benford-analyzer
spec:
  replicas: 3
  selector:
    matchLabels:
      app: benford-analyzer
  template:
    metadata:
      labels:
        app: benford-analyzer
    spec:
      containers:
      - name: api
        image: benford-analyzer:latest
        ports:
        - containerPort: 8000
        env:
        - name: LOG_LEVEL
          value: "INFO"
```

## Limitations

### Statistical Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **Minimum sample size** | Need at least 30 numbers for reliable results | Use larger datasets when possible |
| **Small datasets** | Results become unreliable with <100 numbers | Note confidence band in output |
| **Natural exceptions** | Certain data types don't follow Benford | Understand your data domain |
| **Digit position** | Currently supports only 1st and 2nd digits | Future versions may add more |

### Data Type Exceptions

Benford's Law **does NOT apply** to:

- **Phone numbers** (fixed prefixes)
- **Street addresses** (arbitrary assignment)
- **Tax IDs / SSNs** (structured identifiers)
- **Data with artificial bounds** (prices ending in .99)
- **Small datasets** (<30 numbers)

### Known Working Cases

Benford's Law **does apply** to:

- Financial transactions and accounting data
- Population figures
- River lengths
- Stock prices and market data
- Scientific measurements
- Electoral statistics

### Interpretation Guidelines

| Verdict | Interpretation | Action |
|---------|---------------|--------|
| **NORMAL** | Data follows expected distribution | No action needed |
| **SUSPICIOUS** | Some deviation from expected | Investigate further |
| **HIGHLY SUSPICIOUS** | Significant deviation | Manual review recommended |
| **INSUFFICIENT DATA** | Sample too small | Gather more data |

> ⚠️ **Important**: A "suspicious" verdict is a statistical signal, not proof of fraud or manipulation. Legitimate data can deviate from Benford's Law for many reasons. Always interpret results in context.

## API Reference

### POST /api/v1/analyze

**Request Body:**

```json
{
  "content": "string",           // Text or URL to analyze
  "source": "article | url",     // Content type (default: "article")
  "digits": [1, 2]              // Digit positions (default: [1, 2])
}
```

**Response:**

```json
{
  "numbers_found": 847,
  "digits_analyzed": [1, 2],
  "results": {
    "1": {
      "sample_size": 847,
      "chi_squared": 12.45,
      "p_value": 0.13,
      "mad": 0.015,
      "is_suspicious": false,
      "verdict": "NORMAL",
      "digit_breakdown": [...]
    },
    "2": { ... }
  },
  "source_used": "article",
  "content_preview": "..."
}
```

### GET /health

**Response:**

```json
{
  "status": "ok",
  "version": "1.0.0",
  "app_name": "BenfordFingerprint",
  "debug": false
}
```

### GET /api/v1/info

**Response:**

```json
{
  "name": "BenfordFingerprint",
  "version": "1.0.0",
  "description": "Analyzes numerical data for Benford's Law compliance",
  "endpoints": [...],
  "web_ui": "/docs",
  "documentation": "/redoc"
}
```

## License

MIT License - see LICENSE file for details.

## References

- [Benford's Law - Wikipedia](https://en.wikipedia.org/wiki/Benford%27s_law)
- [Nigrini, M. J. (2012). *Benford's Law: Applications for Forensic Accounting, Auditing, and Fraud Detection*](https://www.wiley.com/en-us/Benford's+Law/p/9781118152850)
- [Statistical Tests for Benford's Law](https://www.jstor.org/stable/2674260)
