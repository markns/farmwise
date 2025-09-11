# Repository Guidelines

## Project Structure & Module Organization
- Python workspace managed by `uv`: `apps/*` (services) and `libs/*` (shared libs).
- Key apps: `apps/farmbase/` (FastAPI), `apps/farmwise/` (AI/WhatsApp), `apps/farmbase-workflows/` (Temporal).
- Frontend: `frontend/` (React + Vite). Docs/assets in `docs/`, infra in `dev/` and `docker-compose.yml`.
- Python sources live under `src/<package>/`; tests typically in `<module>/test/`.

## Build, Test, and Development Commands
- Install deps: `uv sync` (Python), `npm install` in `frontend/` (web).
- Quality suite: `uv run poe all` (format, lint, type-check, tests).
- Individually: `uv run poe fmt` • `uv run poe lint` • `uv run poe check` • `uv run poe test`.
- DB up (dev): `docker-compose up db`.
- Migrations (farmbase):
  - `cd apps/farmbase && uv run alembic revision --autogenerate -m "<msg>"`
  - `uv run alembic upgrade head`.
- Run services:
  - API: `cd apps/farmbase && uv run fastapi dev src/farmbase/main.py`
  - AI service: `cd apps/farmwise && uv run python src/farmwise/main.py`
  - Frontend: `cd frontend && npm run dev` (build: `npm run build`).

## Coding Style & Naming Conventions
- Python: 4-space indent, max line length 120 (Ruff). Type hints required for public interfaces.
- Naming: packages/modules `snake_case`, classes `PascalCase`, functions/vars `snake_case`, constants `UPPER_SNAKE_CASE`.
- Lint/format: Ruff (`uv run poe lint` / `fmt`); type-check: Based Pyright (`uv run poe check`).
- Frontend: ESLint/TS strict; run `npm run lint` and `npm run type-check`.
- Imports: first-party grouped last (Ruff isort; known first-party configured).

## Testing Guidelines
- Python: Pytest (+ asyncio); place tests in `apps/*/test/` or `libs/*/test/` with `test_*.py`.
- Run all: `uv run poe test`. Targeted: `uv run pytest apps/farmbase -q`.
- Prefer fast, isolated tests; add fixtures and async tests where applicable.

## Commit & Pull Request Guidelines
- Commits: short imperative subject; scope prefix optional (e.g., `farmbase: add org middleware`).
- PRs: clear description, linked issues, reproduction/verification steps. Include screenshots for UI changes.
- Before opening: `uv run poe all` and (if frontend changed) `npm run lint && npm run type-check`.

## Security & Configuration Tips
- Do not commit secrets. Use `.env` locally; Docker reads from it. Required keys include `OPENAI_API_KEY` and DB vars.
- Rotate keys if exposed; avoid embedding tokens in code or tests.
- Large data and generated clients live under `libs/`; regenerate via `uv run poe client-gen`.
