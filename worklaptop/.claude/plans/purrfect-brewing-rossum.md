# Net Worth Tracker + Schwab Parser

## Context
User wants a dedicated net worth tracking section with a historical line chart (adjustable window), broken down by taxable accounts, retirement accounts, and housing. The Schwab brokerage account (mask `880`, 93 PDFs from Sep 2018–Apr 2026) is the primary data source — it has 8 years of monthly portfolio snapshots that will anchor the chart. Chase accounts (Dec 2023/2025 onward) contribute liabilities and cash. Retirement accounts are empty now but will be added later; the architecture must support them.

The key challenge: Schwab balances change from market appreciation (not transactions), so we can't reconstruct history from cash flows. We need a `balance_snapshots` table that stores the ending portfolio value each month.

---

## 1. Schema migration — `lib/db.ts`

Add to `migrate()`:

```sql
CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL)

-- v1 migration:
CREATE TABLE IF NOT EXISTS balance_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
  month TEXT NOT NULL,          -- YYYY-MM
  balance REAL NOT NULL,
  created_at TEXT DEFAULT (datetime('now')),
  UNIQUE(account_id, month)
)

ALTER TABLE accounts ADD COLUMN net_worth_category TEXT  -- "taxable" | "retirement" | "housing" | null
```

Migration logic: read `schema_version`, skip if version >= 1. Use `try/catch` around `ALTER TABLE` (SQLite has no `ADD COLUMN IF NOT EXISTS`). Write version 1 after both DDL statements succeed.

---

## 2. Schwab parser — `lib/parsers/schwab.ts`

Input: PDF buffer + filename (`Brokerage Statement_YYYY-MM-DD_880.PDF`)

Extract:
- **Month** from filename: `2026-04-30` → `"2026-04"` (no need to parse PDF for date)
- **Ending Account Value** from PDF text via regex: `/Ending Account Value\s+\$?([\d,]+\.?\d*)/` (the value follows "Ending Account Value as of MM/DD")
- **Mask**: `"880"` (hardcoded or parsed from `Account Number\n4493-2880`)

Skip `(1)` duplicate files (filename contains ` (1)`).

Return type:
```ts
export type SchwabStatement = {
  source_file: string;
  mask: string;
  account_type: "investment";
  account_subtype: "brokerage";
  net_worth_category: "taxable";
  month: string;        // YYYY-MM
  balance: number;
  warnings: string[];
}
```

---

## 3. Extend `/api/ingest/route.ts`

Add to request schema:
```ts
balance_snapshot: z.object({ month: z.string(), balance: z.number() }).optional()
net_worth_category: z.enum(["taxable","retirement","housing"]).optional().nullable()
```

Also move `net_worth_category` inside `account` object (next to `type`/`subtype`).

On account creation/upsert: write `net_worth_category` to the `accounts` row if provided.

After transaction inserts: if `balance_snapshot` is present, do:
```sql
INSERT INTO balance_snapshots(account_id, month, balance) VALUES(?,?,?)
ON CONFLICT(account_id, month) DO UPDATE SET balance=excluded.balance
```

Allow `transactions: []` (0 items) — valid for snapshot-only ingests.

---

## 4. Bulk importer — `scripts/import-schwab.ts`

- Walk `schwab_statements/`, sort files, skip filenames containing ` (1)` to avoid duplicate months
- Parse each PDF with `parseSchwab(buffer, filename)`
- POST to `http://localhost:3000/api/ingest` with:
  ```json
  {
    "source": "<filename>",
    "account": { "mask": "880", "name": "Schwab Brokerage", "type": "investment", "subtype": "brokerage", "institution": "Schwab", "net_worth_category": "taxable" },
    "transactions": [],
    "balance_snapshot": { "month": "2026-04", "balance": 3704311.63 }
  }
  ```
- Print per-file result: `OK  2026-04  $3,704,311.63`
- Summary: total snapshots added/skipped/errors

---

## 5. New queries — `lib/queries.ts`

### `netWorthSeries()`
Returns `{ month: string; taxable: number; retirement: number; housing: number; liabilities: number; net: number }[]` for all months with any data, in chronological order.

Algorithm (TypeScript, not raw SQL — cleaner for multi-source joins):
1. Fetch all accounts (`id, type, subtype, net_worth_category, starting_balance`)
2. Fetch all balance snapshots (`account_id, month, balance`)
3. Fetch all transactions (`account_id, date, amount`) sorted by date
4. Build sorted list of all distinct months from both sources
5. For each month:
   - **Investment accounts** (have snapshots): find latest snapshot with `month <= target_month`; skip if none
   - **All other accounts**: `starting_balance ± cumSum(transactions where date <= lastDayOfMonth(target_month))`
     - credit/loan: `starting_balance + sum`; others: `starting_balance - sum`
   - Bucket: `type === "credit" || type === "loan"` → liabilities (use `balance` directly, will be subtracted in net); else bucket by `net_worth_category` (null → taxable bucket as default)
6. `net = taxable + retirement + housing - liabilities`

### `currentNetWorthByCategory()`
Returns `{ taxable: number; retirement: number; housing: number; liabilities: number; net: number }` — just the last row of the series, or computed directly from `accountBalances()` for efficiency.

---

## 6. `NetWorthChart` component — `components/NetWorthChart.tsx`

`"use client"` component.

Props: `{ data: SeriesRow[] }` where `SeriesRow = { month, taxable, retirement, housing, liabilities, net }`.

Internal state: `window: "1Y" | "3Y" | "5Y" | "All"` (default `"All"`).

Filter `data` to the selected window before rendering.

Chart: Recharts `AreaChart` with:
- `Area` for `taxable` (fill `#7c5cff`, stroke `#7c5cff`) — stacked
- `Area` for `retirement` (fill `#22c55e`, stroke `#22c55e`) — stacked  
- `Area` for `housing` (fill `#f59e0b`, stroke `#f59e0b`) — stacked
- `Line` for `net` (stroke `#e2e8f0`, dot=false) — on top, not stacked

YAxis: compact dollar formatter (`$3.7M`, `$500K`).

Window buttons: styled like the existing app's `btn` patterns — a small row of `1Y | 3Y | 5Y | All` above the chart.

Empty state: centered muted text (mirrors SpendChart pattern).

---

## 7. Net Worth page — `app/net-worth/page.tsx`

Server component (`force-dynamic`).

Sections:
1. **Header**: "Net Worth" + current total (`formatMoney(net)`)
2. **Stat cards** (4-column grid): Taxable, Retirement, Housing, Liabilities — each with current value from `currentNetWorthByCategory()`
3. **`<NetWorthChart data={series} />`** — full series from `netWorthSeries()`
4. **Account breakdown table**: each account row with name, type, `net_worth_category`, current balance. Pulled from `accountBalances()`.

---

## 8. Update Nav + AddAccountButton

**`components/Nav.tsx`**: add `{ href: "/net-worth", label: "Net Worth" }` between Dashboard and Accounts.

**`components/AddAccountButton.tsx`**: add `net_worth_category` select field (Taxable / Retirement / Housing / None) in the create-account form. POST it alongside other account fields. When the ingest/account route handles it, the account gets tagged.

Also update **`app/api/accounts/route.ts`** (POST handler) to accept and store `net_worth_category`.

---

## Execution order

1. Schema migration (`lib/db.ts`)
2. Schwab parser (`lib/parsers/schwab.ts`)
3. Extend `/api/ingest` (body schema + balance_snapshot write + net_worth_category on account)
4. Update `/api/accounts` POST to accept `net_worth_category`
5. Importer script (`scripts/import-schwab.ts`)
6. New queries in `lib/queries.ts`
7. `NetWorthChart` component
8. Net worth page (`app/net-worth/page.tsx`)
9. Nav + AddAccountButton updates

---

## Verification

```bash
# 1. Wipe DB and re-import everything
rm -rf data/
npm run dev &
npx tsx scripts/import-chase.ts   # 2250 txns
npx tsx scripts/import-schwab.ts  # ~88 snapshots (93 files minus 5 duplicates and a few missing months)

# 2. Spot-check snapshots
npx tsx scripts/spot-check.ts     # should show 4 accounts; Schwab with 0 txns

# 3. Open http://localhost:3000/net-worth
#    - Verify chart spans 2018-2026
#    - Verify current value ≈ $3.7M (matches April 2026 statement)
#    - Verify window buttons filter correctly
#    - Verify stat cards show taxable, retirement ($0), housing ($0), liabilities
```
