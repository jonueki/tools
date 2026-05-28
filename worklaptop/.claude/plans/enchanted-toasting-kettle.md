# Plan — Cloud sync for the Poro training tracker

## Context

`plans/poro-training.html` (merged in PR #7) is a static crate-training dashboard. State lives only in each browser's `localStorage`, with manual Export/Import to move it. The user wants his **wife to use the tracker from her phone too**, which means shared state across devices with no manual steps.

A static file can't share state on its own, so this hosts the tracker on **Vercel** (free) and adds a shared store via **Upstash Redis**, with a serverless function mediating reads/writes. Edits auto-sync, debounced ~10s after the last action. This is an early, partial move into `PLAN.md` Stage 5 infrastructure — done for the concrete wife-access reason, not the general "build a UI" trigger.

## Approach

**Hosting:** Vercel project linked to the `jonueki/life-planner` GitHub repo, with **Root Directory set to `plans/`**. This is deliberate — it stops Vercel from publicly serving `state/*.md`, `PLAN.md`, `CLAUDE.md` (personal planning data). Only `plans/` is exposed.

**Store:** one JSON blob in Upstash Redis under key `poro:training:state`. The Upstash↔Vercel marketplace integration injects the REST credentials as env vars.

**Mediator:** `plans/api/state.js` serverless function. No npm deps — raw `fetch` to the Upstash REST API. `GET` returns the blob; `PUT` validates the body, merges it with the stored blob, writes back, returns the merged result.

**Conflict-free merge (last-write-wins per key).** The data model changes so concurrent edits converge:
- `tasks`: `{ [id]: true }` → `{ [id]: { done: bool, ts: number } }`. Entries are kept even when `done:false`, so a timestamp always exists to win against a stale value on the other device.
- `sessions[]`: each gains `updatedAt: number` and `deleted: boolean`. Deletes become tombstones (soft-delete), not array removal.
- Merge rule: per task id, keep the entry with the larger `ts`; per session id, keep the larger `updatedAt`; union of all ids.

**Sync orchestration (client):**
- On load, on focus/`visibilitychange`→visible, and 10s-debounced after any edit: `PUT` local state to `/api/state`, then **adopt the response by merging it into local state** (not blind replace — a checkbox toggled while the request was in flight must survive). Save to `localStorage`, `render()`.
- `localStorage` stays as the offline cache. On `PUT` failure, keep local state and retry on the next edit/focus.
- Small status indicator: Synced ✓ / Syncing… / Offline.
- No interval polling — focus-sync covers picking up the other person's changes.

## Files

- **`plans/api/state.js`** (new) — serverless function: `GET`, `PUT`-merge, Upstash REST calls, minimal server-side validation of incoming bodies. Exports `mergeState` and `normalize` so they're unit-testable.
- **`plans/vercel.json`** (new) — rewrite `/` → `/poro-training.html`.
- **`plans/poro-training.html`** (edit) — the bulk of the work:
  - New data model + a single `normalize(state)` that migrates old→new format, applied to **every** state entering the app (localStorage, server response, imported file).
  - `mergeState(a, b)` — client copy of the merge, used for merge-on-adopt. Kept deliberately identical to the server copy; both are tiny.
  - Update `isValidState` / `isValidSession` for the new shape.
  - Checkbox toggle writes `{done, ts: Date.now()}`; session add includes `updatedAt`/`deleted:false`; session delete sets the tombstone.
  - `sectionDone` / `allTasksDone` read `.done`; `renderSessions` filters out `deleted`.
  - **Reset fix:** clearing to `{}` would be undone by the merge (absence = "no opinion"). Reset must instead tombstone every session and set every known task id to `done:false` with a fresh `ts`, then sync.
  - Sync layer: `syncNow()`, the 10s debounce scheduler, load/focus/edit triggers, status indicator. Import path runs `normalize` then `syncNow()`.
  - Keep Export/Import as a manual backup escape hatch.
- **`PLAN.md`** (edit) — decisions-log entries recording the hosting choice and the accepted trade-offs below.

## Access control — shared passphrase gate

`/api/state` requires a shared secret on every request (GET and PUT):
- Expected value stored as a Vercel env var `TRACKER_PASSPHRASE`. The function compares it against an `X-Tracker-Key` request header; missing/wrong → `401`.
- Client prompts for the passphrase once (`prompt()`), stores it in `localStorage`, and sends it on every fetch. On a `401`, it clears the stored value and re-prompts.
- The secret never lives in the HTML source (which is public) — only in each user's browser and the Vercel env var. This is a fig-leaf gate, not real auth.

## Accepted trade-offs (documented in PLAN.md, not engineered around)

- **Non-atomic GET-merge-PUT** — two simultaneous PUTs could race within one invocation. For 2 low-frequency users, tolerated; not worth a Lua/transaction layer.
- **Clock skew** — LWW uses each phone's `Date.now()`. Skew larger than the gap between two edits to the *same* item could pick the wrong value. Rare at this usage; accepted.
- **No tombstone garbage collection** — soft-deleted sessions stay in the blob. Negligible at dozens-of-sessions scale.
- **Task identity is positional** (`section.id + "-" + index`). The `tasks` arrays in `SECTIONS` are now an append-only frozen schema — reordering or mid-array insertion would silently reassign saved state. Noted in a code comment.

## Manual steps for the user (dashboard clicks — cannot be scripted)

1. Vercel → Add New Project → import the `jonueki/life-planner` repo. Framework preset: **Other**. **Set Root Directory to `plans`.** Deploy.
2. In the project → Storage → add **Upstash Redis** from the marketplace (provisions the DB, injects env vars).
3. Confirm the injected env var names — the function expects `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN`; if Vercel names them differently (e.g. `KV_REST_API_*`), I'll match the function to whatever it injects.
4. Add a project env var `TRACKER_PASSPHRASE` set to the shared secret you and your wife will use.
5. Redeploy so the function sees the env vars. Open `https://<project>.vercel.app/` on both phones, enter the passphrase once each.

## Verification

- `node --check`-style syntax check of the HTML's inline JS and `api/state.js` (as done in earlier rounds).
- Unit-test `mergeState` / `normalize` with `node` by importing `api/state.js`: cover check, uncheck-wins-by-ts, concurrent edits, session add, tombstone delete, reset (all-tombstone), and old→new migration.
- Post-deploy end-to-end: open the URL in two browsers, toggle a task in one, confirm it appears in the other within ~10s and on tab refocus. Add and delete a session; confirm convergence. Test offline (disable network, edit, re-enable) and confirm it syncs without data loss.

## Workflow

Feature branch `jonueki/poro-cloud-sync`, one PR. Run the code-review loop and document rounds on the PR per CLAUDE.md. Return the PR URL for review before merge.
