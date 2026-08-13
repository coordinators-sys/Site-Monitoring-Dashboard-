# CCCM Somalia — Site Monitoring Q2 2026
Run 2026-08-13 04:53. Regenerated from live sources.

## Sources & scope
| | Kobo (all partners except IOM) | Zite Manager (IOM) |
|---|---|---|
| In Q2 2026 window | **469** submissions | **798** site records |
| After dedup to site grain | **467** | **794** |
| Records with no parseable date | 4 | 40 |
| Grain | one row per submission | one row per site (pre-deduplicated) |
| Filter field | `date_entry` | `Date of Assessment` |
| Window | \[2026-04-01, 2026-07-01) — half-open | same |

**Union: 1261 sites.** 19 duplicate Kobo submissions collapsed
(most recent `date_entry`, tie-break most complete). IOM rows in Kobo: 0 — confirms IOM
reports only via Zite.

### Scope warnings acted on
- Both feeds carry assessments well outside the quarter; the window above is applied on
  the **assessment** date, not submission time. Kobo was backfilled during Q2, so
  filtering on submission time instead would have scored the whole asset.
- The window is half-open — `>= 2026-04-01` and `< 2026-07-01` — so an assessment dated the
  last day of the quarter is retained even once the feed carries a time component.
- Undated records (4 Kobo, 40 Zite) compare
  False against any bound and fall outside the filter. They are counted here rather than
  vanishing silently.
- Zite exports **labels**, Kobo exports **codes**. All select values are translated to
  XLSForm codes via the `choices` sheet. Untranslated, the value indicators would return
  "not assessed" for every IOM site — so untranslatable labels are counted at build time
  and reported below, not left to be discovered in the output.

## Indicator mapping
12 sectors resolved on both sources, each reaching its
declared indicator count. Zite label->code translation this run:
**0 untranslated value(s)** across
0 distinct label(s) (clean).

## Divergences from the published methodology
1. **Yellow cannot fire on binary indicators.** `yesno` is `yes`/`no` — no `partial`
   choice. "partial → Yellow" is unreachable for ~60 of 76 indicators; Yellow arises only
   from the 7 value lists. Sector dots read more polarised than the methodology implies.
2. **WASH scores on 10 indicators, not 11.** "Latrines functional & sufficient" has no
   yes/no field — only two integers. Cluster decision: breakdown only, no derived rule.
3. **FSL `income_generating`**: 0%=Red, 1–50%=Yellow, >50%=Green. A cluster decision, not
   a form constraint. **Confirm before publication.**
4. **Site codes do not reconcile.** Kobo `CCCM-SO2801-0313` vs Zite
   `CCCM-BDA-SO2401-11-0015`; raw overlap 0. Sources are kept separate — do not sum into a
   single coverage figure without a validated crosswalk.

## Structural artifacts in the sector dots — read before interpreting
These follow from the methodology as written and are **not** data errors. Stated so the
dots are not misread:

1. **Two-indicator sectors can never show plain Red.** CP and NFI have 2 indicators each,
   so the only reachable red-shares are 0%, 50%, 100% -> Green, Yellow, or dark-red
   critical. The 26-50% (Yellow) and 51-90% (Red) buckets cannot both be occupied, and
   Red is unreachable. CP shows R=0 for this reason alone.
2. **Education carries a hard critical floor.** At a site with no learning centre,
   `access_education`='no' is the *only* assessed Education indicator (the 9 LC items are
   correctly not-applicable, per the methodology). One indicator, red, = 100% -> dark-red
   critical. So "no school on site" renders as critical — arguably the right signal, but
   it is a floor effect, not a gradient. Current split: 620 of 1261 sites are
   critical on that single indicator; the remaining 641 are scored across
   all 11 and distribute normally (G=319 Y=190 R=132).
3. **NFI is mostly not-assessed.** Its 2 indicators are gated on an NFI distribution
   having occurred; where none has, both are blank. Those sites are carried as
   *not assessed*, never as zero or Red.

## Headline
| | |
|---|---|
| Sites | 1261 |
| Districts | 16 |
| Catchments | 36 |
| Households | 169,677 |
| Individuals | 948,171 |
| Partners | 8 |
| National severity | **46.3%** |

National severity is the unweighted mean of per-site scores and is dominated by the
largest district — do not present quarter-on-quarter deltas as like-for-like.

## Validation
- [PASS] sites.json rows (1261) == union (1261)
- [PASS] 467 Kobo + 794 IOM == 1261
- [PASS] every sector cell classified: 15132 == 1261 x 12
- [PASS] sector states within G/Y/R/K/NA (stray: none)
- [PASS] severity within 0-100 (min 4, max 97)
- [PASS] no site with 0 assessed sectors (0 found)
- [PASS] severity band matches score
- [PASS] national severity recomputes (46.3 vs KPI 46.3)
- [PASS] every sector scores its declared indicator count at some site
- [PASS] kpi.catchments (36) == catchAgg rows (36)
- [PASS] Zite label->code translation complete (0 unmapped across 0 labels)
- [PASS] source counts agree across provenance/recon/sites.json (467+794 vs recon 467 vs 1261)
- [PASS] age/sex summed over 382 distinct verification rows (383 site rows matched)
- [PASS] district+name collisions remaining: 3 (kept as distinct sites: [('Baydhaba', 'buur adoy'), ('Baydhaba', 'wabiyow'), ('Daynile', 'marwo')])
- [PASS] district counts reconcile across 16 districts
- [PASS] scrub clean across 4 artefacts (no hits)

Review queue: **90** rows (90 name-pending — enumerator selected
"Other"; free-text name captured, no CCCM code. Counted in coverage, excluded from the
site-detail annex per methodology).

## Spot-check (3 random sites, end to end)
**Wiinle** — Baydhaba (IOM)
  - sectors assessed: 11/12 (not assessed: NFI)
  - sector dots: CCCM=G, Protection=G, CP=G, GBV=G, HLP=G, NFI=NA, Shelter=R, WASH=G, Health=G, FSL=Y, Nutrition=G, Education=G
  - red/critical sectors: Shelter
  - severity 15 -> band Low (mean of per-sector red% across the 11 assessed sectors)
**Warshira** — Xudur (IOM)
  - sectors assessed: 11/12 (not assessed: NFI)
  - sector dots: CCCM=G, Protection=K, CP=K, GBV=G, HLP=K, NFI=NA, Shelter=K, WASH=G, Health=G, FSL=G, Nutrition=G, Education=G
  - red/critical sectors: Protection, CP, HLP, Shelter
  - severity 42 -> band High (mean of per-sector red% across the 11 assessed sectors)
**Arare** — Kismaayo (IOM)
  - sectors assessed: 11/12 (not assessed: NFI)
  - sector dots: CCCM=Y, Protection=Y, CP=Y, GBV=Y, HLP=G, NFI=NA, Shelter=Y, WASH=Y, Health=Y, FSL=Y, Nutrition=R, Education=K
  - red/critical sectors: Nutrition, Education
  - severity 46 -> band High (mean of per-sector red% across the 11 assessed sectors)

## Not done
- **No validated Kobo<->Zite crosswalk.** Master-List matching by code, name and GPS *is*
  performed (799 of 1,261 sites resolved,
  methods: {'code': 281, 'none': 462, 'name': 429, 'gps+name': 95}), and it is what collapses cross-source
  duplicates. What does not exist is a validated crosswalk between the two site-code
  systems themselves (`CCCM-SO2801-0313` vs `CCCM-BDA-SO2401-11-0015`, raw overlap 0), so
  residual duplication across sources is possible where names and GPS both disagree.
  `review_queue.csv` carries the rows that resolved to no Master List entry.
- Prior-quarter comparison uses published Q1/Q2 figures, not a recomputed Q1 dataset —
  no Q1 2026 source data is present in this working directory.
