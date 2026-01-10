# ProcGuard Deployment Troubleshooting Guide

Quick reference for common deployment issues and solutions.

## 🚨 Quick Diagnostics

### Step 1: Identify Your Issue

**Symptom Checklist:**
- [ ] Frontend doesn't load at all
- [ ] Frontend loads but shows "Backend Offline"
- [ ] Database connection errors
- [ ] Build/deployment fails
- [ ] CORS errors in console
- [ ] API endpoints return 500 errors
- [ ] Slow performance

### Step 2: Run Basic Checks

```bash
# Check if services are running
# For Docker:
docker-compose ps

# For local development:
curl http://localhost:8000/docs  # Backend API docs
curl http://localhost:3000        # Frontend

# Check logs
# Docker:
docker-compose logs backend
docker-compose logs frontend

# Local:
# Check terminal windows where services are running
```

---

## 🔧 Common Issues & Solutions

### Issue 1: "Backend Offline" Error

**Symptoms:**
- Frontend loads successfully
- Message appears: "Backend is offline" or similar
- API calls fail in Network tab

**Root Causes:**
1. Incorrect `NEXT_PUBLIC_API_URL` environment variable
2. Backend not running
3. CORS blocking requests
4. Backend crashed/errored

**Solutions:**

#### Solution 1A: Check API URL (Most Common)
```bash
# For Vercel deployment:
# Environment variable should be:
NEXT_PUBLIC_API_URL=/api

# For local development:
NEXT_PUBLIC_API_URL=http://localhost:8000

# For Azure/custom backend:
NEXT_PUBLIC_API_URL=https://your-backend-url.com

# Verify in browser console:
# Open DevTools → Console → Type:
console.log(process.env.NEXT_PUBLIC_API_URL)
```

#### Solution 1B: Verify Backend is Running
```bash
# Test backend directly:
curl http://localhost:8000/docs  # Local
curl https://your-app.vercel.app/api/docs  # Vercel
curl https://your-backend.azurecontainerapps.io/docs  # Azure

# Should return HTML of API documentation
```

#### Solution 1C: Check Backend Logs
```bash
# Docker:
docker-compose logs backend | tail -50

# Vercel:
# Go to Dashboard → Your Project → Logs → Filter by /api

# Azure:
az containerapp logs show --name procguard-api -g procguard-rg --tail 50

# Look for:
# - Database connection errors
# - Python import errors
# - Startup failures
```

---

### Issue 2: Database Connection Errors

**Symptoms:**
- Error: "could not connect to server"
- Error: "password authentication failed"
- Backend starts but fails on first API call
- 500 errors from API endpoints

**Root Causes:**
1. Incorrect DATABASE_URL format
2. Database not accessible from deployment location
3. Firewall blocking connections
4. Database doesn't exist

**Solutions:**

#### Solution 2A: Verify Connection String Format
```bash
# Correct format:
DATABASE_URL=postgresql://username:password@host:port/database

# Common mistakes:
# ❌ Missing port: postgresql://user:pass@host/db
# ❌ Wrong protocol: postgres:// (should be postgresql://)
# ❌ Spaces in password not encoded
# ❌ Missing database name

# Test connection:
psql "$DATABASE_URL"
```

#### Solution 2B: Check Database Firewall
```bash
# For cloud databases, allow connections from:
# - Vercel: 0.0.0.0/0 (serverless IPs vary)
# - Azure: Your container app's outbound IPs
# - Local: Your IP address

# Get your IP:
curl ifconfig.me

# For Neon/Supabase:
# Go to dashboard → Settings → Add allowed IP
```

#### Solution 2C: Verify Database Exists
```bash
# Connect and list databases:
psql "$DATABASE_URL" -c "\l"

# If database doesn't exist:
createdb -h host -U username database_name

# Or via SQL:
psql -h host -U username -c "CREATE DATABASE procguard;"
```

---

### Issue 3: Build Failures

**Symptoms:**
- Deployment fails during build
- Error: "Module not found"
- Error: "Command failed"
- Timeout during build

**Root Causes:**
1. Incorrect Node.js version
2. Incorrect Python version
3. Missing dependencies
4. Build command errors

**Solutions:**

#### Solution 3A: Check Versions
```bash
# Verify versions locally:
node --version    # Should be 20+
python --version  # Should be 3.9+
npm --version

# For Vercel:
# Add to environment variables:
PYTHON_VERSION=3.9

# For Docker:
# Check Dockerfile FROM lines
```

#### Solution 3B: Clear Cache and Rebuild
```bash
# Local:
rm -rf node_modules .next
npm install
npm run build

# Docker:
docker-compose down -v
docker-compose build --no-cache
docker-compose up

# Vercel:
# Dashboard → Deployments → [Latest] → ... → Redeploy → "Clear cache and redeploy"
```

#### Solution 3C: Check Dependencies
```bash
# Frontend:
npm install  # Install missing packages
npm audit fix  # Fix vulnerabilities

# Backend:
pip install -r requirements.txt

# If specific package fails:
pip install package-name --upgrade
```

---

### Issue 4: CORS Errors

**Symptoms:**
- Browser console: "CORS policy: No 'Access-Control-Allow-Origin' header"
- API calls work in Postman but not in browser
- OPTIONS requests failing

**Root Causes:**
1. Backend not configured for frontend origin
2. Different domains for frontend/backend
3. Missing CORS middleware

**Solutions:**

#### Solution 4A: Configure CORS (app/main.py)
```python
from fastapi.middleware.cors import CORSMiddleware

# For development (allow all):
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# For production (specific origins):
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",
        "https://your-custom-domain.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Solution 4B: Use Same-Origin (Vercel)
```bash
# Best practice for Vercel:
# Deploy frontend and backend together
# Set NEXT_PUBLIC_API_URL=/api
# Vercel rewrites handle routing
# CORS not needed!
```

---

### Issue 5: Slow Performance

**Symptoms:**
- API requests take >5 seconds
- Frontend loads slowly
- Database queries timeout

**Solutions:**

#### Solution 5A: Database Connection Pooling
```python
# In app/core/database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,  # Increase pool size
    max_overflow=0,
    pool_pre_ping=True,  # Check connections
)
```

#### Solution 5B: Add Database Indexes
```sql
-- For frequently queried fields:
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_procedures_batch_id ON procedures(batch_id);
```

#### Solution 5C: Enable Caching
```python
# Add response caching for static data
from fastapi import Response
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_data():
    # Expensive operation
    return data
```

---

### Issue 6: Environment Variables Not Working

**Symptoms:**
- Changes to .env don't take effect
- NEXT_PUBLIC_* variables undefined
- Backend can't read environment variables

**Solutions:**

#### Solution 6A: Frontend Variables Must Start with NEXT_PUBLIC_
```bash
# ❌ Wrong:
API_URL=http://localhost:8000

# ✅ Correct:
NEXT_PUBLIC_API_URL=http://localhost:8000

# Reason: Next.js only exposes NEXT_PUBLIC_* to browser
```

#### Solution 6B: Restart After Changes
```bash
# Local development:
# Stop both servers (Ctrl+C)
# Restart them

# Docker:
docker-compose restart

# Vercel:
# Redeploy (environment changes trigger automatic redeploy)
```

#### Solution 6C: Check File Location
```bash
# Frontend: .env.local (not committed)
# Backend: .env (not committed)
# Template: .env.example (committed)

# Verify files exist:
ls -la .env .env.local .env.example
```

---

## 🔍 Diagnostic Commands

### Check All Service Status
```bash
# Docker
docker-compose ps
docker-compose logs --tail=50

# Local - Check if ports are in use
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :5432  # PostgreSQL

# Azure
az containerapp show --name procguard-api -g procguard-rg --query properties.runningStatus
```

### Test Each Component
```bash
# 1. Database
psql "$DATABASE_URL" -c "SELECT 1;"

# 2. Backend API
curl http://localhost:8000/docs
curl http://localhost:8000/api/health  # If health endpoint exists

# 3. Frontend
curl http://localhost:3000

# 4. Full stack (from frontend, check Network tab)
# Open http://localhost:3000 in browser
# Open DevTools → Network
# Look for failed requests
```

### View Detailed Logs
```bash
# Docker - Follow logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Docker - Specific service with timestamps
docker-compose logs -f --timestamps backend

# Local - Backend logs
# Check terminal or uvicorn.log, backend.log

# Vercel - Real-time logs
vercel logs --follow
```

---

## 📋 Pre-Deployment Checklist

Before deploying, verify:

### Environment Variables
- [ ] `DATABASE_URL` is set and correct format
- [ ] `NEXT_PUBLIC_API_URL` is correct for deployment type
- [ ] No sensitive data in frontend env vars (they're exposed!)
- [ ] `.env` files are in `.gitignore`

### Database
- [ ] Database exists and is accessible
- [ ] Firewall allows connections from deployment location
- [ ] Migrations have been run (if applicable)
- [ ] Tables are created

### Code
- [ ] All dependencies installed (`npm install`, `pip install -r requirements.txt`)
- [ ] No build errors locally
- [ ] Tests pass (if you have tests)
- [ ] Code is committed and pushed to GitHub

### Configuration Files
- [ ] `vercel.json` exists (for Vercel)
- [ ] `Dockerfile.backend` exists (for Docker/Azure)
- [ ] `docker-compose.yml` exists (for Docker)
- [ ] `requirements.txt` is up to date
- [ ] `package.json` is up to date

---

## 🆘 Still Having Issues?

1. **Check the logs first** - 90% of issues are visible in logs
2. **Try minimal configuration** - Remove optional features
3. **Test components separately** - Database → Backend → Frontend
4. **Compare with working example** - Use the Quick Start guide
5. **Search existing issues** - [GitHub Issues](https://github.com/Sasisundar2211/Procguard/issues)
6. **Create a new issue** with:
   - Deployment method (Vercel/Azure/Docker/Local)
   - Error messages and logs
   - Environment (OS, versions)
   - Steps to reproduce

---

## 💡 Pro Tips

1. **Always check logs first** - They contain the answer 90% of the time
2. **Use environment variables** - Never hardcode URLs or credentials
3. **Test locally first** - Easier to debug than cloud deployments
4. **Keep it simple** - Start with minimal config, add features gradually
5. **Document your changes** - Future you will thank present you

---

**Happy Debugging! 🐛 → 🎉**
