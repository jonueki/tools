# Tools

Claude Code configuration: agents, slash commands, and settings.

## Structure

```
claude/
  agents/     # Subagents invoked via the Agent tool
  commands/   # Slash commands (/commit, /pr, /standup, /explain)
  settings.json  # Shared MCP permissions (Slack, Jira, Playwright)
.claude/
  settings.json        # Project allowlist (git, find, grep, ls, npx, etc.)
  settings.local.json  # Local overrides (not committed)
```

## Agents

| Agent | Purpose |
|---|---|
| `code-improvement-scanner` | Scan recently written code for readability/performance issues |
| `code-reviewer` | Review for correctness, security, and best practices |
| `data-analyst` | Ad-hoc SQL, dataset exploration, trend analysis |
| `debugger` | Hard-to-reproduce bugs, unexpected behavior, regressions |
| `dependency-auditor` | Audit for outdated packages, CVEs, abandoned deps |
| `designer` | UX review, user flows, accessibility, microcopy |
| `product-manager` | Requirements, user stories, PRDs, acceptance criteria |
| `qa-tester` | Test plans, edge cases, automated test generation |
| `security-auditor` | Security vulnerabilities, auth logic, OWASP Top 10 |
| `swe` | Architecture decisions, system design, technical tradeoffs |
| `technical-writer` | READMEs, API docs, runbooks, changelogs |

## Slash Commands

- `/commit` — stage and commit current changes
- `/pr` — create a pull request for the current branch
- `/standup` — summarize recent work across git repos
- `/explain` — explain a file, function, or concept
