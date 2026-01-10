# ProcGuard

ProcGuard is a full-stack compliance monitoring and audit system built with Next.js (frontend) and FastAPI (backend). This application provides immutable procedure enforcement, violation tracking, and comprehensive audit logging.

## 🏗️ Architecture

- **Frontend**: Next.js 16 with React 19, TypeScript, and Tailwind CSS
- **Backend**: FastAPI with Python 3.9+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Deployment**: Optimized for Vercel (serverless)

## 🚀 Quick Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Sasisundar2211/Procguard)

### Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Cloud Database**: PostgreSQL database accessible from the internet
   - Recommended providers: [Neon](https://neon.tech), [Supabase](https://supabase.com), or [Azure PostgreSQL](https://azure.microsoft.com)
   - You'll need the connection string (format: `postgresql://user:password@host:port/database`)

### Deployment Steps

1. **Import Project to Vercel**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click **"Add New..."** → **"Project"**
   - Import your GitHub repository
   - **Important**: Keep the root directory as `./` (deploy the entire monorepo)

2. **Configure Environment Variables**
   
   Add these variables in Vercel Project Settings → Environment Variables:
   
   | Variable | Value | Description |
   |----------|-------|-------------|
   | `DATABASE_URL` | `postgresql://user:pass@host:port/dbname` | Your cloud PostgreSQL connection string |
   | `NEXT_PUBLIC_API_URL` | `/api` | API endpoint (use relative path for same-origin) |
   | `PYTHON_VERSION` | `3.9` | Python runtime version |

3. **Deploy**
   - Click **"Deploy"**
   - Vercel will automatically:
     - Build the Next.js frontend
     - Deploy the FastAPI backend as serverless functions
     - Configure routing between frontend and backend

4. **Verify Deployment**
   - Visit your deployment URL (e.g., `https://your-app.vercel.app`)
   - Check the API health: `https://your-app.vercel.app/api/health`

### How It Works

The deployment uses the `vercel.json` configuration to:
- Route all `/api/*` requests to the FastAPI backend (`api/index.py`)
- Serve the Next.js frontend for all other routes
- Both run on the same domain, avoiding CORS issues

## 🛠️ Local Development

### Prerequisites

- Node.js 20+
- Python 3.9+
- PostgreSQL database

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Sasisundar2211/Procguard.git
   cd Procguard
   ```

2. **Install Frontend Dependencies**
   ```bash
   npm install
   ```

3. **Install Backend Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   
   Copy `.env.example` to `.env` and update:
   ```bash
   cp .env.example .env
   ```
   
   Update the variables:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/procguard
   NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
   ```

5. **Start the Backend**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

6. **Start the Frontend** (in a new terminal)
   ```bash
   npm run dev
   ```

7. **Access the Application**
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API: [http://localhost:8000](http://localhost:8000)
   - API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## 📦 Build

Build the frontend for production:

```bash
npm run build
npm run start
```

## 🔍 Project Structure

```
Procguard/
├── src/                    # Next.js frontend source
│   ├── app/               # Next.js app directory (pages)
│   ├── components/        # React components
│   ├── lib/              # Utility functions
│   └── types/            # TypeScript type definitions
├── app/                   # FastAPI backend
│   ├── api/              # API route handlers
│   ├── core/             # Core functionality
│   ├── models/           # Database models
│   └── main.py           # FastAPI application entry
├── api/                   # Vercel serverless functions
│   └── index.py          # Backend entry for Vercel
├── public/               # Static assets
├── vercel.json           # Vercel deployment configuration
├── next.config.ts        # Next.js configuration
└── requirements.txt      # Python dependencies
```

## 📚 Additional Documentation

- [Vercel Deployment Guide](VERCEL_DEPLOY.md) - Detailed deployment instructions
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when running locally)

## 🔒 Security

- All procedure changes are immutable and audit-logged
- Circuit breaker pattern for API resilience
- Comprehensive error handling and monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is private and proprietary.

## 🆘 Troubleshooting

### "Backend Offline" Error

If you see this error after deployment:

1. Check Vercel Function Logs in the Vercel dashboard
2. Verify `DATABASE_URL` is correct and accessible from Vercel IPs
3. Ensure `NEXT_PUBLIC_API_URL` is set to `/api`
4. Confirm PostgreSQL allows connections from `0.0.0.0/0` (all IPs)

### Build Failures

- Ensure all environment variables are set in Vercel
- Check that `requirements.txt` includes all Python dependencies
- Verify `package.json` has all Node.js dependencies

### Database Connection Issues

- Confirm database URL format: `postgresql://user:password@host:port/database`
- Check database firewall settings allow Vercel connections
- Test connection string using a PostgreSQL client

## 🌐 Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Vercel Documentation](https://vercel.com/docs)

