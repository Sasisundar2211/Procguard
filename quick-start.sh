#!/bin/bash

# ProcGuard Quick Start Script
# This script helps you quickly set up and deploy ProcGuard

set -e

echo "🛡️  ProcGuard Quick Start"
echo "========================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓${NC} Created .env file"
    echo -e "${YELLOW}⚠${NC}  Please edit .env with your configuration"
    echo ""
fi

# Display menu
echo "Choose deployment method:"
echo "1) Docker Compose (recommended for local/server)"
echo "2) Manual setup (Node.js + Python)"
echo "3) Validation only (check if ready to deploy)"
echo "4) Exit"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo ""
        echo -e "${BLUE}Starting Docker Compose deployment...${NC}"
        echo ""
        
        # Check if Docker is available
        if ! command -v docker &> /dev/null; then
            echo -e "${YELLOW}⚠${NC}  Docker is not installed"
            echo "Please install Docker from: https://docs.docker.com/get-docker/"
            exit 1
        fi
        
        # Check if docker compose is available
        if ! docker compose version &> /dev/null; then
            echo -e "${YELLOW}⚠${NC}  Docker Compose is not available"
            echo "Please install Docker Compose v2"
            exit 1
        fi
        
        echo "Building and starting services..."
        docker compose up -d --build
        
        echo ""
        echo -e "${GREEN}✓${NC} Services started successfully!"
        echo ""
        echo "Waiting for services to be ready..."
        sleep 10
        
        echo ""
        echo "Service status:"
        docker compose ps
        
        echo ""
        echo -e "${GREEN}🚀 ProcGuard is running!${NC}"
        echo ""
        echo "Access the application at:"
        echo "  Frontend:  http://localhost:3000"
        echo "  Backend:   http://localhost:8000"
        echo "  API Docs:  http://localhost:8000/docs"
        echo ""
        echo "Useful commands:"
        echo "  View logs:     docker compose logs -f"
        echo "  Stop:          docker compose down"
        echo "  Restart:       docker compose restart"
        echo ""
        ;;
        
    2)
        echo ""
        echo -e "${BLUE}Manual setup${NC}"
        echo ""
        
        # Check Node.js
        if ! command -v node &> /dev/null; then
            echo -e "${YELLOW}⚠${NC}  Node.js is not installed"
            echo "Please install Node.js 20+ from: https://nodejs.org/"
            exit 1
        fi
        
        # Check Python
        if ! command -v python3 &> /dev/null; then
            echo -e "${YELLOW}⚠${NC}  Python is not installed"
            echo "Please install Python 3.12+ from: https://www.python.org/"
            exit 1
        fi
        
        echo "1. Installing backend dependencies..."
        pip3 install -r requirements.txt
        
        echo ""
        echo "2. Installing frontend dependencies..."
        npm install
        
        echo ""
        echo -e "${GREEN}✓${NC} Dependencies installed"
        echo ""
        echo "To start the services manually:"
        echo ""
        echo "Backend (in one terminal):"
        echo "  export DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/procguard"
        echo "  uvicorn app.main:app --reload --port 8000"
        echo ""
        echo "Frontend (in another terminal):"
        echo "  export NEXT_PUBLIC_API_URL=http://localhost:8000"
        echo "  npm run dev"
        echo ""
        echo "Note: You'll need a PostgreSQL database running first!"
        echo ""
        ;;
        
    3)
        echo ""
        echo -e "${BLUE}Running deployment validation...${NC}"
        echo ""
        ./validate-deployment.sh
        ;;
        
    4)
        echo "Exiting..."
        exit 0
        ;;
        
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac
