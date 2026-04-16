#!/bin/bash

# Benford Analyzer Quick Start Script
# This script sets up and runs the Benford Analyzer application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
PORT=8000
HOST=0.0.0.0

# Parse command line arguments
MODE=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --docker)
            MODE="docker"
            shift
            ;;
        --python)
            MODE="python"
            shift
            ;;
        --go)
            MODE="go"
            shift
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --docker     Use Docker to run the application"
            echo "  --python     Use Python (uvicorn) to run the application (default)"
            echo "  --go         Use Go HTTP server to run the application"
            echo "  --port N     Port to run the server on (default: 8000)"
            echo "  -h, --help   Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Set default mode if not specified
MODE="${MODE:-python}"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           Benford Analyzer - Quick Start                ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prereqs() {
    local all_good=true
    
    if [ "$MODE" = "python" ]; then
        if ! command_exists python3; then
            echo -e "${RED}✗ Python 3 is required but not found${NC}"
            all_good=false
        else
            echo -e "${GREEN}✓ Python 3 found${NC}"
        fi
        
        if ! command_exists pip3; then
            echo -e "${RED}✗ pip3 is required but not found${NC}"
            all_good=false
        else
            echo -e "${GREEN}✓ pip3 found${NC}"
        fi
    fi
    
    if [ "$MODE" = "go" ]; then
        if ! command_exists go; then
            echo -e "${RED}✗ Go is required but not found${NC}"
            all_good=false
        else
            echo -e "${GREEN}✓ Go found${NC}"
        fi
    fi
    
    if [ "$MODE" = "docker" ]; then
        if ! command_exists docker; then
            echo -e "${RED}✗ Docker is required but not found${NC}"
            all_good=false
        else
            echo -e "${GREEN}✓ Docker found${NC}"
        fi
        
        if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
            echo -e "${RED}✗ Docker Compose is required but not found${NC}"
            all_good=false
        else
            echo -e "${GREEN}✓ Docker Compose found${NC}"
        fi
    fi
    
    if [ "$all_good" = false ]; then
        echo ""
        echo -e "${RED}Prerequisites not met. Please install required dependencies.${NC}"
        exit 1
    fi
}

# Function to setup Python environment
setup_python() {
    echo ""
    echo -e "${YELLOW}Setting up Python environment...${NC}"
    
    # Check for pyproject.toml or setup.py
    if [ ! -f "pyproject.toml" ] && [ ! -f "setup.py" ]; then
        echo -e "${RED}✗ No pyproject.toml or setup.py found. Please ensure the project is properly set up.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Project configuration found${NC}"
    
    # Check if virtual environment exists, create if not
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    else
        echo "Using existing virtual environment..."
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo "Installing dependencies..."
    pip install --quiet -e . 2>/dev/null || pip install -e .
    
    echo -e "${GREEN}✓ Python environment ready${NC}"
}

# Function to check if server is running
is_server_running() {
    lsof -Pi ":$PORT" -sTCP:LISTEN -t >/dev/null 2>&1
}

# Function to wait for server to be ready
wait_for_server() {
    local max_attempts=30
    local attempt=0
    echo "Waiting for server to start..."
    while ! curl -s "http://localhost:$PORT/health" >/dev/null 2>&1; do
        attempt=$((attempt + 1))
        if [ $attempt -gt $max_attempts ]; then
            echo -e "${RED}✗ Server failed to start within timeout${NC}"
            return 1
        fi
        sleep 0.5
    done
    echo -e "${GREEN}✓ Server is running${NC}"
    return 0
}

# Function to start Python server
start_python() {
    echo ""
    echo -e "${YELLOW}Starting Benford Analyzer (Python/FastAPI)...${NC}"
    echo ""
    echo -e "Server will be available at:"
    echo -e "  ${GREEN}http://localhost:${PORT}${NC}"
    echo -e "  ${GREEN}http://127.0.0.1:${PORT}${NC}"
    echo ""
    echo -e "API Documentation:"
    echo -e "  ${BLUE}http://localhost:${PORT}/docs${NC}"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
    echo ""
    
    # Check if port is in use
    if is_server_running; then
        echo -e "${RED}Port $PORT is already in use. Server may already be running.${NC}"
        echo ""
        echo "Testing existing server:"
        curl -s "http://localhost:$PORT/health"
        echo ""
        exit 0
    fi
    
    # Start the server
    uvicorn src.api.main:app --host "$HOST" --port "$PORT" --reload
}

# Function to start Go server
start_go() {
    echo ""
    echo -e "${YELLOW}Starting Benford Analyzer (Go HTTP Server)...${NC}"
    echo ""
    echo -e "Server will be available at:"
    echo -e "  ${GREEN}http://localhost:8080${NC}"
    echo -e "  ${GREEN}http://127.0.0.1:8080${NC}"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
    echo ""
    
    go run main.go
}

# Function to start Docker
start_docker() {
    echo ""
    echo -e "${YELLOW}Starting Benford Analyzer (Docker)...${NC}"
    echo ""
    echo -e "Server will be available at:"
    echo -e "  ${GREEN}http://localhost:${PORT}${NC}"
    echo ""
    echo -e "API Documentation:"
    echo -e "  ${BLUE}http://localhost:${PORT}/docs${NC}"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
    echo ""
    
    docker-compose up --build
}

# Function to run a demo analysis
run_demo() {
    echo ""
    echo -e "${YELLOW}Running demo analysis...${NC}"
    echo ""
    
    # Sample data that follows Benford's Law - more realistic financial data
    DEMO_TEXT="Financial analysis report: Q1 2024 revenue totaled 1234567 dollars across 1234 stores. Average transaction value was 1234 dollars. The 2024 population census shows 987654 residents in metro area. Stock prices ranged from 123 to 456 dollars. Scientific measurements: 789 samples averaging 1234 grams. Quarterly figures: 1111, 2222, 3333, 4444, 5555, 6666, 7777, 8888, 9999, 1122, 3344, 5566, 7788, 9900, 1212, 2323, 3434, 4545, 5656, 6767, 7878, 8989, 9090, 1010, 2020, 3030, 4040, 5050, 6060, 7070"
    
    echo "Demo text:"
    echo "$DEMO_TEXT"
    echo ""
    
    # Send request
    echo "Sending analysis request..."
    curl -s -X POST "http://localhost:${PORT}/api/v1/analyze" \
        -H "Content-Type: application/json" \
        -d "{\"content\": \"$DEMO_TEXT\", \"source\": \"article\", \"digits\": [1, 2]}" | python3 -m json.tool 2>/dev/null || \
    curl -s -X POST "http://localhost:${PORT}/api/v1/analyze" \
        -H "Content-Type: application/json" \
        -d "{\"content\": \"$DEMO_TEXT\", \"source\": \"article\", \"digits\": [1, 2]}"
    echo ""
}

# Main execution
case $MODE in
    python)
        setup_python
        
        # Check if server is already running
        if is_server_running; then
            echo ""
            echo -e "${GREEN}Server is already running on port $PORT${NC}"
            echo ""
            read -p "Run demo analysis? (y/n): " -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                run_demo
            fi
            exit 0
        fi
        
        echo ""
        read -p "Run demo analysis? (y/n): " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Starting server in background for demo..."
            nohup uvicorn src.api.main:app --host "$HOST" --port "$PORT" > /tmp/benford.log 2>&1 &
            SERVER_PID=$!
            
            wait_for_server || exit 1
            run_demo
            
            echo ""
            echo "Stopping demo server..."
            kill $SERVER_PID 2>/dev/null || true
        else
            start_python
        fi
        ;;
    go)
        start_go
        ;;
    docker)
        start_docker
        ;;
esac
