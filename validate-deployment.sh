#!/bin/bash

# ProcGuard Deployment Validation Script
# This script validates that all components are ready for deployment

set -e

echo "🔍 ProcGuard Deployment Validation"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Validation counters
PASS=0
FAIL=0
WARN=0

# Helper functions
pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASS++))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAIL++))
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARN++))
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "1. Checking Prerequisites..."
echo "----------------------------"

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    pass "Node.js installed: $NODE_VERSION"
    if [[ "$NODE_VERSION" < "v20" ]]; then
        warn "Node.js version should be 20 or higher"
    fi
else
    fail "Node.js is not installed"
fi

# Check npm
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    pass "npm installed: $NPM_VERSION"
else
    fail "npm is not installed"
fi

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    pass "Python installed: $PYTHON_VERSION"
else
    fail "Python is not installed"
fi

# Check pip
if command_exists pip3; then
    PIP_VERSION=$(pip3 --version)
    pass "pip installed: $PIP_VERSION"
else
    fail "pip is not installed"
fi

# Check Docker
if command_exists docker; then
    DOCKER_VERSION=$(docker --version)
    pass "Docker installed: $DOCKER_VERSION"
else
    warn "Docker is not installed (optional for local deployment)"
fi

# Check Docker Compose
if command_exists docker-compose || docker compose version >/dev/null 2>&1; then
    if command_exists docker-compose; then
        COMPOSE_VERSION=$(docker-compose --version)
    else
        COMPOSE_VERSION=$(docker compose version)
    fi
    pass "Docker Compose installed: $COMPOSE_VERSION"
else
    warn "Docker Compose is not installed (optional for local deployment)"
fi

echo ""
echo "2. Checking Project Files..."
echo "----------------------------"

# Check required files
REQUIRED_FILES=(
    "package.json"
    "requirements.txt"
    "Dockerfile"
    "Dockerfile.backend"
    "docker-compose.yml"
    "app/main.py"
    "next.config.ts"
    "vercel.json"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        pass "Found: $file"
    else
        fail "Missing: $file"
    fi
done

echo ""
echo "3. Checking Configuration..."
echo "----------------------------"

# Check for .env file
if [ -f ".env" ]; then
    pass "Found .env file"
    
    # Check for required environment variables
    if grep -q "DATABASE_URL" .env; then
        pass "DATABASE_URL configured in .env"
    else
        warn "DATABASE_URL not found in .env"
    fi
else
    warn ".env file not found (required for local development)"
fi

# Check vercel.json
if [ -f "vercel.json" ]; then
    if grep -q "api/:path*" vercel.json; then
        pass "Vercel API routing configured"
    else
        warn "Vercel API routing might not be configured correctly"
    fi
fi

echo ""
echo "4. Testing Dependencies..."
echo "----------------------------"

# Test Python imports
if command_exists python3; then
    if python3 -c "from app.main import app; print('OK')" 2>/dev/null; then
        pass "Backend imports successfully"
    else
        fail "Backend has import errors"
    fi
fi

# Check if node_modules exists
if [ -d "node_modules" ]; then
    pass "Frontend dependencies installed"
else
    warn "Frontend dependencies not installed (run: npm install)"
fi

# Check if Python packages are installed
if pip3 list | grep -q "fastapi"; then
    pass "Backend dependencies installed"
else
    warn "Backend dependencies not installed (run: pip install -r requirements.txt)"
fi

echo ""
echo "5. Testing Build Process..."
echo "----------------------------"

# Test Next.js build (skip for now to save time)
if [ -d "node_modules" ]; then
    echo "Skipping frontend build test (run 'npm run build' manually to test)"
    warn "Frontend build not tested (run manually)"
else
    warn "Skipping frontend build (dependencies not installed)"
fi

echo ""
echo "6. Checking Docker Configuration..."
echo "----------------------------"

if command_exists docker; then
    # Skip Docker build test to save time
    warn "Docker build not tested (run manually: docker build -f Dockerfile.backend -t test .)"
else
    warn "Skipping Docker validation (Docker not installed)"
fi

echo ""
echo "=================================="
echo "Validation Summary"
echo "=================================="
echo -e "${GREEN}Passed: $PASS${NC}"
echo -e "${YELLOW}Warnings: $WARN${NC}"
echo -e "${RED}Failed: $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✓ All critical checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. For local deployment: docker-compose up"
    echo "  2. For Vercel deployment: See DEPLOYMENT.md"
    echo "  3. For Azure deployment: Run ./deploy.sh"
    exit 0
else
    echo -e "${RED}✗ Some critical checks failed. Please fix the issues above.${NC}"
    exit 1
fi
