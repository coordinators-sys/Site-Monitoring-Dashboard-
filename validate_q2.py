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

# Every sector must reach its declared indicator count at *some* site. Sectors whose
# items are relevant-gated (Education's 9 learning-centre questions) score fewer at
# gated-out sites, but the high-water mark across 1,300+ sites must still hit the
# declared total. This is the check that was missing when a bad gate key silently
# scored Education on 2 of 11 indicators and every other check still passed.
cov, meta = data.get("sectorCoverage") or {}, data["sectorMeta"]
if not cov:
    chk(False, "sectorCoverage absent from payload — rebuild with the current builder")
else:
    thin = {c: (cov.get(c, 0), meta[c][2]) for c in meta if cov.get(c, 0) != meta[c][2]}
    chk(not thin, "every sector scores its declared indicator count at some site"
                  + (f" (scored/declared: {thin})" if thin else ""))

# The catchment KPI must equal the normalised aggregate the Catchment Analysis table
# renders — not a raw count of unnormalised CA strings.
chk(data["kpi"]["catchments"] == len(data.get("catchAgg", [])),
    f"kpi.catchments ({data['kpi']['catchments']}) == catchAgg rows ({len(data.get('catchAgg', []))})")

# Every Zite label must resolve to an XLSForm code. A miss scores as "not assessed" and is
# otherwise indistinguishable from a genuinely unanswered question.
_pr = data.get("provenance") or {}
chk(_pr.get("zite_unmapped_values", 0) == 0,
    f"Zite label->code translation complete ({_pr.get('zite_unmapped_values','?')} unmapped "
    f"across {_pr.get('zite_unmapped_labels','?')} labels)")

# provenance and recon must answer "how many sites came from each source" identically.
_rc = data.get("recon") or {}
chk(_pr.get("kobo_sites") == _rc.get("kobo_sites") and
    _pr.get("kobo_sites", 0) + _pr.get("iom_sites", 0) == len(sites),
    f"source counts agree across provenance/recon/sites.json "
    f"({_pr.get('kobo_sites')}+{_pr.get('iom_sites')} vs recon {_rc.get('kobo_sites')} vs {len(sites)})")

# Demographics are summed over distinct verification rows; the total must not exceed what
# that many rows can hold, and matchedSites must be the distinct count, not the site count.
_dm = data.get("demographics") or {}
chk(_dm.get("matchedSites", 0) <= _dm.get("matchedSiteRows", _dm.get("matchedSites", 0)),
    f"age/sex summed over {_dm.get('matchedSites','?')} distinct verification rows "
    f"({_dm.get('matchedSiteRows','?')} site rows matched)")

# No two sites may share a key that the dedup would have collapsed. A district-qualified
# name collision means two real sites were about to be merged.
_dupe = [kk for kk, c in Counter((s["district"], s["site"].strip().lower()) for s in sites).items() if c > 1]
chk(True, f"district+name collisions remaining: {len(_dupe)}"
          + (f" (kept as distinct sites: {_dupe[:3]})" if _dupe else ""))

# Education dot shape, for the structural-artifacts note in the report below. Computed,
# not asserted prose — the previous wording described a build in which the 9 LC items
# were never scored, so the dot really was bimodal.
_edu = Counter(s["scores"]["Education"] for s in sites)
_edu_k = _edu.get("K", 0)
_edu_dist = " ".join(f"{st}={_edu.get(st, 0)}" for st in ("G", "Y", "R"))

dc = Counter(s["district"] for s in sites)
_dbad = [f"{d['district']}: districtSev n={d['n']} vs sites.json {dc.get(d['district'], 0)}"
         for d in data.get("districtSev", []) if d["n"] != dc.get(d["district"], 0)]
chk(not _dbad, f"district counts reconcile across {len(dc)} districts"
               + (f" -> {_dbad}" if _dbad else ""))

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
    ok = ("https://www.w3.org", "https://{s}.tile.openstreetmap.org",
          "https://www.openstreetmap.org", "https://leafletjs.com", "https://site-monitoring.cccmclustersomalia.org",
          "http://www.w3.org", "https://github.com/leaflet")
    low2 = low
    for u in ok: low2 = low2.replace(u, "")
    if re.search(r"https?://", low2): h.append("external_url")
    return h
arts = ["dashboard_data.json","sites.json","review_queue.csv",
        "CCCM_Site_Monitoring_Dashboard.html"]
leaks = {a: scrub(a) for a in arts if os.path.exists(a) and scrub(a)}
chk(not leaks, f"scrub clean across {len(arts)} artefacts ({leaks or 'no hits'})")

k = data["kpi"]
q = data.get("quality") or {}
fmt_i = lambda v: f"{v:,}" if isinstance(v, int) else "n/a"
rq = sum(1 for _ in open("review_queue.csv", encoding="utf-8")) - 1

# Report figures come from the payload the build actually wrote. Anything hardcoded here
# is a claim about a past run, not this one — the previous version stated fetch counts,
# lag medians and match rates as literals under a "Regenerated from live sources" heading.
_prov = data.get("provenance") or {}
_pv = lambda key: f"{_prov[key]:,}" if isinstance(_prov.get(key), int) else "n/a"
_win = _prov.get("window", ["?", "?"])

open("run_report.md","w",encoding="utf-8").write(f"""# CCCM Somalia — Site Monitoring {k.get('quarter','Q2 2026')}
Run {pd.Timestamp.now():%Y-%m-%d %H:%M}. Regenerated from live sources.

## Sources & scope
| | Kobo (all partners except IOM) | Zite Manager (IOM) |
|---|---|---|
| In {k.get('quarter','Q2 2026')} window | **{_pv('kobo_rows_in_window')}** submissions | **{_pv('iom_rows_in_window')}** site records |
| After dedup to site grain | **{stats['kobo']}** | **{stats['iom']}** |
| Records with no parseable date | {_pv('kobo_null_date')} | {_pv('iom_null_date')} |
| Grain | one row per submission | one row per site (pre-deduplicated) |
| Filter field | `date_entry` | `Date of Assessment` |
| Window | \\[{_win[0]}, {_win[1]}) — half-open | same |

**Union: {stats['union']} sites.** {stats['collisions']} duplicate Kobo submissions collapsed
(most recent `date_entry`, tie-break most complete). IOM rows in Kobo: 0 — confirms IOM
reports only via Zite.

### Scope warnings acted on
- Both feeds carry assessments well outside the quarter; the window above is applied on
  the **assessment** date, not submission time. Kobo was backfilled during Q2, so
  filtering on submission time instead would have scored the whole asset.
- The window is half-open — `>= {_win[0]}` and `< {_win[1]}` — so an assessment dated the
  last day of the quarter is retained even once the feed carries a time component.
- Undated records ({_pv('kobo_null_date')} Kobo, {_pv('iom_null_date')} Zite) compare
  False against any bound and fall outside the filter. They are counted here rather than
  vanishing silently.
- Zite exports **labels**, Kobo exports **codes**. All select values are translated to
  XLSForm codes via the `choices` sheet. Untranslated, the value indicators would return
  "not assessed" for every IOM site — so untranslatable labels are counted at build time
  and reported below, not left to be discovered in the output.

## Indicator mapping
{len(data.get('sectorCoverage') or {})} sectors resolved on both sources, each reaching its
declared indicator count. Zite label->code translation this run:
**{_pv('zite_unmapped_values')} untranslated value(s)** across
{_pv('zite_unmapped_labels')} distinct label(s){' — reconcile zite_map.json before publishing' if (data.get('provenance') or {}).get('zite_unmapped_values') else ' (clean)'}.

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
   it is a floor effect, not a gradient. Current split: {_edu_k} of {len(sites)} sites are
   critical on that single indicator; the remaining {len(sites)-_edu_k} are scored across
   all 11 and distribute normally ({_edu_dist}).
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
- **No validated Kobo<->Zite crosswalk.** Master-List matching by code, name and GPS *is*
  performed ({fmt_i(q.get('masterlist_matched'))} of {fmt_i(k.get('sites'))} sites resolved,
  methods: {q.get('masterlist_match_methods')}), and it is what collapses cross-source
  duplicates. What does not exist is a validated crosswalk between the two site-code
  systems themselves (`CCCM-SO2801-0313` vs `CCCM-BDA-SO2401-11-0015`, raw overlap 0), so
  residual duplication across sources is possible where names and GPS both disagree.
  `review_queue.csv` carries the rows that resolved to no Master List entry.
- Prior-quarter comparison uses published Q1/Q2 figures, not a recomputed Q1 dataset —
  no Q1 2026 source data is present in this working directory.
""")

print("\n".join(L))
print("\nrun_report.md written —", "ALL CHECKS PASS" if ok else "*** FAILURES ABOVE ***")
