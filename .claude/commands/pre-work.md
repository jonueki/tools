Before writing any code, thoroughly research and prepare context for the task.

If the user described a task, use it. If not, ask what they want to build or fix.

Steps:
1. **Understand the ask** — restate what the user wants in one sentence to confirm alignment
2. **Explore the codebase** — find all files, functions, and patterns relevant to the task. Use Explore agents for broad searches. Read key files.
3. **Identify reusable pieces** — existing utilities, components, patterns, or conventions that should be reused rather than reinvented
4. **Surface risks** — things that could go wrong, edge cases, dependencies that might break, migration concerns
5. **Propose an approach** — a short plan (not a novel) covering what to change, in what order, and why

Output format:
- **Goal**: one sentence
- **Relevant files**: list with `file:line` references
- **Reusable code**: existing functions/patterns to leverage
- **Risks**: anything non-obvious
- **Proposed approach**: numbered steps, under 10

Guidelines:
- Do NOT write any code yet — this is research only
- Bias toward reading the actual code over assumptions
- If the task touches more than 3 files, use Explore agents in parallel
- Flag any ambiguity and ask the user before assuming
