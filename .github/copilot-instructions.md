# GitHub Copilot Instructions for VocalIQ

## Project Context

VocalIQ is an intelligent AI-powered telephone assistant system that automates business phone communications. The project uses:
- **Backend**: FastAPI (Python 3.11+), SQLModel, PostgreSQL, Redis
- **Frontend**: React 18, TypeScript, Material-UI, Tailwind CSS
- **AI/Voice**: OpenAI GPT-4, Whisper, ElevenLabs, Twilio
- **Infrastructure**: Docker, GitHub Actions, Prometheus/Grafana

## Code Style Guidelines

### Python Backend
- Use async/await patterns for all I/O operations
- Follow Google-style docstrings
- Use type hints for all function parameters and returns
- Implement dependency injection for services
- Use SQLModel for database models
- Handle errors with proper HTTPException responses
- Structure: `api/routes/` → `api/services/` → `api/models/`

### TypeScript/React Frontend
- Use functional components with hooks
- Implement proper TypeScript types (no `any`)
- Use React Query for server state management
- Use Zustand for client state management
- Follow Material-UI theming conventions
- Implement proper loading and error states
- Component structure: Small, focused, reusable

### Common Patterns
```python
# Service layer pattern
class AgentService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
    
    async def create_agent(self, agent_data: AgentCreate) -> Agent:
        # Implementation
```

```typescript
// React Query usage
const { data, isLoading, error } = useQuery({
  queryKey: ['agents', agentId],
  queryFn: () => agentService.getAgent(agentId),
});
```

## Security Considerations
- Never log or expose sensitive data (API keys, tokens)
- Always validate user input
- Use proper authentication (JWT bearer tokens)
- Implement rate limiting for public endpoints
- Sanitize all database queries

## Testing Requirements
- Write unit tests for all services
- Use pytest fixtures for test data
- Mock external services (Twilio, OpenAI)
- Maintain 80%+ code coverage
- Test both success and error scenarios

## Common Tasks

### Adding a New API Endpoint
1. Create route in `api/routes/`
2. Implement service logic in `api/services/`
3. Add request/response schemas
4. Write tests
5. Update API documentation

### Adding a New React Component
1. Create component with TypeScript
2. Add Material-UI styling
3. Implement loading/error states
4. Add to routing if needed
5. Write component tests

## Performance Best Practices
- Use Redis caching for frequently accessed data
- Implement database query optimization
- Use pagination for list endpoints
- Optimize bundle size with code splitting
- Monitor with Prometheus metrics

## Git Commit Conventions
Format: `type(scope): subject`

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- refactor: Code refactoring
- test: Tests
- chore: Maintenance

Example: `feat(agent): add multi-language support`

## External Service Integration
- **Twilio**: Handle webhooks for call events
- **OpenAI**: Stream responses for better UX
- **ElevenLabs**: Cache generated audio
- **Weaviate**: Optimize vector queries

## Database Conventions
- Use Alembic for migrations
- Name tables in plural (e.g., `agents`, `calls`)
- Use UUID for primary keys
- Add indexes on foreign keys
- Implement soft deletes where appropriate

## Error Handling
```python
# Consistent error responses
raise HTTPException(
    status_code=404,
    detail={
        "error": "not_found",
        "message": "Agent not found",
        "field": "agent_id"
    }
)
```

## Environment Variables
Always use environment variables for:
- API keys (OPENAI_API_KEY, TWILIO_AUTH_TOKEN, etc.)
- Database URLs
- Feature flags
- External service endpoints

Remember: Focus on writing clean, maintainable, and well-tested code that follows the established patterns in the codebase.