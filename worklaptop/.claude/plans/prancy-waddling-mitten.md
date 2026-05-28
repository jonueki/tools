# Parents Financial Advisor — v1 Plan

## Context

A lightweight web app for two retirement-age households (the user's parents and in-laws) to plan budgeting, track spending, and watch retirement runway. Users are non-technical, will use it on phone + laptop, and the developer (the user) doubles as admin. Hosting must be free. Privacy between households is non-negotiable. Designed to scale to ~10 households with several members each without re-architecting.

v1 features confirmed: **monthly budget vs actual**, **cash flow / retirement runway**, **net worth snapshots**. Manual data entry only — no bank sync.

## Stack

- **Next.js 15 (App Router) + TypeScript** on **Vercel Hobby** (free; personal-use lane, no revenue).
- **Supabase free**: Postgres + Auth (magic links) + RLS for per-household isolation.
- **Tailwind + shadcn/ui** with a forked theme tuned for older users (large fonts, AAA contrast, big touch targets).
- **Brevo free SMTP** (300/day, no domain verification) wired into Supabase Custom SMTP. Avoids Supabase's built-in 2/hr shared SMTP cap and skips Resend's domain-verification step.
- **Server Actions** for mutations; `revalidatePath` after writes.

## Auth: magic link + long-lived session

- `@supabase/ssr` for cookie-managed sessions (not the deprecated `auth-helpers-nextjs`).
- Supabase Auth config:
  - JWT (access token) expiry: 3600s (default).
  - Refresh token rotation: ON.
  - **Inactivity timeout: 90 days.**
  - **Absolute time-box: 365 days.**
- Add a "Sign out everywhere" button calling `supabase.auth.signOut({ scope: 'global' })`.
- Require fresh re-auth for destructive ops (delete account, delete household).
- **Security tradeoff to flag to user**: stolen device = stolen session for up to a year. Acceptable for this use case (low-value PII, no payment rails, trusted users).

## Data model

Tables (all monetary values stored as `_cents` integers):

- `profiles` — id (= `auth.uid()`), display_name, **is_super_admin** (boolean; the user's account flips this on).
- `households` — id, name.
- `household_members` — household_id, user_id, role (`owner` | `member`).
- `accounts` — household_id, name, type (`checking`/`savings`/`investment`/`retirement`/`other`), current_balance_cents.
- `account_snapshots` — account_id, balance_cents, snapshot_date. Time series for net worth.
- `categories` — household_id, name, monthly_budget_cents. Seeded with ~12 sensible defaults per household at signup.
- `transactions` — household_id, category_id (nullable for income), amount_cents, occurred_on, note, type (`income` | `expense`).

**Deferred to v2**: `recurring_items`. Materialization complexity (when to auto-create transactions?) isn't worth it for v1; users enter rent/bills manually each month.

## RLS — the security foundation

Every table carrying household data has a `household_id` column. Policy template:

```sql
USING (
  household_id IN (
    SELECT household_id FROM household_members
    WHERE user_id = (SELECT auth.uid())
  )
  OR EXISTS (
    SELECT 1 FROM profiles
    WHERE id = (SELECT auth.uid()) AND is_super_admin
  )
)
```

Gotchas to bake into the migration:

- **`INSERT` policies need `WITH CHECK`, not `USING`** — separate clauses for `SELECT`/`UPDATE`/`DELETE` vs `INSERT`.
- **Wrap `auth.uid()` in `(SELECT auth.uid())`** for Postgres planner caching (known Supabase perf tip).
- **Never expose the service-role key to the browser.** Admin role solves the cross-household access problem without needing it in app code.
- **Write a Playwright test** that logs in as household A and confirms household B's data is invisible. RLS bugs are silent.

## Hosting gotchas

- **Supabase free pauses after 7 days of zero DB activity.** Wake-up is ~30–60s and the first user hits a cold error.
  - Fix: **Vercel Cron** (Hobby allows 2) hits `/api/heartbeat` every 3 days running `SELECT 1`. Free, prevents the pause.
- **Vercel Hobby commercial-use restriction**: helping family with personal finances is personal use. Documented here so future-me doesn't second-guess.

## UI for retirement-age users

Concrete rules baked into the theme + component patterns:

- Base font **18–20px**. Buttons min **56px tall**.
- **WCAG AAA contrast (7:1)** — override shadcn defaults.
- No hover-only affordances; assume touch half the time.
- **No hamburger menu.** Flat bottom tab bar: **Budget · Cash Flow · Net Worth · Settings**.
- Destructive actions confirm in a full modal, not a toast.
- Money formatted **`$1,234`** on dashboards (no cents); cents only on detail/edit.
- Always label icons.
- **One primary (blue) action per screen.**

## Net worth UX (no bank sync)

The pattern: a **monthly "Update balances" wizard**. One screen per account: *"What's the balance in Chase Checking? Last entry was $4,200 on Apr 15."* Triggers:

- Dashboard banner on the 1st of every month.
- Optional email reminder via Vercel Cron + Brevo on the 1st.

Each wizard step writes an `account_snapshots` row AND updates `accounts.current_balance_cents`.

## Files to create (in order)

Repo is greenfield. Create in this order:

1. `supabase/migrations/0001_init.sql` — schema, seed categories function, RLS policies. Security foundation; gets written and tested first.
2. `lib/supabase/server.ts`, `lib/supabase/client.ts`, `lib/supabase/middleware.ts` — `@supabase/ssr` clients with cookie sessions.
3. `middleware.ts` — refresh-token rotation + auth gate on protected routes.
4. `app/(auth)/login/page.tsx` + `app/auth/callback/route.ts` — magic-link flow.
5. `app/api/heartbeat/route.ts` + `vercel.json` — DB-pause prevention cron.
6. Theme overrides in `app/globals.css` + `tailwind.config.ts` — fonts, contrast, button sizing.
7. App shell with bottom tab bar in `app/(app)/layout.tsx`.
8. Feature pages: `app/(app)/budget`, `app/(app)/cash-flow`, `app/(app)/net-worth`, `app/(app)/settings`.
9. Server Actions per feature (colocated as `actions.ts` next to pages).
10. `app/(admin)/admin/*` — super-admin household switcher for the user.

## Operational setup (outside the repo)

- Create Supabase project (free tier, US region).
- Create Brevo account, generate SMTP creds, paste into Supabase Auth → SMTP settings.
- Vercel project linked to repo; env vars: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY` (server-only).
- Configure Supabase Auth: magic-link template (rewrite the default email to plain language), session inactivity 90d, time-box 365d.
- Manually flip `is_super_admin = true` on the user's `profiles` row via SQL editor after first login.
- Create two households, invite parents + in-laws via magic-link email.

## Verification

End-to-end smoke test before handing the URL to parents:

1. `npm run dev`, sign up via magic link, confirm cookie session survives a browser restart.
2. Run the Playwright RLS test: log in as household A, confirm household B's transactions/accounts/budgets are invisible via direct DB query and via API.
3. Add categories, transactions, account snapshots in household A; confirm budget vs actual math is right.
4. Switch to admin user; confirm visibility into both households.
5. Walk through the monthly "Update balances" wizard end-to-end.
6. Deploy to Vercel preview; verify magic-link emails arrive via Brevo (check spam folder, tune From-name).
7. Test on an actual phone in a browser — confirm tap targets feel right, fonts are readable at arm's length.
8. Confirm Vercel Cron heartbeat fires (check Vercel logs after 24h).

## Out of scope for v1

- Recurring bills/income auto-materialization.
- Bank sync (Plaid/Teller).
- Multi-currency.
- Category CRUD UI (rename only via Settings; full management deferred).
- Reports/exports.
- Mobile app wrapper.
