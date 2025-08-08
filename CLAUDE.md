# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VocalIQ is an intelligent AI-powered telephone assistant system that automates business phone communications. It uses FastAPI (Python) for the backend and React/TypeScript for the frontend dashboard, with integrations for Twilio (telephony), OpenAI GPT-4 (conversation AI), and ElevenLabs (text-to-speech).

## Essential Commands

### Development Workflow
```bash
# Initial setup
make setup              # Create directories and copy environment files
cp env.example .env     # Configure environment (edit with required API keys)
make up                 # Start all development services
make db-init           # Initialize database with migrations and seed data

# Daily development
make up                 # Start services
make down              # Stop services
make restart           # Restart all services
make logs              # View API logs
make status            # Check container status

# Code quality
make lint              # Run Python linters (ruff, mypy)
make format            # Auto-format Python code
npm run lint           # Lint TypeScript/React code
npm run format         # Format TypeScript/React code
npm run type-check     # TypeScript type checking

# Testing
make test              # Run all tests
make test-unit         # Unit tests only
make test-coverage     # Tests with coverage report
npm run test           # Frontend tests
npm run test:coverage  # Frontend coverage

# Database operations
make db-migrate message="your migration message"  # Create new migration
make db-upgrade        # Apply pending migrations
make db-downgrade      # Rollback last migration
make backup            # Create database backup

# Debugging
make shell-api         # Access API container shell
make shell-db          # PostgreSQL shell
make redis-cli         # Redis CLI
```

### Frontend Development
```bash
cd frontend/           # Navigate to frontend directory first
npm run dev           # Start Vite dev server (http://localhost:5173)
npm run build         # Production build
npm run preview       # Preview production build
```

## Architecture Overview

### Service Architecture
The system uses a microservices architecture with Docker Compose:

- **API Service** (`api:8000`): FastAPI backend handling all business logic
  - Uses SQLModel ORM with PostgreSQL
  - Async/await patterns throughout
  - Service layer pattern for business logic
  - Dependency injection for testing

- **Frontend** (`frontend:5173`): React dashboard
  - Vite for fast development
  - Material-UI + Tailwind CSS
  - Zustand for state management
  - React Query for server state

- **Databases**:
  - PostgreSQL 15: Primary data store
  - Redis 7: Caching and session management
  - Weaviate: Vector database for AI features

- **External Services**:
  - Twilio: Phone call handling
  - OpenAI: GPT-4 for conversations
  - ElevenLabs: Text-to-speech

### Key Design Patterns
1. **Event-driven communication** via Redis pub/sub
2. **Multi-tenant isolation** by organization
3. **WebSocket server** for real-time audio streaming
4. **Background job processing** with Celery
5. **API versioning** (v1 prefix)

### Directory Structure
```
backend/
├── api/              # FastAPI application
│   ├── routes/       # API endpoints
│   ├── services/     # Business logic
│   ├── models/       # SQLModel entities
│   └── utils/        # Helpers
├── migrations/       # Alembic database migrations
└── tests/           # Test suites

frontend/
├── src/
│   ├── components/   # React components
│   ├── pages/       # Route pages
│   ├── services/    # API clients
│   ├── stores/      # Zustand stores
│   └── utils/       # Helpers
```

## Development Best Practices

### API Development
- All endpoints require authentication (JWT bearer tokens)
- Use dependency injection for services
- Return consistent response formats
- Implement proper error handling with HTTPException
- Add comprehensive logging
- Write docstrings in Google style

### Frontend Development
- Use TypeScript strict mode
- Implement error boundaries
- Use React Query for all API calls
- Keep components small and focused
- Use Material-UI theme consistently
- Implement proper loading and error states

### Testing Requirements
- Write tests for all new features
- Maintain 80%+ code coverage
- Use pytest fixtures for test data
- Mock external services in tests
- Test both success and error paths

### Git Workflow
- Branch from `develop` using `feature/VOCAL-XXX` naming
- Use conventional commits: `type(scope): message`
- Types: feat, fix, docs, style, refactor, test, chore
- Create pull requests to `develop`
- Require code review before merging

## Common Tasks

### Adding a New API Endpoint
1. Create route in `backend/api/routes/`
2. Implement service logic in `backend/api/services/`
3. Add SQLModel if needed in `backend/api/models/`
4. Write tests in `backend/tests/`
5. Update API documentation

### Adding a New Frontend Page
1. Create component in `frontend/src/pages/`
2. Add route in `frontend/src/App.tsx`
3. Create API service in `frontend/src/services/`
4. Add to navigation if needed
5. Write component tests

### Debugging Production Issues
1. Check logs: `make logs-prod`
2. Access production shell: `docker exec -it vocaliq-api-prod bash`
3. Check monitoring: Grafana at http://localhost:3000
4. Review error tracking in application logs

## Important Configuration

### Required Environment Variables
- `OPENAI_API_KEY`: GPT-4 access
- `TWILIO_ACCOUNT_SID` & `TWILIO_AUTH_TOKEN`: Phone service
- `ELEVENLABS_API_KEY`: Text-to-speech
- `DATABASE_URL`: PostgreSQL connection
- `REDIS_URL`: Redis connection
- `SECRET_KEY` & `JWT_SECRET_KEY`: Security keys

### Feature Flags
Control features via environment variables:
- `FEATURE_VOICE_ANALYSIS`: Enable emotion detection
- `FEATURE_MULTI_LANGUAGE`: Enable language support
- `FEATURE_CALENDAR_SYNC`: Enable calendar integration

## Performance Considerations
- Use Redis caching for frequently accessed data
- Implement pagination for list endpoints
- Use database indexes on foreign keys and filters
- Optimize Weaviate queries with proper vectorization
- Monitor with Prometheus metrics

## Security Notes
- All API endpoints require authentication except `/auth/*`
- Sensitive data is encrypted at rest
- Use environment variables for all secrets
- Implement rate limiting on public endpoints
- Regular security dependency updates via Dependabot