# Используем официальный образ Python
FROM python:3.13-slim

# 1. Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    python3-dev \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 2. Установка uv (самый простой способ)
RUN pip install --no-cache-dir uv

# 3. Установка зависимостей проекта
WORKDIR /app
RUN uv init
COPY pyproject.toml .
RUN uv sync

COPY . .

# 5. Проверяем что uv работает
RUN uv --version

# 6. Запуск приложения
CMD ["uv", "run", "run.py"]
