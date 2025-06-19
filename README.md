# XIBIQ-Messenger - Docker Compose Setup Guide

## Prerequisites
- Docker Engine (v20.10+) and Docker Compose (v2.5+) installed
- OpenSSL for certificate generation (if not using existing certificates)

## Initial Setup

### 1. Environment Configuration
Create `.env` file in project root:

```env
# Database Connections
AUTH_DATABASE_URI=postgresql+asyncpg://xibiq_auth_user:secure_password123@postgres-auth:5432/xibiq_auth
BOT_DATABASE_URI=postgresql+asyncpg://xibiq_bot_user:secure_password123@postgres-bot:5432/xibiq_bot

# Redis Configuration
REDIS_URI=redis://redis:6379

# Telegram Integration
BOT_TOKEN=your_telegram_bot_token_here

# PostgreSQL Database Names
POSTGRES_AUTH_DB=xibiq_auth
POSTGRES_BOT_DB=xibiq_bot
```

Replace all placeholder values with your actual credentials.

### 2. Certificate Setup
For authentication service, place your RSA key pair in:
```
auth/application/certs/
```
Required files:
- `private.pem` - Private key for JWT signing
- `public.pem` - Public key for JWT verification

To generate new certificates:
```bash
openssl genrsa -out auth/application/certs/private.pem 2048
openssl rsa -in auth/application/certs/private.pem -pubout -out auth/application/certs/public.pem
```

## Deployment Commands

Start services:
```bash
docker-compose up -d --build
```

Stop services:
```bash
docker-compose down
```

View logs:
```bash
docker-compose logs -f
```

## Troubleshooting

### Database Connection Issues
If encountering authentication errors:
1. Refer to password change guide:
   ```bash
   cat how-to-change-password.md
   ```
2. Or use quick commands:
   ```bash
   # For auth database
   docker exec -it postgres-auth psql -U postgres -c "ALTER USER xibiq_auth_user WITH PASSWORD 'new_password';"

   # For bot database
   docker exec -it postgres-bot psql -U postgres -c "ALTER USER xibiq_bot_user WITH PASSWORD 'new_password';"
   ```

### Common Errors
- **Missing certificates**: Ensure both PEM files exist in auth/certs
- **Port conflicts**: Verify ports 5432 (PostgreSQL) and 6379 (Redis) are available
- **Environment variables**: All `.env` values must be properly set before startup

## Maintenance Tips
- Regularly backup your database volumes
- Update credentials periodically
- Monitor container resource usage:
  ```bash
  docker stats
  ```