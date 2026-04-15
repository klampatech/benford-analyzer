# Docker Deployment

## Quick Start

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Manual Build

```bash
# Build image
docker build -t benford-analyzer:latest .

# Run container
docker run -p 8000:8000 benford-analyzer:latest
```

## API Endpoints

- Health: `GET http://localhost:8000/health`
- Info: `GET http://localhost:8000/api/v1/info`
- Analyze: `POST http://localhost:8000/api/v1/analyze`
- Docs: `http://localhost:8000/docs`

## Development

```bash
# Run with live code reloading
docker-compose --profile dev up benford-dev
```