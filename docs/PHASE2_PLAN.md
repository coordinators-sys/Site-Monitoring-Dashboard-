# Phase 2 — CCCM Site Monitoring Platform: architecture plan

Status of increments:

| # | Deliverable | Status |
|---|---|---|
| 1 | Interactive map (district choropleth, site points, catchments) | **Shipped** — Map tab |
| 2 | Database + auth foundation | Blocked on a Supabase project (see below) |
| 3 | Coordination Action Tracker (editable, persistent) | Needs #2 |
| 4 | Draft → Validated → Published workflow (IM approval) | Needs #2 |
| 5 | Report generator (PDF/Excel per filter scope) | Needs #2 (or client-side lite version first) |
| 6 | Somali/English UI | Independent — can ship on current stack |

## Why a database is unavoidable for #3–#5

The current product is a single self-contained HTML file rebuilt daily by GitHub Actions.
That architecture cannot: store an action a coordinator assigns, remember an IM officer's
approval, or gate internal data behind a login. Anything requiring *state that outlives a
page load* or *identity* needs a backend.

## Chosen stack (pending owner sign-off)

- **Supabase** (free tier): Postgres + row-level-security auth + REST — no server to run.
- **Next.js on Vercel** (already the hosting account): app shell around the existing
  dashboard; static views stay static, authed views query Supabase.
- The existing Python pipeline keeps running in GitHub Actions and **upserts** into
  Postgres instead of only writing one HTML file.

## Schema (first cut)

- `sites` (cccm_code PK, name, district_pcode, ca, lat, lon, status)
- `assessments` (id, site_id FK, period, partner, source, assessed_on, data_status:
  draft|validated|published)
- `indicator_responses` (assessment_id FK, indicator_id FK, raw_value, score G/Y/R/NA)
- `indicators` (id, machine_name, sector, label, is_scored, value_map)
- `partners`, `admin_districts`, `catchments`, `population_records`
- `publication_batches` (id, period, approved_by, approved_at, notes)
- `validation_issues` (assessment_id, rule, detail, resolved)
- `coordination_actions` (id, period, scope, sector, indicator, severity, population,
  referral_to, responsible, action, due, status, notes, closed_at)
- `users` / roles via Supabase Auth: viewer, partner, im_officer, coordinator, admin

## What the owner must do before increment #2 can start

1. Create a Supabase project (supabase.com — free tier) under a cluster-controlled email.
2. Authorize the Supabase connector for this workspace (claude.ai connector settings),
   or provide the project URL + service key via `.env` (never via chat).

Nothing else in Phase 2 is blocked on anyone but us.
