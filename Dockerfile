# Build stage
FROM python:3.13-slim AS builder

WORKDIR /app

# Install uv for faster package installation
COPY --from=python:3.13-slim /usr/local/bin/pip /usr/local/bin/pip
RUN pip install --no-cache-dir uv

# Copy requirements first for better caching
COPY package.json .env.example ./

# Install dependencies
RUN uv pip install --system --no-cache -r package.json

# Copy source code
COPY src/ ./src/
COPY tests/ ./tests/

# Production stage
FROM python:3.13-slim AS production

WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --from=builder /app/src ./src

# Copy environment template
COPY --from=builder /app/.env.example .env.example

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV APP_NAME=BenfordFingerprint
ENV APP_VERSION=1.0.0

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

# Run the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]