# 🚀 ProcGuard Deployment Guide

This comprehensive guide covers all deployment methods for ProcGuard, a full-stack application with a Next.js frontend and FastAPI backend.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Deployment Methods](#deployment-methods)
   - [Vercel Deployment (Recommended for Quick Deploy)](#vercel-deployment)
   - [Azure Container Apps (Production-Ready)](#azure-container-apps-deployment)
   - [Docker Deployment](#docker-deployment)
   - [Local Development](#local-development)
4. [Environment Configuration](#environment-configuration)
5. [Troubleshooting](#troubleshooting)

> 💡 **Quick Links:** [Quick Start Guide](QUICKSTART.md) | [Troubleshooting Guide](TROUBLESHOOTING.md)

---

## 🎯 Overview

**ProcGuard** is a full-stack application consisting of:
- **Frontend**: Next.js 16 with React 19 (TypeScript)
- **Backend**: FastAPI (Python 3.9+)
- **Database**: PostgreSQL (required for production)

The application supports multiple deployment strategies to suit different needs and environments.

---

## ✅ Prerequisites

Before deploying, ensure you have:

### General Requirements
- Git installed
- Access to the ProcGuard repository
- A cloud database (PostgreSQL) - **Required for production**
  - Recommended providers: [Neon](https://neon.tech), [Supabase](https://supabase.com), [Azure PostgreSQL](https://azure.microsoft.com)

### For Vercel Deployment
- [Vercel Account](https://vercel.com) (free tier available)
- GitHub repository access

### For Azure Deployment
- [Azure Account](https://azure.microsoft.com)
- Azure CLI installed and configured
- Docker installed
- Azure Container Registry access

### For Docker Deployment
- Docker and Docker Compose installed
- Basic Docker knowledge

### For Local Development
- Node.js 20+ and npm
- Python 3.9+
- PostgreSQL (or SQLite for development)

---

## 🚀 Deployment Methods

## Vercel Deployment

**Best for**: Quick deployment, serverless architecture, automatic scaling

### Architecture
- Frontend and backend deployed as a single monorepo
- Backend runs as serverless functions
- Frontend served via Vercel's CDN
- `/api/*` routes automatically proxy to backend

### Step-by-Step Guide

#### 1. Prepare Your Repository
Ensure your code is pushed to GitHub:
```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

#### 2. Set Up Database
Create a cloud PostgreSQL database (e.g., on Neon or Supabase) and note the connection string:
```
postgresql://username:password@host:port/database
```

#### 3. Deploy to Vercel

##### Option A: Via Vercel Dashboard
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Configure settings:
   - **Root Directory**: Leave as `./` (default)
   - **Framework Preset**: Other (or auto-detected Next.js)
   - Click **"Deploy"**

##### Option B: Via Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel
```

#### 4. Configure Environment Variables

In Vercel Dashboard → Your Project → Settings → Environment Variables, add:

| Variable Name | Value | Description |
|--------------|-------|-------------|
| `DATABASE_URL` | `postgresql://user:pass@host:port/dbname` | Your PostgreSQL connection string |
| `NEXT_PUBLIC_API_URL` | `/api` | **CRITICAL**: Relative path for API calls |
| `PYTHON_VERSION` | `3.9` | Python runtime version |
| `AI_ENABLED` | `true` | Enable AI features (optional) |

#### 5. Verify Deployment

1. Wait for deployment to complete
2. Visit your Vercel URL (e.g., `https://your-app.vercel.app`)
3. Check that the frontend loads
4. Verify backend is working by visiting `/api/docs` (FastAPI Swagger UI)

### How It Works

The `vercel.json` configuration:
```json
{
    "rewrites": [
        {
            "source": "/api/:path*",
            "destination": "/api/index.py"
        }
    ]
}
```

- All requests to `/api/*` are routed to the FastAPI backend (serverless function)
- All other requests are served by Next.js
- CORS is automatically handled (same-origin)

---

## Azure Container Apps Deployment

**Best for**: Production environments, enterprise deployments, full control

### Architecture
- Backend and frontend run in separate Azure Container Apps
- Uses Azure Container Registry for Docker images
- Azure PostgreSQL for database
- Infrastructure as Code with Bicep

### Prerequisites
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login

# Create Azure Container Registry (if not exists)
az acr create --name procguardacr --resource-group procguard-rg --sku Basic --location eastus
```

### Step-by-Step Guide

#### 1. Build and Push Docker Images

**Backend Image:**
```bash
cd /path/to/Procguard

# Build backend image
docker build -t procguard-api:latest -f Dockerfile.backend .

# Tag and push to ACR
az acr login --name procguardacr
docker tag procguard-api:latest procguardacr.azurecr.io/procguard-api:latest
docker push procguardacr.azurecr.io/procguard-api:latest
```

**Frontend Image:**
```bash
# Build frontend image with API URL
docker build --build-arg NEXT_PUBLIC_API_URL=https://your-backend-url.azurecontainerapps.io \
  -t procguard-ui:latest .

# Tag and push to ACR
docker tag procguard-ui:latest procguardacr.azurecr.io/procguard-ui:latest
docker push procguardacr.azurecr.io/procguard-ui:latest
```

#### 2. Deploy Infrastructure

The repository includes Bicep templates for infrastructure:

```bash
# Set database password
read -s adminPassword

# Get ACR credentials
registryPassword=$(az acr credential show --name procguardacr --query "passwords[0].value" -o tsv)

# Create resource group
az group create -n procguard-rg -l eastus

# Deploy infrastructure
az deployment group create \
  -g procguard-rg \
  -f infra/main.bicep \
  --parameters adminPassword=$adminPassword registryPassword=$registryPassword
```

Or use the provided script:
```bash
./deploy.sh
```

#### 3. Configure Environment Variables

Update the container app with environment variables:
```bash
az containerapp update \
  --name procguard-api \
  --resource-group procguard-rg \
  --set-env-vars \
    DATABASE_URL="postgresql://user:pass@host:port/dbname" \
    AI_ENABLED="true" \
    ENVIRONMENT="production"
```

#### 4. Verify Deployment

```bash
# Get the URL
az containerapp show \
  --name procguard-api \
  --resource-group procguard-rg \
  --query properties.configuration.ingress.fqdn \
  -o tsv
```

Visit the URL to verify the deployment.

### Infrastructure Components

The Bicep templates create:
- **Container App Environment** (procguard-env)
- **Container Apps** (procguard-api, procguard-ui)
- **PostgreSQL Flexible Server** (procguard-db)
- **Storage Account** (for file uploads)
- **Container Registry** (procguardacr)

---

## Docker Deployment

**Best for**: Self-hosted environments, development, Docker-based infrastructure

### Using Docker Compose (Recommended)

Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: procguard
      POSTGRES_PASSWORD: changeme
      POSTGRES_DB: procguard
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    environment:
      DATABASE_URL: postgresql://procguard:changeme@db:5432/procguard
      AI_ENABLED: "true"
    ports:
      - "8000:8000"
    depends_on:
      - db

  frontend:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        NEXT_PUBLIC_API_URL: http://localhost:8000
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Deploy with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using Docker Only

**Backend:**
```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@host:port/dbname" \
  -e AI_ENABLED="true" \
  --name procguard-api \
  procguardacr.azurecr.io/procguard-api:latest
```

**Frontend:**
```bash
docker run -d \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL="http://localhost:8000" \
  --name procguard-ui \
  procguard-ui:latest
```

---

## Local Development

**Best for**: Development, testing, debugging

### Backend Setup

```bash
# Navigate to project root
cd /path/to/Procguard

# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your DATABASE_URL and other settings

# Run database migrations (if using Alembic)
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Frontend Setup

```bash
# Install dependencies
npm install

# Set up environment variables
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run development server
npm run dev
```

Frontend will be available at: `http://localhost:3000`

### Running Both (Recommended)

Open two terminal windows:

**Terminal 1 - Backend:**
```bash
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

---

## 🔧 Environment Configuration

### Required Environment Variables

#### Backend (.env or environment)
```env
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Optional: AI Features
AI_ENABLED=true
OPENAI_API_KEY=your-openai-key

# Optional: Azure Storage (for file uploads)
AZURE_STORAGE_CONNECTION_STRING=your-connection-string

# Environment
ENVIRONMENT=production  # or development
```

#### Frontend (.env.local or environment)
```env
# API URL - CRITICAL!
# For Vercel: /api
# For Local Dev: http://localhost:8000
# For Azure: https://your-backend-url.azurecontainerapps.io
NEXT_PUBLIC_API_URL=/api
```

### Database Setup

#### For Production
Use a managed PostgreSQL service:
- **Neon**: Free tier available, great for getting started
- **Supabase**: Includes additional features like auth and storage
- **Azure PostgreSQL**: Enterprise-grade, integrates with Azure infrastructure
- **AWS RDS**: Reliable and scalable

#### For Development
You can use SQLite:
```env
DATABASE_URL=sqlite:///./procguard.db
```

### Security Considerations

1. **Never commit secrets**: Use `.env` files and add them to `.gitignore`
2. **Use strong passwords**: For database and admin accounts
3. **HTTPS only in production**: Configure SSL/TLS
4. **Whitelist database IPs**: Restrict access to known IPs
5. **Regular backups**: Set up automated database backups

---

## 🔍 Troubleshooting

### Common Issues

#### "Backend Offline" Error

**Symptoms**: Frontend loads but shows "Backend Offline" message

**Solutions**:
1. Check backend logs:
   - Vercel: Dashboard → Logs
   - Azure: `az containerapp logs show --name procguard-api -g procguard-rg`
   - Docker: `docker logs procguard-api`

2. Verify `NEXT_PUBLIC_API_URL` is correct:
   - Vercel: Should be `/api`
   - Azure: Should be full backend URL
   - Local: Should be `http://localhost:8000`

3. Check database connection:
   - Verify `DATABASE_URL` is correct
   - Ensure database allows connections from deployment IP
   - Test connection: `psql $DATABASE_URL`

#### Database Connection Errors

**Error**: `could not connect to server` or `password authentication failed`

**Solutions**:
1. Check connection string format:
   ```
   postgresql://username:password@host:port/database
   ```
2. Verify credentials are correct
3. Check database firewall rules
4. For Vercel: Ensure database allows connections from `0.0.0.0/0` (serverless IPs vary)

#### Build Failures

**Error**: Build fails during deployment

**Solutions**:
1. Check Node.js version: Should be 20+
2. Check Python version: Should be 3.9+
3. Clear cache:
   - Vercel: Redeploy with "Clear Cache"
   - Local: `rm -rf .next node_modules && npm install`
4. Review build logs for specific errors

#### CORS Errors

**Error**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solutions**:
1. For Vercel: Should not occur (same-origin)
2. For other deployments: Verify CORS settings in `app/main.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-frontend-domain.com"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

#### Module Import Errors

**Error**: `ModuleNotFoundError` or `ImportError`

**Solutions**:
1. Backend: `pip install -r requirements.txt`
2. Frontend: `npm install`
3. Check Python path configuration in `api/index.py` for Vercel

### Getting Help

If you encounter issues not covered here:

1. **Check the detailed [Troubleshooting Guide](TROUBLESHOOTING.md)** - Comprehensive solutions for common issues
2. Review the [GitHub Issues](https://github.com/Sasisundar2211/Procguard/issues)
3. Review application logs
4. Verify all environment variables are set correctly
5. Test with minimal configuration first
6. Create a new issue with:
   - Deployment method used
   - Error messages and logs
   - Steps to reproduce

---

## 📊 Deployment Comparison

| Feature | Vercel | Azure Container Apps | Docker | Local |
|---------|--------|---------------------|--------|-------|
| **Setup Time** | ⚡ Fast (5-10 min) | 🕐 Medium (30-60 min) | 🕐 Medium (15-30 min) | ⚡ Fast (10 min) |
| **Cost** | 💰 Free tier available | 💰💰 Pay-as-you-go | 💰 Infrastructure costs | 💰 Free |
| **Scaling** | ✅ Automatic | ✅ Configurable | ⚠️ Manual | ❌ Not applicable |
| **Database** | ⚠️ External required | ✅ Integrated | ✅ Can include | ✅ SQLite OK |
| **Best For** | Quick deploy, demos | Production, enterprise | Self-hosted | Development |
| **SSL/HTTPS** | ✅ Automatic | ✅ Automatic | ⚠️ Manual | ❌ Not needed |

---

## 🎉 Success Checklist

After deployment, verify:
- [ ] Frontend loads without errors
- [ ] Backend API responds (check `/api/docs`)
- [ ] Database connection is working
- [ ] User registration/login works
- [ ] File uploads work (if using storage)
- [ ] All environment variables are set
- [ ] HTTPS is enabled (production)
- [ ] Monitoring/logging is configured

---

## 📚 Additional Resources

- **[Quick Start Guide](QUICKSTART.md)** - Get started in 5-30 minutes
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Detailed solutions for common problems
- [Next.js Deployment Documentation](https://nextjs.org/docs/deployment)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [Vercel Documentation](https://vercel.com/docs)
- [Azure Container Apps Documentation](https://docs.microsoft.com/azure/container-apps/)
- [Docker Documentation](https://docs.docker.com/)

---

## 📝 Version History

- **v1.0.0** - Initial deployment guide
- Covers Vercel, Azure, Docker, and local development
- Last updated: January 2026

---

**Need Help?** Create an issue on [GitHub](https://github.com/Sasisundar2211/Procguard/issues) or check existing documentation.
