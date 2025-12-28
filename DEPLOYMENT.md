# Production Deployment Checklist

## Environment Variables (REQUIRED for Production)

```bash
# Core Settings
ENVIRONMENT=production
DEBUG=false

# Security
JWT_SECRET=<generated-with-openssl-rand-hex-32>
SESSION_SECRET=<generated-with-openssl-rand-hex-32>

# Database
MONGO_URL=mongodb://user:pass@host:port/db?authSource=admin

# CORS (your frontend domains)
CORS_ALLOW_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Rate Limiting (important for multi-worker)
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REDIS_URL=redis://localhost:6379/0
RATE_LIMIT_LOGIN_PER_MINUTE=10
RATE_LIMIT_REGISTER_PER_HOUR=5
```

## Pre-Deployment Verification

### 1. Run Tests
```bash
cd /app && python -m pytest tests/unit/ -q
# Expected: All tests pass
```

### 2. Lint Check
```bash
cd /app/backend && ruff check . --ignore E501,F401,F841
cd /app/frontend && yarn lint --max-warnings=50
```

### 3. Start Application
```bash
# The app runs via supervisor with server.py as entrypoint
sudo supervisorctl restart backend
sudo supervisorctl status
```

### 4. Verify Key Endpoints
```bash
API_URL="https://your-domain.com"

# Health/Root
curl $API_URL/api/

# Auth
curl -X POST $API_URL/api/auth/register -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test123!","username":"test","full_name":"Test","role":"player"}'

# Training
curl $API_URL/api/training/programs/test_player

# Elite Training
curl $API_URL/api/elite-training/rtp-protocols
```

## Infrastructure Requirements

### Redis (Required for Multi-Worker Rate Limiting)
```bash
# Check Redis is running
redis-cli ping
# Expected: PONG

# If not running, start it
sudo systemctl start redis
```

### MongoDB
```bash
# Verify connection
mongosh "$MONGO_URL" --eval "db.adminCommand('ping')"
```

## Security Checklist

- [ ] JWT_SECRET changed from default
- [ ] SESSION_SECRET changed from default
- [ ] CORS_ALLOW_ORIGINS set to specific domains (not *)
- [ ] DEBUG=false
- [ ] ENVIRONMENT=production
- [ ] Rate limiting enabled
- [ ] HTTPS enforced (via ingress/proxy)
- [ ] Secrets NOT in version control

## Monitoring

### Check Backend Logs
```bash
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/backend.out.log
```

### Check Service Status
```bash
sudo supervisorctl status
```

## Rollback

If issues occur, rollback to the previous version:
```bash
git checkout v0.3  # or previous stable tag
sudo supervisorctl restart backend
```
