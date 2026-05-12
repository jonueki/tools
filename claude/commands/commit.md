Create a git commit for the current changes.

1. Run `git status` to see what's staged vs unstaged
2. Run `git diff --staged` to read staged changes; if nothing staged, run `git diff` instead and show the user what's available — do NOT auto-stage everything
3. Run `git log -5 --oneline` to read this repo's commit message style
4. Write a commit message that:
   - Is concise (subject line under 72 chars)
   - Focuses on WHY, not WHAT — the diff shows what changed
   - Follows the observed style of this repo's recent commits
   - Uses imperative mood ("Add", "Fix", "Remove", not "Added")
5. If nothing is staged, list modified files and ask which to stage before proceeding
6. Create the commit using a HEREDOC to preserve formatting
7. Always append this trailer to the commit body:
   `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`
8. Run `git status` after to confirm success
