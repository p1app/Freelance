#!/bin/bash


echo "Running migrations.."
uv run --frozen --no-group dev alembic upgrade head

echo "Start application.."
exec "$@"