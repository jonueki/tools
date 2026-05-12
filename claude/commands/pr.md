Create a pull request for the current branch.

1. Run `git status` and `git log main..HEAD --oneline` to understand what's on this branch
2. Run `git diff main...HEAD` to read all changes
3. Check if the branch has a remote: `git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null`
   - If no upstream, push first: `git push -u origin HEAD`
4. Draft PR content:
   - **Title**: under 70 chars, imperative mood, describes the change not the ticket
   - **Summary**: 2–4 bullet points on what changed and why
   - **Test plan**: bulleted checklist of how to verify this works
   - **Breaking changes**: call out any API, schema, or behavior changes that affect callers
5. Create the PR with `gh pr create` using a HEREDOC for the body
6. Return the PR URL

Do not push or create the PR without confirming the title and body with the user first unless they explicitly say to proceed automatically.
