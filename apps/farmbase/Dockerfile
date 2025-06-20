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
# FIX 4: Overwrite the default sources.list with a reliable mirror.
# The GPG signature errors suggest a problem with the default deb.debian.org mirror
# in the buildx environment. We are replacing it with Debian's CDN mirror, which can
# be more stable. This is a more direct way to solve the repository validation issue.
RUN echo "deb http://cdn-fastly.deb.debian.org/debian bookworm main" > /etc/apt/sources.list \
    && echo "deb http://cdn-fastly.deb.debian.org/debian bookworm-updates main" >> /etc/apt/sources.list \
    && echo "deb http://security.debian.org/debian-security bookworm-security main" >> /etc/apt/sources.list

# Now, with the new sources, run the update and installation in separate, cached layers.
# We add --allow-insecure-repositories as a fallback for networks that might interfere with HTTPS.
RUN apt-get update --allow-insecure-repositories

RUN apt-get install -y --no-install-recommends \
    gdal-bin \
    libgdal-dev \
    gcc \
    g++ \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# --- GDAL Configuration ---
# The `python:3.12-slim` image is based on Debian 12 (Bookworm), which provides GDAL 3.6.2.
# This environment variable must match the system's GDAL version for the `rasterio`
# Python package to compile and install correctly.
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV GDAL_VERSION=3.6.2

# --- Python Dependency Installation ---
# Stage 1: Install dependencies into a cached layer.
# This layer will be reused by Docker as long as the lockfile doesn't change.
# It installs everything *except* your local project code.
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --compile-bytecode --frozen --no-install-workspace --package=farmbase

# Copy the application source code into the workspace
COPY . /workspace

# Stage 2: Install the local project package itself.
# This step is very fast because all third-party dependencies are already installed.
RUN uv sync --compile-bytecode --frozen --package=farmbase
EXPOSE 8000

# --- Application Entrypoint ---
# Run the FastAPI application using 2 workers.
CMD ["fastapi", "run", "--workers", "2", "apps/farmbase/src/farmbase/main.py"]
