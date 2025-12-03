# FarmWise Project Context

## Project Overview
FarmWise is an agronomic advisor and farm management system designed to empower African farmers. 
It leverages modern technology (AI, Geospatial data, WhatsApp) to provide personalized agricultural advice, weather forecasts, and market insights.

**Key Technologies:**
*   **Backend:** Python (FastAPI, SQLModel, SQLAlchemy), Temporal (Workflows).
*   **Frontend:** React, TypeScript, Vite.
*   **Database:** PostgreSQL with PostGIS & pgvector.
*   **AI:** OpenAI APIs, Custom Agents.
*   **Package Management:** `uv` (Python).

## Architecture & Directory Structure
This project is a monorepo managed by `uv`.

*   `apps/`
    *   `farmbase/`: Core FastAPI backend service (Multi-tenant architecture).
    *   `farmwise/`: AI agent service with WhatsApp integration.
    *   `farmbase-workflows/`: Temporal workflow engine for background tasks.
*   `frontend/`: React web application (Vite).
*   `libs/`: Shared libraries (e.g., `farmbase-client`, `isdasoil-api-client`).
*   `website/`: Public-facing website (Astro).
*   `dev/`: Development resources (notebooks, scripts, docker images).

## Development Workflow

### Prerequisites
*   Python ≤ 3.13
*   Node.js
*   PostgreSQL + PostGIS (usually run via Docker)
*   `uv` (for Python dependency management)

### Setup & Installation
1.  **Install Dependencies:**
    ```bash
    uv sync
    ```
2.  **Database:**
    ```bash
    docker-compose up db
    ```
3.  **Migrations:**
    ```bash
    cd apps/farmbase
    uv run alembic upgrade head
    ```

### Running Services
*   **Backend (FarmBase):**
    ```bash
    cd apps/farmbase && uv run fastapi dev src/farmbase/main.py
    ```
*   **AI Agent (FarmWise):**
    ```bash
    cd apps/farmwise && uv run python src/farmwise/main.py
    ```
*   **Frontend:**
    ```bash
    cd frontend && npm install && npm run dev
    ```

### Code Quality & Testing
The project uses `poethepoet` for task management, configured in the root `pyproject.toml`.

*   **Format Code:** `uv run poe fmt` (uses Ruff)
*   **Lint:** `uv run poe lint` (uses Ruff)
*   **Type Check:** `uv run poe check` (uses BasedPyright)
*   **Test:** `uv run poe test` (uses Pytest)
*   **Run All Checks:** `uv run poe all`

### Database Changes
*   **Generate Migration:**
    ```bash
    cd apps/farmbase
    uv run alembic revision --autogenerate -m "Description"
    ```
*   **Apply Migration:** `uv run alembic upgrade head`

### API Client Generation
To regenerate the Python client for the internal API:
```bash
uv run poe client-gen
```

## Conventions
*   **Python:** Follows `ruff` and `basedpyright` rules. 
*   **Imports:** Sorted by `ruff` (isort). First-party imports are grouped last.
*   **Structure:** Code is organized into `apps` and `libs`. 
*   **Environment:** Use `.env` files for configuration.
