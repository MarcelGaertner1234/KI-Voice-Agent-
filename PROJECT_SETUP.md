# VocalIQ - Vollständige Installationsanleitung

## Inhaltsverzeichnis

1. [Systemvoraussetzungen](#systemvoraussetzungen)
2. [Schnellstart mit Docker](#schnellstart-mit-docker)
3. [Manuelle Installation](#manuelle-installation)
4. [Umgebungsvariablen](#umgebungsvariablen)
5. [Datenbank-Setup](#datenbank-setup)
6. [Externe Services einrichten](#externe-services-einrichten)
7. [SSL/TLS und Nginx](#ssltls-und-nginx)
8. [Erste Schritte](#erste-schritte)
9. [Troubleshooting](#troubleshooting)

## Systemvoraussetzungen

### Minimum Hardware
- **CPU**: 4 Cores (8 Cores empfohlen)
- **RAM**: 8 GB (16 GB empfohlen)
- **Storage**: 50 GB SSD
- **Netzwerk**: Stabile Internetverbindung mit statischer IP

### Software-Anforderungen
- **OS**: Ubuntu 20.04/22.04 LTS, Debian 11, oder macOS 12+
- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Node.js**: Version 18+ (für Frontend-Entwicklung)
- **Python**: Version 3.11+
- **Git**: Version 2.30+

### Entwicklungswerkzeuge
```bash
# Prüfen Sie Ihre Versionen
docker --version
docker-compose --version
node --version
python3 --version
git --version
```

## Schnellstart mit Docker

### 1. Repository klonen
```bash
# Neues Verzeichnis erstellen
mkdir ~/vocaliq
cd ~/vocaliq

# Repository klonen (oder Dateien kopieren)
git clone https://github.com/yourusername/vocaliq.git .
# ODER
# Kopieren Sie alle Setup-Dateien in dieses Verzeichnis
```

### 2. Umgebungsvariablen konfigurieren
```bash
# Kopieren Sie die Beispiel-Umgebungsdatei
cp env.example .env

# Bearbeiten Sie die .env Datei
nano .env
# ODER
vim .env
```

### 3. Docker-Container starten
```bash
# Entwicklungsumgebung starten
make up

# Logs anzeigen
make logs

# Status prüfen
docker-compose ps
```

### 4. Zugriff testen
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Dashboard: http://localhost:5173
- Landing Page: http://localhost:80

## Manuelle Installation

### 1. Backend Setup (FastAPI)

#### Python-Umgebung erstellen
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ODER
.venv\Scripts\activate  # Windows
```

#### Dependencies installieren
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Für Entwicklung
```

#### Datenbank initialisieren
```bash
# SQLite für Entwicklung
export DATABASE_URL="sqlite:///./vocaliq.db"

# PostgreSQL für Produktion
export DATABASE_URL="postgresql://user:password@localhost/vocaliq"

# Migrationen ausführen
alembic upgrade head
```

#### Backend starten
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup (React Dashboard)

#### Dependencies installieren
```bash
cd backend/frontend
npm install
```

#### Entwicklungsserver starten
```bash
npm run dev
```

#### Production Build
```bash
npm run build
npm run preview  # Zum Testen des Builds
```

### 3. Zusätzliche Services

#### Redis (Cache & Sessions)
```bash
# Docker
docker run -d -p 6379:6379 redis:alpine

# Oder native Installation
sudo apt install redis-server
sudo systemctl start redis
```

#### PostgreSQL (Produktion)
```bash
# Docker
docker run -d \
  -p 5432:5432 \
  -e POSTGRES_DB=vocaliq \
  -e POSTGRES_USER=vocaliq \
  -e POSTGRES_PASSWORD=your_password \
  postgres:15-alpine

# Oder native Installation
sudo apt install postgresql
sudo -u postgres createdb vocaliq
sudo -u postgres createuser vocaliq
```

#### Weaviate (Vector Database)
```bash
# Docker Compose für Weaviate
docker-compose -f docker-compose.weaviate.yml up -d
```

## Umgebungsvariablen

Erstellen Sie eine `.env` Datei im Root-Verzeichnis:

```bash
# ===========================
# CORE SETTINGS
# ===========================
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-min-32-characters-long-change-this

# ===========================
# API CONFIGURATION
# ===========================
API_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# ===========================
# DATABASE
# ===========================
# Development (SQLite)
DATABASE_URL=sqlite:///./vocaliq.db

# Production (PostgreSQL)
# DATABASE_URL=postgresql://vocaliq:password@localhost:5432/vocaliq
# DATABASE_POOL_SIZE=20
# DATABASE_MAX_OVERFLOW=0

# ===========================
# REDIS
# ===========================
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=
REDIS_SSL=false

# ===========================
# AUTHENTICATION
# ===========================
JWT_SECRET_KEY=your-jwt-secret-key-change-this
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-admin-password

# ===========================
# TWILIO (Telefonie)
# ===========================
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WEBHOOK_URL=https://your-domain.com/webhooks/twilio
TWILIO_STATUS_CALLBACK_URL=https://your-domain.com/webhooks/twilio/status

# ===========================
# OPENAI (KI & STT)
# ===========================
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000
WHISPER_MODEL=whisper-1
WHISPER_LANGUAGE=de

# ===========================
# ELEVENLABS (TTS)
# ===========================
ELEVENLABS_API_KEY=your-elevenlabs-api-key
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
ELEVENLABS_MODEL=eleven_multilingual_v2
ELEVENLABS_VOICE_SETTINGS_STABILITY=0.5
ELEVENLABS_VOICE_SETTINGS_SIMILARITY_BOOST=0.75

# ===========================
# WEAVIATE (Vector DB)
# ===========================
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=
WEAVIATE_ADDITIONAL_HEADERS=

# ===========================
# GOOGLE CALENDAR
# ===========================
GOOGLE_CALENDAR_CREDENTIALS_FILE=./credentials/google-calendar.json
GOOGLE_CALENDAR_ID=primary

# ===========================
# RATE LIMITING
# ===========================
RATE_LIMIT_ENABLED=true
RATE_LIMIT_GENERAL=100/minute
RATE_LIMIT_AUDIO=20/minute
RATE_LIMIT_CALLS=10/minute

# ===========================
# MONITORING
# ===========================
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
GRAFANA_ENABLED=true
GRAFANA_PORT=3000
LOKI_ENABLED=true
LOKI_URL=http://localhost:3100

# ===========================
# EMAIL (Notifications)
# ===========================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@vocaliq.de
SMTP_FROM_NAME=VocalIQ

# ===========================
# STORAGE
# ===========================
STORAGE_TYPE=local
STORAGE_LOCAL_PATH=./storage
# Für S3
# STORAGE_TYPE=s3
# AWS_ACCESS_KEY_ID=
# AWS_SECRET_ACCESS_KEY=
# AWS_S3_BUCKET=vocaliq-storage

# ===========================
# WEBHOOKS
# ===========================
WEBHOOK_SECRET=your-webhook-secret
WEBHOOK_TIMEOUT=30

# ===========================
# FEATURE FLAGS
# ===========================
FEATURE_OUTBOUND_CALLS=true
FEATURE_CALENDAR_INTEGRATION=true
FEATURE_CRM_INTEGRATION=true
FEATURE_ANALYTICS=true
FEATURE_MULTI_TENANT=true

# ===========================
# SECURITY
# ===========================
CORS_ALLOW_CREDENTIALS=true
SECURE_COOKIES=false  # Set to true in production with HTTPS
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=lax
```

## Datenbank-Setup

### 1. Initiale Migration erstellen
```bash
cd backend
alembic init alembic  # Nur wenn noch nicht vorhanden
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 2. Seed-Daten laden
```bash
# Beispiel-Organisation und Admin-User erstellen
python scripts/seed_database.py
```

### 3. Backup einrichten
```bash
# PostgreSQL Backup Script
cat > backup_database.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/vocaliq"
mkdir -p $BACKUP_DIR
pg_dump vocaliq | gzip > $BACKUP_DIR/vocaliq_$(date +%Y%m%d_%H%M%S).sql.gz
# Alte Backups löschen (älter als 7 Tage)
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
EOF

chmod +x backup_database.sh

# Cron Job einrichten
crontab -e
# Fügen Sie hinzu: 0 2 * * * /path/to/backup_database.sh
```

## Externe Services einrichten

### 1. Twilio Setup
1. Account erstellen auf [twilio.com](https://twilio.com)
2. Telefonnummer kaufen
3. Webhook URLs konfigurieren:
   - Voice URL: `https://your-domain.com/webhooks/twilio/voice`
   - Status Callback: `https://your-domain.com/webhooks/twilio/status`

### 2. OpenAI Setup
1. API Key erstellen auf [platform.openai.com](https://platform.openai.com)
2. Verwendungslimits setzen
3. API Key in .env eintragen

### 3. ElevenLabs Setup
1. Account erstellen auf [elevenlabs.io](https://elevenlabs.io)
2. Voice ID auswählen oder eigene Stimme erstellen
3. API Key in .env eintragen

### 4. Google Calendar Setup
1. Google Cloud Console Projekt erstellen
2. Calendar API aktivieren
3. Service Account erstellen
4. Credentials JSON herunterladen
5. Kalender-Berechtigung erteilen

## SSL/TLS und Nginx

### 1. Nginx installieren
```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx
```

### 2. Nginx Konfiguration
```nginx
# /etc/nginx/sites-available/vocaliq
server {
    listen 80;
    server_name your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # API Backend
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket für Audio Streaming
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Dashboard
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 3. SSL-Zertifikat mit Let's Encrypt
```bash
# Nginx Konfiguration aktivieren
sudo ln -s /etc/nginx/sites-available/vocaliq /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# SSL-Zertifikat erstellen
sudo certbot --nginx -d your-domain.com

# Auto-Renewal testen
sudo certbot renew --dry-run
```

## Erste Schritte

### 1. System Health Check
```bash
# API Health Check
curl http://localhost:8000/health

# Erwartete Antwort:
# {"status":"healthy","timestamp":"2024-01-20T10:00:00Z"}
```

### 2. Admin-Zugang testen
```bash
# Login als Admin
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your-admin-password"
  }'
```

### 3. Erste Organisation anlegen
```bash
# Via Dashboard oder API
curl -X POST http://localhost:8000/api/organizations \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Demo Company",
    "contact_email": "demo@company.com",
    "phone": "+49123456789"
  }'
```

### 4. Test-Anruf durchführen
```bash
# Outbound Demo Call
curl -X POST http://localhost:8000/api/calls/outbound/demo \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to_number": "+49123456789",
    "agent_config": {
      "greeting": "Hallo, hier ist VocalIQ Demo"
    }
  }'
```

## Troubleshooting

### Docker-Probleme

#### Container startet nicht
```bash
# Logs prüfen
docker-compose logs api
docker-compose logs frontend

# Container neu bauen
docker-compose down
docker-compose build --no-cache
docker-compose up
```

#### Port bereits belegt
```bash
# Prozess auf Port finden
sudo lsof -i :8000
sudo lsof -i :5173

# Prozess beenden oder anderen Port verwenden
# In docker-compose.yml ändern:
# ports:
#   - "8001:8000"  # Externer Port geändert
```

### Datenbank-Probleme

#### Migration fehlgeschlagen
```bash
# Datenbank zurücksetzen (VORSICHT: Löscht alle Daten!)
cd backend
alembic downgrade base
alembic upgrade head
```

#### Verbindung fehlgeschlagen
```bash
# PostgreSQL Status prüfen
sudo systemctl status postgresql

# Verbindung testen
psql -U vocaliq -d vocaliq -h localhost
```

### API-Probleme

#### 500 Internal Server Error
```bash
# Logs prüfen
tail -f backend/logs/error.log

# Debug-Modus aktivieren
export DEBUG=true
export LOG_LEVEL=DEBUG
```

#### CORS-Fehler
```bash
# In .env prüfen:
ALLOWED_ORIGINS=http://localhost:5173,https://your-domain.com
```

### Twilio-Probleme

#### Webhook nicht erreichbar
```bash
# Ngrok für lokales Testing
ngrok http 8000

# Twilio Webhook URL aktualisieren mit ngrok URL
```

#### Audio-Qualitätsprobleme
```bash
# In .env anpassen:
AUDIO_SAMPLE_RATE=16000
AUDIO_CHANNELS=1
AUDIO_FORMAT=wav
```

### Performance-Probleme

#### Langsame Antwortzeiten
```bash
# Redis-Cache prüfen
redis-cli ping

# Worker-Prozesse erhöhen (docker-compose.yml)
command: uvicorn api.main:app --workers 4
```

#### Hohe CPU-Auslastung
```bash
# Monitoring aktivieren
docker-compose -f docker-compose.monitoring.yml up -d

# Grafana öffnen: http://localhost:3000
```

## Nächste Schritte

1. **Sicherheit härten**: Firewall-Regeln, Fail2ban, Security Headers
2. **Monitoring einrichten**: Prometheus, Grafana, Alerting
3. **Backup-Strategie**: Automatische Backups, Disaster Recovery
4. **CI/CD Pipeline**: GitHub Actions, automatische Tests
5. **Skalierung planen**: Load Balancer, Container-Orchestrierung

## Support

Bei Problemen:
1. Prüfen Sie die Logs: `make logs`
2. Konsultieren Sie die [API-Dokumentation](http://localhost:8000/docs)
3. Erstellen Sie ein Issue im Repository
4. Kontaktieren Sie den Support: support@vocaliq.de

---

*Diese Anleitung wird regelmäßig aktualisiert. Letzte Änderung: Januar 2024*