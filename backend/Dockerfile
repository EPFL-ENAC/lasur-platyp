FROM python:3.11-alpine
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
ENV PYTHONPATH="$PYTHONPATH:/app"
ENV UV_PROJECT_ENVIRONMENT="/usr/local"
ENV UV_LINK_MODE=copy
ENV UV_NO_CACHE=1

WORKDIR /app

COPY uv.lock pyproject.toml /app/
# Build tools (git for the enacit4r sources, gcc for psycopg2) stay out of the image,
# and so do the base image's setuptools and wheel: each one is a CVE source.
RUN apk upgrade --no-cache \
  && apk add --no-cache libpq libstdc++ \
  && apk add --no-cache --virtual .build-deps git gcc musl-dev libpq-dev \
  && uv sync --locked --no-install-project --no-dev \
  && apk del .build-deps \
  && pip uninstall -y setuptools wheel

COPY alembic.ini start.sh README.md /app/
COPY migrations /app/migrations
COPY api /app/api
COPY scripts /app/scripts

RUN uv sync --locked --no-dev

ENTRYPOINT ["sh", "start.sh"]
