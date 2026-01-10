# ProcGuard

ProcGuard is a full-stack application for immutable procedure enforcement with compliance monitoring and audit logging.

## 🏗️ Architecture

- **Frontend**: Next.js 16 with React 19 and TypeScript
- **Backend**: FastAPI (Python) with PostgreSQL
- **Database**: PostgreSQL 16

## 🚀 Quick Start

### Local Development (Separate Services)

1. **Backend**
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Run backend
   uvicorn app.main:app --reload --port 8000
   ```

2. **Frontend**
   ```bash
   # Install Node dependencies
   npm install
   
   # Run frontend
   npm run dev
   ```

   Open [http://localhost:3000](http://localhost:3000) to view the application.

### Full Deployment (Frontend + Backend Together)

Deploy both frontend and backend as a unified application using Docker Compose:

```bash
# Make deployment script executable
chmod +x deploy.sh

# Deploy locally
./deploy.sh --mode local
```

This will start:
- Frontend at http://localhost:3000
- Backend API at http://localhost:8000
- PostgreSQL database at localhost:5432

For detailed deployment instructions including production and Azure deployments, see:

📖 **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Complete deployment guide

## 📚 Available Commands

```bash
npm run dev      # Start frontend development server
npm run build    # Build frontend for production
npm run start    # Start frontend production server
npm run lint     # Run ESLint on frontend code
```

## 🐳 Docker Deployment

We provide multiple deployment options:

1. **Local Development** (`docker-compose.yml`)
   - All services in one stack
   - Development mode with hot reload
   - Local PostgreSQL database

2. **Production** (`docker-compose.prod.yml`)
   - Optimized builds
   - Nginx reverse proxy
   - Production-ready configuration

3. **Azure** (`deploy.sh --mode azure`)
   - Azure Container Apps
   - Managed PostgreSQL
   - Auto-scaling

See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete instructions.

## 🔧 Environment Variables

Copy `.env.example` to `.env` and configure:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/procguard
NEXT_PUBLIC_API_URL=http://localhost:8000
AI_ENABLED=true
```

## 📖 API Documentation

Once the backend is running, access the interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Testing

```bash
# Backend tests
pytest

# Frontend tests (if configured)
npm test
```

## 📁 Project Structure

```
.
├── app/                    # Backend application
│   ├── api/               # API routes
│   ├── core/              # Core functionality
│   ├── models/            # Database models
│   └── main.py            # FastAPI app entry point
├── src/                   # Frontend source
│   ├── components/        # React components
│   └── types/             # TypeScript types
├── infra/                 # Infrastructure as Code (Azure Bicep)
├── docker-compose.yml     # Local deployment
├── docker-compose.prod.yml # Production deployment
├── Dockerfile.frontend    # Frontend container
├── Dockerfile.backend     # Backend container
└── deploy.sh              # Unified deployment script
```

## 🔒 Security

- Immutable audit logging
- Role-based access control
- SQL injection prevention
- CORS protection
- Environment-based secrets

## 📝 Learn More

### Frontend (Next.js)
- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)

### Backend (FastAPI)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

### Database
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For deployment issues, see [DEPLOYMENT.md](./DEPLOYMENT.md)

For other questions, please open an issue on GitHub.
