# VocalIQ API Reference

## Übersicht

Die VocalIQ API ist eine RESTful API, die auf FastAPI basiert und moderne Standards wie OpenAPI 3.0, JSON Schema Validation und OAuth2 mit JWT unterstützt.

**Base URL**: `https://api.vocaliq.de/api/v1`  
**Documentation**: `https://api.vocaliq.de/docs`  
**OpenAPI Spec**: `https://api.vocaliq.de/openapi.json`

## Authentifizierung

VocalIQ verwendet JWT (JSON Web Tokens) für die Authentifizierung.

### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "organization_id": "org_123",
    "roles": ["admin", "user"]
  }
}
```

### Token Refresh
```http
POST /api/v1/auth/refresh
Authorization: Bearer {refresh_token}
```

### Logout
```http
POST /api/v1/auth/logout
Authorization: Bearer {access_token}
```

## Rate Limiting

API-Anfragen sind limitiert:
- **Standard**: 100 Requests/Minute
- **Audio**: 20 Requests/Minute
- **Calls**: 10 Requests/Minute

Headers in der Response:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## API Endpoints

### 1. Organizations API

#### Liste aller Organisationen
```http
GET /api/v1/organizations
Authorization: Bearer {token}
```

**Query Parameters:**
- `page` (int): Seitennummer (default: 1)
- `limit` (int): Einträge pro Seite (default: 20)
- `search` (string): Suchbegriff

**Response:**
```json
{
  "items": [
    {
      "id": "org_123",
      "name": "Demo Company GmbH",
      "contact_email": "admin@demo.de",
      "phone": "+49301234567",
      "settings": {
        "language": "de",
        "timezone": "Europe/Berlin"
      },
      "created_at": "2024-01-20T10:00:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "pages": 3
}
```

#### Organisation erstellen
```http
POST /api/v1/organizations
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Neue Firma GmbH",
  "contact_email": "kontakt@neuefirma.de",
  "phone": "+49301234567",
  "address": {
    "street": "Hauptstraße 1",
    "city": "Berlin",
    "zip": "10115",
    "country": "DE"
  }
}
```

### 2. Agents API

#### Agent-Konfiguration abrufen
```http
GET /api/v1/agents/{agent_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": "agent_123",
  "organization_id": "org_123",
  "name": "Empfangs-Agent",
  "description": "Hauptagent für eingehende Anrufe",
  "config": {
    "greeting": "Guten Tag, Sie sprechen mit {company_name}. Wie kann ich Ihnen helfen?",
    "language": "de",
    "voice": {
      "provider": "elevenlabs",
      "voice_id": "21m00Tcm4TlvDq8ikWAM",
      "settings": {
        "stability": 0.5,
        "similarity_boost": 0.75
      }
    },
    "personality": {
      "tone": "professional",
      "traits": ["helpful", "patient", "efficient"]
    },
    "knowledge_base_ids": ["kb_123", "kb_456"],
    "capabilities": {
      "appointment_booking": true,
      "order_taking": true,
      "faq_answering": true,
      "call_transfer": true
    }
  },
  "active": true,
  "created_at": "2024-01-20T10:00:00Z"
}
```

#### Agent erstellen/aktualisieren
```http
PUT /api/v1/agents/{agent_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Verkaufs-Agent",
  "config": {
    "greeting": "Hallo! Schön, dass Sie anrufen...",
    "personality": {
      "tone": "friendly",
      "traits": ["enthusiastic", "knowledgeable"]
    }
  }
}
```

### 3. Calls API

#### Outbound Call starten
```http
POST /api/v1/calls/outbound/start
Authorization: Bearer {token}
Content-Type: application/json

{
  "to_number": "+49301234567",
  "agent_id": "agent_123",
  "campaign_id": "campaign_456",
  "scheduled_time": "2024-01-20T15:00:00Z",
  "metadata": {
    "customer_id": "cust_789",
    "purpose": "appointment_reminder"
  }
}
```

**Response:**
```json
{
  "call_id": "call_987",
  "sid": "CA1234567890abcdef",
  "status": "initiated",
  "to_number": "+49301234567",
  "from_number": "+49309876543",
  "webhook_url": "https://api.vocaliq.de/webhooks/twilio/voice",
  "estimated_start": "2024-01-20T15:00:00Z"
}
```

#### Call Status abrufen
```http
GET /api/v1/calls/{call_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": "call_987",
  "sid": "CA1234567890abcdef",
  "direction": "outbound",
  "status": "completed",
  "duration": 180,
  "from_number": "+49309876543",
  "to_number": "+49301234567",
  "agent_id": "agent_123",
  "recording_url": "https://api.vocaliq.de/recordings/rec_123.mp3",
  "transcript": {
    "messages": [
      {
        "role": "agent",
        "content": "Guten Tag, hier ist VocalIQ. Ich rufe wegen Ihres Termins morgen an.",
        "timestamp": "2024-01-20T15:00:05Z"
      },
      {
        "role": "customer",
        "content": "Ah ja, der Termin um 14 Uhr, richtig?",
        "timestamp": "2024-01-20T15:00:12Z"
      }
    ]
  },
  "metadata": {
    "customer_id": "cust_789",
    "sentiment": "positive",
    "topics": ["appointment", "confirmation"]
  },
  "created_at": "2024-01-20T15:00:00Z",
  "ended_at": "2024-01-20T15:03:00Z"
}
```

#### Call-Liste mit Filtern
```http
GET /api/v1/calls
Authorization: Bearer {token}
```

**Query Parameters:**
- `status`: completed, in-progress, failed
- `direction`: inbound, outbound
- `agent_id`: Filter nach Agent
- `date_from`: Start-Datum (ISO 8601)
- `date_to`: End-Datum (ISO 8601)
- `phone_number`: Telefonnummer (partial match)

### 4. Audio API

#### Speech-to-Text (STT)
```http
POST /api/v1/audio/stt
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: audio.wav (binary)
language: de (optional)
```

**Response:**
```json
{
  "text": "Hallo, ich möchte einen Termin vereinbaren.",
  "language": "de",
  "confidence": 0.95,
  "duration": 3.2,
  "words": [
    {"word": "Hallo", "start": 0.0, "end": 0.5, "confidence": 0.98},
    {"word": "ich", "start": 0.6, "end": 0.8, "confidence": 0.96}
  ]
}
```

#### Text-to-Speech (TTS)
```http
POST /api/v1/audio/tts
Authorization: Bearer {token}
Content-Type: application/json

{
  "text": "Vielen Dank für Ihren Anruf. Ihr Termin wurde bestätigt.",
  "voice_id": "21m00Tcm4TlvDq8ikWAM",
  "output_format": "mp3",
  "settings": {
    "stability": 0.5,
    "similarity_boost": 0.75,
    "speed": 1.0
  }
}
```

**Response:**
```json
{
  "audio_url": "https://api.vocaliq.de/audio/tts_output_123.mp3",
  "duration": 4.5,
  "char_count": 58,
  "voice_id": "21m00Tcm4TlvDq8ikWAM"
}
```

### 5. Conversation API

#### Neue Konversation starten
```http
POST /api/v1/conversation/start
Authorization: Bearer {token}
Content-Type: application/json

{
  "agent_id": "agent_123",
  "channel": "phone",
  "metadata": {
    "phone_number": "+49301234567",
    "call_id": "call_987"
  }
}
```

**Response:**
```json
{
  "conversation_id": "conv_456",
  "agent_id": "agent_123",
  "status": "active",
  "context": {
    "customer_phone": "+49301234567",
    "previous_interactions": 3,
    "last_topic": "appointment"
  }
}
```

#### Nachricht an Konversation senden
```http
POST /api/v1/conversation/{conversation_id}/message
Authorization: Bearer {token}
Content-Type: application/json

{
  "message": "Ich möchte meinen Termin verschieben.",
  "audio_url": "https://api.vocaliq.de/audio/customer_123.wav"
}
```

**Response:**
```json
{
  "response": "Natürlich kann ich Ihnen dabei helfen. Wann würde es Ihnen denn besser passen?",
  "audio_url": "https://api.vocaliq.de/audio/response_456.mp3",
  "intent": "reschedule_appointment",
  "entities": {
    "action": "reschedule",
    "object": "appointment"
  },
  "suggested_actions": [
    {
      "type": "show_calendar",
      "data": {
        "available_slots": [
          "2024-01-22T10:00:00Z",
          "2024-01-22T14:00:00Z",
          "2024-01-23T09:00:00Z"
        ]
      }
    }
  ]
}
```

### 6. Calendar API

#### Verfügbare Termine abrufen
```http
GET /api/v1/calendar/availability
Authorization: Bearer {token}
```

**Query Parameters:**
- `start_date`: Startdatum (ISO 8601)
- `end_date`: Enddatum (ISO 8601)
- `duration`: Termindauer in Minuten
- `resource_id`: Ressource/Mitarbeiter ID

**Response:**
```json
{
  "available_slots": [
    {
      "start": "2024-01-22T10:00:00Z",
      "end": "2024-01-22T11:00:00Z",
      "resource_id": "resource_123"
    },
    {
      "start": "2024-01-22T14:00:00Z",
      "end": "2024-01-22T15:00:00Z",
      "resource_id": "resource_123"
    }
  ]
}
```

#### Termin buchen
```http
POST /api/v1/calendar/appointments
Authorization: Bearer {token}
Content-Type: application/json

{
  "customer_id": "cust_789",
  "resource_id": "resource_123",
  "start": "2024-01-22T10:00:00Z",
  "duration": 60,
  "type": "consultation",
  "notes": "Erstberatung zum Thema Versicherungen"
}
```

### 7. Knowledge Base API

#### Wissen hinzufügen
```http
POST /api/v1/knowledge
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Öffnungszeiten",
  "content": "Unsere Öffnungszeiten sind Montag bis Freitag von 9:00 bis 18:00 Uhr.",
  "category": "general_info",
  "tags": ["öffnungszeiten", "zeiten", "geöffnet"],
  "valid_from": "2024-01-01T00:00:00Z",
  "valid_until": "2024-12-31T23:59:59Z"
}
```

#### Wissen durchsuchen
```http
POST /api/v1/knowledge/search
Authorization: Bearer {token}
Content-Type: application/json

{
  "query": "Wann haben Sie geöffnet?",
  "limit": 5,
  "threshold": 0.7
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "kb_123",
      "title": "Öffnungszeiten",
      "content": "Unsere Öffnungszeiten sind...",
      "score": 0.95,
      "category": "general_info"
    }
  ]
}
```

### 8. CRM API

#### Kunde anlegen/aktualisieren
```http
PUT /api/v1/crm/customers/{customer_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Max Mustermann",
  "phone": "+49301234567",
  "email": "max@example.com",
  "tags": ["vip", "longtime_customer"],
  "custom_fields": {
    "birthday": "1980-05-15",
    "preferred_contact": "phone"
  }
}
```

#### Interaktion protokollieren
```http
POST /api/v1/crm/interactions
Authorization: Bearer {token}
Content-Type: application/json

{
  "customer_id": "cust_789",
  "type": "phone_call",
  "channel": "inbound",
  "duration": 180,
  "outcome": "appointment_scheduled",
  "notes": "Kunde war sehr zufrieden",
  "metadata": {
    "call_id": "call_987",
    "agent_id": "agent_123"
  }
}
```

### 9. Monitoring API

#### System-Metriken
```http
GET /api/v1/monitoring/metrics
Authorization: Bearer {token}
```

**Response:**
```json
{
  "system": {
    "cpu_usage": 45.2,
    "memory_usage": 62.8,
    "disk_usage": 38.5,
    "active_calls": 23,
    "queued_calls": 5
  },
  "performance": {
    "avg_response_time": 0.182,
    "stt_latency": 0.423,
    "tts_latency": 0.298,
    "ai_response_time": 0.876
  },
  "business": {
    "calls_today": 487,
    "successful_rate": 0.94,
    "avg_call_duration": 195,
    "appointments_booked": 73
  }
}
```

#### Analytics Dashboard Daten
```http
GET /api/v1/monitoring/analytics
Authorization: Bearer {token}
```

**Query Parameters:**
- `period`: today, week, month, custom
- `start_date`: Bei custom period
- `end_date`: Bei custom period
- `group_by`: hour, day, week

### 10. GDPR API

#### Daten exportieren
```http
POST /api/v1/gdpr/export
Authorization: Bearer {token}
Content-Type: application/json

{
  "customer_id": "cust_789",
  "include": ["calls", "transcripts", "interactions", "appointments"],
  "format": "json"
}
```

**Response:**
```json
{
  "export_id": "export_123",
  "status": "processing",
  "estimated_completion": "2024-01-20T11:00:00Z",
  "download_url": null
}
```

#### Daten löschen
```http
POST /api/v1/gdpr/delete
Authorization: Bearer {token}
Content-Type: application/json

{
  "customer_id": "cust_789",
  "delete_options": {
    "anonymize": true,
    "keep_statistics": true
  }
}
```

### 11. Webhooks API

#### Webhook registrieren
```http
POST /api/v1/webhooks
Authorization: Bearer {token}
Content-Type: application/json

{
  "url": "https://your-domain.com/webhooks/vocaliq",
  "events": ["call.completed", "appointment.created", "agent.error"],
  "secret": "your-webhook-secret",
  "active": true
}
```

#### Webhook Events

**call.completed**
```json
{
  "event": "call.completed",
  "timestamp": "2024-01-20T15:03:00Z",
  "data": {
    "call_id": "call_987",
    "duration": 180,
    "status": "completed",
    "recording_url": "https://api.vocaliq.de/recordings/rec_123.mp3"
  }
}
```

**appointment.created**
```json
{
  "event": "appointment.created",
  "timestamp": "2024-01-20T15:02:45Z",
  "data": {
    "appointment_id": "apt_456",
    "customer_id": "cust_789",
    "start": "2024-01-22T10:00:00Z",
    "type": "consultation"
  }
}
```

### 12. WebSocket API

#### Audio Streaming Endpoint
```
WSS://api.vocaliq.de/ws/media/{call_sid}
```

**Connection Flow:**
```javascript
// Client-Beispiel
const ws = new WebSocket('wss://api.vocaliq.de/ws/media/CA123');

ws.onopen = () => {
  // Send authentication
  ws.send(JSON.stringify({
    event: 'auth',
    token: 'your-jwt-token'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.event) {
    case 'connected':
      console.log('Connected to call:', data.callSid);
      break;
      
    case 'audio':
      // Base64 encoded audio chunk
      processAudioChunk(data.media.payload);
      break;
      
    case 'transcript':
      console.log('Transcript:', data.text);
      break;
      
    case 'error':
      console.error('Error:', data.message);
      break;
  }
};

// Send audio to server
ws.send(JSON.stringify({
  event: 'media',
  media: {
    payload: base64AudioData,
    timestamp: Date.now()
  }
}));
```

## Error Handling

### Standard Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "phone_number",
        "message": "Invalid phone number format"
      }
    ]
  },
  "request_id": "req_123456",
  "timestamp": "2024-01-20T10:00:00Z"
}
```

### Error Codes
- `AUTHENTICATION_ERROR`: Authentifizierung fehlgeschlagen
- `AUTHORIZATION_ERROR`: Keine Berechtigung
- `VALIDATION_ERROR`: Validierung fehlgeschlagen
- `NOT_FOUND`: Ressource nicht gefunden
- `RATE_LIMIT_ERROR`: Rate Limit überschritten
- `INTERNAL_ERROR`: Interner Serverfehler
- `SERVICE_UNAVAILABLE`: Service temporär nicht verfügbar

## SDK Beispiele

### Python
```python
from vocaliq import VocalIQClient

client = VocalIQClient(
    api_key="your-api-key",
    base_url="https://api.vocaliq.de"
)

# Outbound Call starten
call = client.calls.create_outbound(
    to_number="+49301234567",
    agent_id="agent_123"
)

# Auf Completion warten
call.wait_for_completion()

# Transcript abrufen
transcript = call.get_transcript()
```

### JavaScript/TypeScript
```typescript
import { VocalIQ } from '@vocaliq/sdk';

const client = new VocalIQ({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.vocaliq.de'
});

// Agent konfigurieren
const agent = await client.agents.update('agent_123', {
  config: {
    greeting: 'Neuer Begrüßungstext'
  }
});

// WebSocket für Live-Transcription
const stream = await client.calls.streamTranscript('call_987');
stream.on('transcript', (text) => {
  console.log('Live:', text);
});
```

## Best Practices

1. **Pagination**: Nutzen Sie immer Pagination für Listen-Endpoints
2. **Caching**: Implementieren Sie Client-seitiges Caching für statische Daten
3. **Retry Logic**: Implementieren Sie Exponential Backoff für fehlgeschlagene Requests
4. **Webhook Validation**: Verifizieren Sie immer Webhook-Signaturen
5. **Token Management**: Refreshen Sie Access Tokens rechtzeitig
6. **Error Handling**: Behandeln Sie alle möglichen Error Codes
7. **Rate Limiting**: Respektieren Sie Rate Limits und implementieren Sie Throttling

## Changelog

### v1.2.0 (2024-01-20)
- WebSocket Audio Streaming API hinzugefügt
- Verbessertes Error Handling
- Neue CRM Endpoints

### v1.1.0 (2023-12-01)
- Calendar Integration
- GDPR Compliance Endpoints
- Performance Optimierungen

### v1.0.0 (2023-10-01)
- Initial Release

---

*Für interaktive API-Dokumentation besuchen Sie: https://api.vocaliq.de/docs*