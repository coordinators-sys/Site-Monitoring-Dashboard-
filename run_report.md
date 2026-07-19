# CCCM Somalia — Site Monitoring Q2 2026
Run 2026-07-19 15:44. Regenerated from live sources.

## Sources & scope
| | Kobo (all partners except IOM) | Zite Manager (IOM) |
|---|---|---|
| Fetched | 6,088 submissions | 1,075 site records |
| In Q2 2026 | **488** | **852** |
| After dedup to site grain | **467** | **848** |
| Grain | one row per submission | one row per site (pre-deduplicated) |
| Filter field | `date_entry` | `Date of Assessment` |

**Union: 1315 sites.** 19 duplicate Kobo submissions collapsed
(most recent `date_entry`, tie-break most complete). IOM rows in Kobo: 0 — confirms IOM
reports only via Zite.

### Scope warnings acted on
- Kobo `date_entry` spans **2025Q1 → 2026Q3**; only 488 of 6,088 are Q2 2026.
  Median lag between assessment and submission is 226 days (max 499) — the asset was
  backfilled during Q2. Filtering on submission time instead would have scored 6,080 rows.
- Zite spans **Oct 2025 → May 2026**; 852 of 1,075 are Q2. The 40 undated records are
  exactly the 40 with null demographics (empty shells) and fall outside the filter.
- Zite exports **labels**, Kobo exports **codes**. All select values are translated to
  XLSForm codes via the `choices` sheet. Untranslated, all 7 value indicators would have
  returned "not assessed" for every IOM site.

## Indicator mapping
76/76 scored indicators resolved on both sources, derived from XLSForm
`aRQhLp3M6yhXzAPtVTafRW` — not guessed. Zite mapping derived by matching
`label::English`; 3 Health indicators that the label matcher missed were resolved
empirically against the IOM Q2 Excel at **100% agreement over 826 sites**.

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
2. **Education is bimodal by construction.** At a site with no learning centre,
   `access_education`='no' is the *only* assessed Education indicator (the 9 LC items are
   correctly not-applicable, per the methodology). One indicator, red, = 100% -> dark-red
   critical. So "no school on site" renders as critical. That is arguably the right
   signal, but it means the Education dot splits sharply rather than distributing.
3. **NFI is mostly not-assessed.** Its 2 indicators are gated on an NFI distribution
   having occurred; where none has, both are blank. Those sites are carried as
   *not assessed*, never as zero or Red.

## Headline
| | |
|---|---|
| Sites | 1315 |
| Districts | 16 |
| Catchments | 90 |
| Households | 174,351 |
| Individuals | 975,417 |
| Partners | 8 |
| National severity | **44.0%** |

National severity is the unweighted mean of per-site scores and is dominated by the
largest district — do not present quarter-on-quarter deltas as like-for-like.

## Validation
- [PASS] sites.json rows (1315) == union (1315)
- [PASS] 467 Kobo + 848 IOM == 1315
- [PASS] every sector cell classified: 15780 == 1315 x 12
- [PASS] sector states within G/Y/R/K/NA (stray: none)
- [PASS] severity within 0-100 (min 4, max 97)
- [PASS] no site with 0 assessed sectors (0 found)
- [PASS] severity band matches score
- [PASS] national severity recomputes (44.0 vs KPI 44.0)
- [PASS] district counts reconcile across 16 districts
- [PASS] scrub clean across 4 artefacts (no hits)

Review queue: **90** rows (90 name-pending — enumerator selected
"Other"; free-text name captured, no CCCM code. Counted in coverage, excluded from the
site-detail annex per methodology).

## Spot-check (3 random sites, end to end)
**Hilac 1** — Baydhaba (IOM)
  - sectors assessed: 11/12 (not assessed: NFI)
  - sector dots: CCCM=G, Protection=G, CP=G, GBV=G, HLP=G, NFI=NA, Shelter=R, WASH=G, Health=G, FSL=Y, Nutrition=G, Education=G
  - red/critical sectors: Shelter
  - severity 13 -> band Low (mean of per-sector red% across the 11 assessed sectors)
**Wadajir** — Kismaayo (IOM)
  - sectors assessed: 11/12 (not assessed: NFI)
  - sector dots: CCCM=Y, Protection=Y, CP=Y, GBV=G, HLP=G, NFI=NA, Shelter=Y, WASH=R, Health=G, FSL=G, Nutrition=G, Education=G
  - red/critical sectors: WASH
  - severity 27 -> band Moderate (mean of per-sector red% across the 11 assessed sectors)
**Deg Gaduuda** — Baydhaba (IOM)
  - sectors assessed: 11/12 (not assessed: NFI)
  - sector dots: CCCM=Y, Protection=Y, CP=Y, GBV=Y, HLP=K, NFI=NA, Shelter=Y, WASH=Y, Health=Y, FSL=G, Nutrition=Y, Education=G
  - red/critical sectors: HLP
  - severity 40 -> band High (mean of per-sector red% across the 11 assessed sectors)

## Not done
- No GPS/master-list matching: the Kobo↔Zite code systems do not reconcile and no
  validated crosswalk exists. `review_queue.csv` carries the unresolved rows.
- Prior-quarter comparison is absent — no Q1 2026 baseline in this working directory.
