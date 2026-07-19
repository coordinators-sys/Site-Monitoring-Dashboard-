# CCCM Cluster Somalia · Site Monitoring Dashboard · Q2 2026 (April–June)

Interactive, self-contained dashboard for the CCCM Cluster Somalia site monitoring
round: **1,315 sites**, 16 districts, 8 reporting partners, scored Green/Yellow/Red
across 76 indicators in 12 sectors.

**➜ Open [`CCCM_Site_Monitoring_Dashboard.html`](CCCM_Site_Monitoring_Dashboard.html)
in any browser.** No server, no internet connection and no dependencies are needed —
all data, styling, logos and icons are embedded in the single file.

## Views

| Tab | For |
|---|---|
| **Overview** | KPIs, key findings, Q1→Q2 coverage change, sector gap vs coverage, severity distribution, top-10 gaps/strengths, district ranking, age & sex profile |
| **Severity by District** | Stacked severity bands per district, sortable district table, partner coverage table |
| **Site Explorer** | Every site with 12 sector dots and severity badge; filter by region / district / severity band / sector gap / partner; search by name or CCCM code; CSV export |
| **Sector Deep-Dive** | Per-sector indicator scoring (Green/Yellow/Red), sorted by gap |

## Data sources

- CCCM Cluster partner submissions (all reporting partners, including IOM), filtered to
  assessments dated 1 April – 30 June 2026 and deduplicated to one row per site.
- Population (HH / individuals): CCCM IDP Site Master List Q2-2026 where a site matches
  by CCCM code or verified name; the monitoring submission otherwise.
- Age & sex: IDP Site Verification dataset, for the 439 matched sites (33% of caseload —
  stated on the chart; not collected by the monitoring instrument itself).

Severity Score = mean share of red-scored indicators across the sectors assessed at a
site (sectors not assessed are excluded, never counted as zero). Bands: Severe ≥55% ·
High 40–55% · Moderate 25–40% · Low <25%.

## Known caveats (stated in-product where relevant)

- 90 sites carry field-reported names pending verification against the Master List
  (`review_queue.csv`); they are counted in coverage.
- Quarter-on-quarter severity comparisons are **not** like-for-like: coverage narrowed
  from Q1 (1,902 sites) to Q2.
- This dashboard covers sites where CCCM partners are actively present — it is not a
  census of all displacement sites.

## Rebuilding from live data

```
pip install requests pandas openpyxl python-dotenv numpy
cp .env.example .env        # fill in your own API credentials — never commit .env
python fetch_kobo_cache.py
python build_q2.py
python validate_q2.py       # 10 integrity checks + secret-leak scrub; fails the build on any breach
```

Raw submission caches, source datasets and credentials are deliberately excluded from
this repository (see `.gitignore`): they contain personal data of site focal points.

---
CCCM Cluster Somalia · IM: im@cccmclustersomalia.org
