# this Dockerfile should be built from the repo root
FROM python:3.13.1-slim-bookworm

ENV PYTHONUNBUFFERED=1
WORKDIR /workspace

# Place executables in the environment at the front of the path
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#using-the-environment
ENV PATH="/workspace/.venv/bin:$PATH"

# Install uv
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Compile bytecode
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
ENV UV_COMPILE_BYTECODE=1

# uv Cache
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_LINK_MODE=copy

# Install dependencies
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-workspace --package=farmbase

ENV PYTHONPATH=/app

COPY . /workspace
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --package=farmbase

CMD ["fastapi", "run", "--workers", "4", "/workspace/apps/farmbase/src/farmbase/main.py"]