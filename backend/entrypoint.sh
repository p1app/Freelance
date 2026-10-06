#!/bin/bash

echo "Running check"
uv run alembic check 
CHECK_STATUS=$?

if [ $((CHECK_STATUS)) -ne 0 ]
then 
    echo "Check status failed"
    echo "Running migrations.."
    uv run alembic upgrade head
fi

echo "Start application.."
exec "$@"