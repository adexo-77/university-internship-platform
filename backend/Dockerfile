# Multi-stage Dockerfile for FastAPI Backend

# Stage 1: Build Python virtual environment with dependencies
FROM python:3.12.7-slim-bookworm AS builder

WORKDIR /build

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Minimal runtime image with non-root user and healthcheck
FROM python:3.12.7-slim-bookworm AS runtime

RUN groupadd --gid 10001 appgroup && \
    useradd --uid 10001 --gid appgroup --shell /bin/bash --create-home appuser

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

COPY --chown=appuser:appgroup backend/alembic.ini /app/
COPY --chown=appuser:appgroup backend/alembic /app/alembic
COPY --chown=appuser:appgroup backend/app /app/app
COPY --chown=appuser:appgroup scripts /app/scripts

# Symlink so CLI scripts importing REPO_ROOT / "backend" resolve to /app
RUN ln -s /app /app/backend

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://127.0.0.1:8000/api/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
