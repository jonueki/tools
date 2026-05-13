# Claude Instructions for this repo

## Git workflow

After completing any task that results in file changes, proactively ask the user if they want to commit and push. Don't do it silently — always wait for explicit approval before running `git push`.

## After implementing anything non-trivial

Run through this checklist before declaring a task done. The Stop hook enforces steps 1–2 automatically for npm projects, but running them manually surfaces failures earlier.

1. **Tests** — if the project has `npm test`, run it. If you added or changed a pure function, query, or data transformation, add tests for it. Fix any failures before stopping.
2. **Typecheck** — if the project has `npm run typecheck` or a `tsconfig.json`, run `tsc --noEmit`. Fix all errors; no suppressions.
3. **Browser validation** — for any UI change, start the dev server and verify the affected page. Test the golden path and at least one edge case. Type checks and tests verify code correctness, not visual/UX correctness.
4. **Update docs** — if the project has a `STATUS.md` or equivalent handoff doc and you added a significant feature, update it.

## When to spin up sub-agents

Sub-agents run in parallel and protect the main context window from large explorations. The Agent tool accepts a `subagent_type` parameter — use the right specialist rather than a general-purpose agent.

| When | Agent |
| --- | --- |
| Starting a large or ambiguous feature | `Plan` — alignment on approach before writing code |
| After implementing a non-trivial feature | `code-reviewer` — independent correctness + security check |
| Something feels wrong but you can't pin it down | `debugger` — provide symptom, relevant files, error output |
| Adding a new page or user-facing flow | `designer` — UX review, accessibility, information architecture |
| Need test coverage for a complex module | `qa-tester` — test plan + edge cases |
| Code works but feels messy | `swe` — cleanup and refactoring (use a worktree to isolate) |
| Features or APIs are undocumented | `technical-writer` — update docs and inline comments |
| Feature handles sensitive data or user input | `security-auditor` — OWASP review |

Run independent agents in a single message so they execute in parallel:

```
Agent(subagent_type="code-reviewer", ...) launched at same time as Agent(subagent_type="designer", ...)
```
