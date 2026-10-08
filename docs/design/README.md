# Galene design guide

Galene is a private web app for one person to catalog belongings and prepare for apartment moves. The prototype uses reviewed AI observations, persistent inventory, and explicit planning assumptions. Capturing a room should reduce typing without implying that the camera has found everything.

Design date: 2026-10-08. This is a proposed implementation baseline. Decisions made by the owner and defaults selected by the engineer are distinguished in the decision record.

| Document | What it settles |
| --- | --- |
| [Product and user experience](01-product.md) | First usable release, screens, useful follow-up features, acceptance criteria |
| [Decisions and assumptions](02-decisions.md) | Stack choices, alternatives, owner questions, scope boundaries |
| [Architecture](03-architecture.md) | Services, dependency direction, interfaces, background work |
| [Data and API contracts](04-data-and-api.md) | Inventory semantics, persistence, HTTP operations, review transactions |
| [AI capture and assistance](05-ai.md) | Image handling, uncertain observations, recommendations, limits and evaluation |
| [Moving plans and estimates](06-moving.md) | Decisions, packing, transparent time ranges and a worked example |
| [Security and operations](07-security-and-operations.md) | Firebase access, private media, Docker, host data, recovery |
| [Testing and delivery](08-delivery.md) | Small test suite, acceptance checks and implementation PR stack |

Read product and decisions first. Architecture and contracts guide implementation; AI and moving define behavior; security and delivery define the minimum bar for running it.

The prototype has one owner, one Linux host, one API process, and one worker. It has no automatic backups, public registration, autonomous disposal actions, marketplace integrations, or distributed infrastructure. Persistence across container recreation is required.

The first release covers photos. Short video is an explicitly scoped follow-up unless the owner chooses to bring it forward. Exact dependency versions and the AI model ID will be pinned during implementation after a small compatibility and quality check.
