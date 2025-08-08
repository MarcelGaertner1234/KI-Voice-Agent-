# VocalIQ Configuration Reference

## Übersicht

Diese Referenz dokumentiert alle Konfigurationsoptionen für VocalIQ. Die Konfiguration erfolgt primär über Umgebungsvariablen, die in der `.env` Datei definiert werden.

## Umgebungsvariablen

### Core Settings

```bash
# Umgebung: development, staging, production
ENVIRONMENT=development

# Debug-Modus (nur in development)
DEBUG=true

# Log-Level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Geheimer Schlüssel für Verschlüsselung (min. 32 Zeichen)
SECRET_KEY=your-very-secret-key-change-this-in-production

# Zeitzone
TIMEZONE=Europe/Berlin

# Sprache (Standard)
DEFAULT_LANGUAGE=de
```

### API Configuration

```bash
# API Base URL (öffentlich erreichbar)
API_BASE_URL=https://api.vocaliq.de

# Frontend URL
FRONTEND_URL=https://app.vocaliq.de

# Erlaubte Origins für CORS
ALLOWED_ORIGINS=https://app.vocaliq.de,https://admin.vocaliq.de

# API Version
API_VERSION=v1

# Request Timeout (Sekunden)
REQUEST_TIMEOUT=30

# Max Request Size (MB)
MAX_REQUEST_SIZE=50

# Pagination
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

### Database Configuration

```bash
# Datenbank URL
# SQLite (Development)
DATABASE_URL=sqlite:///./vocaliq.db

# PostgreSQL (Production)
DATABASE_URL=postgresql://user:password@localhost:5432/vocaliq

# Connection Pool
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=0
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600

# Query Settings
DATABASE_ECHO=false
DATABASE_ECHO_POOL=false
DATABASE_STATEMENT_TIMEOUT=30000  # milliseconds

# Backup Settings
DATABASE_BACKUP_ENABLED=true
DATABASE_BACKUP_SCHEDULE="0 2 * * *"  # Cron format
DATABASE_BACKUP_RETENTION_DAYS=30
```

### Redis Configuration

```bash
# Redis URL
REDIS_URL=redis://localhost:6379/0

# Redis Password (optional)
REDIS_PASSWORD=

# Redis SSL
REDIS_SSL=false

# Connection Pool
REDIS_MAX_CONNECTIONS=50
REDIS_CONNECTION_TIMEOUT=20

# Cache Settings
CACHE_DEFAULT_TIMEOUT=300  # Sekunden
CACHE_KEY_PREFIX=vocaliq

# Session Settings
SESSION_LIFETIME=86400  # 24 Stunden
SESSION_COOKIE_SECURE=true  # HTTPS only
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=lax
```

### Authentication & Security

```bash
# JWT Settings
JWT_SECRET_KEY=your-jwt-secret-key-change-this
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Credentials (Initial Setup)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure-admin-password
ADMIN_EMAIL=admin@vocaliq.de

# Password Policy
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_DIGITS=true
PASSWORD_REQUIRE_SPECIAL=true

# Security Headers
SECURITY_HEADERS_ENABLED=true
SECURITY_HSTS_SECONDS=31536000
SECURITY_CONTENT_TYPE_NOSNIFF=true
SECURITY_BROWSER_XSS_FILTER=true
SECURITY_CONTENT_SECURITY_POLICY="default-src 'self'"

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_GENERAL=100/minute
RATE_LIMIT_AUTH=5/minute
RATE_LIMIT_AUDIO=20/minute
RATE_LIMIT_CALLS=10/minute
RATE_LIMIT_STORAGE_URL=redis://localhost:6379/1
```

### Twilio Configuration

```bash
# Twilio Account
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-twilio-auth-token

# Twilio Phone Numbers
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_PHONE_NUMBER_SID=PNxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Twilio Settings
TWILIO_VOICE_URL=https://api.vocaliq.de/webhooks/twilio/voice
TWILIO_STATUS_CALLBACK_URL=https://api.vocaliq.de/webhooks/twilio/status
TWILIO_VOICE_METHOD=POST
TWILIO_VOICE_FALLBACK_URL=https://api.vocaliq.de/webhooks/twilio/fallback
TWILIO_VOICE_FALLBACK_METHOD=POST

# Twilio Media Streams
TWILIO_STREAM_URL=wss://api.vocaliq.de/ws/media
TWILIO_STREAM_TRACK=inbound
TWILIO_STREAM_STATUS_CALLBACK=https://api.vocaliq.de/webhooks/twilio/stream-status

# Twilio Recording
TWILIO_RECORDING_ENABLED=true
TWILIO_RECORDING_CHANNELS=dual
TWILIO_RECORDING_STATUS_CALLBACK=https://api.vocaliq.de/webhooks/twilio/recording
TWILIO_RECORDING_STATUS_CALLBACK_METHOD=POST
TWILIO_RECORDING_TRIM=do-not-trim

# Twilio Webhook Security
TWILIO_WEBHOOK_VALIDATE=true

# Twilio Limits
TWILIO_MAX_CALL_DURATION=3600  # Sekunden
TWILIO_MAX_RECORDING_DURATION=3600
TWILIO_CONCURRENT_CALLS_LIMIT=100
```

### OpenAI Configuration

```bash
# OpenAI API
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_ORGANIZATION=org-xxxxxxxxxxxxxxxxxxxxxxxx

# Model Settings
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000
OPENAI_TOP_P=1.0
OPENAI_FREQUENCY_PENALTY=0.0
OPENAI_PRESENCE_PENALTY=0.0

# Whisper STT
WHISPER_MODEL=whisper-1
WHISPER_LANGUAGE=de
WHISPER_PROMPT="Dies ist ein Telefongespräch auf Deutsch."
WHISPER_RESPONSE_FORMAT=json
WHISPER_TEMPERATURE=0

# Rate Limits
OPENAI_RATE_LIMIT_REQUESTS=3000/minute
OPENAI_RATE_LIMIT_TOKENS=250000/minute

# Retry Settings
OPENAI_MAX_RETRIES=3
OPENAI_RETRY_DELAY=1
OPENAI_TIMEOUT=30
```

### ElevenLabs Configuration

```bash
# ElevenLabs API
ELEVENLABS_API_KEY=your-elevenlabs-api-key

# Voice Settings
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
ELEVENLABS_VOICE_NAME="Rachel"
ELEVENLABS_MODEL=eleven_multilingual_v2

# Voice Parameters
ELEVENLABS_VOICE_SETTINGS_STABILITY=0.5
ELEVENLABS_VOICE_SETTINGS_SIMILARITY_BOOST=0.75
ELEVENLABS_VOICE_SETTINGS_STYLE=0.0
ELEVENLABS_VOICE_SETTINGS_USE_SPEAKER_BOOST=true

# Audio Settings
ELEVENLABS_OUTPUT_FORMAT=mp3_44100_128
ELEVENLABS_OPTIMIZE_STREAMING_LATENCY=0

# Limits
ELEVENLABS_MAX_TEXT_LENGTH=5000
ELEVENLABS_RATE_LIMIT=100/minute
```

### Weaviate Configuration

```bash
# Weaviate Connection
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=
WEAVIATE_ADDITIONAL_HEADERS=

# Schema Settings
WEAVIATE_SCHEMA_NAME=VocalIQKnowledge
WEAVIATE_DEFAULT_CLASS=Knowledge
WEAVIATE_DEFAULT_VECTORIZER=text2vec-openai

# Search Settings
WEAVIATE_SEARCH_LIMIT=10
WEAVIATE_SEARCH_CERTAINTY=0.7
WEAVIATE_SEARCH_DISTANCE=0.3

# Batch Import
WEAVIATE_BATCH_SIZE=100
WEAVIATE_BATCH_DYNAMIC=true
WEAVIATE_BATCH_TIMEOUT=30
```

### Google Calendar Configuration

```bash
# Google Calendar API
GOOGLE_CALENDAR_ENABLED=true
GOOGLE_CALENDAR_CREDENTIALS_FILE=./credentials/google-calendar.json
GOOGLE_CALENDAR_TOKEN_FILE=./credentials/google-calendar-token.json

# Calendar Settings
GOOGLE_CALENDAR_ID=primary
GOOGLE_CALENDAR_TIMEZONE=Europe/Berlin
GOOGLE_CALENDAR_DEFAULT_EVENT_LENGTH=60  # Minuten

# Availability Settings
GOOGLE_CALENDAR_WORKING_HOURS_START=09:00
GOOGLE_CALENDAR_WORKING_HOURS_END=18:00
GOOGLE_CALENDAR_WORKING_DAYS=1,2,3,4,5  # Mo-Fr
GOOGLE_CALENDAR_SLOT_DURATION=30  # Minuten
GOOGLE_CALENDAR_BUFFER_TIME=15  # Minuten zwischen Terminen

# Sync Settings
GOOGLE_CALENDAR_SYNC_ENABLED=true
GOOGLE_CALENDAR_SYNC_INTERVAL=300  # Sekunden
GOOGLE_CALENDAR_SYNC_DAYS_AHEAD=30
```

### Email Configuration

```bash
# SMTP Settings
SMTP_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true
SMTP_USE_SSL=false
SMTP_TIMEOUT=30

# Email Settings
SMTP_FROM_EMAIL=noreply@vocaliq.de
SMTP_FROM_NAME=VocalIQ
SMTP_REPLY_TO=support@vocaliq.de

# Email Templates
EMAIL_TEMPLATE_PATH=./templates/email
EMAIL_TEMPLATE_LANGUAGE=de

# Email Rate Limiting
EMAIL_RATE_LIMIT=50/hour
EMAIL_BATCH_SIZE=50
```

### Storage Configuration

```bash
# Storage Type: local, s3, gcs, azure
STORAGE_TYPE=local

# Local Storage
STORAGE_LOCAL_PATH=./storage
STORAGE_LOCAL_MAX_SIZE=10GB

# S3 Storage
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_BUCKET=vocaliq-storage
AWS_S3_REGION=eu-central-1
AWS_S3_ENDPOINT_URL=
AWS_S3_USE_SSL=true
AWS_S3_VERIFY=true

# File Upload Settings
UPLOAD_MAX_SIZE=50MB
UPLOAD_ALLOWED_EXTENSIONS=wav,mp3,m4a,ogg,webm,pdf,doc,docx
UPLOAD_CHUNK_SIZE=5MB

# Audio File Settings
AUDIO_FORMAT=wav
AUDIO_SAMPLE_RATE=16000
AUDIO_CHANNELS=1
AUDIO_BITS_PER_SAMPLE=16
```

### Monitoring Configuration

```bash
# Prometheus
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
PROMETHEUS_METRICS_PATH=/metrics
PROMETHEUS_SCRAPE_INTERVAL=15s

# Grafana
GRAFANA_ENABLED=true
GRAFANA_PORT=3000
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin-password

# Loki (Logging)
LOKI_ENABLED=true
LOKI_URL=http://localhost:3100
LOKI_TENANT_ID=vocaliq

# Jaeger (Tracing)
JAEGER_ENABLED=true
JAEGER_AGENT_HOST=localhost
JAEGER_AGENT_PORT=6831
JAEGER_SAMPLER_TYPE=const
JAEGER_SAMPLER_PARAM=1

# Sentry (Error Tracking)
SENTRY_ENABLED=false
SENTRY_DSN=
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1

# Health Check
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=10
```

### Feature Flags

```bash
# Feature Toggles
FEATURE_OUTBOUND_CALLS=true
FEATURE_INBOUND_CALLS=true
FEATURE_CALL_RECORDING=true
FEATURE_CALL_TRANSCRIPTION=true
FEATURE_REALTIME_TRANSCRIPTION=true
FEATURE_CALENDAR_INTEGRATION=true
FEATURE_CRM_INTEGRATION=true
FEATURE_EMAIL_NOTIFICATIONS=true
FEATURE_SMS_NOTIFICATIONS=false
FEATURE_MULTI_TENANT=true
FEATURE_ANALYTICS=true
FEATURE_EXPORT_DATA=true
FEATURE_IMPORT_DATA=true
FEATURE_WEBHOOKS=true
FEATURE_API_KEYS=true

# Experimental Features
FEATURE_VOICE_CLONING=false
FEATURE_VIDEO_CALLS=false
FEATURE_AI_COACHING=false
FEATURE_SENTIMENT_ANALYSIS=true
FEATURE_AUTO_SCHEDULING=true
```

### Integration Configuration

```bash
# CRM Integrations
CRM_SALESFORCE_ENABLED=false
CRM_SALESFORCE_CLIENT_ID=
CRM_SALESFORCE_CLIENT_SECRET=
CRM_SALESFORCE_DOMAIN=

CRM_HUBSPOT_ENABLED=false
CRM_HUBSPOT_API_KEY=
CRM_HUBSPOT_PORTAL_ID=

CRM_PIPEDRIVE_ENABLED=false
CRM_PIPEDRIVE_API_TOKEN=
CRM_PIPEDRIVE_DOMAIN=

# Calendar Integrations
CALENDAR_OUTLOOK_ENABLED=false
CALENDAR_OUTLOOK_CLIENT_ID=
CALENDAR_OUTLOOK_CLIENT_SECRET=
CALENDAR_OUTLOOK_TENANT_ID=

# Analytics Integrations
ANALYTICS_GOOGLE_ENABLED=false
ANALYTICS_GOOGLE_TRACKING_ID=

ANALYTICS_MIXPANEL_ENABLED=false
ANALYTICS_MIXPANEL_TOKEN=

# Payment Integrations
PAYMENT_STRIPE_ENABLED=false
PAYMENT_STRIPE_PUBLIC_KEY=
PAYMENT_STRIPE_SECRET_KEY=
PAYMENT_STRIPE_WEBHOOK_SECRET=
```

### Performance Tuning

```bash
# Worker Configuration
WORKER_PROCESSES=4
WORKER_THREADS=2
WORKER_CONNECTIONS=1000
WORKER_KEEPALIVE=75

# Async Configuration
ASYNC_WORKERS=10
ASYNC_QUEUE_SIZE=1000
ASYNC_TIMEOUT=300

# Cache Configuration
CACHE_AGENT_CONFIG_TTL=600
CACHE_USER_SESSION_TTL=3600
CACHE_KNOWLEDGE_SEARCH_TTL=300
CACHE_STATISTICS_TTL=60

# Database Optimization
DB_STATEMENT_CACHE_SIZE=1000
DB_QUERY_CACHE_SIZE=1000
DB_CONNECTION_RECYCLE=3600

# API Optimization
API_RESPONSE_COMPRESSION=true
API_RESPONSE_CACHE_CONTROL="max-age=0, no-cache, no-store, must-revalidate"
API_STATIC_CACHE_CONTROL="max-age=31536000, immutable"
```

## Service-Konfigurationen

### Agent-Konfiguration

```json
{
  "agent_config": {
    "name": "Standard Agent",
    "description": "Haupt-Empfangsagent",
    "personality": {
      "tone": "professional",
      "traits": ["helpful", "patient", "efficient"],
      "communication_style": "formal"
    },
    "greeting": {
      "default": "Guten Tag, Sie sprechen mit {company_name}. Mein Name ist {agent_name}. Wie kann ich Ihnen helfen?",
      "morning": "Guten Morgen, Sie sprechen mit {company_name}. Mein Name ist {agent_name}. Wie kann ich Ihnen helfen?",
      "evening": "Guten Abend, Sie sprechen mit {company_name}. Mein Name ist {agent_name}. Wie kann ich Ihnen helfen?"
    },
    "capabilities": {
      "appointment_booking": true,
      "order_taking": true,
      "information_provision": true,
      "complaint_handling": true,
      "call_transfer": true,
      "callback_scheduling": true
    },
    "language": {
      "primary": "de",
      "supported": ["de", "en", "fr", "es"],
      "auto_detect": true
    },
    "voice": {
      "provider": "elevenlabs",
      "voice_id": "21m00Tcm4TlvDq8ikWAM",
      "speed": 1.0,
      "pitch": 1.0,
      "emotion": "neutral"
    },
    "behavior": {
      "max_retry_attempts": 3,
      "clarification_phrases": [
        "Entschuldigung, ich habe das nicht ganz verstanden. Könnten Sie das bitte wiederholen?",
        "Darf ich Sie bitten, das noch einmal zu erklären?",
        "Ich möchte sichergehen, dass ich Sie richtig verstehe. Meinen Sie..."
      ],
      "hold_music": true,
      "hold_message_interval": 30,
      "max_hold_time": 300
    },
    "knowledge_base": {
      "sources": ["main_kb", "faq_kb", "product_kb"],
      "confidence_threshold": 0.7,
      "fallback_to_human": true,
      "cache_responses": true
    },
    "escalation": {
      "triggers": [
        "sprechen mit mensch",
        "beschwerde",
        "vorgesetzter",
        "nicht zufrieden"
      ],
      "human_available_hours": "09:00-18:00",
      "queue_message": "Ich verbinde Sie gerne mit einem Mitarbeiter. Einen Moment bitte.",
      "no_agent_message": "Aktuell sind alle Mitarbeiter im Gespräch. Kann ich Ihnen anderweitig helfen?"
    }
  }
}
```

### Multi-Tenant-Konfiguration

```json
{
  "organization_settings": {
    "id": "org_123",
    "name": "Demo Company GmbH",
    "tier": "professional",
    "limits": {
      "monthly_minutes": 10000,
      "concurrent_calls": 10,
      "agents": 5,
      "users": 20,
      "storage_gb": 100,
      "api_requests_per_minute": 100
    },
    "features": {
      "outbound_calls": true,
      "call_recording": true,
      "custom_voices": false,
      "api_access": true,
      "white_label": false,
      "dedicated_support": true
    },
    "billing": {
      "plan": "professional",
      "billing_cycle": "monthly",
      "payment_method": "invoice",
      "overage_charges": {
        "per_minute": 0.02,
        "per_gb": 0.10
      }
    },
    "branding": {
      "company_name": "Demo Company",
      "logo_url": "https://example.com/logo.png",
      "primary_color": "#1976d2",
      "email_signature": "Mit freundlichen Grüßen,\nIhr Demo Company Team"
    },
    "compliance": {
      "data_retention_days": 90,
      "gdpr_compliant": true,
      "recording_announcement": "Dieses Gespräch wird zu Qualitätszwecken aufgezeichnet.",
      "consent_required": true
    },
    "integrations": {
      "crm": {
        "type": "salesforce",
        "enabled": true,
        "sync_interval": 300
      },
      "calendar": {
        "type": "google",
        "enabled": true,
        "calendars": ["primary", "support"]
      }
    }
  }
}
```

### Webhook-Konfiguration

```json
{
  "webhook_config": {
    "endpoints": [
      {
        "url": "https://example.com/webhooks/vocaliq",
        "events": ["call.started", "call.completed", "call.failed"],
        "headers": {
          "Authorization": "Bearer webhook-token",
          "X-Custom-Header": "value"
        },
        "retry": {
          "max_attempts": 3,
          "backoff_multiplier": 2,
          "max_delay": 60
        },
        "timeout": 30,
        "verify_ssl": true
      }
    ],
    "event_types": {
      "call.started": {
        "description": "Anruf wurde gestartet",
        "payload": {
          "call_id": "string",
          "direction": "inbound|outbound",
          "from_number": "string",
          "to_number": "string",
          "agent_id": "string",
          "timestamp": "ISO8601"
        }
      },
      "call.completed": {
        "description": "Anruf wurde beendet",
        "payload": {
          "call_id": "string",
          "duration": "integer",
          "recording_url": "string",
          "transcript_url": "string",
          "summary": "string",
          "timestamp": "ISO8601"
        }
      },
      "appointment.created": {
        "description": "Termin wurde erstellt",
        "payload": {
          "appointment_id": "string",
          "customer_id": "string",
          "datetime": "ISO8601",
          "duration": "integer",
          "type": "string"
        }
      }
    },
    "security": {
      "signature_header": "X-VocalIQ-Signature",
      "signature_algorithm": "HMAC-SHA256",
      "timestamp_tolerance": 300,
      "ip_whitelist": []
    }
  }
}
```

### Audio-Processing-Konfiguration

```json
{
  "audio_processing": {
    "input": {
      "format": "pcm",
      "encoding": "LINEAR16",
      "sample_rate": 16000,
      "channels": 1,
      "chunk_size": 4096,
      "silence_threshold": -40,
      "silence_duration": 1.5
    },
    "output": {
      "format": "mp3",
      "bitrate": 128,
      "sample_rate": 44100,
      "channels": 1
    },
    "vad": {
      "enabled": true,
      "mode": 3,
      "frame_duration": 30,
      "min_speech_duration": 0.5,
      "max_silence_duration": 2.0,
      "speech_pad_ms": 300
    },
    "noise_reduction": {
      "enabled": true,
      "level": "medium",
      "algorithm": "spectral_subtraction"
    },
    "echo_cancellation": {
      "enabled": true,
      "mode": "aggressive",
      "filter_length": 200
    },
    "gain_control": {
      "enabled": true,
      "target_level": -3,
      "compression_gain": 9,
      "limiter": true
    }
  }
}
```

## Deployment-Profile

### Development Profile

```bash
# .env.development
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///./vocaliq_dev.db
REDIS_URL=redis://localhost:6379/0
RATE_LIMIT_ENABLED=false
TWILIO_WEBHOOK_VALIDATE=false
SECURE_COOKIES=false
CORS_ALLOW_CREDENTIALS=true
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Staging Profile

```bash
# .env.staging
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL=postgresql://vocaliq:password@postgres-staging:5432/vocaliq_staging
REDIS_URL=redis://redis-staging:6379/0
RATE_LIMIT_ENABLED=true
TWILIO_WEBHOOK_VALIDATE=true
SECURE_COOKIES=true
CORS_ALLOW_CREDENTIALS=true
ALLOWED_ORIGINS=https://staging.vocaliq.de
SENTRY_ENABLED=true
```

### Production Profile

```bash
# .env.production
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
DATABASE_URL=postgresql://vocaliq:${DB_PASSWORD}@postgres-prod:5432/vocaliq
REDIS_URL=redis://:${REDIS_PASSWORD}@redis-prod:6379/0
RATE_LIMIT_ENABLED=true
TWILIO_WEBHOOK_VALIDATE=true
SECURE_COOKIES=true
CORS_ALLOW_CREDENTIALS=false
ALLOWED_ORIGINS=https://app.vocaliq.de
SENTRY_ENABLED=true
PROMETHEUS_ENABLED=true
DATABASE_POOL_SIZE=50
WORKER_PROCESSES=8
```

## Konfiguration validieren

### Validation Script

```python
#!/usr/bin/env python3
# scripts/validate_config.py

import os
import sys
from typing import Dict, List, Tuple

REQUIRED_VARS = [
    "SECRET_KEY",
    "DATABASE_URL",
    "REDIS_URL",
    "JWT_SECRET_KEY",
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
    "OPENAI_API_KEY",
    "ELEVENLABS_API_KEY"
]

PRODUCTION_REQUIRED = [
    "SENTRY_DSN",
    "SMTP_HOST",
    "SMTP_USERNAME",
    "SMTP_PASSWORD"
]

def validate_config() -> Tuple[bool, List[str]]:
    """Validiert die Konfiguration."""
    errors = []
    
    # Check required variables
    for var in REQUIRED_VARS:
        if not os.getenv(var):
            errors.append(f"Missing required variable: {var}")
    
    # Check production requirements
    if os.getenv("ENVIRONMENT") == "production":
        for var in PRODUCTION_REQUIRED:
            if not os.getenv(var):
                errors.append(f"Missing production variable: {var}")
        
        # Security checks
        if os.getenv("DEBUG", "false").lower() == "true":
            errors.append("DEBUG must be false in production")
        
        if os.getenv("SECRET_KEY", "").startswith("your-"):
            errors.append("SECRET_KEY must be changed from default")
    
    # Validate formats
    db_url = os.getenv("DATABASE_URL", "")
    if "sqlite" in db_url and os.getenv("ENVIRONMENT") == "production":
        errors.append("SQLite not recommended for production")
    
    return len(errors) == 0, errors

if __name__ == "__main__":
    valid, errors = validate_config()
    
    if not valid:
        print("Configuration errors found:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("Configuration is valid!")
```

### Health Check Script

```bash
#!/bin/bash
# scripts/health_check.sh

echo "VocalIQ Configuration Health Check"
echo "================================="

# Check environment
echo -n "Environment: "
echo $ENVIRONMENT

# Check services
echo -n "Database: "
if pg_isready -h ${DATABASE_HOST:-localhost} > /dev/null 2>&1; then
    echo "✓ Connected"
else
    echo "✗ Not reachable"
fi

echo -n "Redis: "
if redis-cli -h ${REDIS_HOST:-localhost} ping > /dev/null 2>&1; then
    echo "✓ Connected"
else
    echo "✗ Not reachable"
fi

echo -n "Twilio: "
if curl -s -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN" \
    "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID.json" \
    > /dev/null; then
    echo "✓ Authenticated"
else
    echo "✗ Authentication failed"
fi

echo -n "OpenAI: "
if curl -s -H "Authorization: Bearer $OPENAI_API_KEY" \
    "https://api.openai.com/v1/models" > /dev/null; then
    echo "✓ API key valid"
else
    echo "✗ API key invalid"
fi
```

## Best Practices

### 1. Umgebungsvariablen-Management

- Nutzen Sie unterschiedliche `.env` Dateien für verschiedene Umgebungen
- Versionieren Sie niemals `.env` Dateien mit Secrets
- Verwenden Sie `.env.example` als Template
- Nutzen Sie einen Secret Manager in Production (Vault, AWS Secrets Manager)

### 2. Sicherheit

- Ändern Sie alle Default-Passwörter
- Nutzen Sie starke, zufällige Secrets
- Aktivieren Sie HTTPS in Production
- Implementieren Sie IP-Whitelisting wo möglich
- Rotieren Sie API-Keys regelmäßig

### 3. Performance

- Tunen Sie Database Connection Pools
- Konfigurieren Sie Redis-Cache-Strategien
- Setzen Sie angemessene Rate Limits
- Optimieren Sie Worker-Prozesse basierend auf CPU-Cores

### 4. Monitoring

- Aktivieren Sie alle Monitoring-Tools in Production
- Setzen Sie sinnvolle Alert-Schwellwerte
- Konfigurieren Sie Log-Rotation
- Implementieren Sie Health Checks

### 5. Backup & Recovery

- Automatisieren Sie Datenbank-Backups
- Testen Sie Recovery-Prozeduren regelmäßig
- Dokumentieren Sie Disaster Recovery Pläne
- Verschlüsseln Sie Backup-Daten

---

*Diese Konfigurations-Referenz wird bei Änderungen am System aktualisiert. Für spezifische Fragen kontaktieren Sie das DevOps-Team.*