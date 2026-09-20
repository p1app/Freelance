FROM python:3.14-slim

RUN pip install uv

WORKDIR /backend

COPY pyproject.toml uv.lock ./
RUN uv sync

COPY alembic.ini .
COPY entrypoint.sh .

RUN echo "CACHE DROP"

COPY migration/ ./migration
COPY src/ ./src

RUN chmod +x /backend/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/bin/bash", "/backend/entrypoint.sh"]
CMD ["uv","run", "src/main.py"]