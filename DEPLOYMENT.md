# VocalIQ Production Deployment Guide

## Inhaltsverzeichnis

1. [Infrastruktur-Anforderungen](#infrastruktur-anforderungen)
2. [Deployment-Strategien](#deployment-strategien)
3. [Docker Production Setup](#docker-production-setup)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Monitoring & Observability](#monitoring--observability)
6. [Backup & Recovery](#backup--recovery)
7. [Skalierung](#skalierung)
8. [Security Hardening](#security-hardening)
9. [CI/CD Pipeline](#cicd-pipeline)
10. [Troubleshooting](#troubleshooting)

## Infrastruktur-Anforderungen

### Minimum Production Setup

#### Single Server (Klein)
- **vCPUs**: 8 Cores
- **RAM**: 32 GB
- **Storage**: 500 GB SSD (NVMe bevorzugt)
- **Network**: 1 Gbps, Statische IP
- **OS**: Ubuntu 22.04 LTS

#### Multi-Server Setup (Empfohlen)
```yaml
Load Balancer:
  - 2x vCPUs: 4 Cores
  - RAM: 8 GB
  - Network: 10 Gbps

Application Servers (3x):
  - vCPUs: 8 Cores
  - RAM: 16 GB
  - Storage: 100 GB SSD

Database Server:
  - vCPUs: 16 Cores
  - RAM: 64 GB
  - Storage: 1 TB NVMe SSD
  - Backup Storage: 2 TB

Cache/Queue Server:
  - vCPUs: 8 Cores
  - RAM: 32 GB (Redis)
  - Storage: 200 GB SSD
```

### Cloud Provider Empfehlungen

#### AWS
```yaml
Load Balancer: Application Load Balancer (ALB)
Compute: EC2 c5.2xlarge (App), r5.2xlarge (DB)
Storage: EBS gp3, S3 für Backups
Database: RDS PostgreSQL oder selbst-verwaltet
Cache: ElastiCache Redis
Container: ECS oder EKS
```

#### Google Cloud
```yaml
Load Balancer: Cloud Load Balancing
Compute: n2-standard-8 (App), n2-highmem-16 (DB)
Storage: Persistent Disks, Cloud Storage
Database: Cloud SQL oder selbst-verwaltet
Cache: Memorystore Redis
Container: GKE
```

#### Azure
```yaml
Load Balancer: Azure Load Balancer
Compute: D8s_v5 (App), E16s_v5 (DB)
Storage: Premium SSD, Blob Storage
Database: Azure Database for PostgreSQL
Cache: Azure Cache for Redis
Container: AKS
```

## Deployment-Strategien

### 1. Blue-Green Deployment

```bash
#!/bin/bash
# Blue-Green Deployment Script

BLUE_ENV="vocaliq-blue"
GREEN_ENV="vocaliq-green"
CURRENT_ENV=$(cat /etc/vocaliq/current_env)

if [ "$CURRENT_ENV" == "$BLUE_ENV" ]; then
    NEW_ENV=$GREEN_ENV
else
    NEW_ENV=$BLUE_ENV
fi

echo "Deploying to $NEW_ENV..."

# Deploy to new environment
docker-compose -f docker-compose.prod.yml -p $NEW_ENV up -d

# Health check
for i in {1..30}; do
    if curl -f http://localhost:8001/health; then
        echo "Health check passed"
        break
    fi
    sleep 10
done

# Switch traffic
echo $NEW_ENV > /etc/vocaliq/current_env
nginx -s reload

# Stop old environment
docker-compose -f docker-compose.prod.yml -p $CURRENT_ENV down
```

### 2. Rolling Update

```yaml
# Kubernetes Rolling Update
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vocaliq-api
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    spec:
      containers:
      - name: api
        image: vocaliq/api:v1.2.0
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

### 3. Canary Deployment

```nginx
# Nginx Canary Configuration
upstream vocaliq_backend {
    server backend_stable:8000 weight=9;
    server backend_canary:8000 weight=1;
}
```

## Docker Production Setup

### docker-compose.prod.yml

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - static_volume:/static
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - api
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  api:
    image: vocaliq/api:${VERSION:-latest}
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASS}@postgres:5432/${DB_NAME}
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./backend/alembic:/app/alembic
      - media_volume:/app/media
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: always
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    image: vocaliq/frontend:${VERSION:-latest}
    build:
      context: ./backend/frontend
      dockerfile: Dockerfile.prod
      args:
        - VITE_API_URL=${API_URL}
    restart: always
    depends_on:
      - api

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASS}
      - POSTGRES_INITDB_ARGS=--encoding=UTF8
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backup:/backup
    restart: always
    command: >
      postgres
      -c max_connections=200
      -c shared_buffers=256MB
      -c effective_cache_size=1GB
      -c maintenance_work_mem=64MB
      -c checkpoint_completion_target=0.9
      -c wal_buffers=16MB
      -c default_statistics_target=100
      -c random_page_cost=1.1
      -c effective_io_concurrency=200
      -c work_mem=4MB
      -c min_wal_size=1GB
      -c max_wal_size=4GB
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: >
      redis-server
      --maxmemory 2gb
      --maxmemory-policy allkeys-lru
      --save 900 1
      --save 300 10
      --save 60 10000
    volumes:
      - redis_data:/data
    restart: always
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  weaviate:
    image: semitechnologies/weaviate:latest
    environment:
      - QUERY_DEFAULTS_LIMIT=25
      - AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=false
      - PERSISTENCE_DATA_PATH=/var/lib/weaviate
      - DEFAULT_VECTORIZER_MODULE=text2vec-openai
      - ENABLE_MODULES=text2vec-openai
      - OPENAI_APIKEY=${OPENAI_API_KEY}
    volumes:
      - weaviate_data:/var/lib/weaviate
    restart: always

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
    restart: always

  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    depends_on:
      - prometheus
    restart: always

  loki:
    image: grafana/loki:latest
    volumes:
      - ./monitoring/loki-config.yml:/etc/loki/local-config.yaml:ro
      - loki_data:/loki
    command: -config.file=/etc/loki/local-config.yaml
    restart: always

  promtail:
    image: grafana/promtail:latest
    volumes:
      - ./monitoring/promtail-config.yml:/etc/promtail/config.yml:ro
      - /var/log:/var/log:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
    command: -config.file=/etc/promtail/config.yml
    restart: always

volumes:
  postgres_data:
  redis_data:
  weaviate_data:
  prometheus_data:
  grafana_data:
  loki_data:
  static_volume:
  media_volume:

networks:
  default:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### Production Dockerfile

```dockerfile
# backend/Dockerfile.prod
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels and install
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 vocaliq && chown -R vocaliq:vocaliq /app
USER vocaliq

# Run with gunicorn
CMD ["gunicorn", "api.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "50"]
```

## Kubernetes Deployment

### Namespace und ConfigMap

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: vocaliq

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: vocaliq-config
  namespace: vocaliq
data:
  ENVIRONMENT: "production"
  API_BASE_URL: "https://api.vocaliq.de"
  LOG_LEVEL: "INFO"
```

### Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: vocaliq-secrets
  namespace: vocaliq
type: Opaque
stringData:
  DATABASE_URL: "postgresql://user:pass@postgres:5432/vocaliq"
  SECRET_KEY: "your-secret-key"
  JWT_SECRET_KEY: "your-jwt-secret"
  OPENAI_API_KEY: "sk-..."
  TWILIO_AUTH_TOKEN: "..."
```

### API Deployment

```yaml
# k8s/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vocaliq-api
  namespace: vocaliq
spec:
  replicas: 3
  selector:
    matchLabels:
      app: vocaliq-api
  template:
    metadata:
      labels:
        app: vocaliq-api
    spec:
      containers:
      - name: api
        image: vocaliq/api:v1.2.0
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: vocaliq-config
              key: ENVIRONMENT
        envFrom:
        - secretRef:
            name: vocaliq-secrets
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: media
          mountPath: /app/media
      volumes:
      - name: media
        persistentVolumeClaim:
          claimName: vocaliq-media-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: vocaliq-api
  namespace: vocaliq
spec:
  selector:
    app: vocaliq-api
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

### Ingress Configuration

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: vocaliq-ingress
  namespace: vocaliq
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
    nginx.ingress.kubernetes.io/websocket-services: "vocaliq-websocket"
spec:
  tls:
  - hosts:
    - api.vocaliq.de
    secretName: vocaliq-tls
  rules:
  - host: api.vocaliq.de
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: vocaliq-api
            port:
              number: 8000
      - path: /ws
        pathType: Prefix
        backend:
          service:
            name: vocaliq-websocket
            port:
              number: 8001
```

### Horizontal Pod Autoscaler

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: vocaliq-api-hpa
  namespace: vocaliq
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: vocaliq-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Monitoring & Observability

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'vocaliq-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - '/etc/prometheus/alerts/*.yml'
```

### Alert Rules

```yaml
# monitoring/alerts/vocaliq.yml
groups:
  - name: vocaliq
    rules:
    - alert: HighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "High error rate detected"
        description: "Error rate is above 5% for 5 minutes"

    - alert: HighResponseTime
      expr: histogram_quantile(0.95, http_request_duration_seconds_bucket) > 1
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High response time"
        description: "95th percentile response time is above 1s"

    - alert: LowCallSuccessRate
      expr: rate(calls_success_total[5m]) / rate(calls_total[5m]) < 0.9
      for: 10m
      labels:
        severity: critical
      annotations:
        summary: "Low call success rate"
        description: "Call success rate is below 90%"

    - alert: DatabaseConnectionPoolExhausted
      expr: database_connections_active / database_connections_max > 0.9
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "Database connection pool almost exhausted"
        description: "More than 90% of database connections are in use"
```

### Grafana Dashboards

```json
// monitoring/grafana/dashboards/vocaliq-overview.json
{
  "dashboard": {
    "title": "VocalIQ Overview",
    "panels": [
      {
        "title": "API Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Call Volume",
        "targets": [
          {
            "expr": "rate(calls_total[5m])"
          }
        ]
      },
      {
        "title": "Response Time",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds_bucket)"
          }
        ]
      },
      {
        "title": "Active Calls",
        "targets": [
          {
            "expr": "calls_active"
          }
        ]
      }
    ]
  }
}
```

### Logging Configuration

```yaml
# monitoring/loki-config.yml
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /loki/boltdb-shipper-active
    cache_location: /loki/boltdb-shipper-cache
    shared_store: filesystem
  filesystem:
    directory: /loki/chunks

limits_config:
  reject_old_samples: true
  reject_old_samples_max_age: 168h
```

## Backup & Recovery

### Automated Backup Script

```bash
#!/bin/bash
# backup.sh

set -e

# Configuration
BACKUP_DIR="/backup"
S3_BUCKET="vocaliq-backups"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Function to backup PostgreSQL
backup_postgres() {
    echo "Backing up PostgreSQL..."
    docker exec postgres pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/postgres_$TIMESTAMP.sql.gz
    
    # Also backup globals
    docker exec postgres pg_dumpall -U $DB_USER --globals-only | gzip > $BACKUP_DIR/postgres_globals_$TIMESTAMP.sql.gz
}

# Function to backup Redis
backup_redis() {
    echo "Backing up Redis..."
    docker exec redis redis-cli BGSAVE
    sleep 5
    docker cp redis:/data/dump.rdb $BACKUP_DIR/redis_$TIMESTAMP.rdb
}

# Function to backup media files
backup_media() {
    echo "Backing up media files..."
    tar -czf $BACKUP_DIR/media_$TIMESTAMP.tar.gz -C /var/vocaliq media/
}

# Function to backup Weaviate
backup_weaviate() {
    echo "Backing up Weaviate..."
    curl -X POST http://localhost:8080/v1/backups \
      -H "Content-Type: application/json" \
      -d "{\"id\": \"backup-$TIMESTAMP\"}"
}

# Upload to S3
upload_to_s3() {
    echo "Uploading to S3..."
    aws s3 sync $BACKUP_DIR s3://$S3_BUCKET/$(date +%Y/%m/%d)/ \
      --exclude "*" \
      --include "*_$TIMESTAMP*"
}

# Cleanup old backups
cleanup_old_backups() {
    echo "Cleaning up old backups..."
    find $BACKUP_DIR -name "*.gz" -mtime +$RETENTION_DAYS -delete
    find $BACKUP_DIR -name "*.rdb" -mtime +$RETENTION_DAYS -delete
    find $BACKUP_DIR -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
}

# Main execution
main() {
    mkdir -p $BACKUP_DIR
    
    backup_postgres
    backup_redis
    backup_media
    backup_weaviate
    upload_to_s3
    cleanup_old_backups
    
    echo "Backup completed successfully!"
}

# Run backup
main

# Add to crontab:
# 0 2 * * * /opt/vocaliq/scripts/backup.sh >> /var/log/vocaliq-backup.log 2>&1
```

### Disaster Recovery Procedure

```bash
#!/bin/bash
# restore.sh

set -e

# Configuration
BACKUP_DATE=$1
S3_BUCKET="vocaliq-backups"
RESTORE_DIR="/tmp/restore"

if [ -z "$BACKUP_DATE" ]; then
    echo "Usage: ./restore.sh YYYYMMDD_HHMMSS"
    exit 1
fi

# Download from S3
download_from_s3() {
    echo "Downloading backups from S3..."
    mkdir -p $RESTORE_DIR
    aws s3 sync s3://$S3_BUCKET/ $RESTORE_DIR/ \
      --exclude "*" \
      --include "*_$BACKUP_DATE*"
}

# Restore PostgreSQL
restore_postgres() {
    echo "Restoring PostgreSQL..."
    
    # Stop API to prevent connections
    docker-compose stop api
    
    # Drop and recreate database
    docker exec postgres psql -U $DB_USER -c "DROP DATABASE IF EXISTS $DB_NAME;"
    docker exec postgres psql -U $DB_USER -c "CREATE DATABASE $DB_NAME;"
    
    # Restore globals
    gunzip -c $RESTORE_DIR/postgres_globals_$BACKUP_DATE.sql.gz | \
      docker exec -i postgres psql -U $DB_USER
    
    # Restore database
    gunzip -c $RESTORE_DIR/postgres_$BACKUP_DATE.sql.gz | \
      docker exec -i postgres psql -U $DB_USER $DB_NAME
}

# Restore Redis
restore_redis() {
    echo "Restoring Redis..."
    docker-compose stop redis
    docker cp $RESTORE_DIR/redis_$BACKUP_DATE.rdb redis:/data/dump.rdb
    docker-compose start redis
}

# Restore media files
restore_media() {
    echo "Restoring media files..."
    tar -xzf $RESTORE_DIR/media_$BACKUP_DATE.tar.gz -C /var/vocaliq/
}

# Main execution
main() {
    download_from_s3
    restore_postgres
    restore_redis
    restore_media
    
    # Restart all services
    docker-compose restart
    
    echo "Restore completed successfully!"
}

# Run restore
main
```

## Skalierung

### Horizontal Scaling Strategy

```yaml
# Auto-scaling configuration
scaling:
  api:
    min_replicas: 3
    max_replicas: 20
    target_cpu: 70%
    target_memory: 80%
    scale_up_rate: 2 pods/minute
    scale_down_rate: 1 pod/minute
    
  websocket:
    min_replicas: 2
    max_replicas: 10
    target_connections: 1000/pod
    
  workers:
    min_replicas: 2
    max_replicas: 15
    target_queue_length: 100
```

### Database Scaling

```sql
-- PostgreSQL Read Replica Setup
-- On Primary
ALTER SYSTEM SET wal_level = replica;
ALTER SYSTEM SET max_wal_senders = 10;
ALTER SYSTEM SET wal_keep_segments = 64;
ALTER SYSTEM SET hot_standby = on;

-- Create replication user
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'secure_password';

-- On Replica
pg_basebackup -h primary-host -D /var/lib/postgresql/data -U replicator -W -P -R
```

### Redis Cluster Setup

```bash
# Redis Cluster Configuration
port 7000
cluster-enabled yes
cluster-config-file nodes.conf
cluster-node-timeout 5000
appendonly yes

# Create cluster
redis-cli --cluster create \
  redis1:7000 redis2:7000 redis3:7000 \
  redis4:7000 redis5:7000 redis6:7000 \
  --cluster-replicas 1
```

## Security Hardening

### Network Security

```yaml
# Network Policies
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: vocaliq-network-policy
  namespace: vocaliq
spec:
  podSelector:
    matchLabels:
      app: vocaliq-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: vocaliq
    - podSelector:
        matchLabels:
          app: nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: vocaliq
    ports:
    - protocol: TCP
      port: 5432  # PostgreSQL
    - protocol: TCP
      port: 6379  # Redis
```

### Security Checklist

```bash
#!/bin/bash
# security-check.sh

echo "VocalIQ Security Audit"
echo "====================="

# Check SSL/TLS
echo -n "SSL/TLS Configuration: "
if openssl s_client -connect api.vocaliq.de:443 < /dev/null 2>/dev/null | grep -q "Verify return code: 0"; then
    echo "✓ Valid"
else
    echo "✗ Invalid"
fi

# Check Security Headers
echo -n "Security Headers: "
headers=$(curl -s -I https://api.vocaliq.de)
required_headers=("X-Content-Type-Options" "X-Frame-Options" "X-XSS-Protection" "Strict-Transport-Security")
missing_headers=()

for header in "${required_headers[@]}"; do
    if ! echo "$headers" | grep -q "$header"; then
        missing_headers+=("$header")
    fi
done

if [ ${#missing_headers[@]} -eq 0 ]; then
    echo "✓ All present"
else
    echo "✗ Missing: ${missing_headers[*]}"
fi

# Check for exposed ports
echo -n "Exposed Ports: "
exposed_ports=$(nmap -p- api.vocaliq.de | grep "open" | grep -v "443\|80")
if [ -z "$exposed_ports" ]; then
    echo "✓ Only 80/443 exposed"
else
    echo "✗ Additional ports exposed"
    echo "$exposed_ports"
fi

# Check file permissions
echo -n "File Permissions: "
insecure_files=$(find /var/vocaliq -type f -perm -o+w 2>/dev/null)
if [ -z "$insecure_files" ]; then
    echo "✓ Secure"
else
    echo "✗ World-writable files found"
fi

# Check for default passwords
echo -n "Default Passwords: "
if grep -q "password123\|admin123\|default" /var/vocaliq/.env 2>/dev/null; then
    echo "✗ Default passwords detected"
else
    echo "✓ No defaults found"
fi
```

### WAF Configuration

```nginx
# ModSecurity with OWASP Core Rule Set
server {
    modsecurity on;
    modsecurity_rules_file /etc/nginx/modsec/main.conf;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=audio:10m rate=2r/s;
    
    location /api {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://backend;
    }
    
    location /api/audio {
        limit_req zone=audio burst=5 nodelay;
        proxy_pass http://backend;
    }
}
```

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    tags:
      - 'v*'

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        cd backend
        pytest --cov=api --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Build and push API image
      uses: docker/build-push-action@v4
      with:
        context: ./backend
        file: ./backend/Dockerfile.prod
        push: true
        tags: |
          ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/api:${{ github.ref_name }}
          ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/api:latest
    
    - name: Build and push Frontend image
      uses: docker/build-push-action@v4
      with:
        context: ./backend/frontend
        file: ./backend/frontend/Dockerfile.prod
        push: true
        tags: |
          ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend:${{ github.ref_name }}
          ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    
    steps:
    - name: Deploy to Kubernetes
      uses: azure/k8s-deploy@v4
      with:
        manifests: |
          k8s/api-deployment.yaml
          k8s/frontend-deployment.yaml
        images: |
          ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/api:${{ github.ref_name }}
          ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend:${{ github.ref_name }}
    
    - name: Wait for rollout
      run: |
        kubectl rollout status deployment/vocaliq-api -n vocaliq
        kubectl rollout status deployment/vocaliq-frontend -n vocaliq
    
    - name: Run smoke tests
      run: |
        curl -f https://api.vocaliq.de/health || exit 1
        curl -f https://app.vocaliq.de || exit 1
    
    - name: Notify deployment
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        text: 'Production deployment ${{ github.ref_name }} completed'
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

### Rollback Procedure

```bash
#!/bin/bash
# rollback.sh

PREVIOUS_VERSION=$1

if [ -z "$PREVIOUS_VERSION" ]; then
    echo "Usage: ./rollback.sh v1.1.0"
    exit 1
fi

echo "Rolling back to version $PREVIOUS_VERSION"

# Update Kubernetes deployments
kubectl set image deployment/vocaliq-api \
  api=$REGISTRY/vocaliq/api:$PREVIOUS_VERSION \
  -n vocaliq

kubectl set image deployment/vocaliq-frontend \
  frontend=$REGISTRY/vocaliq/frontend:$PREVIOUS_VERSION \
  -n vocaliq

# Wait for rollout
kubectl rollout status deployment/vocaliq-api -n vocaliq
kubectl rollout status deployment/vocaliq-frontend -n vocaliq

# Run health checks
./scripts/health-check.sh

echo "Rollback completed"
```

## Troubleshooting

### Common Issues

#### High Memory Usage
```bash
# Check memory usage
docker stats

# Analyze memory leaks
docker exec api python -m memory_profiler api/main.py

# Increase memory limits
docker update --memory 4g api
```

#### Database Connection Issues
```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity;

-- Kill idle connections
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle' 
AND state_change < now() - interval '30 minutes';

-- Increase connection pool
ALTER SYSTEM SET max_connections = 400;
```

#### Slow API Response
```bash
# Enable profiling
export PROFILE=true
docker-compose restart api

# Analyze slow queries
docker exec postgres psql -U $DB_USER -c "
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;"

# Check Redis latency
docker exec redis redis-cli --latency
```

#### WebSocket Connection Drops
```nginx
# Increase timeouts in nginx
proxy_read_timeout 3600s;
proxy_send_timeout 3600s;
proxy_connect_timeout 60s;
websocket_connect_timeout 60s;
websocket_send_timeout 3600s;
websocket_read_timeout 3600s;
```

### Emergency Procedures

#### Service Degradation
```bash
# Enable read-only mode
docker exec api python -m api.emergency --read-only

# Disable non-critical features
docker exec api python -m api.emergency --disable-features analytics,reports

# Scale down background workers
docker-compose scale worker=1
```

#### Data Corruption Recovery
```bash
# Stop all services
docker-compose stop

# Run integrity checks
docker exec postgres psql -U $DB_USER -c "
SELECT schemaname, tablename 
FROM pg_tables 
WHERE schemaname = 'public';" | \
while read schema table; do
    echo "Checking $table..."
    docker exec postgres psql -U $DB_USER -c "
    ANALYZE $table;
    REINDEX TABLE $table;"
done

# Restore from backup if needed
./scripts/restore.sh 20240120_020000
```

## Performance Tuning

### API Optimization
```python
# Caching configuration
CACHE_CONFIG = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PARSER_CLASS": "redis.connection.HiredisParser",
            "CONNECTION_POOL_CLASS": "redis.BlockingConnectionPool",
            "CONNECTION_POOL_CLASS_KWARGS": {
                "max_connections": 50,
                "timeout": 20,
            },
        },
        "KEY_PREFIX": "vocaliq",
        "TIMEOUT": 300,
    }
}

# Database query optimization
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "OPTIONS": {
            "connect_timeout": 10,
            "options": "-c statement_timeout=30000",
        },
        "CONN_MAX_AGE": 60,
        "ATOMIC_REQUESTS": True,
    }
}
```

### Load Testing
```bash
# Locust load test
cat > locustfile.py << EOF
from locust import HttpUser, task, between

class VocalIQUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def health_check(self):
        self.client.get("/health")
    
    @task(3)
    def get_agent(self):
        self.client.get("/api/v1/agents/agent_123",
                       headers={"Authorization": "Bearer token"})
    
    @task(2)
    def create_call(self):
        self.client.post("/api/v1/calls/outbound/start",
                        json={"to_number": "+1234567890"},
                        headers={"Authorization": "Bearer token"})
EOF

# Run load test
locust -f locustfile.py -H https://api.vocaliq.de --users 1000 --spawn-rate 10
```

## Maintenance Windows

### Planned Maintenance Procedure
```bash
#!/bin/bash
# maintenance.sh

# Enable maintenance mode
docker exec api python -m api.maintenance --enable

# Wait for active calls to complete
while [ $(docker exec api python -m api.calls --count-active) -gt 0 ]; do
    echo "Waiting for active calls to complete..."
    sleep 30
done

# Perform maintenance tasks
docker-compose pull
docker-compose up -d --no-deps api

# Run migrations
docker exec api alembic upgrade head

# Disable maintenance mode
docker exec api python -m api.maintenance --disable

# Send notification
curl -X POST $SLACK_WEBHOOK -d '{
    "text": "Maintenance completed successfully"
}'
```

---

*Dieses Deployment-Handbuch wird kontinuierlich aktualisiert. Bei Fragen kontaktieren Sie das DevOps-Team.*