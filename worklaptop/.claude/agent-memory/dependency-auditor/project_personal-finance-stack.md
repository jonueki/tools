---
name: project_personal-finance-stack
description: Key dependency decisions and known constraints for the personal-finance Next.js project
metadata:
  type: project
---

personal-finance is a Next.js 15 App Router + SQLite single-user local finance app. Key dep decisions:

- `pdf-parse` v2.4.5 is intentionally used for PDF parsing. v2.4+ exports a `PDFParse` class (not a default function). All parsers use `new PDFParse({ data: ... })`. Do not suggest downgrading.
- `better-sqlite3` must stay in `next.config.ts` `serverExternalPackages` or Next will try to bundle it and crash.
- `.npmrc` pins `registry=https://registry.npmjs.org` to override a work CodeArtifact registry in `~/.npmrc`.
- The app is localhost-bound by design — no auth, no Plaid (removed deliberately due to cost).
- `next` is currently on the 15.x `backport` tag (15.5.18). `latest` as of 2026-05-13 is next@16.2.6 (requires React 19.x — which is already installed, so peer deps align).

**Why:** Single-user personal finance app with intentional architecture constraints. Stability > cutting-edge.

**How to apply:** Avoid recommending removal of pdf-parse or better-sqlite3. Flag next@16 as an upgrade path but note it's a major version bump. Do not recommend adding auth or Plaid.
