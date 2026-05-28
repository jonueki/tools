# Global Claude Preferences

## About me
- Full-stack engineer working primarily in TypeScript and Python
- Use Jira and Slack for project tracking — prefer MCP tools over manual lookups
- Main languages: TypeScript, Python, SQL

## Communication style
- Keep responses short and direct — no trailing summaries of what you just did
- No em-dashes when drafting a message on behalf of me. but make me sound positive and enthusiastic with exclamation points!
- No emojis unless I ask
- No multi-paragraph explanations for simple changes
- When referencing code, always include `file:line` so I can jump to it

## Code style
- No comments unless the WHY is non-obvious
- No extra abstractions or future-proofing beyond what the task needs
- No error handling for impossible cases
- Prefer editing existing files over creating new ones
- Delete dead code rather than commenting it out or leaving `_unused` prefixes

## Workflow preferences
- Use `/commit`, `/pr`, `/standup` skills for git tasks
- Use `/explain` when I ask you to explain something
- Use `/simplify` after significant implementations
- For broad changes, enter plan mode first and get alignment before coding
- When in doubt about scope, ask rather than guess
- Don't commit directly to `main` or `master`. If I'm on the default branch, create a feature branch first (e.g. `jonueki/<short-slug>`) before making changes.
- Don't `git push` to `main`/`master`. Push the feature branch and open a PR with `gh pr create` instead.
- Before starting non-trivial work, verify the current branch with `git branch --show-current`. If it's the default branch, branch off before editing.
- One logical change per PR. If scope creeps, stop and ask whether to split.
- Always run tests + typecheck locally before opening the PR. don't rely on CI to catch basics.
- Whenever a PR gets created or updated, automatically use the code review agent to review it. and then have the swe agent to read through the feedback and make fixes. Keep doing this loop until the code-reviewer has no feedback left.
- **Document each review round on the PR itself via `gh pr comment`.** Post the reviewer's findings as one comment, then a resolution log as a second comment (what was fixed, what was deliberately skipped and why, commit refs for each). The reviewer agent's output is otherwise transient and the audit trail is lost. Future me reading the PR should see what was flagged and how it was handled without re-running anything.
- After opening, return the PR URL so I can review the diff myself before merging. I want to actually read what shipped.
- Never use `--no-verify`, `--force` to `main`, or amend commits already pushed unless I explicitly ask.

## TypeScript projects
- Always check `tsconfig.json` exists before running tsc
- Prefer `npx` over global tool assumptions
- ESLint with `--max-warnings 0`

## Data / SQL
- Prefer dedicated schema tools over `information_schema` queries when available (they're faster)
