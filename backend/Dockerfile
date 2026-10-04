FROM python:3.14-slim

RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /backend

RUN pip install uv

RUN chown appuser:appuser /backend

USER appuser

COPY --chown=appuser:appuser pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY --chown=appuser:appuser alembic.ini entrypoint.sh ./
COPY --chown=appuser:appuser migration/ ./migration
COPY --chown=appuser:appuser src/ ./src

EXPOSE 8000

ENTRYPOINT ["/bin/bash", "/backend/entrypoint.sh"]
CMD ["uv", "run", "src/main.py"]
