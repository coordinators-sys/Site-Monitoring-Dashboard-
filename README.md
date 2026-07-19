# CCCM Cluster Somalia · Site Monitoring Dashboard · Q2 2026 (April–June)

Interactive, self-contained dashboard for the CCCM Cluster Somalia site monitoring
round: 16 districts across 10 regions, 8 reporting partners, scored Green/Yellow/Red
across 76 indicators in 12 sectors.

**➜ Open [`CCCM_Site_Monitoring_Dashboard.html`](CCCM_Site_Monitoring_Dashboard.html)
in any browser.** No server and no dependencies are needed — all data, styling, logos
and icons are embedded in the single file. The map basemap is the only thing that
needs a connection; without one the districts and catchments still draw, on a blank
background.

## Published vs draft — read this first

Two figures for the same quarter appear throughout, and they are never mixed:

| | Sites | HHs | Individuals | Partners | Severity |
|---|---|---|---|---|---|
| **Published** — official, use for external reporting | 1,275 | 131,520 | 719,747 | 7 | 44.6% |
| **Draft rebuild** — regenerated from live sources daily | 1,315 | 174,351 | 975,417 | 8 | 45.3% |

The published round applied additional site-eligibility filtering. The KPI cards and the
Q1→Q2 coverage panel show **published** figures. Every site-level view — Site Explorer,
Sector Deep-Dive, Priority Gaps, the map's site points, all CSV exports marked DRAFT —
is built from the **draft** rebuild and labelled as such in-product. Reconciliation of
the +40 difference is pending; the Data Quality tab carries the full waterfall.

## Views

| Tab | For |
|---|---|
| **Overview** | KPIs, key findings, Q1→Q2 coverage change, sector gap vs coverage, severity distribution, top-10 gaps/strengths, district ranking, age & sex profile |
| **Map** | District severity choropleth, assessment-coverage layer, site points, catchment-area polygons (OpenStreetMap basemap) |
| **Severity by District** | Stacked severity bands per district, sortable district table, partner coverage table |
| **Site Explorer** | Every site with 12 sector dots and severity badge; filter by region / district / severity band / sector gap / partner; search by name or CCCM code; CSV export |
| **Sector Deep-Dive** | Per-sector indicator scoring (Green/Yellow/Red), sorted by gap |
| **Priority Gaps** | Indicator ranking by red share and affected caseload |
| **Data Quality** | Reconciliation from raw submissions to draft to published; Master List and Site Verification match rates; per-partner reporting |
| **Reports** | CSV exports (published KPI summary, plus DRAFT-labelled gap, catchment, district and full-site extracts) and print |
| **Methodology** | Scoring rules, sources, and stated limitations |

## Data sources

- CCCM Cluster partner submissions from two systems — Kobo (all partners except IOM) and
  Zite Manager (IOM) — filtered to assessments dated **1 April – 30 June 2026** and
  deduplicated to one row per site. The window is half-open (`>= 2026-04-01`,
  `< 2026-07-01`) so a last-day assessment is retained even when a feed carries a time.
- Population (HH / individuals): CCCM IDP Site Master List Q2-2026 where a site matches
  by CCCM code, verified name, or GPS + name; the monitoring submission otherwise.
- Age & sex: IDP Site Verification dataset (Q1-2026 vintage), summed over the **436
  distinct verification records** matching 437 of 1,315 sites — about a third of the
  caseload, stated on the chart. Not collected by the monitoring instrument itself.

Severity Score = mean share of red-scored indicators across the sectors assessed at a
site (sectors not assessed are excluded, never counted as zero). Bands: Severe ≥55% ·
High 40–55% · Moderate 25–40% · Low <25%.

## Known caveats (stated in-product where relevant)

- **90 sites** carry field-reported names pending verification against the Master List
  (`review_queue.csv`); they are counted in coverage.
- **127 sites have no GPS** and so do not appear on the map's site-points layer, though
  they are present in every other view.
- Quarter-on-quarter severity comparisons are **not** like-for-like: coverage narrowed
  from Q1 (1,902 sites) to Q2.
- The two source systems' site codes do not reconcile (`CCCM-SO2801-0313` vs
  `CCCM-BDA-SO2401-11-0015`, raw overlap 0). Cross-source duplicates are resolved via the
  Master List by code, name and GPS, but no validated code crosswalk exists, so residual
  duplication is possible where name and GPS both disagree.
- Education carries a hard critical floor: at a site with no learning centre,
  `access_education` is the only assessed Education indicator, so "no school on site"
  scores 100% red. That is a floor effect, not a gradient.
- This dashboard covers sites where CCCM partners are actively present — it is not a
  census of all displacement sites.

## Rebuilding from live data

Both fetches are required — Zite supplies 848 of the 1,315 sites, and `build_q2.py`
reads both caches.

```
pip install requests pandas openpyxl python-dotenv numpy
cp .env.example .env        # fill in your own API credentials — never commit .env
python fetch_kobo_cache.py  # -> _cache_kobo.json   (Kobo: all partners except IOM)
python fetch_zite_cache.py  # -> _cache_zite.json   (Zite Manager: IOM)
python build_q2.py          # score, aggregate, render the single-file dashboard
python validate_q2.py       # 16 integrity checks + secret-leak scrub; fails on any breach
cp CCCM_Site_Monitoring_Dashboard.html public/index.html   # the deployed artefact
```

`build_q2.py` aborts on a missing indicator gate column, and `validate_q2.py` fails the
build if any sector scores fewer than its declared indicator count, if a Zite label fails
to translate to an XLSForm code, if source counts disagree across the payload, or if a
credential appears in any artefact. `validate_q2.py` also regenerates `run_report.md`
from the payload the build actually wrote — every figure in it is computed, not asserted.

A GitHub Actions workflow (`.github/workflows/refresh-dashboard.yml`) runs the whole
sequence daily at 03:00 UTC and commits only if validation passes.

## Repository contents

Raw submission caches and credentials are excluded (see `.gitignore`) — the caches
contain names and phone numbers of site focal points.

⚠️ **`data/masterlist_q2.xlsx` and `data/site_verification.xlsx` are currently tracked**,
though `.gitignore` excludes the same datasets by folder as not-for-publication. They are
site-level (names, GPS, catchments, population, age-sex bands) and contain no focal-point
contact details, but this contradicts the stated policy and is unresolved. Do not add
further source datasets to `data/` without a decision on this.

---
CCCM Cluster Somalia · IM: im@cccmclustersomalia.org
