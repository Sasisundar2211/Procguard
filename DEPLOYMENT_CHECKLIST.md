# Vercel Deployment Checklist

This document provides a quick checklist for deploying ProcGuard to Vercel.

## ✅ Pre-Deployment Checklist

### 1. Database Setup
- [ ] Create a cloud PostgreSQL database (Neon, Supabase, or Azure)
- [ ] Get the database connection string (format: `postgresql://user:password@host:port/database`)
- [ ] Ensure database accepts connections from all IPs (0.0.0.0/0) for serverless

### 2. Vercel Account
- [ ] Sign up at [vercel.com](https://vercel.com)
- [ ] Connect your GitHub account to Vercel

## 🚀 Deployment Steps

### Step 1: Import to Vercel
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Select your GitHub repository: `Sasisundar2211/Procguard`
4. **Important**: Keep root directory as `./` (don't change it)

### Step 2: Configure Environment Variables
In Vercel Project Settings → Environment Variables, add:

**Required:**
- `DATABASE_URL` = Your PostgreSQL connection string
- `NEXT_PUBLIC_API_URL` = `/api`

**Optional:**
- `PYTHON_VERSION` = `3.9`
- `CORS_ALLOWED_ORIGINS` = Your custom origins (comma-separated)

### Step 3: Deploy
Click **"Deploy"** and wait for:
- ✅ Frontend build to complete
- ✅ Backend functions to deploy
- ✅ Deployment to go live

### Step 4: Verify
1. Visit your deployment URL (e.g., `https://your-app.vercel.app`)
2. Check API health: `https://your-app.vercel.app/api/health`
3. Verify frontend loads correctly
4. Test backend connectivity

## 📋 Post-Deployment

### Update CORS Origins
After first deployment, update the `CORS_ALLOWED_ORIGINS` environment variable to include your Vercel URL:
```
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-app.vercel.app
```

### Monitor Logs
- Check Vercel Function Logs for any errors
- Monitor database connection issues
- Watch for API timeout errors (increase maxDuration if needed)

## 🔧 Configuration Files

All necessary files are already configured in this repository:

- ✅ `vercel.json` - Vercel deployment configuration
- ✅ `.vercelignore` - Files to exclude from deployment
- ✅ `.env.example` - Environment variables template
- ✅ `next.config.ts` - Next.js configuration with standalone output
- ✅ `api/index.py` - Serverless function entry point
- ✅ `app/main.py` - FastAPI app with Vercel support

## 🆘 Troubleshooting

### "Backend Offline" Error
1. Check Vercel Function Logs
2. Verify `DATABASE_URL` is correct
3. Confirm database allows Vercel connections
4. Ensure `NEXT_PUBLIC_API_URL=/api` is set

### Build Failures
1. Check all environment variables are set
2. Review Vercel build logs
3. Verify `requirements.txt` is complete

### Function Timeout
If API calls timeout:
1. Increase `maxDuration` in `vercel.json` (max 60s on Pro plan)
2. Optimize database queries
3. Check database response time

## 📚 Documentation

- **Full Guide**: See [README.md](README.md)
- **Detailed Instructions**: See [VERCEL_DEPLOY.md](VERCEL_DEPLOY.md)
- **Environment Variables**: See [.env.example](.env.example)

## 🎉 Success Indicators

Your deployment is successful when:
- ✅ Frontend loads at your Vercel URL
- ✅ `/api/health` returns `{"status": "ok"}`
- ✅ Dashboard displays data from backend
- ✅ No "Backend Offline" errors
- ✅ API calls complete successfully

## 🔄 Continuous Deployment

After initial setup, Vercel automatically:
- Deploys on every push to your main branch
- Creates preview deployments for PRs
- Runs builds with your environment variables

**That's it! Your ProcGuard application should now be live on Vercel! 🚀**
