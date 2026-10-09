# FinSight Deployment Guide

## Overview
This document describes how to deploy FinSight to production environments.

## Prerequisites
- Docker and Docker Compose
- Domain name with SSL certificate (Let's Encrypt recommended)
- PostgreSQL 16+
- MongoDB 7+
- Redis 7+

## Production Deployment

### 1. Environment Configuration
Copy `.env.example` to `.env` and configure all variables:
```bash
cp .env.example .env
# Edit .env with production values
```

Key production settings:
- `POSTGRES_PASSWORD`: Strong random password
- `MONGO_PASSWORD`: Strong random password
- `JWT_SECRET_KEY`: Very strong random string (64+ chars)
- `DEBUG`: `False`
- `CORS_ORIGINS`: Your production domain(s)

### 2. SSL/TLS Setup
Use a reverse proxy (Traefik, Nginx, or Caddy) for SSL termination.

Example with Caddy:
```caddy
finsight.yourdomain.com {
    reverse_proxy backend:8000
}

finsight.yourdomain.com/api/* {
    reverse_proxy backend:8000
}

finsight.yourdomain.com/* {
    reverse_proxy frontend:5173
}
```

### 3. Database Initialization
```bash
# Run migrations
docker-compose run --rm backend alembic upgrade head

# Or initialize tables directly (development)
docker-compose run --rm backend python -c "from backend.app.db.postgres import init_db; init_db()"
```

### 4. Seed Data (Optional)
```bash
docker-compose run --rm backend python scripts/seed.py
```

### 5. Start Services
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Docker Compose Production Override
Create `docker-compose.prod.yml`:
```yaml
version: '3.9'

services:
  postgres:
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    # No port exposure in production
    # ports:
    #   - "5432:5432"

  mongodb:
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_USER}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
      MONGO_INITDB_DATABASE: ${MONGO_DB}
    volumes:
      - mongodb_data:/data/db
    # No port exposure
    # ports:
    #   - "27017:27017"

  redis:
    volumes:
      - redis_data:/data
    # No port exposure
    # ports:
    #   - "6379:6379"

  backend:
    environment:
      - DEBUG=False
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
    # No volume mount in production
    # volumes:
    #   - ./backend:/app

  frontend:
    command: npm run build && npm run preview -- --host --port 5173
    # No volume mount
    # volumes:
    #   - ./frontend/src:/app/src
```

## Backup Strategy
Run the backup script regularly (cron):
```bash
# Daily at 2 AM
0 2 * * * /path/to/finsight/scripts/backup.sh
```

## Monitoring
- Check `/health` endpoint for service health
- Monitor PostgreSQL: `pg_stat_activity`, `pg_stat_database`
- Monitor MongoDB: `db.serverStatus()`
- Monitor Redis: `INFO memory`, `INFO stats`

## Scaling
- Backend: Run multiple workers (`--workers 4` or more)
- PostgreSQL: Read replicas for analytics queries
- MongoDB: Sharding for large analytics datasets
- Redis: Cluster mode for high availability

## Security Checklist
- [ ] Strong passwords for all databases
- [ ] JWT secret is 64+ random characters
- [ ] HTTPS enforced everywhere
- [ ] CORS restricted to production domain
- [ ] Database ports not exposed publicly
- [ ] Regular security updates applied
- [ ] Audit logs monitored
- [ ] Rate limiting configured

## Rollback Procedure
1. Stop new version: `docker-compose stop backend frontend`
2. Restore database from backup: `scripts/restore.sh <backup_file>`
3. Start previous version: `docker-compose up -d`