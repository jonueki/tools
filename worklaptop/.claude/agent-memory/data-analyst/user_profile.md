---
name: User Profile
description: Who the user is and their data/analysis preferences
type: user
---

Senior engineer building a personal finance dashboard (Next.js + SQLite). Tracks spending, income, and net worth from Chase and Schwab statements.

**Data context:**
- `transactions` table: amount column uses positive = expense (money out), negative = income/deposit. This is the most important sign convention — get it wrong and all analytics flip.
- Investment accounts (Schwab) use `balance_snapshots`, not transactions. Market appreciation is not a transaction.
- Date columns are YYYY-MM-DD text strings. Month filtering uses `date LIKE 'YYYY-MM%'`.
- Dedup is via `INSERT OR IGNORE ON UNIQUE(account_id, external_id)`.

**Analysis preferences:**
- Sanity-check totals against statement summaries before reporting.
- Call out null handling explicitly — it's never obvious.
- Percentages need a stated denominator.
- Terse output. No narration. Results + interpretation + caveats.
