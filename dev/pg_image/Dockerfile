# Use the official PostgreSQL 17 image as a base
FROM postgres:17

# Install PostGIS and pgvector extensions
# Pinning versions (e.g., postgresql-17-postgis-3=3.4.*) is recommended for production
# to ensure reproducible builds.
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-17-postgis-3 \
    postgresql-17-postgis-3-scripts \
    postgresql-17-pgvector \
    # Clean up the apt cache to reduce image size
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set default environment variables for local development.
# WARNING: For production, supply these at runtime via a secure mechanism
# (e.g., Docker secrets, environment files) instead of hardcoding them here.
ENV POSTGRES_DB=postgres
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres

# Copy the database initialization script to the entrypoint directory.
# This script will be executed automatically when the container starts for the first time.
COPY init-db.sh /docker-entrypoint-initdb.d/init-db.sh

# Make the initialization script executable.
RUN chmod +x /docker-entrypoint-initdb.d/init-db.sh
