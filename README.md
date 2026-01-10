# 🛡️ ProcGuard

**ProcGuard** is a comprehensive compliance and regulatory audit management system built with Next.js and FastAPI. It provides real-time monitoring, audit tracking, and compliance enforcement for regulatory procedures.

## 🌟 Features

- **Full-Stack Application**: Next.js 16 frontend + FastAPI backend
- **Real-time Audit Tracking**: Monitor compliance and regulatory procedures
- **AI-Powered Analysis**: Intelligent insights and recommendations (optional)
- **Secure & Scalable**: Built with enterprise-grade security practices
- **Multiple Deployment Options**: Vercel, Azure, Docker, or local development

## 🚀 Quick Start

Get started in minutes! Choose your preferred method:

### ⚡ Fastest Path (Vercel)
```bash
# 1. Fork this repo and connect to Vercel
# 2. Add DATABASE_URL environment variable
# 3. Deploy!
```
[📖 See Quick Start Guide](QUICKSTART.md)

### 💻 Local Development
```bash
# Backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (in another terminal)
npm install
npm run dev
```

### 🐳 Docker
```bash
docker-compose up -d
```

Visit `http://localhost:3000` after starting!

## 📚 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get running in 5-30 minutes
- **[Full Deployment Guide](DEPLOYMENT.md)** - Comprehensive deployment instructions
- **[Vercel Deployment](VERCEL_DEPLOY.md)** - Specific Vercel instructions

## 🏗️ Architecture

```
ProcGuard/
├── app/              # FastAPI backend application
├── src/              # Next.js frontend source
├── api/              # Vercel serverless API adapter
├── infra/            # Azure Bicep infrastructure templates
├── alembic/          # Database migrations
└── tests/            # Test suites
```

**Tech Stack:**
- **Frontend**: Next.js 16, React 19, TypeScript, TailwindCSS
- **Backend**: FastAPI, Python 3.9+, SQLAlchemy
- **Database**: PostgreSQL (SQLite for development)
- **Deployment**: Vercel, Azure Container Apps, Docker

## 🔧 Configuration

Copy `.env.example` to `.env` and configure:

```env
# Required
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Optional
AI_ENABLED=true
OPENAI_API_KEY=your-key
```

See [Full Deployment Guide](DEPLOYMENT.md#environment-configuration) for all options.

## 🧪 Development

### Prerequisites
- Node.js 20+
- Python 3.9+
- PostgreSQL (or SQLite for local dev)

### Running Tests
```bash
# Backend tests
pytest

# Frontend tests (if configured)
npm test
```

### API Documentation
When the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📦 Deployment Options

| Method | Best For | Setup Time | Cost |
|--------|----------|------------|------|
| **Vercel** | Quick deploy, demos | ⚡ 5-10 min | 💰 Free tier |
| **Azure** | Production, enterprise | 🕐 30-60 min | 💰💰 Pay-as-you-go |
| **Docker** | Self-hosted | 🕐 15-30 min | 💰 Infrastructure |
| **Local** | Development | ⚡ 10 min | 💰 Free |

[📖 See Full Deployment Guide](DEPLOYMENT.md) for detailed instructions.

## 🔒 Security

- SQL injection prevention via parameterized queries
- CORS configuration for production
- Environment-based secrets management
- Audit logging for all critical operations

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is part of an academic/competition submission. Please check with the repository owner for licensing details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/Sasisundar2211/Procguard/issues)
- **Documentation**: See [DEPLOYMENT.md](DEPLOYMENT.md) and [QUICKSTART.md](QUICKSTART.md)

## 📈 Project Status

This project is actively maintained and being developed for the Microsoft Imagine Cup 2026.

---

**Built with ❤️ for compliance and regulatory excellence**
