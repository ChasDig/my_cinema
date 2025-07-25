#!/bin/sh
set -e

echo "🔄 Выполнение миграций..."
alembic upgrade head

echo "🚀 Запуск приложения..."
exec uvicorn run:app --host 0.0.0.0 --port "$AUTH_SERVICE_PORT" --workers $AUTH_SERVICE_WORKERS
