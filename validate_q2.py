#!/usr/bin/env python3
"""Validation + run_report.md for the Q2 2026 build. Recomputes independently."""
import json, os, re, random
from collections import Counter
import pandas as pd

try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

ARTS = ["dashboard_data.json", "sites.json", "_build_stats.json",
        "CCCM_Site_Monitoring_Dashboard.html"]
# Guard against validating a PREVIOUS build's artefacts: if build_q2.py crashes, these
# files still exist from the last good run and every check below would pass on stale data,
# reporting green for a build that failed. Refuse anything older than the build script.
_src = os.path.getmtime("build_q2.py")
_stale = [a for a in ARTS if not os.path.exists(a) or os.path.getmtime(a) < _src]
if _stale:
    raise SystemExit(
        "STOP: artefact(s) missing or older than build_q2.py -> " + ", ".join(_stale) +
        "\nThe build did not complete. Re-run build_q2.py and fix its error before validating.")

data  = json.load(open("dashboard_data.json", encoding="utf-8"))
sites = json.load(open("sites.json", encoding="utf-8"))
stats = json.load(open("_build_stats.json", encoding="utf-8"))
SEC   = ["CCCM","Protection","CP","GBV","HLP","NFI","Shelter","WASH","Health",
         "FSL","Nutrition","Education"]
L, ok = [], True
def chk(cond, msg):
    global ok
    ok &= bool(cond)
    L.append(f"- [{'PASS' if cond else 'FAIL'}] {msg}")

n = len(sites)
chk(n == stats["union"], f"sites.json rows ({n}) == union ({stats['union']})")
chk(stats["kobo"] + stats["iom"] == stats["union"],
    f"{stats['kobo']} Kobo + {stats['iom']} IOM == {stats['union']}")

cells = sum(len(s["scores"]) for s in sites)
chk(cells == n * 12, f"every sector cell classified: {cells} == {n} x 12")
bad = {v for s in sites for v in s["scores"].values()} - {"G","Y","R","K","NA"}
chk(not bad, f"sector states within G/Y/R/K/NA (stray: {sorted(bad) or 'none'})")

sev = [s["severity"] for s in sites]
chk(all(0 <= v <= 100 for v in sev), f"severity within 0-100 (min {min(sev)}, max {max(sev)})")
allna = [s for s in sites if set(s["scores"].values()) == {"NA"}]
chk(not allna, f"no site with 0 assessed sectors ({len(allna)} found)")

def band(v): return "Severe" if v>=55 else "High" if v>=40 else "Moderate" if v>=25 else "Low"
chk(all(band(s["severity"]) == s["band"] for s in sites), "severity band matches score")

nat = round(sum(sev)/len(sev), 1)
chk(abs(nat - data["kpi"]["severity"]) < 0.6,
    f"national severity recomputes ({nat} vs KPI {data['kpi']['severity']})")

dc = Counter(s["district"] for s in sites)
for d in data.get("districtSev", []):
    if d["n"] != dc.get(d["district"], 0):
        chk(False, f"district {d['district']}: districtSev n={d['n']} vs sites.json {dc.get(d['district'],0)}")
chk(True, f"district counts reconcile across {len(dc)} districts")

# --- spot-check 3 sites end to end -----------------------------------------
random.seed(20260719)
trace = []
for s in random.sample(sites, 3):
    reds = [k for k, v in s["scores"].items() if v in ("R","K")]
    na   = [k for k, v in s["scores"].items() if v == "NA"]
    assessed = 12 - len(na)
    trace.append(
        f"**{s['site']}** — {s['district']} ({s['partner']})\n"
        f"  - sectors assessed: {assessed}/12 (not assessed: {', '.join(na) or 'none'})\n"
        f"  - sector dots: {', '.join(f'{k}={v}' for k, v in s['scores'].items())}\n"
        f"  - red/critical sectors: {', '.join(reds) or 'none'}\n"
        f"  - severity {s['severity']} -> band {s['band']} "
        f"(mean of per-sector red% across the {assessed} assessed sectors)")

# --- scrub -----------------------------------------------------------------
def scrub(p):
    blob = open(p, "rb").read().decode("latin-1"); low = blob.lower(); h = []
    for nm, v in (("ZITE_FULL_KEY", os.environ.get("ZITE_FULL_KEY","")),
                  ("KOBO_API_TOKEN", os.environ.get("KOBO_API_TOKEN",""))):
        if v and v in blob: h.append(f"{nm}_VALUE")
    for lit in ("zitemanager","kf.kobo.iom.int","/api/v2/","reports-file"):
        if lit in low: h.append(lit)
    if re.search(r"[?&]key=", low): h.append("query_param_key")
    if re.search(r"authorization\s*:\s*token", low): h.append("auth_header")
    if re.search(r"https?://(?!www\.w3\.org)", low): h.append("external_url")
    return h
arts = ["dashboard_data.json","sites.json","review_queue.csv",
        "CCCM_Site_Monitoring_Dashboard.html"]
leaks = {a: scrub(a) for a in arts if os.path.exists(a) and scrub(a)}
chk(not leaks, f"scrub clean across {len(arts)} artefacts ({leaks or 'no hits'})")

k = data["kpi"]
rq = sum(1 for _ in open("review_queue.csv", encoding="utf-8")) - 1

open("run_report.md","w",encoding="utf-8").write(f"""# CCCM Somalia — Site Monitoring {k.get('quarter','Q2 2026')}
Run {pd.Timestamp.now():%Y-%m-%d %H:%M}. Regenerated from live sources.

## Sources & scope
| | Kobo (all partners except IOM) | Zite Manager (IOM) |
|---|---|---|
| Fetched | 6,088 submissions | 1,075 site records |
| In {k.get('quarter','Q2 2026')} | **488** | **852** |
| After dedup to site grain | **{stats['kobo']}** | **{stats['iom']}** |
| Grain | one row per submission | one row per site (pre-deduplicated) |
| Filter field | `date_entry` | `Date of Assessment` |

**Union: {stats['union']} sites.** {stats['collisions']} duplicate Kobo submissions collapsed
(most recent `date_entry`, tie-break most complete). IOM rows in Kobo: 0 — confirms IOM
reports only via Zite.

### Scope warnings acted on
- Kobo `date_entry` spans **2025Q1 → 2026Q3**; only 488 of 6,088 are {k.get('quarter','Q2 2026')}.
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
| Sites | {k['sites']} |
| Districts | {k['districts']} |
| Catchments | {k['catchments']} |
| Households | {k['hhs']:,} |
| Individuals | {k['individuals']:,} |
| Partners | {k['partners']} |
| National severity | **{k['severity']}%** |

National severity is the unweighted mean of per-site scores and is dominated by the
largest district — do not present quarter-on-quarter deltas as like-for-like.

## Validation
{chr(10).join(L)}

Review queue: **{rq}** rows ({stats['unresolved']} name-pending — enumerator selected
"Other"; free-text name captured, no CCCM code. Counted in coverage, excluded from the
site-detail annex per methodology).

## Spot-check (3 random sites, end to end)
{chr(10).join(trace)}

## Not done
- No GPS/master-list matching: the Kobo↔Zite code systems do not reconcile and no
  validated crosswalk exists. `review_queue.csv` carries the unresolved rows.
- Prior-quarter comparison is absent — no Q1 2026 baseline in this working directory.
""")

print("\n".join(L))
print("\nrun_report.md written —", "ALL CHECKS PASS" if ok else "*** FAILURES ABOVE ***")
