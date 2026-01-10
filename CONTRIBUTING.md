# Contributing to ProcGuard

Thank you for your interest in contributing to ProcGuard! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Code Style](#code-style)

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Procguard.git
   cd Procguard
   ```
3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/Sasisundar2211/Procguard.git
   ```

## Development Setup

### Quick Setup

```bash
# Copy environment file
cp .env.example .env

# Install dependencies
make install

# Start development environment
make docker-up
```

### Manual Setup

#### Backend Setup

```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Set up environment
export DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/procguard"
export AI_ENABLED="false"

# Run backend
uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup

```bash
# Install Node.js dependencies
npm install

# Set up environment
export NEXT_PUBLIC_API_URL="http://localhost:8000"

# Run frontend
npm run dev
```

## Project Structure

```
Procguard/
├── app/                      # FastAPI Backend
│   ├── api/                 # API routes
│   │   ├── batches.py       # Batch management
│   │   ├── procedures.py    # Procedure management
│   │   └── ...
│   ├── core/                # Core business logic
│   │   ├── fsm.py          # Finite State Machine
│   │   ├── audit.py        # Audit logging
│   │   └── ...
│   ├── models/              # SQLAlchemy models
│   ├── services/            # Service layer
│   └── main.py              # FastAPI app entry
├── src/                     # Next.js Frontend
│   ├── app/                # Next.js app directory
│   └── components/         # React components
├── infra/                   # Infrastructure as Code (Bicep)
├── tests/                   # Test files
└── docs/                    # Documentation

```

## Making Changes

### Branching Strategy

- `main` - Production-ready code
- `develop` - Development branch
- `feature/*` - New features
- `fix/*` - Bug fixes
- `docs/*` - Documentation updates

### Creating a Feature Branch

```bash
# Update your fork
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/my-new-feature
```

### Commit Guidelines

Write clear, concise commit messages:

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

**Example:**
```
feat: add batch filtering by date range

- Add date range filter to batch list API
- Update frontend to support date filtering
- Add tests for new filtering logic

Closes #123
```

## Testing

### Running Tests

```bash
# All tests
make test

# Backend tests only
pytest -v

# Frontend linting
npm run lint
```

### Writing Tests

- Add tests for all new features
- Ensure existing tests pass
- Aim for good test coverage

**Backend test example:**
```python
def test_batch_creation(db: Session):
    batch = create_batch(db, procedure_id="test-proc")
    assert batch.state == "PENDING"
    assert batch.procedure_id == "test-proc"
```

## Submitting Changes

### Pull Request Process

1. **Update your branch**:
   ```bash
   git checkout main
   git pull upstream main
   git checkout feature/my-feature
   git rebase main
   ```

2. **Run tests and validation**:
   ```bash
   make test
   make validate
   ```

3. **Push to your fork**:
   ```bash
   git push origin feature/my-feature
   ```

4. **Create Pull Request**:
   - Go to GitHub and create a PR from your fork
   - Fill in the PR template
   - Link related issues

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No merge conflicts
- [ ] CI/CD pipeline passes

## Code Style

### Python (Backend)

- Follow PEP 8
- Use type hints
- Write docstrings for functions/classes
- Keep functions focused and small

**Example:**
```python
from typing import Optional
from sqlalchemy.orm import Session

def get_batch_by_id(db: Session, batch_id: str) -> Optional[Batch]:
    """
    Retrieve a batch by its ID.
    
    Args:
        db: Database session
        batch_id: Unique identifier of the batch
        
    Returns:
        Batch object if found, None otherwise
    """
    return db.query(Batch).filter(Batch.id == batch_id).first()
```

### TypeScript/React (Frontend)

- Use TypeScript for type safety
- Follow React best practices
- Use functional components and hooks
- Keep components small and reusable

**Example:**
```typescript
interface BatchListProps {
  batches: Batch[];
  onBatchClick: (id: string) => void;
}

export function BatchList({ batches, onBatchClick }: BatchListProps) {
  return (
    <div>
      {batches.map(batch => (
        <BatchCard 
          key={batch.id} 
          batch={batch} 
          onClick={() => onBatchClick(batch.id)}
        />
      ))}
    </div>
  );
}
```

### SQL/Database

- Use migrations for schema changes (Alembic)
- Add indexes for frequently queried columns
- Use transactions for data consistency

## Development Tips

### Useful Commands

```bash
# See all available commands
make help

# Check code health
make validate

# View service logs
make docker-logs

# Restart services
make docker-restart

# Clean build artifacts
make clean
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Debugging

**Backend:**
- Use breakpoint debugger with VSCode/PyCharm
- Add logging: `import logging; logging.info("Debug message")`
- Check logs: `docker compose logs backend`

**Frontend:**
- Use browser DevTools
- Check console for errors
- Use React DevTools extension

## Getting Help

- **Documentation**: Check [DEPLOYMENT.md](./DEPLOYMENT.md) and [README.md](./README.md)
- **Issues**: Create a GitHub issue
- **Questions**: Add discussion in PR or issue

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to ProcGuard! 🛡️
