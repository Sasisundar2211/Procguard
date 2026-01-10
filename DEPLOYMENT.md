# 🚀 ProcGuard Deployment Guide

This guide provides comprehensive instructions for deploying both the frontend and backend together.

## Table of Contents
1. [Quick Start (Local Deployment)](#quick-start-local-deployment)
2. [Production Deployment](#production-deployment)
3. [Azure Deployment](#azure-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Troubleshooting](#troubleshooting)

---

## Quick Start (Local Deployment)

Deploy both frontend and backend together on your local machine using Docker Compose.

### Prerequisites
- Docker and Docker Compose V2 installed
- At least 4GB of RAM available
- Ports 3000, 8000, and 5432 available

### Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Procguard
   ```

2. **Deploy using the script**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh --mode local
   ```

   Or manually with docker compose:
   ```bash
   docker compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

4. **View logs**
   ```bash
   docker compose logs -f
   ```

5. **Stop services**
   ```bash
   docker compose down
   ```

---

## Production Deployment

Deploy to production using Docker Compose with Nginx as a reverse proxy.

### Prerequisites
- Docker and Docker Compose installed on production server
- Domain name configured (optional but recommended)
- SSL certificates (for HTTPS - recommended)

### Steps

1. **Create production environment file**
   ```bash
   cp .env.example .env.prod
   ```

   Update `.env.prod` with your production settings:
   ```env
   # PostgreSQL Configuration
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your_secure_password_here
   POSTGRES_DB=procguard

   # Application Configuration
   AI_ENABLED=true
   ENVIRONMENT=production

   # Frontend Configuration
   NEXT_PUBLIC_API_URL=/api
   FRONTEND_PORT=3000

   # CORS Configuration (Update with your domain)
   CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

   # Nginx Port
   NGINX_PORT=80
   ```

2. **Deploy to production**
   ```bash
   ./deploy.sh --mode prod
   ```

   Or manually:
   ```bash
   docker compose -f docker-compose.prod.yml up -d
   ```

3. **Access the application**
   - Application: http://your-server-ip (or your domain)
   - API: http://your-server-ip/api
   - API Docs: http://your-server-ip/api/docs

4. **Set up HTTPS (Recommended)**
   
   Use Let's Encrypt with Certbot:
   ```bash
   # Install certbot
   sudo apt-get update
   sudo apt-get install certbot

   # Get certificate
   sudo certbot certonly --standalone -d yourdomain.com

   # Update nginx.conf to use SSL
   # Add SSL configuration to nginx.conf
   ```

---

## Azure Deployment

Deploy to Azure Container Apps with managed PostgreSQL database.

### Prerequisites
- Azure CLI installed (`az`)
- Azure subscription
- Azure Container Registry (procguardacr)

### Steps

1. **Login to Azure**
   ```bash
   az login
   ```

2. **Deploy using the script**
   ```bash
   ./deploy.sh --mode azure
   ```

   This will:
   - Create resource group
   - Deploy PostgreSQL database
   - Deploy backend container
   - Deploy frontend container
   - Configure networking

3. **Access the application**
   
   After deployment completes, the script will output the URLs for your deployed services.

---

## Environment Configuration

### Local Development (.env)
```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/procguard
AI_ENABLED=true
ENVIRONMENT=development
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Production (.env.prod)
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=procguard
AI_ENABLED=true
ENVIRONMENT=production
NEXT_PUBLIC_API_URL=/api
CORS_ALLOWED_ORIGINS=https://yourdomain.com
NGINX_PORT=80
```

### Azure Container Apps
- Configured via `infra/main.bicep`
- Environment variables set in container configuration
- Managed PostgreSQL instance
- Auto-scaling enabled

---

## Architecture

### Local/Production Deployment
```
┌─────────────────────────────────────────┐
│            Nginx (Port 80)              │
│         Reverse Proxy                    │
└───────────┬─────────────────────────────┘
            │
            ├─────► /api → Backend (Port 8000)
            │                FastAPI
            │
            └─────► / → Frontend (Port 3000)
                         Next.js
                              │
                              ▼
                    PostgreSQL (Port 5432)
```

### Network Flow
1. User accesses application through Nginx (port 80)
2. Nginx routes `/api/*` requests to backend container
3. Nginx routes all other requests to frontend container
4. Backend connects to PostgreSQL database
5. Frontend makes API calls to `/api` (proxied by Nginx)

---

## Troubleshooting

### Services won't start
```bash
# Check Docker status
docker ps -a

# Check logs
docker compose logs

# Check specific service
docker compose logs backend
docker compose logs frontend
```

### Database connection issues
```bash
# Check if PostgreSQL is running
docker compose ps postgres

# Check database logs
docker compose logs postgres

# Connect to database
docker compose exec postgres psql -U postgres -d procguard
```

### Frontend can't connect to backend
1. Check backend health: `curl http://localhost:8000/health`
2. Check CORS configuration in `app/main.py`
3. Verify `NEXT_PUBLIC_API_URL` environment variable

### Port conflicts
```bash
# Check what's using the port
lsof -i :3000
lsof -i :8000
lsof -i :5432

# Stop conflicting services or change ports in docker-compose.yml
```

### Rebuild after code changes
```bash
# Local
docker compose down
docker compose build
docker compose up -d

# Production
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

### Clean slate (removes all data)
```bash
docker compose down -v
docker system prune -a
```

---

## Monitoring

### Health Checks
- Frontend: http://localhost:3000
- Backend: http://localhost:8000/health
- System Health: http://localhost:8000/system/health

### Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres

# Last 100 lines
docker compose logs --tail=100 backend
```

### Resource Usage
```bash
docker stats
```

---

## Maintenance

### Backup Database
```bash
docker compose exec postgres pg_dump -U postgres procguard > backup.sql
```

### Restore Database
```bash
docker compose exec -T postgres psql -U postgres procguard < backup.sql
```

### Update Application
```bash
git pull
docker compose down
docker compose build
docker compose up -d
```

---

## Security Checklist

- [ ] Change default PostgreSQL password
- [ ] Use HTTPS in production (SSL certificates)
- [ ] Configure firewall rules
- [ ] Set up regular database backups
- [ ] Use environment variables for secrets
- [ ] Enable Docker security scanning
- [ ] Keep Docker images updated
- [ ] Review and update CORS origins

---

## Support

For issues and questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review logs: `docker compose logs`
3. Check GitHub Issues
4. Consult the API documentation at `/api/docs`

---

## Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
