# Security and operations

The deployment protects photographs of the owner's home and a detailed inventory. The essential controls are private access, authenticated media, bounded uploads and AI work, careful handling of secrets, and persistent host storage. Keep operational procedures small enough to use on one Linux host.

## Authentication and authorization

Provision one email/password user through Firebase administration and configure its UID as `OWNER_FIREBASE_UID`. The browser uses the Firebase client SDK for sign-in. The API verifies the ID token with the Firebase Admin SDK, including expected project, validity and signature, then requires an exact UID match. Use revocation checking for this low-volume app. Never authorize based on a client-supplied UID or email. [Firebase ID token verification](https://firebase.google.com/docs/auth/admin/verify-id-tokens)

Disable public user creation at the identity provider, not just in the frontend. Identity Platform exposes an administrator-only signup configuration through `client.permissions.disabledUserSignup`. During setup, verify the Firebase project's supported configuration and enable the needed Identity Platform option if required. Create the owner first, disable signup, and test a direct registration attempt before exposure. No blocking Cloud Function is needed for this design. [Identity Platform user self-service](https://docs.cloud.google.com/identity-platform/docs/concepts-manage-users), [configuration reference](https://docs.cloud.google.com/identity-platform/docs/reference/rest/v2/Config)

The UID allowlist remains mandatory even when signup is disabled. An account from the wrong Firebase project or any other UID has no application access. There is no “first person to log in becomes owner” flow. Account recovery and password reset are handled through Firebase administration for the prototype.

Use SDK-managed session persistence and obtain a fresh ID token when needed. Send tokens only in the Authorization header. Refresh and retry once after a 401, preserving any idempotency key. There are no application session cookies; if that changes later, add the corresponding CSRF protection. Clear query caches, generated media object URLs and unsaved sensitive state on logout.

Every inventory, job, plan, advice and image lookup goes through the same owner-scoped authorization. Return not found for inaccessible object IDs. Provider credentials, admin credentials and image bytes never enter frontend configuration or logs. Firebase's public client configuration is not treated as an authorization boundary.

## Media and browser controls

- Store media outside the static web root. Nginx cannot serve the private media directory directly.
- Fetch images through the authenticated API with Authorization, convert responses to browser object URLs, and revoke those URLs on view cleanup. Never put bearer tokens in image URLs.
- Set private data and image responses to `Cache-Control: no-store`. Do not install a service worker or persistent offline media cache initially.
- Enforce byte limits at both Nginx and the streaming API, then validate decoded media in the worker. Use server-generated storage paths and refuse user-selected filesystem locations.
- Keep upload temp files on a bounded disk allocation, with cleanup after failures. Redact logs and strip image metadata during normalization.
- Use a Content Security Policy appropriate to the Firebase SDK, restrict framing, set `X-Content-Type-Options: nosniff`, and use a conservative referrer policy. Render model output without executable HTML.

Use same-origin API routes; no permissive CORS policy. The edge replaces forwarded headers rather than trusting client-supplied values, and the API trusts proxy headers only from the internal edge. Test the final CSP with Firebase sign-in and blob-backed images before treating it as complete.

## Docker and host configuration

| Setting | Initial policy |
| --- | --- |
| Host | One Linux machine with local filesystem; start around 2 vCPU, 4 GiB RAM and 20 GiB free disk, then measure |
| Persistent paths | `${GALENE_DATA_DIR}/db` and `${GALENE_DATA_DIR}/media` mounted as directories |
| Database | `inventory.sqlite3`, WAL, `foreign_keys=ON`, `busy_timeout=5000`, `synchronous=FULL` |
| Process count | One API process and one worker; no replicated workers |
| Users | Non-root API, worker and frontend; matching numeric UID for shared data access |
| Container privileges | Drop unnecessary capabilities, no privileged containers, no Docker socket mounts |
| Filesystems | Read-only application image; explicitly writable data and temporary paths |
| Restarts | Restart long-running services unless stopped; migration job exits after completion |
| Logging | Structured stdout/stderr, bounded Docker log rotation |
| Upload limit | Nginx request cap 21 MiB for multipart overhead; API file cap 20 MiB |
| Timeouts | Bounded request and upload timeouts; AI work runs outside HTTP requests |

Mount the entire SQLite directory, including its WAL and shared-memory files, into both API and worker at the same container path. Do not put it on NFS or mount only the main database file. Use a writable host path with restricted permissions; normal Compose shutdown must not delete data. [SQLite WAL](https://www.sqlite.org/wal.html)

Use one-shot migrations and explicit Compose health/dependency conditions. A successful migration precedes API and worker startup. On later host restarts, both processes also check the database revision and refuse incompatible schemas; startup ordering alone is insufficient. Failed upgrades leave the prior data in place and report an actionable error. [Compose startup ordering](https://docs.docker.com/compose/how-tos/startup-order/)

Pin supported language and image versions in implementation, use lockfiles, and update dependencies through small PRs. Do not bind dependency choices to unverified “latest” tags.

## HTTPS and networking

Local development publishes the edge on `127.0.0.1:8080` and uses a test authentication configuration or a development Firebase project. Phone access uses an HTTPS deployment profile with a hostname the phone can reach. For a public Linux host, point a domain at the server and terminate TLS in Nginx; use Certbot as a Compose maintenance service with persistent certificate storage and a host timer for renewal and Nginx reload.

For a private network, use an existing trusted certificate or a documented private-access arrangement. Domain and certificate details are deployment inputs; they do not change the application boundaries. HTTPS is required outside localhost. Allow only the intended edge ports at the host firewall. Restrict SSH separately.

Nginx proxies `/api/` to the API and page/asset requests to the frontend. API 404s must never become SPA HTML. Configure upload limits explicitly; Nginx's `client_max_body_size` rejects oversized requests before the application handles them. [Nginx body limits](https://nginx.org/en/docs/http/ngx_http_core_module.html#client_max_body_size)

## Secrets and settings

Commit only example configuration with placeholders. Ignore `.env` files, service-account JSON, host data, logs, local certificates, and developer-local hidden configuration. Mount Firebase admin credentials as a read-only secret file. Provide the AI key through a secret file or protected host environment; it is read only by the worker. Neither belongs in container build arguments or browser variables.

| Configuration | Consumer |
| --- | --- |
| `APP_ENV`, `PUBLIC_ORIGIN` | API and frontend deployment settings |
| `FIREBASE_PROJECT_ID`, `OWNER_FIREBASE_UID`, credentials path | API |
| Firebase public web configuration | Frontend |
| `GALENE_DATA_DIR` | Compose host path selection |
| `AI_PROVIDER`, `VISION_MODEL`, `ADVICE_MODEL`, key path | Worker |
| AI limits and model price configuration | API reservations and worker reconciliation |
| Logging, media limits, timeouts | Relevant service |

Fail startup on missing owner identity, incompatible database schema, or an emulator/test authentication setting in deployment mode. AI configuration may be absent in manual-only mode, with a visible disabled state; never substitute fake AI results in a deployed app. Worker does not need Firebase administrative credentials.

## Health and recovery

Provide internal liveness and readiness routes. API readiness checks database access and expected schema. Track worker heartbeat, oldest queued job, last error and disk capacity in an authenticated status view. An AI provider outage degrades AI features while manual inventory stays available.

Rate-limit request floods at the edge and expensive work in the application. Keep at most three active AI jobs and a bounded media-preparation queue. Refuse new uploads if less than 1 GiB remains free, with a clear cleanup message. Reserve adequate temporary space for the maximum accepted upload; avoid repeatedly accepting work when the disk is full.

Document five short maintenance procedures during implementation: first setup, deploy an image update, restart after a host reboot, rotate/revoke credentials, and recover from a failed job or full disk. No automated schema downgrades; compatible application rollback is allowed only when the database revision is supported.

No scheduled backups or backup service are included. Local persistence survives container recreation but does not protect against host loss, accidental deletion, or a bad migration. The owner has chosen that prototype tradeoff. Add backup plus restore verification as a separate later feature; do not describe host volumes as backups.
