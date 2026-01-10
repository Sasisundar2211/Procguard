# 🛡️ ProcGuard - Immutable Procedure Enforcement System

**ProcGuard** is a full-stack application that enforces immutable compliance procedures using cryptographic guarantees, finite state machines, and comprehensive audit logging.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Development](#development)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)

## 🎯 Overview

ProcGuard provides:
- **Immutable Procedures**: Cryptographically-signed standard operating procedures (SOPs)
- **Finite State Machine**: Enforces procedural compliance through state transitions
- **Role-Based Access Control**: Operator, Supervisor, and Auditor roles
- **Comprehensive Audit Logging**: Every action is logged and traceable
- **Real-Time Monitoring**: Live dashboard showing batch execution status
- **Violation Detection**: Automatic detection of compliance violations

### Technology Stack

**Frontend:**
- Next.js 16 with React 19
- TypeScript
- Tailwind CSS

**Backend:**
- FastAPI (Python)
- SQLAlchemy ORM
- PostgreSQL database
- Alembic migrations

## 🏗️ Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Next.js UI    │─────▶│   FastAPI API    │─────▶│   PostgreSQL    │
│   (Port 3000)   │      │   (Port 8000)    │      │   (Port 5432)   │
└─────────────────┘      └──────────────────┘      └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose (recommended)
- OR Node.js 20+ and Python 3.12+

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/Sasisundar2211/Procguard.git
cd Procguard

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manual Setup

#### Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/procguard"
export AI_ENABLED="false"

# Run database migrations (if needed)
alembic upgrade head

# Start the backend
uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup

```bash
# Install Node.js dependencies
npm install

# Set environment variables
export NEXT_PUBLIC_API_URL="http://localhost:8000"

# Start development server
npm run dev

# Or build for production
npm run build
npm start
```

## 💻 Development

### Project Structure

```
Procguard/
├── app/                    # FastAPI backend
│   ├── api/               # API routes
│   ├── core/              # Core business logic
│   ├── models/            # Database models
│   ├── services/          # Service layer
│   └── main.py            # FastAPI app entry point
├── src/                   # Next.js frontend source
├── public/                # Static assets
├── infra/                 # Azure Bicep infrastructure
├── .github/workflows/     # CI/CD pipelines
├── docker-compose.yml     # Local deployment
├── Dockerfile             # Frontend container
├── Dockerfile.backend     # Backend container
└── DEPLOYMENT.md          # Detailed deployment guide
```

### Running Tests

```bash
# Backend tests
pytest

# Frontend linting
npm run lint

# Validate deployment readiness
./validate-deployment.sh
```

### Environment Variables

#### Backend (.env)
```env
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/procguard
AI_ENABLED=false
ENVIRONMENT=development
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📦 Deployment

ProcGuard supports multiple deployment platforms:

### 1. Docker Compose (Local/Server)
```bash
docker-compose up -d
```

### 2. Vercel (Serverless)
See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

**Quick summary:**
- Push to GitHub
- Connect to Vercel
- Set environment variables:
  - `DATABASE_URL`: Your PostgreSQL connection string
  - `NEXT_PUBLIC_API_URL`: `/api`
- Deploy!

### 3. Azure Container Apps
```bash
./deploy.sh
```

### 4. Manual Deployment
Follow the comprehensive guide in [DEPLOYMENT.md](./DEPLOYMENT.md).

### Deployment Validation

Run the validation script before deploying:
```bash
./validate-deployment.sh
```

## 📚 API Documentation

Once the backend is running, access interactive API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

```
GET  /health                    # Health check
GET  /system/health             # System health with circuit breaker
GET  /dashboard                 # Dashboard data
GET  /batches                   # List batches
POST /batches                   # Create batch
GET  /procedures                # List procedures
POST /batches/{id}/transition   # Execute state transition
GET  /audit                     # Audit logs
```

## 🔒 Security

- All database operations are audited
- Role-based access control enforced at API level
- Cryptographic signatures for procedure immutability
- CORS configured for specific origins only
- SQL injection protection via SQLAlchemy ORM

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
- Check `DATABASE_URL` is correct
- Ensure PostgreSQL is running
- Verify Python dependencies are installed

**Frontend can't reach backend:**
- Check `NEXT_PUBLIC_API_URL` is set
- Verify backend is running: `curl http://localhost:8000/health`
- Check CORS configuration

**Docker issues:**
- View logs: `docker-compose logs -f`
- Restart: `docker-compose restart`
- Rebuild: `docker-compose up -d --build`

See [DEPLOYMENT.md](./DEPLOYMENT.md) for more troubleshooting tips.

## 📄 License

This project is part of an academic/competition submission.

## 🤝 Contributing

This is a competition/academic project. For questions or issues, please create a GitHub issue.

## 📞 Support

- **Documentation**: See [DEPLOYMENT.md](./DEPLOYMENT.md)
- **Issues**: Create a GitHub issue
- **Demo Scripts**: See `DEMO_SCRIPT.md` and `IMAGINE_CUP_DEMO_SCRIPT.md`

---

**Built with ❤️ for regulatory compliance and immutable procedure enforcement**
