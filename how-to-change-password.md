# How to Change PostgreSQL Password in a Docker Container

## 1. Access the Container
### First, make sure your container is running (via Docker Desktop or CLI)
```bash
docker exec -it container_name bash
```

## 2. Connect to PostgreSQL
```bash
psql -U postgres
```

## 3. Change Password
```sql
ALTER USER postgres WITH PASSWORD 'new_password';
```

## Ready-to-Use Commands

For container named "postgres-auth":
```bash
docker exec -it postgres-auth bash -c "psql -U postgres -c \"ALTER USER postgres WITH PASSWORD 'new_password';\""
```

For container named "postgres-bot":
```bash
docker exec -it postgres-bot bash -c "psql -U postgres -c \"ALTER USER postgres WITH PASSWORD 'new_password';\""
```