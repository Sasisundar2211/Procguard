# 🚀 ProcGuard Deployment Guide

This guide provides comprehensive instructions for deploying ProcGuard across multiple platforms.

## Table of Contents

1. [Quick Start (Docker Compose)](#quick-start-docker-compose)
2. [Vercel Deployment](#vercel-deployment)
3. [Azure Container Apps](#azure-container-apps)
4. [Manual Deployment](#manual-deployment)
5. [Environment Variables](#environment-variables)
6. [Health Checks](#health-checks)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start (Docker Compose)

The fastest way to deploy ProcGuard locally or on any server with Docker installed.

### Prerequisites

- Docker (20.10+)
- Docker Compose (2.0+)

### Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Sasisundar2211/Procguard.git
   cd Procguard
   ```

2. **Start all services**:
   ```bash
   docker-compose up -d
   ```

3. **Verify deployment**:
   ```bash
   # Check service status
   docker-compose ps
   
   # View logs
   docker-compose logs -f
   
   # Test health endpoints
   curl http://localhost:8000/health
   curl http://localhost:3000
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

5. **Stop services**:
   ```bash
   docker-compose down
   ```

6. **Clean up (including database)**:
   ```bash
   docker-compose down -v
   ```

---

## Vercel Deployment

Deploy the full-stack application to Vercel with serverless functions.

### Prerequisites

- Vercel account (https://vercel.com)
- GitHub repository connected to Vercel
- Cloud PostgreSQL database (Neon, Supabase, or Azure)

### Configuration

1. **Database Setup**:
   - Create a PostgreSQL database on Neon, Supabase, or Azure
   - Get your connection string: `postgresql://user:password@host:port/database`

2. **Import to Vercel**:
   - Go to Vercel Dashboard → Add New Project
   - Import your GitHub repository
   - Keep Root Directory as `./` (deploy entire monorepo)

3. **Environment Variables** (in Vercel Project Settings):

   | Variable | Value | Description |
   |----------|-------|-------------|
   | `DATABASE_URL` | `postgresql://...` | Your PostgreSQL connection string |
   | `NEXT_PUBLIC_API_URL` | `/api` | **Critical**: Use relative path for API calls |
   | `PYTHON_VERSION` | `3.12` | Python runtime version |
   | `AI_ENABLED` | `false` | Enable/disable AI features |
   | `ENVIRONMENT` | `production` | Environment identifier |

4. **Deploy**:
   - Click "Deploy"
   - Vercel will automatically build and deploy both frontend and backend

### How It Works

- The `vercel.json` routes all `/api/*` requests to the FastAPI backend
- Frontend calls `/api/*` which are same-origin (no CORS issues)
- Backend runs as serverless functions
- Frontend is served as static/edge content

### Troubleshooting Vercel

If you see "Backend Offline":
1. Check Vercel Function Logs
2. Verify `DATABASE_URL` is correct and allows connections from `0.0.0.0/0`
3. Ensure `NEXT_PUBLIC_API_URL` is set to `/api`

---

## Azure Container Apps

Deploy using Azure Container Apps with the provided Bicep templates.

### Prerequisites

- Azure account with active subscription
- Azure CLI installed
- Docker for building images
- Azure Container Registry (ACR)

### Steps

1. **Build and push Docker images**:
   ```bash
   # Login to Azure
   az login
   
   # Create container registry
   az acr create --resource-group procguard-rg \
     --name procguardacr --sku Basic
   
   # Login to ACR
   az acr login --name procguardacr
   
   # Build and push backend
   docker build -f Dockerfile.backend -t procguardacr.azurecr.io/procguard-api:latest .
   docker push procguardacr.azurecr.io/procguard-api:latest
   
   # Build and push frontend
   docker build --build-arg NEXT_PUBLIC_API_URL=/api \
     -t procguardacr.azurecr.io/procguard-ui:latest .
   docker push procguardacr.azurecr.io/procguard-ui:latest
   ```

2. **Deploy infrastructure**:
   ```bash
   # Run the deployment script
   ./deploy.sh
   ```

3. **Access your application**:
   - The script will output the URL of your deployed application
   - Format: `https://procguard-ui.*.azurecontainerapps.io`

### Configuration Files

- `infra/main.bicep` - Main infrastructure definition
- `infra/container.bicep` - Container app configuration
- `infra/postgres.bicep` - PostgreSQL database
- `infra/storage.bicep` - Azure storage account

---

## Manual Deployment

Deploy to any server or cloud platform manually.

### Prerequisites

- Server with SSH access
- Node.js 20+ and npm
- Python 3.12+
- PostgreSQL 15+

### Backend Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   export DATABASE_URL="postgresql+psycopg2://user:pass@host:5432/procguard"
   export AI_ENABLED="false"
   export ENVIRONMENT="production"
   ```

3. **Run database migrations** (if using Alembic):
   ```bash
   alembic upgrade head
   ```

4. **Start the backend**:
   ```bash
   # Development
   uvicorn app.main:app --reload --port 8000
   
   # Production
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

### Frontend Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Set environment variables**:
   ```bash
   export NEXT_PUBLIC_API_URL="http://your-backend-url:8000"
   ```

3. **Build the frontend**:
   ```bash
   npm run build
   ```

4. **Start the frontend**:
   ```bash
   npm start
   ```

### Using a Process Manager

For production, use PM2 or systemd to manage processes:

```bash
# Install PM2
npm install -g pm2

# Start backend
pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8000" --name procguard-api

# Start frontend
pm2 start "npm start" --name procguard-ui

# Save configuration
pm2 save

# Set to start on boot
pm2 startup
```

---

## Environment Variables

### Backend Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `AI_ENABLED` | No | `false` | Enable AI features (requires OpenAI API key) |
| `OPENAI_API_KEY` | No | - | OpenAI API key (if AI_ENABLED=true) |
| `ENVIRONMENT` | No | `development` | Environment (development/production) |
| `CORS_ALLOWED_ORIGINS` | No | See code | Comma-separated list of allowed origins |
| `VERCEL` | Auto | - | Set automatically by Vercel |

### Frontend Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | - | Backend API URL (use `/api` for Vercel) |

### Example .env file

```env
# Backend
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/procguard
AI_ENABLED=false
ENVIRONMENT=production
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-domain.com

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Health Checks

The application provides health check endpoints for monitoring:

### Backend Health Checks

```bash
# Basic health check
curl http://localhost:8000/health
# Response: {"status": "ok"}

# System health with circuit breaker status
curl http://localhost:8000/system/health

# Sync state
curl http://localhost:8000/system/sync/state
```

### Frontend Health Check

```bash
curl http://localhost:3000
# Should return 200 OK
```

### Docker Health Checks

```bash
# Check container health status
docker-compose ps

# View health check logs
docker inspect procguard-backend | grep Health
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed

**Symptoms**: Backend fails to start, logs show connection errors

**Solutions**:
- Verify `DATABASE_URL` is correct
- Ensure PostgreSQL is running: `docker-compose ps` or `systemctl status postgresql`
- Check database credentials
- Verify network connectivity: `telnet db-host 5432`

#### 2. Frontend Can't Reach Backend

**Symptoms**: "Backend Offline" message, API calls fail

**Solutions**:
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check CORS configuration in `app/main.py`
- Ensure backend is running: `curl http://localhost:8000/health`
- Check browser console for CORS errors

#### 3. Build Failures

**Symptoms**: `npm run build` or `docker build` fails

**Solutions**:
- Clear caches: `npm cache clean --force`, `docker builder prune`
- Delete `node_modules` and `.next`: `rm -rf node_modules .next && npm install`
- Check Node.js version: `node --version` (should be 20+)
- Verify disk space: `df -h`

#### 4. Docker Compose Issues

**Symptoms**: Services crash or restart constantly

**Solutions**:
- View logs: `docker-compose logs -f service-name`
- Check resource limits: `docker stats`
- Restart services: `docker-compose restart`
- Rebuild containers: `docker-compose up -d --build`

#### 5. Port Already in Use

**Symptoms**: Error: "port 3000/8000 is already allocated"

**Solutions**:
```bash
# Find and kill process using port
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9

# Or change ports in docker-compose.yml
```

### Getting Help

- Check application logs: `docker-compose logs -f`
- Review error messages in browser console
- Verify environment variables: `docker-compose config`
- Test individual services separately

### Debug Mode

Enable debug logging:

```bash
# Backend
export LOG_LEVEL=DEBUG
uvicorn app.main:app --reload --log-level debug

# Frontend
npm run dev
```

---

## Production Best Practices

### Security

1. **Use HTTPS**: Always use TLS/SSL in production
2. **Secure Database**: Use strong passwords, enable SSL connections
3. **Environment Variables**: Never commit secrets to version control
4. **CORS**: Configure allowed origins restrictively
5. **Rate Limiting**: Implement rate limiting on API endpoints

### Performance

1. **Database**: Use connection pooling, add indexes
2. **Caching**: Enable Redis or similar for caching
3. **CDN**: Use CDN for static assets
4. **Monitoring**: Set up logging and monitoring (e.g., Datadog, New Relic)

### Backup

1. **Database Backups**: Schedule regular PostgreSQL backups
2. **Code Backups**: Ensure code is in version control
3. **Disaster Recovery**: Test restore procedures

---

## Deployment Checklist

Before deploying to production:

- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Health checks working
- [ ] HTTPS/SSL certificates configured
- [ ] Monitoring and logging set up
- [ ] Backups configured
- [ ] Security review completed
- [ ] Load testing performed
- [ ] Documentation updated
- [ ] Team trained on operations

---

## Support

For issues or questions:
- Create an issue on GitHub
- Check existing documentation
- Review logs and health endpoints

---

**Last Updated**: January 2026  
**Version**: 1.0.0
