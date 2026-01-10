#!/bin/bash

# ProcGuard Unified Deployment Script
# This script deploys both frontend and backend together

set -e

echo "======================================"
echo "ProcGuard Unified Deployment Script"
echo "======================================"
echo ""

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -m, --mode MODE          Deployment mode: local, prod, or azure (default: local)"
    echo "  -h, --help               Display this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --mode local          Deploy locally using docker-compose"
    echo "  $0 --mode prod           Deploy production using docker-compose.prod.yml"
    echo "  $0 --mode azure          Deploy to Azure Container Apps"
    exit 1
}

# Default values
MODE="local"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--mode)
            MODE="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Deploy based on mode
case $MODE in
    local)
        echo "🚀 Starting local deployment..."
        echo ""
        
        # Check if Docker is running
        if ! docker info > /dev/null 2>&1; then
            echo "❌ Docker is not running. Please start Docker and try again."
            exit 1
        fi
        
        # Check if docker compose is available
        if ! docker compose version &> /dev/null; then
            echo "❌ docker compose is not available. Please install Docker Compose and try again."
            exit 1
        fi
        
        echo "📦 Building and starting services with docker compose..."
        docker compose down -v
        docker compose build
        docker compose up -d
        
        echo ""
        echo "✅ Deployment complete!"
        echo ""
        echo "Services are running:"
        echo "  - Frontend: http://localhost:3000"
        echo "  - Backend API: http://localhost:8000"
        echo "  - API Docs: http://localhost:8000/docs"
        echo "  - Database: localhost:5432"
        echo ""
        echo "To view logs: docker compose logs -f"
        echo "To stop services: docker compose down"
        ;;
        
    prod)
        echo "🚀 Starting production deployment..."
        echo ""
        
        # Check if .env.prod exists
        if [ ! -f .env.prod ]; then
            echo "⚠️  .env.prod file not found. Creating from template..."
            cat > .env.prod << EOF
# PostgreSQL Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changeme_in_production
POSTGRES_DB=procguard

# Application Configuration
AI_ENABLED=true
ENVIRONMENT=production

# Frontend Configuration (Update with your domain)
NEXT_PUBLIC_API_URL=/api
FRONTEND_PORT=3000

# CORS Configuration (Update with your domain)
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Nginx Port (80 for production)
NGINX_PORT=80
EOF
            echo "⚠️  Please update .env.prod with your production settings and run again."
            exit 1
        fi
        
        # Load environment variables
        export $(cat .env.prod | grep -v '^#' | xargs)
        
        echo "📦 Building and starting production services..."
        docker compose -f docker-compose.prod.yml down -v
        docker compose -f docker-compose.prod.yml build
        docker compose -f docker-compose.prod.yml up -d
        
        echo ""
        echo "✅ Production deployment complete!"
        echo ""
        echo "Services are running:"
        echo "  - Application: http://localhost:${NGINX_PORT:-80}"
        echo "  - Frontend (direct): http://localhost:${FRONTEND_PORT:-3000}"
        echo "  - Backend API (via nginx): http://localhost:${NGINX_PORT:-80}/api"
        echo ""
        echo "To view logs: docker compose -f docker-compose.prod.yml logs -f"
        echo "To stop services: docker compose -f docker-compose.prod.yml down"
        ;;
        
    azure)
        echo "🚀 Starting Azure deployment..."
        echo ""
        
        echo "Please enter the admin password for the PostgreSQL database:"
        read -s adminPassword
        echo ""
        
        registryPassword=$(az acr credential show --name procguardacr --query "passwords[0].value" -o tsv)
        
        az group create -n procguard-rg -l eastus
        
        az deployment group create \
          -g procguard-rg \
          -f infra/main.bicep \
          --parameters adminPassword=$adminPassword registryPassword=$registryPassword
        
        echo ""
        echo "✅ Azure deployment complete!"
        ;;
        
    *)
        echo "❌ Invalid mode: $MODE"
        usage
        ;;
esac