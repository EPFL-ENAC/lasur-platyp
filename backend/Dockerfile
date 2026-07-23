FROM python:3.11-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
ENV PYTHONPATH="$PYTHONPATH:/app"
ENV UV_PROJECT_ENVIRONMENT="/usr/local"
ENV UV_LINK_MODE=copy

WORKDIR /app

RUN apt-get update && apt-get install -y g++ libpq-dev libgl1 gdal-bin libgdal-dev

COPY uv.lock pyproject.toml /app/
RUN uv sync --locked --no-install-project --no-dev

COPY alembic.ini start.sh README.md /app/
COPY migrations /app/migrations
COPY api /app/api

RUN uv sync --locked --no-dev

ENTRYPOINT ["sh", "start.sh"]
