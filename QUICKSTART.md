# Quick Start Guide

Get ProcGuard up and running in minutes!

## Prerequisites

- Docker and Docker Compose V2
- At least 4GB of RAM
- Ports 3000, 8000, and 5432 available

## Option 1: Using the Deployment Script (Recommended)

### Local Development

```bash
# Make the script executable
chmod +x deploy.sh

# Deploy everything with one command
./deploy.sh --mode local
```

That's it! The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Production Deployment

```bash
# Deploy in production mode
./deploy.sh --mode prod
```

Access the application at http://localhost

### Azure Deployment

```bash
# Deploy to Azure Container Apps
./deploy.sh --mode azure
```

## Option 2: Manual Docker Compose

### Local Development

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### Production

```bash
# Create production environment file
cp .env.example .env.prod

# Edit .env.prod with your settings
nano .env.prod

# Start production services
docker compose -f docker-compose.prod.yml up -d
```

## What Gets Deployed?

The unified deployment includes:

1. **PostgreSQL Database** - Persistent data storage
2. **Backend API** - FastAPI application
3. **Frontend** - Next.js application
4. **Nginx** (production only) - Reverse proxy

## Verify Deployment

Check that all services are running:

```bash
# Check service status
docker compose ps

# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000
```

## Common Commands

```bash
# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f frontend

# Restart a service
docker compose restart backend

# Stop all services
docker compose down

# Stop and remove all data
docker compose down -v
```

## Troubleshooting

### Services won't start
```bash
# Check Docker is running
docker --version

# View detailed logs
docker compose logs
```

### Port conflicts
```bash
# Check what's using the ports
lsof -i :3000
lsof -i :8000
lsof -i :5432

# Kill conflicting process or change ports in docker-compose.yml
```

### Database connection issues
```bash
# Check if database is running
docker compose ps postgres

# View database logs
docker compose logs postgres
```

## Next Steps

- Read the full [DEPLOYMENT.md](./DEPLOYMENT.md) for advanced configuration
- Check the [README.md](./README.md) for development instructions
- Access API documentation at http://localhost:8000/docs

## Need Help?

- Check [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed troubleshooting
- Review logs: `docker compose logs -f`
- Open an issue on GitHub

---

**Enjoy using ProcGuard! 🚀**
