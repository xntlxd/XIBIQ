# Xibiq Messenger - Docker Compose Setup

## Prerequisites
- Docker and Docker Compose installed on your system

## Setup Instructions

1. First, create a `.env` file in the root directory of the project with the following content:

```env
AUTH_DATABASE_URI=postgresql+asyncpg://user:pass@postgres-auth:5432/xibiq_auth
BOT_DATABASE_URI=postgresql+asyncpg://user:pass@postgres-bot:5432/xibiq_bot

REDIS_URI=redis://redis:6379

BOT_TOKEN=TELEGRAM_BOT_TOKEN

POSTGRES_AUTH_DB=xibiq_auth
POSTGRES_BOT_DB=xibiq_bot
```

Replace the placeholder values with your actual credentials:
- `user:pass` with your PostgreSQL credentials
- `db_name` with your database names
- `TELEGRAM_BOT_TOKEN` with your actual Telegram bot token

2. Run the application using Docker Compose:

```bash
docker-compose up -d
```

This will start all the necessary services in detached mode.

3. To stop the application:

```bash
docker-compose down
```

## Notes
- Make sure the `.env` file is in the same directory as your `docker-compose.yml` file
- The database URIs point to services named `postgres-auth` and `postgres-bot` which should be defined in your docker-compose file
- The Redis connection points to a service named `redis` which should also be defined in your docker-compose file