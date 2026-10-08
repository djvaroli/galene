# Testing and delivery

Build in small vertical steps that leave a useful, testable application after each merge. The first usable release includes reviewed capture and moving assistance; video and backups follow later. This session delivers design documents only.

## Minimum test suite

| Layer | Tests worth keeping |
| --- | --- |
| Domain unit tests | Group splitting preserves quantities; unknown quantities remain unknown; disposition intent differs from actual removal; no packing double count; estimator worked example and missing-input behavior |
| Application unit tests | Review creates only selected items; attach-existing preserves confirmed values; a replay returns the same result; stale advice cannot overwrite newer decisions |
| AI adapter tests | Valid fixtures, refusal, incomplete output, bad item/media IDs, capped attempts, unavailable provider, and exhausted budget |
| Frontend tests | Edit/select/save review cards; show partial/failed upload progress; preserve unsaved edits on an API error; mark stale plans |
| Docker integration tests | Real SQLite, migrations, local media, HTTP API, worker and edge routing; Firebase emulator and fake provider at external boundaries |
| Browser smoke tests | Sign in, add manually, scan fixture images, review, ask a question, generate a plan, sign out |

Use pytest for Python, Vitest and Testing Library for the frontend, and a small Playwright smoke suite. Do not require a coverage percentage, snapshot every screen, or test library internals. Keep pure estimator tests independent of the database and provider SDKs.

Docker integration uses disposable test volumes and synthetic photos. The test runner starts the same API/worker images as deployment with explicit test configuration. Use the Firebase Auth emulator for token/UID integration and fixtures for verifier failures such as wrong issuer or expiry. A live manual check confirms real Firebase signature/revocation behavior and disabled signup; the emulator does not prove production identity configuration.

Use an injected fake provider to make job and failure tests deterministic, not paid model calls in CI. Configure it through test-only composition and assert that deployment mode rejects that configuration. Integration should still exercise the production job repository, HTTP schemas, owner checks, media paths, and transaction boundaries.

## High-value integration scenarios

1. Missing token and a valid token for another UID cannot read inventory, images, jobs, or plans.
2. Create a room and manual item; fetch them after recreating API and worker containers against the same test volume.
3. Upload a JPEG and HEIC fixture, normalize them, verify metadata removal and private retrieval, and reject a malformed or oversized upload.
4. Process a scan; only reviewed candidates become items. Replaying the review does not duplicate records; linking an existing object adds evidence only.
5. Stop a worker during a job; restart it and observe an interrupted result with an explicit retry, while queued jobs continue.
6. Generate a plan from mixed active/disposed/boxed/grouped inventory; verify totals and that a later edit marks it stale.
7. Run migrations from an empty database and the previous schema. Start with an incompatible revision and verify a clear startup refusal.
8. Request an unknown API route and an oversized upload through Nginx; verify correct status rather than frontend HTML or an unbounded transfer.

A single full browser happy path plus focused unit/integration checks is enough for the prototype. No load-testing platform or elaborate chaos suite.

## Development and CI commands

Implementation should provide simple documented commands such as `make dev`, `make test-unit`, `make test-integration`, `make test-e2e`, and `make check`. These are planned entry points, not commands available in this design-only repository.

`make check` runs formatting/linting, Python and TypeScript type checks, unit tests, generated OpenAPI/client drift checks, and a frontend build. Docker integration runs for changes to backend, infrastructure, contracts, or relevant tests. Use a small GitHub Actions workflow; no mandatory live-provider credentials in CI.

## Implementation PR stack

Each row is a PR branch based on the preceding branch until that predecessor lands. Register the branches as a native GitHub stack through the official `gh stack` extension. Each PR description states dependencies, the user-visible outcome, and checks actually run. Update docs when implementation changes a decision.

| Order and branch | Scope and deliverable | Exit check |
| --- | --- | --- |
| 1 `feat/foundation` | Repo tooling, React/FastAPI shells, edge and frontend services, worker entrypoint, host mounts, initial schema/migration plumbing, health checks, test Compose profile | Compose starts; edge serves UI and API; migration and test commands work |
| 2 `feat/private-inventory` | Firebase access, owner checks, rooms and manual items, search/filter, lifecycle, group splitting, generated client | Owner-only CRUD works through UI; persistence/restart and unauthorized access checks pass |
| 3 `feat/photo-capture` | Private uploads, HEIC normalization, media lifecycle, durable jobs, scan screens and progress | Phone photos prepare and survive refresh; upload limits and worker interruption tested |
| 4 `feat/reviewed-extraction` | Vision adapter, structured candidates, correction and duplicate review, atomic save, budgets and usage | One room reaches saved inventory; retry/review cannot duplicate items; small paid evaluation recorded separately |
| 5 `feat/moving-plans` | Move settings, boxes, packing/lifecycle flags, deterministic estimates, saved snapshots, stale detection, basic checklist | Complete moving plan available without AI; worked example and no-double-count tests pass |
| 6 `feat/inventory-assistant` | Scoped questions, disposition suggestions, explicit apply, plan commentary and provider degradation | Answers link saved items; stale recommendations rejected; no automatic item changes |
| 7 `feat/deployment` | HTTPS/cert renewal profile, final headers and limits, secret setup guide, runbook, browser smoke path, release acceptance | Private deployment walkthrough succeeds with real Firebase; container recreation retains data |

Implement owner checks and private-media controls in the PR that introduces the feature; PR 7 verifies deployment and integrates the remaining infrastructure. It must not be the first security pass.

After the first usable release, `feat/video-capture` branches from the merged baseline and adds only clip ingestion, bounded frame extraction, timestamps and frame selection. `feat/backups` later adds scheduled database/media backups and a tested restore procedure. Neither is required to call this prototype usable.

## GitHub stack mechanics

Use GitHub's native stacked pull requests feature. PR 1 targets `main`, PR 2 targets branch 1, and so on; the stack is registered as one unit in GitHub. Keep histories linear and create draft PRs for design review.

For the existing design branches, use the official CLI extension to adopt them from bottom to top, then submit. `--auto` creates draft PRs; set the prepared titles and descriptions after creation. [GitHub stack adoption](https://docs.github.com/en/pull-requests/reference/use-other-tools-with-stacked-pull-requests)

```sh
gh extension install github/gh-stack
gh stack init --base main docs/product-design docs/application-design docs/moving-and-delivery
gh stack submit --auto
gh stack view
```

After editing a lower layer, use `gh stack rebase` and `gh stack push` to carry its changes upward. Merge through GitHub's native stack controls, from the bottom or as a contiguous group including the bottom. GitHub rebases the remaining stack and retargets its next PR after a merge; use `gh stack sync` to refresh local state. Do not manually merge an upper PR into its predecessor's feature branch. No design PR is merged during this session. [GitHub stack management](https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/managing-stacked-pull-requests), [merging stacks](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-stacked-pull-requests)

Initialize the empty remote with a minimal `main` baseline, then publish three documentation PRs: product and decisions, architecture and contracts including AI, and moving/security/delivery. Keep documentation indexes valid at each layer. The owner has approved publication to public `djvaroli/galene` using the native stack feature.

## First release acceptance

Run the product acceptance journey on the owner's phone and desktop, using two rooms and a sample move. Verify real authentication, direct signup rejection, private photo access, reviewed extraction, persistent data, bounded AI work, and a plan whose assumptions can be edited. Record actual review effort and observed AI cost before choosing whether video or inventory refinement delivers more value next.

The prototype is ready when that journey works with understandable failure states and the listed targeted tests pass. It does not require perfect object recall, highly accurate moving predictions, multiple deployment hosts, or an extensive test suite.
