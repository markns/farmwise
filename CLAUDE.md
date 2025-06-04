# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Structure

This is a multi-app workspace built with Python and uv for dependency management. The project consists of:

**Core Applications:**
- `apps/farmbase/` - Main FastAPI backend application with multi-tenant architecture
- `apps/farmwise/` - AI agent service for agricultural guidance with integrated WhatsApp support

**Libraries:**
- `libs/farmbase-client/` - Auto-generated API client for farmbase
- `libs/farmbase-agent-toolkit/` - Toolkit for AI agents to interact with farmbase
- `libs/farmwise-client/` - Client library for farmwise service
- `libs/farmwise-schema/` - Shared schemas and models (deprecated - merged into farmwise app)

## Development Commands

**Setup:**
```bash
# Environment setup (requires at least one LLM API key)
echo 'OPENAI_API_KEY=your_openai_api_key' >> .env
```

**Core Development Tasks:**
```bash
# Format code
uv run poe fmt

# Lint with auto-fix
uv run poe lint

# Type checking
uv run poe check

# Run tests
uv run poe test

# Run all checks (format, lint, typecheck, test)
uv run poe all

# Generate farmbase API client
uv run poe client-gen
```

**Database Operations (Farmbase):**
```bash
# Create migration after model changes
uv run alembic revision --autogenerate -m "Description of changes"

# Apply migrations
uv run alembic upgrade head
```

**Services:**
```bash
# Start database and adminer
docker-compose up db adminer

# Run farmbase locally
cd apps/farmbase && uv run fastapi dev src/farmbase/main.py

# Run farmwise agent service with WhatsApp integration
cd apps/farmwise && uv run python src/farmwise/main.py
```

## Architecture

**Multi-Tenant Database Design:**
- Farmbase uses PostgreSQL with schema-based multi-tenancy
- Each organization gets its own schema: `farmbase_organization_{slug}`
- Database sessions are scoped per-request with automatic schema switching
- Middleware handles organization resolution from URL paths

**API Structure:**
- Main API mounted at `/api/v1/`
- Organization-specific endpoints: `/api/v1/{organization}/...`
- Frontend SPA served from root `/`
- API documentation at `/api/v1/docs`

**Plugin System:**
- Farmbase supports plugins via entry points
- Auth providers are pluggable (basic auth, header auth)
- Plugin events can be registered to extend API functionality

**AI Agent Framework:**
- Farmwise provides specialized agricultural AI agents with WhatsApp integration
- Agents handle: crop pathogen diagnosis, variety selection, field registration, onboarding
- Integration with farmbase via the agent toolkit
- Support for triage and handoff between agents
- WhatsApp handlers directly invoke the FarmwiseService class methods

**Data Sources:**
- GAEZ (Global Agro-ecological Zones) climate and soil data
- KALRO crop variety databases
- Weather data integration via Temporal workflows
- Geospatial data processing with GeoPandas and rioxarray

## Code Conventions

- **Python version:** <=3.13
- **Linting:** Ruff with line length 120
- **Type checking:** Pyright
- **Import sorting:** Ruff isort with farmwise as first-party
- **Database:** SQLModel/SQLAlchemy with async sessions
- **API:** FastAPI with automatic OpenAPI generation
- **Frontend:** Vue.js SPA with Vite build system

## Environment Variables

Key environment variables for development:
- `OPENAI_API_KEY` - Required for AI functionality
- `DATABASE_*` - PostgreSQL connection details
- `SECRET_KEY` - JWT token signing
- `FIRST_SUPERUSER*` - Initial admin account
- `WHATSAPP_TOKEN` - WhatsApp Business API token
- `WHATSAPP_PHONE_ID` - WhatsApp phone number ID
- `WHATSAPP_CALLBACK_URL` - Webhook callback URL for WhatsApp
- `DOWNLOAD_DIR` - Directory for media file downloads
- `MEDIA_SERVER` - Media server URL for file serving