# Environment Variables

This directory contains environment configuration for the Benford Analyzer application.

## Files

- `.env.example` - Template with all available environment variables
- `.env` - Local development overrides (not committed to git)

## Configuration

### Server

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Server port |

### Application

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `BenfordFingerprint` | Application name |
| `APP_VERSION` | `1.0.0` | Application version |
| `DEBUG` | `false` | Enable debug mode |

### API

| Variable | Default | Description |
|----------|---------|-------------|
| `API_TIMEOUT` | `30` | API request timeout (seconds) |
| `MAX_CONTENT_SIZE` | `10485760` | Max request size (10MB) |

### CORS

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ALLOWED_ORIGINS` | `*` | Allowed CORS origins |
| `CORS_ALLOW_CREDENTIALS` | `true` | Allow credentials in CORS |

### Security

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | - | Secret key for production (REQUIRED) |

## Docker Usage

```bash
# Copy example and configure
cp .env.example .env

# Run with environment file
docker-compose up -d
```

## Security Notes

- Never commit `.env` files to version control
- Use strong secret keys in production
- Review CORS settings before deploying publicly