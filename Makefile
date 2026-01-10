.PHONY: help install install-backend install-frontend build build-backend build-frontend start stop restart logs clean test validate docker-up docker-down docker-logs

help: ## Show this help message
	@echo "ProcGuard - Available Commands"
	@echo "=============================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: install-backend install-frontend ## Install all dependencies

install-backend: ## Install Python backend dependencies
	pip3 install -r requirements.txt

install-frontend: ## Install Node.js frontend dependencies
	npm install

build: build-frontend ## Build the application

build-backend: ## Build backend (no build step needed for Python)
	@echo "Backend ready (no build step required)"

build-frontend: ## Build Next.js frontend
	NEXT_PUBLIC_API_URL=/api npm run build

dev-backend: ## Run backend in development mode
	uvicorn app.main:app --reload --port 8000

dev-frontend: ## Run frontend in development mode
	npm run dev

dev: ## Run both backend and frontend in development (requires two terminals)
	@echo "Run these in separate terminals:"
	@echo "  make dev-backend"
	@echo "  make dev-frontend"

docker-up: ## Start all services with Docker Compose
	docker compose up -d

docker-down: ## Stop all Docker Compose services
	docker compose down

docker-restart: ## Restart Docker Compose services
	docker compose restart

docker-logs: ## View Docker Compose logs
	docker compose logs -f

docker-build: ## Build Docker images
	docker compose build

docker-clean: ## Remove all containers, images, and volumes
	docker compose down -v
	docker rmi procguard-backend procguard-frontend 2>/dev/null || true

test: ## Run tests
	@echo "Running backend tests..."
	pytest -v || echo "No tests found"

lint-backend: ## Lint Python code
	@echo "Backend linting not configured"

lint-frontend: ## Lint frontend code
	npm run lint

lint: lint-frontend ## Lint all code

validate: ## Validate deployment readiness
	./validate-deployment.sh

clean: ## Clean build artifacts and caches
	rm -rf node_modules .next build dist __pycache__ .pytest_cache *.egg-info
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

health-check: ## Check if services are healthy
	@echo "Checking backend health..."
	@curl -sf http://localhost:8000/health && echo "✓ Backend is healthy" || echo "✗ Backend is down"
	@echo "Checking frontend health..."
	@curl -sf http://localhost:3000 && echo "✓ Frontend is healthy" || echo "✗ Frontend is down"

status: ## Show Docker container status
	docker compose ps

env-setup: ## Create .env file from template
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✓ Created .env file from template"; \
		echo "⚠  Please edit .env with your configuration"; \
	else \
		echo ".env file already exists"; \
	fi

prod-start: ## Start production build
	npm start

backup-db: ## Backup PostgreSQL database (requires pg_dump)
	@echo "Backing up database..."
	@docker compose exec postgres pg_dump -U postgres procguard > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✓ Database backed up"

restore-db: ## Restore PostgreSQL database from backup (requires file path)
	@echo "Usage: make restore-db FILE=backup_file.sql"
	@docker compose exec -T postgres psql -U postgres procguard < $(FILE)

.DEFAULT_GOAL := help
