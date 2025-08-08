# VocalIQ Makefile
SHELL := /bin/bash

.PHONY: help up down logs test clean setup

# Default target
help:
	@echo "VocalIQ Development Commands:"
	@echo "  make setup     - Initial project setup"
	@echo "  make up        - Start all services"
	@echo "  make down      - Stop all services"
	@echo "  make logs      - Show API logs"
	@echo "  make test      - Run tests"
	@echo "  make clean     - Clean up containers and volumes"
	@echo "  make db-init   - Initialize database"
	@echo "  make ngrok     - Start ngrok tunnel"
	@echo ""
	@echo "Production Commands:"
	@echo "  make up-prod   - Start production environment"
	@echo "  make down-prod - Stop production environment"
	@echo "  make backup    - Create database backup"
	@echo ""
	@echo "GitHub Integration:"
	@echo "  make gh-pr     - Create pull request"
	@echo "  make gh-issues - List GitHub issues"
	@echo "  make gh-setup  - Setup GitHub CLI"
	@echo ""
	@echo "Code Quality:"
	@echo "  make pre-commit-install - Install pre-commit hooks"
	@echo "  make pre-commit-run     - Run pre-commit on all files"
	@echo "  make security-scan      - Run security scans"

# Development Commands
setup:
	@echo "Setting up VocalIQ..."
	@cp -n env.example .env || true
	@mkdir -p backend/logs backend/storage
	@echo "Setup complete! Edit .env file and run 'make up'"

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f api

test:
	cd backend && docker compose exec api pytest -v

clean:
	docker compose down -v
	rm -rf backend/__pycache__ backend/.pytest_cache
	find . -name "*.pyc" -delete

# Database Commands
db-init:
	docker compose exec api alembic upgrade head
	docker compose exec api python scripts/seed_database.py

db-migrate:
	docker compose exec api alembic revision --autogenerate -m "$(message)"

db-upgrade:
	docker compose exec api alembic upgrade head

db-downgrade:
	docker compose exec api alembic downgrade -1

# Production Commands
up-prod:
	docker compose -f docker-compose.prod.yml up --build -d

down-prod:
	docker compose -f docker-compose.prod.yml down

logs-prod:
	docker compose -f docker-compose.prod.yml logs -f

# Utility Commands
ngrok:
	ngrok http 8000

shell-api:
	docker compose exec api /bin/bash

shell-db:
	docker compose exec postgres psql -U vocaliq -d vocaliq

redis-cli:
	docker compose exec redis redis-cli

# Monitoring
monitoring-up:
	docker compose --profile monitoring up -d

monitoring-down:
	docker compose --profile monitoring down

# Testing specific services
test-unit:
	cd backend && docker compose exec api pytest tests/unit -v

test-integration:
	cd backend && docker compose exec api pytest tests/integration -v

test-coverage:
	cd backend && docker compose exec api pytest --cov=api --cov-report=html

# Linting and formatting
lint:
	cd backend && docker compose exec api ruff check .
	cd backend && docker compose exec api mypy api/

format:
	cd backend && docker compose exec api black .
	cd backend && docker compose exec api ruff check --fix .

# Build commands
build-api:
	docker build -t vocaliq/api:latest ./backend

build-frontend:
	docker build -t vocaliq/frontend:latest ./backend/frontend

# Backup
backup:
	@mkdir -p backups
	@docker compose exec postgres pg_dump -U vocaliq vocaliq | gzip > backups/vocaliq_$(shell date +%Y%m%d_%H%M%S).sql.gz
	@echo "Backup created: backups/vocaliq_$(shell date +%Y%m%d_%H%M%S).sql.gz"

restore:
	@echo "Restoring from $(file)..."
	@gunzip -c $(file) | docker compose exec -T postgres psql -U vocaliq vocaliq

# Development helpers
dev-install:
	cd backend && pip install -r requirements.txt -r requirements-dev.txt
	cd backend/frontend && npm install

dev-api:
	cd backend && uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd backend/frontend && npm run dev

# Documentation
docs-serve:
	mkdocs serve -f docs/mkdocs.yml

docs-build:
	mkdocs build -f docs/mkdocs.yml

# Quick commands
restart: down up

rebuild: clean up

status:
	docker compose ps

version:
	@echo "VocalIQ Development Environment v1.0.0"

# GitHub Integration Commands
gh-setup:
	@echo "Setting up GitHub CLI..."
	@gh auth login
	@gh repo set-default MarcelGaertner1234/KI-Voice-Agent-

gh-pr:
	@echo "Creating pull request..."
	@gh pr create --fill

gh-issues:
	@echo "Listing GitHub issues..."
	@gh issue list

gh-pr-status:
	@gh pr status

gh-workflow-status:
	@gh workflow list
	@gh run list --limit 5

# Pre-commit Commands
pre-commit-install:
	@echo "Installing pre-commit hooks..."
	@pip install pre-commit
	@pre-commit install
	@pre-commit autoupdate
	@echo "Pre-commit hooks installed successfully!"

pre-commit-run:
	@echo "Running pre-commit on all files..."
	@pre-commit run --all-files

pre-commit-update:
	@echo "Updating pre-commit hooks..."
	@pre-commit autoupdate

# Security Scanning
security-scan:
	@echo "Running security scans..."
	@echo "Checking Python dependencies..."
	@pip install pip-audit
	@pip-audit || true
	@echo ""
	@echo "Checking Node dependencies..."
	@if [ -f package.json ]; then npm audit || true; fi
	@echo ""
	@echo "Checking for secrets..."
	@pip install detect-secrets
	@detect-secrets scan --baseline .secrets.baseline || true

security-fix:
	@echo "Attempting to fix security issues..."
	@pip-audit --fix || true
	@if [ -f package.json ]; then npm audit fix || true; fi

# Git Commands
git-setup:
	@echo "Setting up Git configuration..."
	@git config --global push.default current
	@git config --global push.autoSetupRemote true
	@echo "Git configuration completed!"

git-status:
	@git status -sb
	@echo ""
	@echo "Recent commits:"
	@git log --oneline -5

git-push:
	@echo "Pushing to remote repository..."
	@git push origin HEAD

# Combined Commands
init: setup pre-commit-install gh-setup git-setup
	@echo "Full initialization complete!"

check: lint test security-scan
	@echo "All checks completed!"

deploy-check: check
	@echo "Running deployment readiness check..."
	@docker compose config -q && echo "✓ Docker Compose configuration valid"
	@test -f .env && echo "✓ Environment file exists" || echo "✗ Missing .env file"
	@echo "Deployment check complete!"

# Development Workflow Commands
feature-start:
	@read -p "Feature name (VOCAL-XXX-description): " feature; \
	git checkout -b feature/$$feature

feature-finish:
	@git add -A
	@git commit
	@git push origin HEAD
	@gh pr create --fill

# Docker Utilities
docker-prune:
	@echo "Cleaning up Docker resources..."
	@docker system prune -af --volumes
	@echo "Docker cleanup complete!"

docker-stats:
	@docker stats --no-stream

# Help for specific topics
help-github:
	@echo "GitHub Integration Commands:"
	@echo "  make gh-setup       - Initial GitHub CLI setup"
	@echo "  make gh-pr          - Create a pull request"
	@echo "  make gh-issues      - List all issues"
	@echo "  make gh-pr-status   - Show PR status"
	@echo "  make gh-workflow-status - Show workflow status"

help-security:
	@echo "Security Commands:"
	@echo "  make security-scan  - Run all security scans"
	@echo "  make security-fix   - Attempt to fix security issues"
	@echo "  make pre-commit-run - Run pre-commit security checks"