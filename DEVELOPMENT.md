# VocalIQ Developer Handbook

## Inhaltsverzeichnis

1. [Entwicklungsumgebung einrichten](#entwicklungsumgebung-einrichten)
2. [Projekt-Struktur](#projekt-struktur)
3. [Coding Standards](#coding-standards)
4. [Git Workflow](#git-workflow)
5. [Testing-Strategie](#testing-strategie)
6. [API-Entwicklung](#api-entwicklung)
7. [Frontend-Entwicklung](#frontend-entwicklung)
8. [Datenbank-Entwicklung](#datenbank-entwicklung)
9. [Debugging & Troubleshooting](#debugging--troubleshooting)
10. [Performance-Optimierung](#performance-optimierung)
11. [Sicherheitspraktiken](#sicherheitspraktiken)
12. [CI/CD Integration](#cicd-integration)

## Entwicklungsumgebung einrichten

### 1. Systemvoraussetzungen

```bash
# Überprüfen Sie Ihre Entwicklungsumgebung
python --version  # Python 3.11+
node --version    # Node 18+
docker --version  # Docker 20.10+
git --version     # Git 2.30+
```

### 2. Repository Setup

```bash
# Repository klonen
git clone https://github.com/vocaliq/vocaliq.git
cd vocaliq

# Git Hooks installieren
pip install pre-commit
pre-commit install

# Entwicklungsumgebung initialisieren
make dev-setup
```

### 3. IDE-Konfiguration

#### VS Code Settings
```json
// .vscode/settings.json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "88"],
  "python.sortImports.args": ["--profile", "black"],
  "python.testing.pytestEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "typescript.updateImportsOnFileMove.enabled": "always",
  "eslint.validate": ["javascript", "typescript", "typescriptreact"]
}
```

#### PyCharm Configuration
```xml
<!-- .idea/vocaliq.iml -->
<module type="PYTHON_MODULE" version="4">
  <component name="NewModuleRootManager">
    <content url="file://$MODULE_DIR$">
      <sourceFolder url="file://$MODULE_DIR$/backend" isTestSource="false" />
      <excludeFolder url="file://$MODULE_DIR$/backend/.venv" />
    </content>
    <orderEntry type="jdk" jdkName="Python 3.11 (vocaliq)" jdkType="Python SDK" />
  </component>
  <component name="PyDocumentationSettings">
    <option name="format" value="GOOGLE" />
    <option name="myDocStringFormat" value="Google" />
  </component>
</module>
```

### 4. Lokale Services starten

```bash
# Alle Services mit Docker Compose
make up

# Einzelne Services für Entwicklung
make up-db      # Nur Datenbank
make up-redis   # Nur Redis
make up-api     # Nur API (mit Hot-Reload)

# Frontend separat entwickeln
cd backend/frontend
npm install
npm run dev
```

## Projekt-Struktur

```
vocaliq/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI Application
│   │   ├── config.py            # Konfiguration
│   │   ├── dependencies.py      # Dependency Injection
│   │   ├── middleware/          # Custom Middleware
│   │   │   ├── auth.py
│   │   │   ├── cors.py
│   │   │   ├── logging.py
│   │   │   └── metrics.py
│   │   ├── models/              # SQLModel Datenmodelle
│   │   │   ├── base.py
│   │   │   ├── organization.py
│   │   │   ├── agent.py
│   │   │   ├── call.py
│   │   │   └── user.py
│   │   ├── routers/             # API Endpoints
│   │   │   ├── auth.py
│   │   │   ├── agents.py
│   │   │   ├── calls.py
│   │   │   └── ...
│   │   ├── services/            # Business Logic
│   │   │   ├── auth.py
│   │   │   ├── conversation.py
│   │   │   ├── stt.py
│   │   │   ├── tts.py
│   │   │   └── twilio_client.py
│   │   ├── schemas/             # Pydantic Schemas
│   │   │   ├── request/
│   │   │   └── response/
│   │   └── utils/               # Hilfsfunktionen
│   ├── alembic/                 # Datenbank-Migrationen
│   ├── tests/                   # Tests
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   └── frontend/                # React Dashboard
│       ├── src/
│       │   ├── components/
│       │   ├── hooks/
│       │   ├── pages/
│       │   ├── services/
│       │   ├── store/
│       │   └── utils/
│       └── public/
├── docker/                      # Docker-Konfigurationen
├── k8s/                        # Kubernetes Manifests
├── scripts/                    # Utility Scripts
├── docs/                       # Dokumentation
└── monitoring/                 # Monitoring-Konfiguration
```

## Coding Standards

### Python Code Style

```python
"""
Modul-Docstring im Google Style.

Dieses Modul implementiert die Hauptfunktionalität für...
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from api.models.agent import Agent
from api.schemas.request.agent import AgentCreateRequest
from api.schemas.response.agent import AgentResponse
from api.dependencies import get_db

logger = logging.getLogger(__name__)


class AgentService:
    """Service-Klasse für Agent-Operationen.
    
    Diese Klasse kapselt die Business-Logik für Agent-Management.
    
    Attributes:
        db: Datenbank-Session
        cache: Redis-Cache-Client
    """
    
    def __init__(self, db: Session = Depends(get_db)):
        """Initialisiert den AgentService.
        
        Args:
            db: SQLModel Datenbank-Session
        """
        self.db = db
    
    async def create_agent(
        self,
        agent_data: AgentCreateRequest,
        organization_id: str
    ) -> AgentResponse:
        """Erstellt einen neuen Agent.
        
        Args:
            agent_data: Agent-Erstellungsdaten
            organization_id: ID der Organisation
            
        Returns:
            Der erstellte Agent
            
        Raises:
            HTTPException: Bei Validierungsfehlern
        """
        # Validierung
        if await self._agent_name_exists(agent_data.name, organization_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Agent mit Namen '{agent_data.name}' existiert bereits"
            )
        
        # Agent erstellen
        agent = Agent(
            **agent_data.dict(),
            organization_id=organization_id,
            created_at=datetime.utcnow()
        )
        
        try:
            self.db.add(agent)
            self.db.commit()
            self.db.refresh(agent)
            
            logger.info(
                f"Agent erstellt: {agent.id} für Organisation {organization_id}"
            )
            
            return AgentResponse.from_orm(agent)
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Agents: {e}")
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Interner Serverfehler"
            )
    
    async def _agent_name_exists(
        self,
        name: str,
        organization_id: str
    ) -> bool:
        """Prüft, ob ein Agent-Name bereits existiert.
        
        Args:
            name: Name des Agents
            organization_id: ID der Organisation
            
        Returns:
            True wenn der Name existiert, sonst False
        """
        statement = select(Agent).where(
            Agent.name == name,
            Agent.organization_id == organization_id
        )
        result = self.db.exec(statement).first()
        return result is not None


# Konstanten am Ende des Moduls
DEFAULT_AGENT_CONFIG = {
    "greeting": "Guten Tag, wie kann ich Ihnen helfen?",
    "language": "de",
    "voice": {
        "provider": "elevenlabs",
        "voice_id": "default"
    }
}

MAX_AGENTS_PER_ORGANIZATION = 10
```

### TypeScript/React Code Style

```typescript
/**
 * Agent-Konfigurations-Komponente
 * 
 * Diese Komponente ermöglicht die Konfiguration von Voice Agents.
 */
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Box, TextField, Button, Alert } from '@mui/material';
import { useTranslation } from 'react-i18next';

import { AgentService } from '@/services/agent.service';
import { useAuth } from '@/hooks/useAuth';
import { AgentConfig, UpdateAgentRequest } from '@/types/agent';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';

interface AgentConfigurationProps {
  agentId: string;
  onSave?: (agent: AgentConfig) => void;
  readonly?: boolean;
}

/**
 * Agent-Konfigurations-Komponente
 */
export const AgentConfiguration: React.FC<AgentConfigurationProps> = ({
  agentId,
  onSave,
  readonly = false,
}) => {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  
  // State Management
  const [config, setConfig] = useState<Partial<AgentConfig>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  
  // API Queries
  const { data: agent, isLoading, error } = useQuery({
    queryKey: ['agent', agentId],
    queryFn: () => AgentService.getAgent(agentId),
    enabled: !!agentId,
    staleTime: 5 * 60 * 1000, // 5 Minuten
  });
  
  // Mutations
  const updateMutation = useMutation({
    mutationFn: (data: UpdateAgentRequest) => 
      AgentService.updateAgent(agentId, data),
    onSuccess: (updatedAgent) => {
      queryClient.invalidateQueries({ queryKey: ['agent', agentId] });
      onSave?.(updatedAgent);
    },
    onError: (error: Error) => {
      setErrors({ general: error.message });
    },
  });
  
  // Memoized Values
  const isValid = useMemo(() => {
    return config.name?.trim().length > 0 && 
           config.greeting?.trim().length > 0;
  }, [config]);
  
  // Effects
  useEffect(() => {
    if (agent) {
      setConfig(agent.config);
    }
  }, [agent]);
  
  // Callbacks
  const handleChange = useCallback((
    field: keyof AgentConfig,
    value: string
  ) => {
    setConfig(prev => ({ ...prev, [field]: value }));
    setErrors(prev => ({ ...prev, [field]: '' }));
  }, []);
  
  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!isValid) {
      setErrors({ general: t('errors.invalidForm') });
      return;
    }
    
    try {
      await updateMutation.mutateAsync({
        config: config as AgentConfig,
      });
    } catch (error) {
      console.error('Failed to update agent:', error);
    }
  }, [config, isValid, updateMutation, t]);
  
  // Render
  if (isLoading) {
    return <LoadingSpinner />;
  }
  
  if (error) {
    return (
      <Alert severity="error">
        {t('errors.loadingFailed')}
      </Alert>
    );
  }
  
  return (
    <ErrorBoundary>
      <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
        <TextField
          fullWidth
          label={t('agent.name')}
          value={config.name || ''}
          onChange={(e) => handleChange('name', e.target.value)}
          error={!!errors.name}
          helperText={errors.name}
          disabled={readonly}
          margin="normal"
          required
        />
        
        <TextField
          fullWidth
          multiline
          rows={4}
          label={t('agent.greeting')}
          value={config.greeting || ''}
          onChange={(e) => handleChange('greeting', e.target.value)}
          error={!!errors.greeting}
          helperText={errors.greeting}
          disabled={readonly}
          margin="normal"
          required
        />
        
        {errors.general && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {errors.general}
          </Alert>
        )}
        
        {!readonly && (
          <Button
            type="submit"
            variant="contained"
            fullWidth
            sx={{ mt: 3 }}
            disabled={!isValid || updateMutation.isPending}
          >
            {updateMutation.isPending ? t('common.saving') : t('common.save')}
          </Button>
        )}
      </Box>
    </ErrorBoundary>
  );
};

// Default Export
export default AgentConfiguration;
```

### Code Review Checklist

```markdown
## Code Review Checklist

### Allgemein
- [ ] Code folgt den Projekt-Coding-Standards
- [ ] Keine auskommentierten Code-Blöcke
- [ ] Aussagekräftige Variablen- und Funktionsnamen
- [ ] Angemessene Kommentare für komplexe Logik

### Python
- [ ] Type Hints für alle Funktionen
- [ ] Docstrings im Google Style
- [ ] Keine zirkulären Imports
- [ ] Async/Await korrekt verwendet
- [ ] Exception Handling implementiert

### TypeScript/React
- [ ] Props und State korrekt typisiert
- [ ] Keine any-Types ohne Begründung
- [ ] useCallback/useMemo für Performance
- [ ] Error Boundaries implementiert
- [ ] Accessibility (a11y) berücksichtigt

### Testing
- [ ] Unit Tests vorhanden
- [ ] Integration Tests für kritische Pfade
- [ ] Test Coverage > 80%
- [ ] Edge Cases getestet

### Security
- [ ] Keine Secrets im Code
- [ ] Input Validierung
- [ ] SQL Injection Prevention
- [ ] XSS Prevention
- [ ] CORS korrekt konfiguriert

### Performance
- [ ] Keine N+1 Queries
- [ ] Caching wo sinnvoll
- [ ] Lazy Loading implementiert
- [ ] Bundle Size optimiert
```

## Git Workflow

### Branch-Strategie

```bash
main
├── develop
│   ├── feature/VOCAL-123-add-voice-selection
│   ├── feature/VOCAL-124-improve-stt-accuracy
│   └── feature/VOCAL-125-dashboard-redesign
├── release/v1.2.0
└── hotfix/VOCAL-126-fix-call-routing
```

### Commit-Konventionen

```bash
# Format: <type>(<scope>): <subject>

# Typen:
# feat: Neue Funktion
# fix: Bugfix
# docs: Dokumentation
# style: Formatierung
# refactor: Code-Refactoring
# perf: Performance-Verbesserung
# test: Tests
# chore: Wartungsarbeiten

# Beispiele:
git commit -m "feat(agent): add multi-language support"
git commit -m "fix(calls): resolve WebSocket connection drops"
git commit -m "docs(api): update authentication examples"
git commit -m "perf(stt): optimize audio processing pipeline"

# Commit mit Details
git commit -m "feat(dashboard): add real-time call monitoring

- Add WebSocket connection for live updates
- Implement call status indicators
- Add call duration counter
- Include participant information

Closes #123"
```

### Pull Request Template

```markdown
<!-- .github/pull_request_template.md -->
## Beschreibung
Kurze Beschreibung der Änderungen.

## Typ der Änderung
- [ ] Bug Fix
- [ ] Neue Funktion
- [ ] Breaking Change
- [ ] Dokumentation

## Checkliste
- [ ] Code folgt den Style Guidelines
- [ ] Selbst-Review durchgeführt
- [ ] Tests hinzugefügt/aktualisiert
- [ ] Dokumentation aktualisiert
- [ ] Keine Breaking Changes (oder dokumentiert)

## Testing
Beschreibung der durchgeführten Tests.

## Screenshots (falls zutreffend)
Fügen Sie Screenshots für UI-Änderungen hinzu.

## Related Issues
Closes #(issue)
```

## Testing-Strategie

### Unit Tests (Backend)

```python
# tests/unit/services/test_agent_service.py
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from api.services.agent import AgentService
from api.schemas.request.agent import AgentCreateRequest
from api.models.agent import Agent


class TestAgentService:
    """Tests für AgentService."""
    
    @pytest.fixture
    def agent_service(self, db_session):
        """AgentService Fixture."""
        return AgentService(db=db_session)
    
    @pytest.fixture
    def sample_agent_data(self):
        """Beispiel Agent-Daten."""
        return AgentCreateRequest(
            name="Test Agent",
            description="Test Beschreibung",
            config={
                "greeting": "Hallo!",
                "language": "de"
            }
        )
    
    async def test_create_agent_success(
        self,
        agent_service,
        sample_agent_data
    ):
        """Test: Erfolgreiche Agent-Erstellung."""
        # Arrange
        organization_id = "org_123"
        
        # Act
        result = await agent_service.create_agent(
            sample_agent_data,
            organization_id
        )
        
        # Assert
        assert result.name == sample_agent_data.name
        assert result.organization_id == organization_id
        assert result.id is not None
    
    async def test_create_agent_duplicate_name(
        self,
        agent_service,
        sample_agent_data,
        db_session
    ):
        """Test: Agent mit doppeltem Namen."""
        # Arrange
        organization_id = "org_123"
        existing_agent = Agent(
            name=sample_agent_data.name,
            organization_id=organization_id
        )
        db_session.add(existing_agent)
        db_session.commit()
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await agent_service.create_agent(
                sample_agent_data,
                organization_id
            )
        
        assert exc_info.value.status_code == 400
        assert "existiert bereits" in str(exc_info.value.detail)
    
    @pytest.mark.parametrize("invalid_name", [
        "",
        "   ",
        None,
        "a" * 256,  # Zu lang
    ])
    async def test_create_agent_invalid_name(
        self,
        agent_service,
        sample_agent_data,
        invalid_name
    ):
        """Test: Agent mit ungültigem Namen."""
        # Arrange
        sample_agent_data.name = invalid_name
        
        # Act & Assert
        with pytest.raises(ValidationError):
            await agent_service.create_agent(
                sample_agent_data,
                "org_123"
            )
```

### Integration Tests (API)

```python
# tests/integration/test_api_calls.py
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

from api.main import app


class TestCallsAPI:
    """Integration Tests für Calls API."""
    
    @pytest.fixture
    async def authenticated_client(self, client: AsyncClient):
        """Client mit Authentifizierung."""
        # Login
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "test@example.com", "password": "password"}
        )
        token = response.json()["access_token"]
        
        # Set auth header
        client.headers["Authorization"] = f"Bearer {token}"
        return client
    
    @patch("api.services.twilio_client.TwilioClient.make_call")
    async def test_create_outbound_call(
        self,
        mock_make_call,
        authenticated_client: AsyncClient
    ):
        """Test: Outbound Call erstellen."""
        # Arrange
        mock_make_call.return_value = AsyncMock(
            sid="CA123456",
            status="initiated"
        )
        
        # Act
        response = await authenticated_client.post(
            "/api/v1/calls/outbound/start",
            json={
                "to_number": "+49301234567",
                "agent_id": "agent_123"
            }
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["sid"] == "CA123456"
        assert data["status"] == "initiated"
        mock_make_call.assert_called_once()
    
    async def test_get_call_details(
        self,
        authenticated_client: AsyncClient,
        sample_call
    ):
        """Test: Call-Details abrufen."""
        # Act
        response = await authenticated_client.get(
            f"/api/v1/calls/{sample_call.id}"
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_call.id)
        assert "transcript" in data
```

### Frontend Tests

```typescript
// tests/components/AgentConfiguration.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi } from 'vitest';

import { AgentConfiguration } from '@/components/AgentConfiguration';
import { AgentService } from '@/services/agent.service';

// Mocks
vi.mock('@/services/agent.service');
vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({ user: { id: 'user_123' } }),
}));

describe('AgentConfiguration', () => {
  let queryClient: QueryClient;
  
  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });
    
    vi.clearAllMocks();
  });
  
  const renderComponent = (props = {}) => {
    return render(
      <QueryClientProvider client={queryClient}>
        <AgentConfiguration agentId="agent_123" {...props} />
      </QueryClientProvider>
    );
  };
  
  it('sollte Agent-Daten laden und anzeigen', async () => {
    // Arrange
    const mockAgent = {
      id: 'agent_123',
      name: 'Test Agent',
      config: {
        greeting: 'Hallo!',
        language: 'de',
      },
    };
    
    (AgentService.getAgent as jest.Mock).mockResolvedValue(mockAgent);
    
    // Act
    renderComponent();
    
    // Assert
    await waitFor(() => {
      expect(screen.getByDisplayValue('Test Agent')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Hallo!')).toBeInTheDocument();
    });
  });
  
  it('sollte Änderungen speichern können', async () => {
    // Arrange
    const mockAgent = {
      id: 'agent_123',
      name: 'Test Agent',
      config: { greeting: 'Hallo!' },
    };
    
    const onSave = vi.fn();
    (AgentService.getAgent as jest.Mock).mockResolvedValue(mockAgent);
    (AgentService.updateAgent as jest.Mock).mockResolvedValue({
      ...mockAgent,
      config: { greeting: 'Neuer Gruß!' },
    });
    
    // Act
    renderComponent({ onSave });
    
    // Warte auf Laden
    await waitFor(() => {
      expect(screen.getByDisplayValue('Hallo!')).toBeInTheDocument();
    });
    
    // Ändere Greeting
    const greetingInput = screen.getByLabelText(/greeting/i);
    await userEvent.clear(greetingInput);
    await userEvent.type(greetingInput, 'Neuer Gruß!');
    
    // Speichern
    const saveButton = screen.getByRole('button', { name: /save/i });
    await userEvent.click(saveButton);
    
    // Assert
    await waitFor(() => {
      expect(AgentService.updateAgent).toHaveBeenCalledWith(
        'agent_123',
        expect.objectContaining({
          config: expect.objectContaining({
            greeting: 'Neuer Gruß!',
          }),
        })
      );
      expect(onSave).toHaveBeenCalled();
    });
  });
  
  it('sollte Validierungsfehler anzeigen', async () => {
    // Arrange
    const mockAgent = {
      id: 'agent_123',
      name: 'Test Agent',
      config: { greeting: 'Hallo!' },
    };
    
    (AgentService.getAgent as jest.Mock).mockResolvedValue(mockAgent);
    
    // Act
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByDisplayValue('Test Agent')).toBeInTheDocument();
    });
    
    // Lösche Name
    const nameInput = screen.getByLabelText(/name/i);
    await userEvent.clear(nameInput);
    
    // Versuche zu speichern
    const saveButton = screen.getByRole('button', { name: /save/i });
    await userEvent.click(saveButton);
    
    // Assert
    expect(screen.getByText(/invalid form/i)).toBeInTheDocument();
    expect(AgentService.updateAgent).not.toHaveBeenCalled();
  });
});
```

### E2E Tests

```typescript
// tests/e2e/call-flow.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Call Flow E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password');
    await page.click('button[type="submit"]');
    
    // Wait for redirect
    await page.waitForURL('/dashboard');
  });
  
  test('sollte einen Outbound Call starten können', async ({ page }) => {
    // Navigate to calls
    await page.goto('/calls');
    
    // Click new call button
    await page.click('button:has-text("New Call")');
    
    // Fill form
    await page.fill('[name="phoneNumber"]', '+49301234567');
    await page.selectOption('[name="agentId"]', 'agent_123');
    
    // Start call
    await page.click('button:has-text("Start Call")');
    
    // Verify call started
    await expect(page.locator('.call-status')).toContainText('Initiated');
    
    // Wait for connection
    await page.waitForSelector('.call-status:has-text("Connected")', {
      timeout: 30000
    });
    
    // Verify transcript appears
    await expect(page.locator('.transcript')).toBeVisible();
  });
  
  test('sollte Call-Historie anzeigen', async ({ page }) => {
    // Navigate to call history
    await page.goto('/calls/history');
    
    // Verify table loads
    await expect(page.locator('table')).toBeVisible();
    
    // Check for entries
    const rows = page.locator('tbody tr');
    await expect(rows).toHaveCount(10); // Default pagination
    
    // Click on a call
    await rows.first().click();
    
    // Verify details page
    await expect(page).toHaveURL(/\/calls\/[a-z0-9-]+/);
    await expect(page.locator('h1')).toContainText('Call Details');
  });
});
```

### Test-Utilities

```python
# tests/utils/fixtures.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from api.main import app
from api.dependencies import get_db
from api.models.base import Base


@pytest.fixture(scope="session")
def test_db():
    """Test-Datenbank Setup."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(bind=engine)
    
    yield SessionLocal()
    
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    """Test Client mit Test-DB."""
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client


@pytest.fixture
def auth_headers(client):
    """Authentifizierungs-Headers."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "test@example.com", "password": "password"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

## API-Entwicklung

### Router-Struktur

```python
# api/routers/agents.py
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from api.dependencies import get_db, get_current_user
from api.models.user import User
from api.services.agent import AgentService
from api.schemas.request.agent import (
    AgentCreateRequest,
    AgentUpdateRequest
)
from api.schemas.response.agent import (
    AgentResponse,
    AgentListResponse
)

router = APIRouter(
    prefix="/agents",
    tags=["agents"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/",
    response_model=AgentListResponse,
    summary="Liste aller Agents",
    description="Gibt eine paginierte Liste aller Agents der Organisation zurück."
)
async def list_agents(
    page: int = Query(1, ge=1, description="Seitennummer"),
    limit: int = Query(20, ge=1, le=100, description="Einträge pro Seite"),
    search: Optional[str] = Query(None, description="Suchbegriff"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> AgentListResponse:
    """Liste aller Agents abrufen."""
    service = AgentService(db)
    
    agents, total = await service.list_agents(
        organization_id=current_user.organization_id,
        page=page,
        limit=limit,
        search=search
    )
    
    return AgentListResponse(
        items=agents,
        total=total,
        page=page,
        pages=(total + limit - 1) // limit
    )


@router.post(
    "/",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Neuen Agent erstellen"
)
async def create_agent(
    agent_data: AgentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> AgentResponse:
    """Erstellt einen neuen Agent."""
    service = AgentService(db)
    
    return await service.create_agent(
        agent_data=agent_data,
        organization_id=current_user.organization_id
    )


@router.get(
    "/{agent_id}",
    response_model=AgentResponse,
    summary="Agent-Details abrufen"
)
async def get_agent(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> AgentResponse:
    """Ruft Details eines spezifischen Agents ab."""
    service = AgentService(db)
    
    return await service.get_agent(
        agent_id=agent_id,
        organization_id=current_user.organization_id
    )


@router.patch(
    "/{agent_id}",
    response_model=AgentResponse,
    summary="Agent aktualisieren"
)
async def update_agent(
    agent_id: str,
    update_data: AgentUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> AgentResponse:
    """Aktualisiert einen bestehenden Agent."""
    service = AgentService(db)
    
    return await service.update_agent(
        agent_id=agent_id,
        update_data=update_data,
        organization_id=current_user.organization_id
    )


@router.delete(
    "/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Agent löschen"
)
async def delete_agent(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """Löscht einen Agent."""
    service = AgentService(db)
    
    await service.delete_agent(
        agent_id=agent_id,
        organization_id=current_user.organization_id
    )
```

### Service Layer Pattern

```python
# api/services/base.py
from typing import TypeVar, Generic, Type, Optional, List, Tuple
from sqlmodel import Session, select
from fastapi import HTTPException, status

T = TypeVar("T")


class BaseService(Generic[T]):
    """Basis-Service-Klasse mit CRUD-Operationen."""
    
    model: Type[T]
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get(self, id: str) -> Optional[T]:
        """Einzelnes Objekt abrufen."""
        return self.db.get(self.model, id)
    
    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[T]:
        """Liste von Objekten abrufen."""
        query = select(self.model)
        
        # Filter anwenden
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.where(getattr(self.model, key) == value)
        
        query = query.offset(skip).limit(limit)
        results = self.db.exec(query)
        return results.all()
    
    async def create(self, **data) -> T:
        """Neues Objekt erstellen."""
        obj = self.model(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    async def update(self, id: str, **data) -> Optional[T]:
        """Objekt aktualisieren."""
        obj = await self.get(id)
        if not obj:
            return None
        
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    async def delete(self, id: str) -> bool:
        """Objekt löschen."""
        obj = await self.get(id)
        if not obj:
            return False
        
        self.db.delete(obj)
        self.db.commit()
        return True
```

### Background Tasks

```python
# api/tasks/call_processor.py
import asyncio
from typing import Optional
from celery import Celery
from datetime import datetime

from api.config import settings
from api.services.call import CallService
from api.services.transcription import TranscriptionService

# Celery Setup
celery_app = Celery(
    "vocaliq",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 Minuten
    task_soft_time_limit=25 * 60,  # 25 Minuten
)


@celery_app.task(bind=True, max_retries=3)
def process_call_recording(
    self,
    call_id: str,
    recording_url: str
) -> dict:
    """Verarbeitet eine Call-Aufnahme."""
    try:
        # Services initialisieren
        call_service = CallService()
        transcription_service = TranscriptionService()
        
        # Audio herunterladen
        audio_data = call_service.download_recording(recording_url)
        
        # Transkription erstellen
        transcript = transcription_service.transcribe(
            audio_data,
            language="de"
        )
        
        # Call aktualisieren
        call_service.update_transcript(call_id, transcript)
        
        # Analytics aktualisieren
        analyze_call_sentiment.delay(call_id, transcript)
        
        return {
            "status": "completed",
            "call_id": call_id,
            "transcript_length": len(transcript)
        }
        
    except Exception as e:
        # Retry mit exponential backoff
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))


@celery_app.task
def analyze_call_sentiment(call_id: str, transcript: str) -> dict:
    """Analysiert die Stimmung eines Anrufs."""
    # Sentiment-Analyse durchführen
    sentiment = analyze_sentiment(transcript)
    
    # Topics extrahieren
    topics = extract_topics(transcript)
    
    # Call-Metadaten aktualisieren
    call_service = CallService()
    call_service.update_metadata(
        call_id,
        {
            "sentiment": sentiment,
            "topics": topics,
            "analyzed_at": datetime.utcnow()
        }
    )
    
    return {
        "call_id": call_id,
        "sentiment": sentiment,
        "topics": topics
    }


# Worker starten mit:
# celery -A api.tasks.call_processor worker --loglevel=info
```

## Frontend-Entwicklung

### React Hooks

```typescript
// hooks/useWebSocket.ts
import { useEffect, useRef, useState, useCallback } from 'react';
import { useAuth } from './useAuth';

interface UseWebSocketOptions {
  onMessage?: (data: any) => void;
  onError?: (error: Event) => void;
  onClose?: () => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export function useWebSocket(
  url: string,
  options: UseWebSocketOptions = {}
) {
  const {
    onMessage,
    onError,
    onClose,
    reconnectInterval = 5000,
    maxReconnectAttempts = 5,
  } = options;
  
  const { token } = useAuth();
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectCount = useRef(0);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }
    
    const wsUrl = `${url}?token=${token}`;
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      reconnectCount.current = 0;
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLastMessage(data);
      onMessage?.(data);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      onError?.(error);
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
      onClose?.();
      
      // Auto-reconnect
      if (reconnectCount.current < maxReconnectAttempts) {
        reconnectCount.current++;
        setTimeout(connect, reconnectInterval);
      }
    };
    
    wsRef.current = ws;
  }, [url, token, onMessage, onError, onClose]);
  
  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);
  
  const sendMessage = useCallback((data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    } else {
      console.error('WebSocket is not connected');
    }
  }, []);
  
  useEffect(() => {
    connect();
    
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);
  
  return {
    isConnected,
    lastMessage,
    sendMessage,
    reconnect: connect,
    disconnect,
  };
}
```

### State Management (Zustand)

```typescript
// store/callStore.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

interface Call {
  id: string;
  status: 'initiated' | 'ringing' | 'connected' | 'completed' | 'failed';
  phoneNumber: string;
  agentId: string;
  startTime: Date;
  endTime?: Date;
  transcript?: TranscriptMessage[];
}

interface TranscriptMessage {
  role: 'agent' | 'customer';
  content: string;
  timestamp: Date;
}

interface CallState {
  calls: Record<string, Call>;
  activeCalls: string[];
  
  // Actions
  addCall: (call: Call) => void;
  updateCall: (id: string, updates: Partial<Call>) => void;
  removeCall: (id: string) => void;
  addTranscriptMessage: (callId: string, message: TranscriptMessage) => void;
  
  // Selectors
  getActiveCallsCount: () => number;
  getCallById: (id: string) => Call | undefined;
}

export const useCallStore = create<CallState>()(
  devtools(
    persist(
      immer((set, get) => ({
        calls: {},
        activeCalls: [],
        
        addCall: (call) =>
          set((state) => {
            state.calls[call.id] = call;
            if (call.status !== 'completed' && call.status !== 'failed') {
              state.activeCalls.push(call.id);
            }
          }),
        
        updateCall: (id, updates) =>
          set((state) => {
            if (state.calls[id]) {
              Object.assign(state.calls[id], updates);
              
              // Update active calls list
              const isActive = 
                updates.status !== 'completed' && 
                updates.status !== 'failed';
              
              const index = state.activeCalls.indexOf(id);
              if (isActive && index === -1) {
                state.activeCalls.push(id);
              } else if (!isActive && index !== -1) {
                state.activeCalls.splice(index, 1);
              }
            }
          }),
        
        removeCall: (id) =>
          set((state) => {
            delete state.calls[id];
            const index = state.activeCalls.indexOf(id);
            if (index !== -1) {
              state.activeCalls.splice(index, 1);
            }
          }),
        
        addTranscriptMessage: (callId, message) =>
          set((state) => {
            if (state.calls[callId]) {
              if (!state.calls[callId].transcript) {
                state.calls[callId].transcript = [];
              }
              state.calls[callId].transcript!.push(message);
            }
          }),
        
        getActiveCallsCount: () => get().activeCalls.length,
        
        getCallById: (id) => get().calls[id],
      })),
      {
        name: 'call-storage',
        partialize: (state) => ({ calls: state.calls }),
      }
    )
  )
);
```

### API Client Service

```typescript
// services/api.client.ts
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { useAuthStore } from '@/store/authStore';

class ApiClient {
  private client: AxiosInstance;
  
  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    this.setupInterceptors();
  }
  
  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = useAuthStore.getState().accessToken;
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
    
    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            await useAuthStore.getState().refreshToken();
            const newToken = useAuthStore.getState().accessToken;
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            return this.client(originalRequest);
          } catch (refreshError) {
            useAuthStore.getState().logout();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }
        
        return Promise.reject(error);
      }
    );
  }
  
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config);
    return response.data;
  }
  
  async post<T>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }
  
  async put<T>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response = await this.client.put<T>(url, data, config);
    return response.data;
  }
  
  async patch<T>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response = await this.client.patch<T>(url, data, config);
    return response.data;
  }
  
  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config);
    return response.data;
  }
}

export const apiClient = new ApiClient();
```

## Datenbank-Entwicklung

### Migration erstellen

```bash
# Neue Migration erstellen
cd backend
alembic revision --autogenerate -m "add user preferences table"

# Migration manuell bearbeiten
vim alembic/versions/xxx_add_user_preferences_table.py
```

### Migration Beispiel

```python
# alembic/versions/001_add_user_preferences_table.py
"""add user preferences table

Revision ID: 001
Revises: 
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Create user_preferences table
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('theme', sa.String(), nullable=True, default='light'),
        sa.Column('language', sa.String(), nullable=True, default='de'),
        sa.Column('notifications_enabled', sa.Boolean(), nullable=True, default=True),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Create indexes
    op.create_index(
        'ix_user_preferences_user_id',
        'user_preferences',
        ['user_id'],
        unique=True
    )
    
    # Add check constraint
    op.create_check_constraint(
        'ck_user_preferences_theme',
        'user_preferences',
        "theme IN ('light', 'dark', 'auto')"
    )


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_table('user_preferences')
```

### Datenbank-Optimierung

```sql
-- Indexes für Performance
CREATE INDEX idx_calls_organization_created 
ON calls(organization_id, created_at DESC);

CREATE INDEX idx_calls_status 
ON calls(status) 
WHERE status IN ('initiated', 'ringing', 'connected');

CREATE INDEX idx_conversations_call_id 
ON conversations(call_id);

-- Partitionierung für große Tabellen
CREATE TABLE calls_2024_01 PARTITION OF calls
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Materialized Views für Analytics
CREATE MATERIALIZED VIEW daily_call_stats AS
SELECT 
    date_trunc('day', created_at) as day,
    organization_id,
    COUNT(*) as total_calls,
    COUNT(*) FILTER (WHERE status = 'completed') as completed_calls,
    AVG(duration) as avg_duration,
    COUNT(DISTINCT agent_id) as active_agents
FROM calls
GROUP BY 1, 2;

-- Refresh Schedule
CREATE OR REPLACE FUNCTION refresh_daily_stats()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY daily_call_stats;
END;
$$ LANGUAGE plpgsql;

-- Scheduled Job
SELECT cron.schedule(
    'refresh-daily-stats',
    '0 1 * * *',  -- Täglich um 1 Uhr
    'SELECT refresh_daily_stats();'
);
```

## Debugging & Troubleshooting

### Logging Setup

```python
# api/utils/logging.py
import logging
import sys
from pythonjsonlogger import jsonlogger
from contextvars import ContextVar

# Context variable für Request ID
request_id_var: ContextVar[str] = ContextVar('request_id', default='')


class RequestIdFilter(logging.Filter):
    """Fügt Request ID zu Log Records hinzu."""
    
    def filter(self, record):
        record.request_id = request_id_var.get()
        return True


def setup_logging(log_level: str = "INFO"):
    """Konfiguriert das Logging-System."""
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # JSON Formatter
    json_formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={
            "asctime": "timestamp",
            "levelname": "level",
            "name": "logger"
        }
    )
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    console_handler.addFilter(RequestIdFilter())
    
    root_logger.addHandler(console_handler)
    
    # Spezielle Logger-Konfiguration
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    return root_logger
```

### Debug Middleware

```python
# api/middleware/debug.py
import time
import json
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Message

from api.utils.logging import request_id_var


class DebugMiddleware(BaseHTTPMiddleware):
    """Debug Middleware für Request/Response Logging."""
    
    async def dispatch(self, request: Request, call_next):
        # Request ID setzen
        request_id = request.headers.get("X-Request-ID", generate_id())
        request_id_var.set(request_id)
        
        # Start time
        start_time = time.time()
        
        # Request logging
        logger.debug(
            "Request started",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "headers": dict(request.headers),
            }
        )
        
        # Process request
        response = await call_next(request)
        
        # Duration
        duration = time.time() - start_time
        
        # Response logging
        logger.debug(
            "Request completed",
            extra={
                "status_code": response.status_code,
                "duration": duration,
                "request_id": request_id,
            }
        )
        
        # Add headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = str(duration)
        
        return response
```

### Profiling

```python
# api/utils/profiling.py
import cProfile
import pstats
import io
from functools import wraps
from typing import Callable

def profile(sort_by: str = "cumulative"):
    """Decorator für Performance Profiling."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            profiler.enable()
            
            try:
                result = await func(*args, **kwargs)
            finally:
                profiler.disable()
                
                # Stats ausgeben
                s = io.StringIO()
                ps = pstats.Stats(profiler, stream=s).sort_stats(sort_by)
                ps.print_stats(20)  # Top 20 Functions
                
                logger.info(f"Profile for {func.__name__}:\n{s.getvalue()}")
            
            return result
        return wrapper
    return decorator


# Verwendung:
@profile()
async def slow_endpoint():
    # Code hier
    pass
```

### Debug Tools

```bash
# Memory Profiling
pip install memory-profiler
python -m memory_profiler api/main.py

# Line Profiling
pip install line_profiler
kernprof -l -v api/services/conversation.py

# API Testing mit httpie
http POST localhost:8000/api/v1/calls/outbound/start \
  Authorization:"Bearer $TOKEN" \
  to_number="+49301234567" \
  agent_id="agent_123"

# WebSocket Testing
pip install websocket-client
python -m websocket ws://localhost:8000/ws/media/test

# Database Query Monitoring
echo "SELECT * FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;" | \
  docker exec -i postgres psql -U vocaliq
```

## Performance-Optimierung

### Caching-Strategie

```python
# api/utils/cache.py
from functools import wraps
from typing import Optional, Callable, Any
import hashlib
import json
import redis.asyncio as redis

from api.config import settings

# Redis Client
redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)


def cache_key_wrapper(prefix: str) -> Callable:
    """Erstellt Cache Keys basierend auf Funktionsargumenten."""
    def generate_key(*args, **kwargs) -> str:
        # Serialisiere Argumente
        key_data = {
            "args": args,
            "kwargs": kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    return generate_key


def cache(
    expire: int = 300,
    prefix: Optional[str] = None,
    condition: Optional[Callable[..., bool]] = None
):
    """Caching Decorator für async Funktionen."""
    def decorator(func: Callable) -> Callable:
        key_prefix = prefix or f"{func.__module__}.{func.__name__}"
        generate_key = cache_key_wrapper(key_prefix)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Check condition
            if condition and not condition(*args, **kwargs):
                return await func(*args, **kwargs)
            
            # Generate cache key
            cache_key = generate_key(*args, **kwargs)
            
            # Try to get from cache
            cached = await redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await redis_client.setex(
                cache_key,
                expire,
                json.dumps(result)
            )
            
            return result
        
        # Add cache control methods
        wrapper.invalidate = lambda *args, **kwargs: redis_client.delete(
            generate_key(*args, **kwargs)
        )
        wrapper.invalidate_pattern = lambda pattern: redis_client.delete(
            *redis_client.scan_iter(match=f"{key_prefix}:{pattern}")
        )
        
        return wrapper
    return decorator


# Verwendung:
@cache(expire=600, prefix="agent_config")
async def get_agent_config(agent_id: str) -> dict:
    # Expensive database query
    return await db.get_agent_config(agent_id)

# Cache invalidieren
await get_agent_config.invalidate("agent_123")
```

### Query Optimierung

```python
# api/services/optimized_queries.py
from sqlmodel import select, col
from sqlalchemy import func
from sqlalchemy.orm import selectinload, joinedload

class OptimizedCallService:
    """Service mit optimierten Datenbank-Queries."""
    
    async def get_calls_with_details(
        self,
        organization_id: str,
        limit: int = 100
    ):
        """Lädt Calls mit allen Details in einem Query."""
        # Verwende joinedload für 1:1 Beziehungen
        # und selectinload für 1:n Beziehungen
        stmt = (
            select(Call)
            .where(Call.organization_id == organization_id)
            .options(
                joinedload(Call.agent),
                selectinload(Call.conversations).selectinload(
                    Conversation.messages
                ),
                selectinload(Call.recordings)
            )
            .order_by(Call.created_at.desc())
            .limit(limit)
        )
        
        result = await self.db.exec(stmt)
        return result.unique().all()
    
    async def get_call_statistics(
        self,
        organization_id: str,
        start_date: datetime,
        end_date: datetime
    ):
        """Aggregierte Statistiken in einem Query."""
        stmt = (
            select(
                func.date_trunc('day', Call.created_at).label('day'),
                func.count(Call.id).label('total_calls'),
                func.count(Call.id).filter(
                    Call.status == 'completed'
                ).label('completed_calls'),
                func.avg(Call.duration).label('avg_duration'),
                func.sum(Call.duration).label('total_duration')
            )
            .where(
                Call.organization_id == organization_id,
                Call.created_at >= start_date,
                Call.created_at <= end_date
            )
            .group_by(func.date_trunc('day', Call.created_at))
            .order_by(col('day'))
        )
        
        result = await self.db.exec(stmt)
        return result.all()
```

### Frontend Performance

```typescript
// components/optimized/VirtualizedCallList.tsx
import React, { useMemo } from 'react';
import { VariableSizeList } from 'react-window';
import AutoSizer from 'react-virtualized-auto-sizer';

interface VirtualizedCallListProps {
  calls: Call[];
  onCallClick: (call: Call) => void;
}

export const VirtualizedCallList: React.FC<VirtualizedCallListProps> = React.memo(({
  calls,
  onCallClick,
}) => {
  // Memoize row heights
  const getItemSize = useMemo(() => {
    const sizes = new Map<number, number>();
    
    return (index: number) => {
      if (sizes.has(index)) {
        return sizes.get(index)!;
      }
      
      // Calculate based on content
      const call = calls[index];
      const baseHeight = 80;
      const extraHeight = call.transcript ? 20 : 0;
      const height = baseHeight + extraHeight;
      
      sizes.set(index, height);
      return height;
    };
  }, [calls]);
  
  // Memoize row renderer
  const Row = useMemo(() => {
    return React.memo(({ index, style }: any) => {
      const call = calls[index];
      
      return (
        <div style={style} onClick={() => onCallClick(call)}>
          <CallListItem call={call} />
        </div>
      );
    });
  }, [calls, onCallClick]);
  
  return (
    <AutoSizer>
      {({ height, width }) => (
        <VariableSizeList
          height={height}
          width={width}
          itemCount={calls.length}
          itemSize={getItemSize}
          overscanCount={5}
        >
          {Row}
        </VariableSizeList>
      )}
    </AutoSizer>
  );
});

// Lazy load heavy components
const HeavyComponent = React.lazy(() => import('./HeavyComponent'));

// Code splitting for routes
const routes = [
  {
    path: '/dashboard',
    component: React.lazy(() => import('./pages/Dashboard')),
  },
  {
    path: '/calls',
    component: React.lazy(() => import('./pages/Calls')),
  },
];
```

## Sicherheitspraktiken

### Input Validation

```python
# api/validators/security.py
import re
from typing import Optional
from pydantic import BaseModel, validator, Field

class PhoneNumberValidator(BaseModel):
    """Validator für Telefonnummern."""
    
    phone_number: str = Field(..., min_length=10, max_length=20)
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        # Entferne alle Nicht-Ziffern außer +
        cleaned = re.sub(r'[^\d+]', '', v)
        
        # Validiere Format
        if not re.match(r'^\+?[1-9]\d{7,14}$', cleaned):
            raise ValueError('Ungültiges Telefonnummer-Format')
        
        return cleaned


class SQLInjectionProtection(BaseModel):
    """Schutz vor SQL Injection."""
    
    search_term: Optional[str] = Field(None, max_length=100)
    
    @validator('search_term')
    def sanitize_search(cls, v):
        if v is None:
            return v
        
        # Blocke gefährliche Zeichen
        dangerous_chars = ['--', ';', '/*', '*/', 'xp_', 'sp_']
        for char in dangerous_chars:
            if char in v.lower():
                raise ValueError('Ungültige Zeichen im Suchbegriff')
        
        # Escape special characters
        v = v.replace("'", "''")
        v = v.replace('"', '""')
        
        return v


class XSSProtection:
    """Schutz vor XSS-Angriffen."""
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """Entfernt potentiell gefährliche HTML-Tags."""
        import bleach
        
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a']
        allowed_attributes = {'a': ['href', 'title']}
        
        return bleach.clean(
            text,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
```

### Authentication & Authorization

```python
# api/middleware/auth.py
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional, List

from api.config import settings
from api.models.user import User

security = HTTPBearer()


class JWTAuth:
    """JWT Authentication Handler."""
    
    @staticmethod
    def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Erstellt einen JWT Access Token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({"exp": expire, "type": "access"})
        
        return jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
    
    @staticmethod
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ) -> User:
        """Extrahiert und validiert den aktuellen Benutzer."""
        token = credentials.credentials
        
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            user_id: str = payload.get("sub")
            token_type: str = payload.get("type")
            
            if user_id is None or token_type != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials"
                )
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Load user from database
        user = db.get(User, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        return user


class RoleChecker:
    """Role-based Access Control."""
    
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, user: User = Depends(JWTAuth.get_current_user)):
        if not any(role in user.roles for role in self.allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return user


# Verwendung:
require_admin = RoleChecker(["admin"])
require_agent = RoleChecker(["agent", "admin"])
```

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: '3.11'
  NODE_VERSION: '18'
  POETRY_VERSION: '1.5.1'

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies
      run: |
        pip install ruff black mypy
        cd backend && pip install -r requirements-dev.txt
    
    - name: Run linters
      run: |
        cd backend
        ruff check .
        black --check .
        mypy api/

  test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run migrations
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost/test
      run: |
        cd backend
        alembic upgrade head
    
    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost/test
        REDIS_URL: redis://localhost:6379
      run: |
        cd backend
        pytest --cov=api --cov-report=xml --cov-report=html
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml

  test-frontend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: ${{ env.NODE_VERSION }}
        cache: 'npm'
        cache-dependency-path: backend/frontend/package-lock.json
    
    - name: Install dependencies
      run: |
        cd backend/frontend
        npm ci
    
    - name: Run linters
      run: |
        cd backend/frontend
        npm run lint
        npm run type-check
    
    - name: Run tests
      run: |
        cd backend/frontend
        npm run test:ci
    
    - name: Build
      run: |
        cd backend/frontend
        npm run build

  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy scan results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'
    
    - name: Run Bandit security linter
      run: |
        pip install bandit
        bandit -r backend/api/ -f json -o bandit-report.json
    
    - name: OWASP Dependency Check
      uses: dependency-check/Dependency-Check_Action@main
      with:
        project: 'VocalIQ'
        path: '.'
        format: 'HTML'

  build-and-push:
    needs: [lint, test-backend, test-frontend, security-scan]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Log in to GitHub Container Registry
      uses: docker/login-action@v2
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Build and push API image
      uses: docker/build-push-action@v4
      with:
        context: ./backend
        file: ./backend/Dockerfile.prod
        push: true
        tags: |
          ghcr.io/${{ github.repository }}/api:${{ github.sha }}
          ghcr.io/${{ github.repository }}/api:latest
        cache-from: type=gha
        cache-to: type=gha,mode=max
    
    - name: Build and push Frontend image
      uses: docker/build-push-action@v4
      with:
        context: ./backend/frontend
        file: ./backend/frontend/Dockerfile.prod
        push: true
        tags: |
          ghcr.io/${{ github.repository }}/frontend:${{ github.sha }}
          ghcr.io/${{ github.repository }}/frontend:latest
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    needs: build-and-push
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    
    steps:
    - name: Deploy to Kubernetes
      uses: azure/k8s-set-context@v3
      with:
        kubeconfig: ${{ secrets.KUBE_CONFIG }}
    
    - name: Update deployment
      run: |
        kubectl set image deployment/vocaliq-api \
          api=ghcr.io/${{ github.repository }}/api:${{ github.sha }} \
          -n vocaliq
        
        kubectl set image deployment/vocaliq-frontend \
          frontend=ghcr.io/${{ github.repository }}/frontend:${{ github.sha }} \
          -n vocaliq
        
        kubectl rollout status deployment/vocaliq-api -n vocaliq
        kubectl rollout status deployment/vocaliq-frontend -n vocaliq
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: detect-private-key

  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3.11
        args: [--line-length=88]

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.287
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        files: ^backend/api/

  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.48.0
    hooks:
      - id: eslint
        files: \.[jt]sx?$
        types: [file]
        additional_dependencies:
          - eslint@8.48.0
          - eslint-config-prettier@9.0.0
          - '@typescript-eslint/eslint-plugin@6.5.0'
          - '@typescript-eslint/parser@6.5.0'

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.0.3
    hooks:
      - id: prettier
        types_or: [javascript, jsx, ts, tsx, json, yaml]

  - repo: https://github.com/commitizen-tools/commitizen
    rev: 3.7.1
    hooks:
      - id: commitizen
        stages: [commit-msg]
```

---

*Dieses Developer Handbook wird kontinuierlich erweitert und aktualisiert. Für Fragen und Verbesserungsvorschläge erstellen Sie bitte ein Issue im Repository.*