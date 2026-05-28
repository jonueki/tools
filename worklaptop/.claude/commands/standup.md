Generate a standup summary of recent work across git repos.

1. Determine the time window:
   - If today is Monday, use `--since="3 days ago"` to cover the weekend
   - Otherwise use `--since="yesterday"`
2. Run `git log --since=<window> --oneline --author="$(git config user.email)"` in the current repo
3. If there are sibling repos nearby (check `ls ../`), run the same command in each that is a git repo
4. Summarize what was done in plain English — group by project if multiple repos
5. Output in this format:

---
**Yesterday / Since last standup:**
- [bullet per logical chunk of work, not per commit]

**Today:**
- [infer from the most recent commits or in-progress branch names]

**Blockers / Notes:**
- [any stale branches, failing tests, or open PRs worth flagging]
---

Keep it tight — 5–10 bullets max. If there are no commits, say so clearly.
