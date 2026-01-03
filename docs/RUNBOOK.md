# Campus Assistant Operations Runbook

## Quick Reference

| Service | Port | Health Check |
|---------|------|--------------|
| Backend | 8000 | `GET /health` |
| Frontend | 3000 | `GET /` |
| PostgreSQL | 5432 | `pg_isready` |

## Startup Procedures

### Development Environment

```bash
# Start all services
docker-compose up --build

# Or start individually
cd backend && uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev
```

### Production Environment

```bash
# Pull latest images
docker-compose pull

# Run migrations
docker-compose run --rm backend alembic upgrade head

# Start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verify health
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

## Common Operations

### Generate Admin Password Hash

```bash
cd backend
python -m app.cli hash-password --password "your-secure-password"
# Set output as ADMIN_PASSWORD_HASH environment variable
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# View current version
alembic current
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Filter by level (structured logs)
docker-compose logs backend | jq 'select(.level == "ERROR")'
```

### Check Metrics

```bash
# Prometheus metrics
curl http://localhost:8000/metrics

# Key metrics to monitor:
# - http_requests_total
# - http_request_duration_seconds
# - chat_messages_total
```

## Troubleshooting

### Backend Not Starting

**Symptoms:** Container exits immediately, health check fails

**Diagnosis:**
```bash
docker-compose logs backend
```

**Common causes:**
1. **Database connection failed**
   - Check `DATABASE_URL` is correct
   - Ensure PostgreSQL is running: `docker-compose ps postgres`
   - Check network connectivity

2. **Missing environment variables**
   - Verify `.env` file exists
   - Check required variables are set

3. **Port already in use**
   ```bash
   lsof -i :8000
   kill -9 <PID>
   ```

### Database Connection Issues

**Symptoms:** `/ready` returns 503, database errors in logs

**Diagnosis:**
```bash
# Check PostgreSQL status
docker-compose exec postgres pg_isready -U campus

# Check connections
docker-compose exec postgres psql -U campus -c "SELECT count(*) FROM pg_stat_activity;"
```

**Resolution:**
1. Restart PostgreSQL: `docker-compose restart postgres`
2. Check max_connections limit
3. Verify connection string format

### High Memory Usage

**Symptoms:** Container OOM kills, slow responses

**Diagnosis:**
```bash
docker stats
docker-compose exec backend ps aux
```

**Resolution:**
1. Increase container memory limits
2. Check for memory leaks in logs
3. Restart affected containers

### Chat Not Responding

**Symptoms:** Messages timeout, no responses

**Diagnosis:**
1. Check backend logs for errors
2. Verify Gemini API key is valid
3. Check rate limits

**Resolution:**
```bash
# Test Gemini API
curl -X POST "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=$GOOGLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}'
```

### Vector Search Not Working

**Symptoms:** Responses don't include document context

**Diagnosis:**
```bash
# Check ChromaDB directory
docker-compose exec backend ls -la /app/data/chroma

# Check document indexing status
docker-compose exec postgres psql -U campus -c "SELECT filename, is_indexed FROM documents;"
```

**Resolution:**
1. Re-index documents via admin panel
2. Check disk space for ChromaDB
3. Verify embedding model is loaded

## Scaling Operations

### Horizontal Scaling (Backend)

```bash
# Scale to 3 replicas
docker-compose up -d --scale backend=3

# With load balancer configured
docker-compose -f docker-compose.yml -f docker-compose.scale.yml up -d
```

### Database Backup

```bash
# Backup
docker-compose exec postgres pg_dump -U campus campus_assistant > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T postgres psql -U campus campus_assistant < backup_20240101.sql
```

### Rolling Update

```bash
# Pull new images
docker-compose pull

# Update one service at a time
docker-compose up -d --no-deps backend
docker-compose up -d --no-deps frontend
```

## Incident Response

### High Error Rate

1. Check error logs: `docker-compose logs backend | grep ERROR`
2. Check metrics: `curl localhost:8000/metrics | grep http_requests_total`
3. Check external dependencies (Gemini API, database)
4. Scale up if needed: `docker-compose up -d --scale backend=3`

### Security Incident

1. Rotate secrets immediately:
   ```bash
   # Generate new SECRET_KEY
   python -c "import secrets; print(secrets.token_urlsafe(32))"

   # Generate new admin password hash
   python -m app.cli hash-password --password "new-password"
   ```
2. Update environment variables
3. Restart all services
4. Review access logs

### Data Recovery

1. Stop writes: `docker-compose stop backend`
2. Restore from backup (see Database Backup section)
3. Verify data integrity
4. Resume services: `docker-compose start backend`

## Monitoring Alerts

### Recommended Alert Rules

| Metric | Threshold | Severity |
|--------|-----------|----------|
| `http_request_duration_seconds{quantile="0.95"}` | > 5s | Warning |
| `http_request_duration_seconds{quantile="0.99"}` | > 10s | Critical |
| `http_requests_total{status=~"5.."}` rate | > 1% | Warning |
| Container memory usage | > 80% | Warning |
| Container memory usage | > 95% | Critical |
| Database connections | > 80% of max | Warning |

## Contact Information

- **On-call:** [Configure your on-call rotation]
- **Escalation:** [Configure escalation path]
- **Documentation:** See `docs/ARCHITECTURE.md`
