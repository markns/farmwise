# This Dockerfile should be built from the repo root
FROM python:3.12-slim

# Install uv, the fast Python package installer
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# --- Environment Configuration ---
ENV PYTHONUNBUFFERED=1
WORKDIR /workspace

# Place executables from the virtual environment at the front of the PATH
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#using-the-environment
ENV PATH="/workspace/.venv/bin:$PATH"

# Compile bytecode for better performance
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
ENV UV_COMPILE_BYTECODE=1

# Configure uv to use hard links or copies instead of symlinks inside the container
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_LINK_MODE=copy

# --- System Dependency Installation ---
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gdal-bin \
    libgdal-dev \
    git \
    g++ \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# --- GDAL Configuration ---
# The `python:3.12-slim` image is based on Debian 12 (Bookworm), which provides GDAL 3.6.2.
# This environment variable must match the system's GDAL version for the `rasterio`
# Python package to compile and install correctly.
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV GDAL_VERSION=3.6.2

# --- Python Dependency Installation ---
# Copy the application source code into the workspace first
COPY . /workspace

# Install dependencies and local packages
# Since farmbase-workflows is a local package, we need the source code available
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --compile-bytecode --frozen --package=farmbase-workflows

# --- Application Entrypoint ---
# Run the FastAPI application using 2 workers.
CMD ["python", "apps/farmbase-workflows/src/farmbase_workflows/main.py"]
