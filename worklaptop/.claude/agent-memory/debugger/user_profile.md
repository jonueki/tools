---
name: User Profile
description: Who the user is and how they approach debugging
type: user
---

Senior/staff-level engineer at Remitly. Side projects in TypeScript/Next.js/SQLite.

**Stack:** TypeScript, Next.js, React, better-sqlite3, pdf-parse, yarn. Node.js server-side. Mac (darwin).

**Debugging preferences:**
- Skip the basics — they know how to read a stack trace.
- Focus on root cause, not symptoms.
- Prefers minimal, targeted fixes. Doesn't want surrounding cleanup bundled with a bug fix.
- Terse communication. No narration — just findings and the fix.

**Environment quirks to know:**
- better-sqlite3 must stay in Next.js serverExternalPackages or bundling crashes.
- pdf-parse v2.4+ exports a class, not a default function.
- Date columns are stored as YYYY-MM-DD text strings, not SQL DATE type.
