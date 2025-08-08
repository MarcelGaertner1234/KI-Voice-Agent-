# VocalIQ - Setup Documentation

Diese Dokumentation enthält alle notwendigen Informationen für die Neuaufsetzung des VocalIQ-Projekts.

## 📁 Dokumentations-Struktur

### 1. **PRODUCT_OVERVIEW.md**
Kundenfreundliche Produktbeschreibung mit:
- Was ist VocalIQ und wie funktioniert es
- Hauptfunktionen und Vorteile
- Anwendungsfälle für verschiedene Branchen
- Preismodelle und ROI-Berechnung

### 2. **PROJECT_SETUP.md**
Vollständige Installationsanleitung mit:
- Systemvoraussetzungen
- Schritt-für-Schritt Installation
- Docker und manuelle Installation
- Umgebungsvariablen-Konfiguration
- Troubleshooting-Guide

### 3. **ARCHITECTURE.md**
Technische Systemarchitektur mit:
- Komponenten-Übersicht und Diagramme
- Technologie-Stack Details
- Service-Architektur
- Datenbank-Schema
- Skalierungsstrategie

### 4. **API_REFERENCE.md**
Komplette API-Dokumentation mit:
- Alle Endpoints (15+ Router)
- Request/Response Beispiele
- Authentifizierung und Rate Limiting
- WebSocket-Protokolle
- SDK-Beispiele

### 5. **DEPLOYMENT.md**
Production Deployment Guide mit:
- Infrastruktur-Anforderungen
- Docker und Kubernetes Setup
- Monitoring und Logging
- Backup und Recovery
- CI/CD Pipeline

### 6. **DEVELOPMENT.md**
Entwickler-Handbuch mit:
- Entwicklungsumgebung einrichten
- Coding Standards und Best Practices
- Testing-Strategie
- Git Workflow
- Performance-Optimierung

### 7. **CONFIGURATION.md**
Konfigurations-Referenz mit:
- Alle 40+ Umgebungsvariablen erklärt
- Service-Konfigurationen
- Multi-Tenant Setup
- Feature Flags
- Deployment-Profile

## 🚀 Quick Start

1. **Repository erstellen**
   ```bash
   mkdir vocaliq
   cd vocaliq
   ```

2. **Dateien kopieren**
   - Kopieren Sie alle Dateien aus diesem Ordner in Ihr neues Projekt

3. **Umgebung konfigurieren**
   ```bash
   cp env.example .env
   # Bearbeiten Sie .env mit Ihren Werten
   ```

4. **Services starten**
   ```bash
   make setup
   make up
   ```

5. **Datenbank initialisieren**
   ```bash
   make db-init
   ```

6. **Zugriff testen**
   - API: http://localhost:8000
   - Dashboard: http://localhost:5173
   - API Docs: http://localhost:8000/docs

## 📋 Projekt-Struktur

```
vocaliq/
├── backend/
│   ├── api/                  # FastAPI Application
│   ├── alembic/             # Database Migrations
│   ├── tests/               # Test Suite
│   └── frontend/            # React Dashboard
├── docker/                  # Docker Configurations
├── k8s/                    # Kubernetes Manifests
├── monitoring/             # Monitoring Setup
├── scripts/                # Utility Scripts
├── docker-compose.yml      # Development Setup
├── docker-compose.prod.yml # Production Setup
├── Makefile               # Common Commands
├── requirements.txt       # Python Dependencies
├── package.json          # Frontend Dependencies
└── .env.example          # Environment Template
```

## 🛠️ Wichtige Befehle

```bash
# Entwicklung
make up          # Services starten
make down        # Services stoppen
make logs        # Logs anzeigen
make test        # Tests ausführen

# Datenbank
make db-init     # DB initialisieren
make db-migrate  # Migration erstellen
make backup      # Backup erstellen

# Production
make up-prod     # Production starten
make deploy      # Deployment durchführen
```

## 🔧 Technologie-Stack

- **Backend**: FastAPI, Python 3.11+
- **Frontend**: React 18, TypeScript, Material-UI
- **Datenbank**: PostgreSQL 15, Redis 7
- **KI/ML**: OpenAI GPT-4, Whisper, ElevenLabs
- **Telefonie**: Twilio
- **Container**: Docker, Kubernetes-ready
- **Monitoring**: Prometheus, Grafana, Loki

## 📞 Support

Bei Fragen zur Neuaufsetzung:
1. Konsultieren Sie zuerst die Dokumentation
2. Prüfen Sie die Troubleshooting-Abschnitte
3. Erstellen Sie ein Issue mit detaillierter Beschreibung

---

*VocalIQ - Intelligente KI-Telefonassistenz für moderne Unternehmen*