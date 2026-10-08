---
name: galene-resume
description: Resume a Galene workstream from its local .HANDOFF, verify current repository and native GitHub stack state, and continue the authorized next increment. Use for a fresh-session resumption, not ordinary continuation or requests to create or edit this skill.
---

# Galene resume

Read the shared [session continuity guide](../../../docs/engineering/session-continuity.md) and applicable repository instructions. A checkpoint supplies context; the current user request and repository state determine what to do.

## Restore context

Confirm the repository and worktree with `pwd`, `git rev-parse --show-toplevel`, `git status --short --branch`, and `git worktree list`. Read the selected `.HANDOFF`, or the current worktree's brief by default. Check its repository/worktree identity and source before relying on it. Do not select a different checkout's brief just because it is newer.

If the brief is missing, recover what is possible from the current request, Git, and the design guide. State the gap; ask one focused question only if the next outcome or workstream cannot be established. Do not invent a checkpoint, create one as a prerequisite, or assume a design document authorizes implementation.

Read `docs/design/README.md`, `docs/design/02-decisions.md`, `docs/design/08-delivery.md`, and the brief's required reading. Follow detailed architecture, data/API, AI, moving, or operations documents only for the current task. Check actual files and commands before treating a planned service, test target, or environment as implemented.

Inspect local changes, commits, relevant PRs and review comments. Preserve unfinished work. Compare recorded bases/heads with current branches and merges before choosing a PR base. Read additional history only to resolve a discrepancy or recover an active constraint. Reuse historical test evidence until changes or failures justify another check.

## Next increment

State the session outcome, next complete PR scope, dependencies, required checks, and likely stopping point. Retain the existing implementation sequence when it fits. Split a large scope by useful behavior; Galene has no fixed line-count cap or routine planning-approval requirement.

Distinguish owner requirements, engineering defaults, and unresolved choices. Do not treat an unanswered preference as approval or a settled choice as a fresh approval request. Continue independent work while a material decision is pending; pause only the work that depends on the answer. A design-only request stays design-only, and a checkpoint at a user review boundary stays there unless the current request authorizes proceeding.

For authorized implementation, preserve Galene's boundaries: reviewed observations become inventory only through explicit save, advice does not mutate belongings autonomously, moving arithmetic is deterministic, and private inventory/media require owner authorization. Apply the targeted unit and Docker integration checks described in the delivery plan when their code exists.

## Continue work

Use GitHub's native stack workflow from the shared guide for requested PR work. Verify live state before adding a layer; a completed stack needs a new stack rooted at its current trunk. Do not infer stack membership from base branches alone. Publishing permission must cover the destination and content, and local handoff records never belong in a public PR.

Do not start containers, make paid AI calls, send room photographs, apply migrations to personal data, deploy, or merge merely because a recorded command mentions them. Those actions must fit the current authorized task. Use the review and test tools actually available in Galene; no additional review skills or hooks are required.

At a meaningful stopping point, use [galene-handoff](../galene-handoff/SKILL.md) to preserve the updated checkpoint unless the user asks otherwise. Report completed work, checks actually run, remaining work, PR links, and the local handoff path. A request to inspect or edit this skill does not execute this workflow.
