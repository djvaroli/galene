FROM ghcr.io/astral-sh/uv:0.11.16@sha256:440fd6477af86a2f1b38080c539f1672cd22acb1b1a47e321dba5158ab08864d AS uv
FROM python:3.12-slim-bookworm@sha256:34386ef0cb081344d7ec1c103ba398e6e9f64e9ab3a1509accc92a4e24a07258 AS base
COPY --from=uv /uv /usr/local/bin/uv
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_NO_CACHE=1 PATH="/app/.venv/bin:$PATH"
COPY pyproject.toml uv.lock ./
RUN mkdir -p /data/db /data/media && chown -R 1000:1000 /data
COPY app ./app
COPY migrations ./migrations

FROM base AS check
RUN uv sync --locked
COPY tests ./tests
ENV RUFF_CACHE_DIR=/tmp/ruff-cache MYPY_CACHE_DIR=/tmp/mypy-cache PYTEST_ADDOPTS="-o cache_dir=/tmp/pytest-cache"
USER 1000:1000
CMD ["pytest"]

FROM base AS runtime
RUN uv sync --locked --no-dev
USER 1000:1000
CMD ["uvicorn", "app.bootstrap:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--no-proxy-headers"]
