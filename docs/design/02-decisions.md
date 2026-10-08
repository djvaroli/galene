# Decisions and assumptions

This baseline favors a useful personal app with clear responsibilities and a small operating footprint. Owner requirements are settled; the remaining choices below are engineering defaults that can change during review.

## Owner requirements

- Design documents in this session; implementation in the next.
- Multiple focused documents and a stack of reviewable PRs ultimately merged into `main`.
- Frontend, backend, and Nginx in Docker, with simple persistent storage on the host.
- One user, Firebase authentication, and no signup.
- Interfaces at useful boundaries, isolated concerns, basic unit tests, and small Docker integration tests.
- No automatic backups yet. Avoid enterprise infrastructure and exhaustive race-condition engineering.

## Proposed defaults

| Decision | Default and reason | Alternative or revisit trigger |
| --- | --- | --- |
| Capture scope | Multiple photos first; easier to guide, inspect and evaluate | Add video once photo review is useful, or bring forward at owner's request |
| Storage | SQLite file plus media directory on local host disk | Redis if the owner prefers it; PostgreSQL when multiple hosts or sustained concurrent writes are needed |
| Frontend | React, TypeScript, Vite, React Router, TanStack Query, ordinary CSS | No SSR requirement or separate frontend application server logic |
| Backend | Python, FastAPI, Pydantic, SQLAlchemy and Alembic | Two languages are justified by a conventional browser frontend and Python image/AI tooling |
| Background work | One worker from the backend image, polling a SQLite jobs table | Redis and a queue framework only when real scheduling or concurrency needs justify them |
| AI | OpenAI Responses API behind narrow provider interfaces | Different managed provider or local inference through a replacement adapter |
| AI model | Configured model IDs; select and pin after testing a small room fixture set | Do not choose a model based only on its name or make unverified cost claims |
| Authentication | One pre-created email/password Firebase user, fixed UID allowlist, provider signup disabled | Google sign-in later if desired, retaining the UID authorization check |
| Deployment | Docker Compose on one Linux host; same-origin HTTPS when accessed beyond localhost | Public domain versus private network remains an owner choice |
| Client updates | Poll background jobs while visible | WebSockets or server-sent events only if polling becomes inadequate |
| Planning | Deterministic arithmetic, AI explanations and suggestions | No autonomous agent framework, vector database, or generated code execution |

## Why SQLite instead of Redis

Items relate to rooms, images, boxes, and move snapshots. SQLite gives us transactions and referential checks in a local file, without a database service to administer. JSON columns can hold evolving model observations and plan snapshots while core inventory fields stay explicit.

Use small Alembic migrations rather than inventing an unversioned data format. Redis would not remove schema evolution: renamed fields, new defaults, and changed relationships still need compatible readers or conversion. Durable Redis also requires choosing and operating a persistence policy. [Redis persistence](https://redis.io/docs/latest/management/persistence/)

Mount the database directory into the API and worker on the same Linux host. Use WAL, short write transactions, and a busy timeout. WAL supports readers alongside a writer but still permits only one writer at a time and requires local shared storage. [SQLite WAL](https://www.sqlite.org/wal.html)

If Redis is chosen instead, revise the persistence design before implementation: enable AOF, disable eviction for application records, keep media on disk, define key ownership and indexes, and version stored documents. Do not simply substitute Redis for SQL queries.

## Major choices raised with the owner

| Question | Current status | Working assumption until answered |
| --- | --- | --- |
| SQLite versus Redis | Asked; awaiting response | SQLite remains a proposed default, not an owner-approved decision |
| Photos first versus immediate video | Asked; awaiting response | Photos first; video has a defined follow-up scope |
| Hosting environment | Asked; awaiting response | One Linux host; localhost development and HTTPS deployment profiles |
| PRs this session or next | Owner approved publication to public `djvaroli/galene` and requested GitHub's native stacks feature | Three draft design PRs in one native GitHub stack rooted at `main`, plus the documented implementation stack |

Managed cloud AI is an explicit assumption: analyzed room images and selected inventory details leave the host. The capture screen will name the provider before the first analysis. Nothing is sent during this design session. A requirement to keep all inference local would materially change model selection, host sizing, and quality expectations.

Initialize the empty remote's `main` with a minimal README and ignore rules. Publish the three design branches through the official `gh stack` extension so GitHub records their stack membership. All substantive design changes remain on draft PR branches for review; no application implementation or deployment occurs in this session.

## Changes that need another product discussion

Revisit the design before adding multiple users, external sharing, automatic marketplace actions, always-on camera capture, offline editing, or multiple application hosts. Routine field additions, presentation choices, and implementation details can be decided in the PR that introduces them.
