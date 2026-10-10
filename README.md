# Galene

A personal inventory and moving assistant: capture your belongings, review the inventory, and turn it into a practical moving plan.

The first implementation increment is a localhost foundation: a React preview, FastAPI service, SQLite migrations, an idle worker, and Nginx routing. Authentication, inventory, photo capture, and moving plans are still to come. No credentials or AI calls are needed for this increment.

## Run locally

Install Docker with Compose 2.24.4 or newer, GNU Make, and Python 3.12. Containers provide the application toolchains.

```sh
cp .env.example .env
export GALENE_UID=$(id -u) GALENE_GID=$(id -g)
install -d -m 700 data/db data/media
make dev
```

Open <http://localhost:8080>. `make stop` removes containers and retains `data/`. Set the UID/GID in `.env` to keep them across shells. For a custom `GALENE_DATA_DIR`, create its `db` and `media` directories with the same ownership first.

```sh
make check             # lint, formatting, types, Python tests, frontend build
make test-integration  # disposable Docker stack; no personal data or host ports
```

See [development and operations](docs/engineering/development.md) for commands, storage, migrations, and current limitations.

Start with the [design guide](docs/design/README.md), then read the [product scope](docs/design/01-product.md) and [decisions](docs/design/02-decisions.md). The [delivery plan](docs/design/08-delivery.md) divides implementation into a stack of reviewable PRs.

For work across sessions, use the repository skills `$galene-handoff` and `$galene-resume`. Their [session continuity guide](docs/engineering/session-continuity.md) describes local records, recovery, and native GitHub stack handling. Adding these skills does not create a handoff or start implementation.
