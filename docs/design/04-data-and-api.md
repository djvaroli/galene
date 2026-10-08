# Data and API contracts

Confirmed inventory is the source of truth. Media observations, recommendations, and plans are supporting records with their own state and provenance. The application must preserve this distinction across database transactions and HTTP requests.

## Core records

All application IDs are server-generated UUIDs. Timestamps use UTC ISO 8601 at the API boundary. The verified Firebase UID supplies ownership; the client never selects an owner. Store foreign keys and enable SQLite foreign-key enforcement on every connection.

| Record | Principal fields and purpose |
| --- | --- |
| `profile` | Firebase UID, display name, preferred units, `inventory_revision`; created only for the configured owner |
| `room` | Owner, name, coverage notes, `reviewed_at` |
| `item` | Owner, room, name, category, quantity, quantity basis, location note, owner notes, confirmed disposition, lifecycle, packing class, fragile, essential, disassembly flag, move preparation state, optional box, timestamps |
| `box` | Owner, label, destination room label, packing status; belongs to one move |
| `media` | Owner, scan, internal storage keys, SHA-256, detected format, size, dimensions, preparation state, source kind |
| `scan` | Owner, room, state, current analysis job, created date |
| `candidate` | Scan, observation payload, evidence media IDs, review state, resolved item ID, review decision |
| `item_evidence` | Item and media link; unique pair |
| `job` | Owner, kind, state, input/result JSON, attempts, request key/hash, safe error, timing, provider usage |
| `move` | Owner, date, origin/destination access, helpers, travel and trip assumptions, preferences, manual checklist JSON, settings revision |
| `plan` | Move, inventory and settings revisions, immutable snapshot, estimator version, assumptions, calculated totals, AI notes, creation date |

Schema changes use small Alembic revisions. Version model observations and plan JSON separately through `schema_version`. Schema-free blobs are limited to variable observations, job payloads, and immutable snapshots; fields needed for inventory filtering remain columns.

Each top-level record is owner-scoped. Use composite owner/reference constraints where practical; application validation checks every related ID belongs to that owner and, where relevant, the same scan or move. Index room and item ownership, active inventory filters, pending jobs, and scan candidates. Simple text search is sufficient for one apartment; postpone full-text search until needed.

## Item semantics

- `quantity` is a positive integer or null. `quantity_basis` is `exact`, `approximate`, or `unknown`; null is required for unknown. A user may confirm an approximate grouped quantity.
- `category` is a small enum: furniture, electronics, kitchen, clothing, books, decor, tools, other. Name and notes remain free text.
- `disposition` is `undecided`, `keep`, `sell`, `donate`, or `discard`. It records intent.
- `lifecycle` is `active`, `sold`, `donated`, `discarded`, or `archived`. It records what happened. Only active records count toward transport.
- `packing_class` is `boxable`, `bulky`, or `unknown`. Suggested class values become canonical only through review.
- `handling_units` is an optional positive count for bulky transport units; `packing_box_override` is an optional nonnegative box-equivalent estimate for a group. Both are owner-confirmed planning inputs.
- `prepared_for_move_id` and `disassembled_for_move_id` are nullable move references. They record completed preparation and disassembly without carrying that completion into the next move.
- `source` is `manual` or `scan_review`; `last_confirmed_at` records the owner's last confirmation. Model identifiers belong to observation/job provenance, not inventory truth.

A group must share room, disposition, lifecycle, and packing destination. Split it into separate records before donating half or packing it into multiple boxes. A small transactional split operation preserves the original total quantity when known and copies evidence links. Furniture such as one desk stays separate from its contents.

Assigning an item to a box requires an active item and a box in the active move. A grouped entry fits wholly into one box; split it first if needed. Essentials can be boxed but are flagged for late packing. Clear box assignments when starting a new move; retain old contents in the old plan snapshot.

Items may be archived and restored without erasing history. Actual removal from the home uses the lifecycle operation. Hard deletion is a separate explicit action that also removes evidence links; old plan snapshots may still contain historical item descriptions, which the UI identifies as historical.

## State transitions

| Entity | Transitions |
| --- | --- |
| Media | `pending -> ready` or `failed`; explicit retry creates a new preparation job |
| Job | `queued -> running -> succeeded / failed / interrupted`; retry creates a new job linked to the old one |
| Scan | `draft -> processing -> review_ready -> complete`; processing failure or interruption yields `failed`, explicit retry returns to processing |
| Candidate | `pending -> accepted / dismissed`; accepted stores its item and decision |
| Box | `open -> packed -> unpacked`; owner may reopen |

The scan can only start when all included media are ready and at least one remains. Freeze its media list on analysis. To add more photos after analysis, create another scan. No automatic inventory deletion follows from an item being absent in a later scan.

Review actions are `create`, `attach_existing`, or `dismiss`. `attach_existing` adds evidence only; existing name, quantity, and decisions stay intact. Editing the existing record is a separate visible action. The same action replay returns its saved outcome; trying to resolve an already-resolved candidate differently returns `409`.

## HTTP conventions

Use `/api/v1`, JSON, and `Authorization: Bearer <Firebase ID token>` on every protected route. The media upload endpoint alone uses multipart form data. List responses are `{items, next_cursor}` with opaque cursors, default limit 50 and maximum 100. Return `201` for created resources, `202` plus job reference for queued work, and `204` for successful deletion.

Errors use `{error: {code, message, details}, request_id}`. Expected codes include `unauthenticated` (401), `forbidden` (403), `not_found` (404), `conflict` (409), `upload_too_large` (413), `unsupported_media` (415), `validation_error` (422), `rate_limited` (429), and `temporarily_unavailable` (503). Do not include tokens, raw prompts, server paths, or provider tracebacks. The client handles a proxy-generated 413 even if its body is not JSON.

| Route | Contract |
| --- | --- |
| `GET /me`, `PATCH /me` | Read/update allowed display preferences; never UID or access policy |
| `GET, POST /rooms`; `PATCH, DELETE /rooms/{id}` | Room management; deleting a populated room returns conflict until items are moved |
| `GET, POST /items`; `GET, PATCH, DELETE /items/{id}` | Search/filter inventory; edit canonical fields; explicit hard delete |
| `POST /items/{id}/split` | Split a group using quantity and proposed new fields in one transaction; unknown totals require owner-supplied quantities for both resulting groups |
| `POST /items/{id}/lifecycle` | Record an actual outcome or restore; clear incompatible box assignments |
| `POST /scans`; `GET /scans`; `GET /scans/{id}` | Create and resume room scans; detail includes media and candidates |
| `POST /scans/{id}/media` | One file per request; return media ID and preparation job |
| `GET /media/{id}/content`, `GET /media/{id}/thumbnail` | Authenticated normalized image retrieval; pending gives 409 |
| `DELETE /media/{id}` | Remove media and evidence references; refuse while an active job uses it |
| `POST /scans/{id}/analyze` | Freeze ready media and queue analysis; repeat while active returns the existing job |
| `POST /scans/{id}/review` | Atomic list of candidate decisions with corrected item fields |
| `GET /jobs/{id}`; `POST /jobs/{id}/retry` | Inspect work/result; retry eligible failed/interrupted work explicitly |
| `GET, POST /moves`; `GET, PATCH /moves/{id}` | Move settings and active move selection; only one active move |
| `GET, POST /moves/{id}/boxes`; `PATCH, DELETE /boxes/{id}` | Labeled boxes; deletion requires empty contents |
| `POST /moves/{id}/plans`; `GET /moves/{id}/plans`; `GET /plans/{id}` | Queue snapshot-based plan with optional `include_ai_notes` (default false); read versions and freshness |
| `POST /advice/dispositions` | Queue suggestions for up to 100 selected active item IDs and explicit preferences |
| `POST /advice/questions` | Queue question with room/item scope and optional short conversation context |
| `POST /advice/{job_id}/apply` | Apply selected disposition suggestions after checking snapshot freshness |

Health routes are internal operations endpoints, not part of the inventory API. FastAPI emits OpenAPI; generate frontend types in CI and fail on an uncommitted contract change. API routes and schemas, not separately handwritten TypeScript models, define the transport contract.

### Review request example

```json
{
  "decisions": [
    {
      "candidate_id": "candidate-uuid",
      "action": "create",
      "item": {
        "name": "Desk lamp",
        "category": "electronics",
        "quantity": 1,
        "quantity_basis": "exact",
        "packing_class": "boxable",
        "fragile": true
      }
    },
    {
      "candidate_id": "another-candidate-uuid",
      "action": "attach_existing",
      "item_id": "existing-item-uuid"
    }
  ]
}
```

IDs above are illustrative placeholders. Owner and room are derived from the authenticated scan. All selected decisions succeed together or none are committed. The response maps candidate IDs to the saved outcome and item IDs. Unselected candidates remain pending.

## Transactions and repeat requests

Review commits item changes, evidence links, candidate outcomes, scan state, and the profile inventory revision together. Replaying resolved candidates with identical decisions does not create another item. A unique accepted-candidate reference enforces this at storage level.

Require a client-generated `Idempotency-Key` UUID on job creation, manual item creation, uploads, group splits, and advice application. Store the owner, route scope, key, request fingerprint and completed response in a small `request_receipt` table, unique on owner/scope/key. A reused key with a different request returns conflict. Preserve receipts for seven days; the client never retries older writes automatically. For uploads, compute the fingerprint from bytes plus scan ID; identical retries return the original media ID. File writes use temporary files and atomic rename, with orphan cleanup after a failed DB commit.

Increment `inventory_revision` on any item, room, evidence or box change affecting a plan. Move settings have their own revision. Persist both on plans and advice input snapshots. A plan GET computes `is_stale` by comparing revisions. Applying advice requires matching revisions and active referenced items; otherwise return conflict and offer regeneration. Routine item edits use ordinary last-write-wins behavior for this one-user prototype; no general collaboration protocol.

## Deletion and retention

Normalized photos remain until explicitly deleted. Raw uploads are removed after successful normalization; failed temporary uploads expire within 24 hours. Reject deletion while a queued/running job references a photo. Deleting media clears live evidence links and retains a tombstone so historical snapshots can show unavailable evidence instead of a broken image.

Keep scan review outcomes and plan snapshots until explicitly deleted in a later retention feature. Prune terminal job payloads after 30 days once durable scan/plan outputs are saved; expired advice can no longer be applied. Preserve the small job metadata, including reserved and actual cost, without the expired payload. A full personal data reset is a documented host maintenance operation, not a prominent UI control.
