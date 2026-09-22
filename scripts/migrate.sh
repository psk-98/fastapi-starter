#!/bin/bash

set -e

echo "🧱 Creating Alembic migration..."

MESSAGE="${1:-auto migration}"

uv run alembic revision \
  --autogenerate \
  -m "$MESSAGE"

echo "⬆️ Applying migrations..."

uv run alembic upgrade head

echo "✅ Alembic migrations complete"
