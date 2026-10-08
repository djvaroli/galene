---
name: galene-handoff
description: Save a Galene workstream for a later session in the current worktree's local .HANDOFF, preserving previous briefs in .handoff/. Use when asked to hand off, save session context, or prepare to resume later; creating or editing this skill does not invoke it.
---

# Galene handoff

Read the shared [session continuity guide](../../../docs/engineering/session-continuity.md) and applicable repository instructions. Use the current worktree unless the user selects another source.

## Checkpoint

Confirm the repository, worktree, branch, HEAD, and local changes with `pwd`, `git rev-parse --show-toplevel`, `git status --short --branch`, and `git worktree list`. Read the existing brief and only the history needed to explain current work. Resolve a workstream mismatch before replacing its records.

Reconcile the session with Git, relevant code and docs, and current PR/review state when accessible. For a native stack, inspect `gh stack view --json` and verify PR bases and heads; ordinary dependency links are not proof of stack membership. If remote access fails, record the last verified state and the gap without changing the stack.

Record implemented, tested, published, and merged work separately. Preserve unfinished changes and useful failed approaches. Reuse test evidence with its command and tested revision; do not rerun tests merely to produce a checkpoint.

Keep Galene's current phase explicit: design, implementation, or review. Record which defaults in `docs/design/02-decisions.md` remain provisional, including database, capture scope, hosting, or AI choices when still relevant. Carry the active outcome and remaining work from `docs/design/08-delivery.md`; refine a PR boundary when useful without importing another repository's line-count rules.

## Record

Write a concise draft using the shared record format. Keep the overall objective, next complete increment, required reading, actual blockers, and any unanswered user question in the brief. Link detailed evidence from local history. Preserve important user-authored context with targeted edits.

Save through the bundled writer from the selected worktree:

```sh
python3 .agents/skills/galene-handoff/scripts/write_handoff.py /path/to/private-draft.md
```

Use `--history` for a supporting note without replacing the current brief. The writer archives the previous brief before replacement and rejects tracked or redirected destinations. Resolve a rejected destination; do not bypass the check, silently untrack records, or write into a different checkout.

Read back `.HANDOFF` and verify its necessary local links. Do not commit, stash, discard, push, merge, deploy, or modify runtime data as part of saving context. Use existing session authorization for separate requested actions; a handoff is not an instruction to perform them.

## Result

Report the local handoff path, checkpoint, next action, and any blocker. State that the records stay with this worktree and are not included in the public PR. Give the next-session invocation `$galene-resume` with the worktree path when needed. Do not start the next phase while handing it off.
