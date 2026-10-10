# Development and foundation operations

This increment supplies the service boundaries and repeatable tooling for Galene. The browser renders an early preview. `GET /api/v1/info` returns public service metadata. There are no inventory or media HTTP endpoints, identity bypasses, model calls, or job handlers. The worker checks database compatibility, holds a single-worker lock, and updates an internal heartbeat while idle.

## Toolchains

The Dockerfiles pin Python 3.12, Node 24, the unprivileged Nginx image, and uv 0.11.16 by immutable multi-platform digest. Python's resolved runtime is 3.12.15. Python 3.12 receives security updates through October 2028 ([release schedule](https://peps.python.org/pep-0693/)); Node 24 is an LTS line ([Node release schedule](https://github.com/nodejs/Release)). The chosen Vite release is built and type checked with the pinned Node image. Update image digests and lockfiles together in a focused PR.

`backend/uv.lock` and `frontend/package-lock.json` fix transitive dependencies. Image builds use `uv sync --locked` and `npm ci`; they do not resolve a new dependency set. Backend packages currently include FastAPI 0.143.0, SQLAlchemy 2.1.4, Alembic 1.20.0, and Pydantic 2.14.0. Frontend packages include React 19.3.0, TypeScript 7.0.2, and Vite 8.3.4.

Run commands from the repository root. Required host tools are Docker Engine, Compose >=2.24.4 (for test mount replacement), GNU Make, and Python 3.12. No host Node installation is necessary. For direct Python editing, `cd backend && uv sync --locked` creates a local virtual environment; use its Ruff, mypy, and pytest binaries. Formatting is `uv run ruff format .` in `backend/` and `npm run format` in `frontend/` with Node 24.

## Commands

| Command | Behavior |
| --- | --- |
| `make dev` | Build images, apply migrations, and wait for the localhost stack to be healthy |
| `make stop` | Remove application containers and network; preserve host data |
| `make logs` | Follow bounded container logs |
| `make migrate` | Build and run the one-shot migration service |
| `make check` | Python lint/format/type checks and unit tests; frontend format/type checks and build |
| `make test-unit` | Python foundation tests in the pinned toolchain |
| `make test-integration` | Build and test real services with unique disposable volumes, then remove them |

`make dev` serves the built frontend. After edits, rerun it to rebuild affected images. A Vite hot-reload Compose override can be added when interactive inventory development needs it. React Router, query caching, generated API client/drift checks, frontend interaction tests, and browser E2E commands arrive with the first feature that uses them; they are not implemented by this shell.

## First setup and local storage

Follow the root README to create `.env` and `data/db`, `data/media`. Both directories must be writable by `GALENE_UID:GALENE_GID` (default 1000:1000). Compose refuses to silently create missing bind directories as root. Keep the directories on a local Linux filesystem, not NFS. The whole database directory is mounted so SQLite's WAL and shared-memory files stay together.

The edge listens on `127.0.0.1:8080`; only that port is published. `GALENE_PORT` changes the local port. API, frontend and worker remain internal. All long-running services have health checks, read-only image filesystems, limited temporary storage, dropped capabilities, and rotated logs. API and worker run under the configured numeric UID; Nginx and the frontend use their image's non-root user. No private storage is mounted into either web server.

SQLite uses WAL, foreign keys, a five-second busy timeout, and FULL synchronous writes. The initial migration creates Alembic's revision record only; domain tables come with their features. Restart and container replacement preserve data, but host storage is not a backup. Automatic backups remain out of scope.

## Updating and restarting

For a local code update, stop API and worker before applying an incompatible migration: `make stop`, then `make dev`. The migration container runs successfully before API and worker start. Both entrypoints independently verify the current revision; Docker daemon restarts cannot bypass that check. A mismatched or missing schema stops startup with a migration instruction.

For a host reboot, start Docker and verify `docker compose ps` and `make logs`. Long-running services have `unless-stopped` restart policies. If services were deliberately stopped, `make dev` starts them again. The edge resolves Docker service names periodically, so replacing an API/frontend container does not require manually restarting Nginx.

Do not edit or delete an existing revision after it has been used. Add an Alembic revision under `backend/migrations/versions/`, chain its `down_revision`, and test upgrading a disposable database from the previous revision. There is no automated downgrade. If a migration fails, stop dependent services, inspect logs, and fix the failure before retrying `make migrate`. Never erase `data/` to resolve a version mismatch. Confirm a rollback's schema compatibility before using an older application image.

## Test boundaries

Unit tests cover repeatable initial migration, SQLite settings, schema refusal, readiness degradation, JSON API errors, and rejecting production mode before authentication exists. Docker integration starts the same runtime images as local development. It writes synthetic database/media markers, recreates API and worker, checks persistence through the real mounted volumes, verifies HTTP routing and the 21 MiB edge cap, refuses a second worker, and tests both entrypoints against a future schema. Every expected failure has a bounded timeout and checks the actual failure reason.

The integration runner uses a unique Compose project/image tag, ignores the developer `.env`, replaces bind mounts with named volumes, and removes published ports. Its `finally` block removes only that project's containers, network, and test volumes. An interrupted/killed runner may require `docker compose -p <printed-test-project> -f compose.yaml -f compose.test.yaml down --volumes`; verify the test project name before cleanup. Test images remain cached for subsequent runs.

The GitHub Actions workflow runs `make check` and `make test-integration` without secrets. No provider, Firebase, personal photo, or production database participates. There is no previous application schema yet; migration from previous revisions will be tested when a second revision is introduced.

## Current exposure boundary

This is a localhost development preview. `GALENE_APP_ENV` accepts `development` and `test` only; `production` fails validation. Owner authentication and protected resources belong to the next PR. Do not expose this foundation beyond localhost. HTTPS, Firebase provisioning, credentials rotation/revocation, and private media recovery instructions will be added when those features exist.

Health routes and OpenAPI are internal; the edge returns 404 for them. Unknown API routes return JSON errors, never frontend HTML. Uvicorn ignores forwarded headers for now; proxy trust and the CSP will be revisited alongside authenticated deployment. The edge currently adds a restrictive same-origin CSP, frame protection, content-type protection, request timeouts, and the upload-size cap. These settings are not a claim that Firebase or uploads have been implemented.
