---
name: project-personal-finance
description: Personal finance app at /Users/jonathanu/personal-finance — current state and roadmap context
metadata:
  type: project
---

Localhost Next.js 15 + SQLite personal finance app. Schema v2. As of 2026-05-12:
- 5 accounts: Chase credit (personal, 1999 txns), Chase credit (joint, 156 txns), Chase checking (95 txns), Schwab brokerage (86 balance snapshots), Chase mortgage (44 balance snapshots)
- Net worth ~$3.24M (Schwab taxable + housing equity, minus $488K mortgage)
- Pages: dashboard, accounts, transactions, budgets, analytics (w/ YoY), subscriptions, category-rules, import, net-worth

**Why:** Single-user tool replacing Plaid (removed for cost/access reasons). All data stays on-machine.

**Roadmap from STATUS.md:** Retirement projection is the next stated goal (net worth chart is live; needs contributions table + forward projection). Other parsers (Amex, Capital One, BofA) are noted but not started. Backup/restore also called out.

**How to apply:** When suggesting features, check whether they're already on the roadmap. Retirement projection is a stated next step — weight it accordingly.
