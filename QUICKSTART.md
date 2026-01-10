# 🚀 ProcGuard Quick Start Guide

Get ProcGuard up and running in minutes!

## Choose Your Path

### 🌐 Quick Deploy to Production (Vercel - 5 minutes)

**Best for**: Fastest way to get ProcGuard online

1. **Get a Database**
   ```bash
   # Sign up at https://neon.tech (free tier)
   # Create a database and copy the connection string
   ```

2. **Deploy to Vercel**
   - Go to https://vercel.com
   - Click "Import Project" and select your GitHub repo
   - Add these environment variables:
     - `DATABASE_URL`: Your database connection string
     - `NEXT_PUBLIC_API_URL`: `/api`
     - `PYTHON_VERSION`: `3.9`
   - Click "Deploy"

3. **Done!** Visit your Vercel URL

---

### 💻 Local Development (10 minutes)

**Best for**: Development and testing

#### Prerequisites
- Node.js 20+
- Python 3.9+
- Git

#### Steps

```bash
# 1. Clone the repository
git clone https://github.com/Sasisundar2211/Procguard.git
cd Procguard

# 2. Set up Backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings (SQLite works for development)

# 4. Start Backend (in one terminal)
uvicorn app.main:app --reload

# 5. Set up Frontend (in another terminal)
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# 6. Start Frontend
npm run dev

# 7. Open http://localhost:3000
```

---

### 🐳 Docker Deployment (15 minutes)

**Best for**: Self-hosted, consistent environments

#### Prerequisites
- Docker and Docker Compose installed

#### Steps

```bash
# 1. Clone the repository
git clone https://github.com/Sasisundar2211/Procguard.git
cd Procguard

# 2. Start everything with Docker Compose
docker-compose up -d

# 3. Wait for services to start (check status)
docker-compose ps

# 4. Open http://localhost:3000
```

**To stop:**
```bash
docker-compose down
```

**To view logs:**
```bash
docker-compose logs -f
```

---

### ☁️ Azure Production Deploy (30 minutes)

**Best for**: Enterprise production deployment

#### Prerequisites
- Azure account and Azure CLI
- Docker installed

#### Steps

```bash
# 1. Login to Azure
az login

# 2. Set variables
RESOURCE_GROUP="procguard-rg"
LOCATION="eastus"
ACR_NAME="procguardacr"

# 3. Create resources
az group create -n $RESOURCE_GROUP -l $LOCATION
az acr create --name $ACR_NAME --resource-group $RESOURCE_GROUP --sku Basic

# 4. Build and push images
az acr login --name $ACR_NAME
docker build -t procguard-backend -f Dockerfile.backend .
docker tag procguard-backend $ACR_NAME.azurecr.io/procguard-api:latest
docker push $ACR_NAME.azurecr.io/procguard-api:latest

docker build -t procguard-frontend .
docker tag procguard-frontend $ACR_NAME.azurecr.io/procguard-ui:latest
docker push $ACR_NAME.azurecr.io/procguard-ui:latest

# 5. Deploy with Bicep (or use provided deploy.sh)
./deploy.sh
```

---

## 🔍 Verification Checklist

After deployment, verify:

- [ ] Frontend loads at your URL
- [ ] Navigate to `/api/docs` - see API documentation
- [ ] Backend responds to API calls
- [ ] Database connection works
- [ ] No errors in console/logs

## 📚 Next Steps

- Read the [full deployment guide](DEPLOYMENT.md) for detailed instructions
- Configure environment variables for your needs
- Set up monitoring and backups
- Review security best practices

## ❓ Quick Troubleshooting

**Frontend loads but shows "Backend Offline"**
- Check `NEXT_PUBLIC_API_URL` environment variable
- Verify backend is running: visit `/api/docs`
- Check database connection string

**Database connection errors**
- Verify `DATABASE_URL` format: `postgresql://user:pass@host:port/db`
- Check database firewall allows your IP
- For Vercel: allow connections from `0.0.0.0/0`

**Build fails**
- Check Node.js version: `node --version` (should be 20+)
- Check Python version: `python --version` (should be 3.9+)
- Clear cache and reinstall dependencies

## 🆘 Need Help?

- 📖 [Full Deployment Guide](DEPLOYMENT.md)
- 🐛 [GitHub Issues](https://github.com/Sasisundar2211/Procguard/issues)
- 📧 Check the repository for contact information

---

**Happy Deploying! 🎉**
