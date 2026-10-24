#!/usr/bin/env python3
"""
Builds the PUBLIC dashboard — the only artefact ever deployed to
site-monitoring.cccmclustersomalia.org.

Every reconciled figure (KPI totals, sector-gap %, district table, downloads) comes
from a published quarter: published_q1.py / published_data.py (Q1, Q2 2026, page-verified
from the released PDFs) or published/published_<YYYY-Qn>.json (Q3 2026 onward, written by
the report pipeline with the same computations as that quarter's National PDF). This
script has no code path from those figures to the live draft rebuild (_cache_kobo.json,
_cache_zite.json, sites.json).

One deliberate, narrow exception, added at the Cluster Coordinator's explicit written
request: a catchment/district-level "Operational Snapshot (live field data)" block —
aggregate counts only, never a site name or site code, never blended into the
reconciled KPIs/downloads above, rendered under its own distinct badge and caveat so
it can never be mistaken for PUBLISHED RESULTS. Its primary source at runtime is the
live api/operational.py endpoint (queries Kobo/Zite server-side on each request,
credentials never reach the browser); operational.json here is only the offline
fallback snapshot baked in at build time for when that endpoint is unreachable.

Writes: public/index.html
"""
import base64, json, os, re, sys
import pandas as pd
import published_data as P
import published_q1 as Q1P

ICON_FILES = {"CCCM": "CCCM icon.png", "Prot": "Protection.png", "CP": "CP.png",
              "GBV": "GBV.png", "HLP": "HLP.png", "NFI": "Shelter SNFI.png",
              "Shel": "Shelter SNFI.png", "WASH": "WASH.png", "Hlth": "Health .png",
              "FSL": "Food Security .png", "Nutr": "Natrution .png", "Educ": "Eduction.png"}

def b64(path):
    with open(path, "rb") as fh:
        return "data:image/png;base64," + base64.b64encode(fh.read()).decode()

# ---------------------------------------------------------------- assemble DATA
icons = {}
for code, fn in ICON_FILES.items():
    p = os.path.join("icons", fn)
    if os.path.exists(p):
        icons[code] = b64(p)
logo_p = os.path.join("logo", "CCCMCluster_Somalia.png")
assets = {"logo": b64(logo_p) if os.path.exists(logo_p) else "", "icons": icons}

GEO = (json.load(open(os.path.join("data", "geo.json"), encoding="utf-8"))
       if os.path.exists(os.path.join("data", "geo.json")) else None)

districts = []
for d in P.DISTRICTS_RANKED:
    districts.append({"district": d["district"], "region": d["region"], "n": d["n"],
                       "gap": d["gap"], "cov": d["cov"], "bands": d["bands"], "pc": None})
# pcodes for the map join, read from the district boundary layer itself (OCHA COD-AB names).
PCODE_BY_NAME = {g["n"]: g["pc"] for g in (GEO or {}).get("districts", [])}
PCODE_BY_NAME.update({"Kahda": "SO2210", "Daynile": "SO2203"})   # Banadir split (pcodeAlias)
for d in districts:
    d["pc"] = PCODE_BY_NAME.get(d["district"])

# Q1 2026 published district ranking (from published_q1.py). n/bands are None because
# the Q1 report did not publish per-district site counts or severity bands on its
# summary page; gap/cov are shown where the district was ranked, a dash otherwise.
q1_districts = [{"district": d["district"], "region": d["region"], "n": d["n"],
                 "gap": d["gap"], "cov": d["cov"], "bands": d["bands"],
                 "pc": PCODE_BY_NAME.get(d["district"])} for d in Q1P.DISTRICTS_RANKED]

q2_full = {
    "sectors": P.SECTORS, "topRed": P.TOP_RED, "topGreen": P.TOP_GREEN,
    "lcNote": P.LC_SAMPLE_NOTE, "districts": districts, "keyFindings": P.KEY_FINDINGS,
    "districtFootnote": (
        f"{len(districts)} districts had at least 10 assessed sites this quarter and are "
        f"eligible for national comparison. {P.DISTRICTS_BELOW_THRESHOLD_N} further "
        f"districts ({P.DISTRICTS_BELOW_THRESHOLD_SITES} sites combined) fell below that "
        f"threshold and are not individually ranked. Severity band counts (Severe/High/"
        f"Moderate/Low) are shown only where published at district level; a dash means "
        f"the published report did not disclose that breakdown for this district. "
        f"Kahda and Daynile are reported jointly as \"Mogadishu\" for severity bands in "
        f"the published map (341 sites: 153 Severe · 150 High · 22 Moderate · 16 Low)."),
}
q1_full = {
    "sectors": Q1P.SECTORS, "topRed": Q1P.TOP_RED, "topGreen": Q1P.TOP_GREEN,
    "lcNote": "", "districts": q1_districts, "keyFindings": Q1P.KEY_FINDINGS,
    "districtFootnote": (
        "Q1 2026 district ranking from the published national report summary page. "
        "The union of the report's top-10 highest-gap and top-10 highest-coverage "
        "districts is the 17 districts assessed. Gap % and Coverage % are shown where "
        "the district was ranked in that dimension; a dash means it was not. Per-district "
        "site counts were not published at that granularity."),
}

# ---------------------------------------------------------------- pipeline quarters (Q3 2026 onward)
# Each published/published_<YYYY-Qn>.json is written by the report pipeline
# (kobo_partner_agencies_tracker/export_dashboard_figures.py) with the same computations as
# that quarter's National PDF. Dropping a new file in published/ adds the quarter — no
# hand-transcription. Q1 and Q2 2026 predate the exporter and stay as page-verified modules.
PUB_DIR = "published"
pipeline_periods = []
for fn in sorted(os.listdir(PUB_DIR)) if os.path.isdir(PUB_DIR) else []:
    if not re.fullmatch(r"published_\d{4}-Q[1-4]\.json", fn):
        continue
    f = json.load(open(os.path.join(PUB_DIR, fn), encoding="utf-8"))
    bt = f["districtsBelowThreshold"]
    mog = f.get("mogadishu") or {}
    pipeline_periods.append({
        "id": f["id"], "key": f["key"], "label": f["label"], "full": True, "note": "",
        "source": f["source"], "kpi": f["kpi"], "partners": f["partners"],
        "previous": f.get("previous"), "popNote": f.get("popNote"),
        # per-area indicator counts for the Gap Finder (aggregates only; national = report's indicator table)
        "gapFinder": f.get("gapFinder"),
        "sectors": [{k: s[k] for k in ("name", "code", "gap", "cov")} for s in f["sectors"]],
        "topRed": f["topRed"], "topGreen": f["topGreen"], "lcNote": f["lcNote"],
        "districts": [{**d, "pc": d.get("pc") or PCODE_BY_NAME.get(d["district"])} for d in f["districts"]],
        "keyFindings": f["keyFindings"],
        "districtFootnote": (
            f"{len(f['districts'])} districts had at least 10 assessed sites this quarter and are "
            f"eligible for national comparison. {bt['districts']} further districts ({bt['sites']} "
            f"sites combined) fell below that threshold and are not individually ranked. Severity "
            f"bands (Severe ≥55% · High 40–55% · Moderate 25–40% · Low &lt;25%) are counted from "
            f"the same site scores as the published report."
            + (f" {len(mog['unassessed'])} of Mogadishu's {mog['total']} catchment areas were not "
               f"assessed this quarter." if mog.get("total") else "")),
    })

# Newest quarter first: the selector opens on it, and each quarter compares with the one before.
_qkey = lambda pid: (int(pid.split()[1]), int(pid.split()[0][1]))      # "Q3 2026" -> (2026, 3)

data = {
    "kpi": P.KPI,
    "period": P.PERIOD,
    "source": P.SOURCE,
    "generated": pd.Timestamp.now().strftime("%d %B %Y"),
    "contact": P.CONTACT,
    # Period-neutral: the reporting period is a user-selectable filter, so the standing
    # copy must not name one. The period itself is stated by the chip beside the heading
    # and by the selector in the header.
    "intro": ("The CCCM Cluster Somalia Site Monitoring provides a quarterly overview "
              "of service availability and priority gaps in displacement sites assessed "
              "by CCCM partners. Results represent the locations assessed in the selected "
              "reporting period and should not be interpreted as a census of all "
              "displacement sites."),
    "keyFindings": P.KEY_FINDINGS,
    "q1": P.Q1,
    # Both Q1 and Q2 2026 are now full published periods, each carrying its own sector
    # gaps, top-10 indicators, district ranking and key findings from its published
    # national report. The renderers read the active period's payload, so switching the
    # selector re-renders every analytical surface with that quarter's published data.
    "periods": sorted([p for p in pipeline_periods if p["id"] not in ("Q1 2026", "Q2 2026")] + [
        {"id": "Q2 2026", "label": P.PERIOD, "full": True, "kpi": P.KPI, "note": "",
         "source": P.SOURCE, "partners": P.PARTNERS, **q2_full},
        {"id": "Q1 2026", "label": Q1P.PERIOD, "full": True, "note": "",
         "source": Q1P.SOURCE, "partners": None,
         "kpi": {"sites": Q1P.KPI["sites"], "catchments": Q1P.KPI["catchments"],
                 "districts": Q1P.KPI["districts"], "partners": Q1P.KPI["partners"],
                 "hhs": Q1P.KPI["hhs"], "individuals": Q1P.KPI["individuals"],
                 "severity": Q1P.KPI["severity"]},
         **q1_full},
    ], key=lambda p: _qkey(p["id"]), reverse=True),
    "coverageNote": ("Direct trend comparison is not recommended: the sites, districts and "
                     "partners assessed differ from one quarter to the next, so differences "
                     "reflect assessment coverage, not a change in conditions."),
    "sectors": P.SECTORS,
    "topRed": P.TOP_RED,
    "topGreen": P.TOP_GREEN,
    "lcNote": P.LC_SAMPLE_NOTE,
    "districts": districts,
    "districtFootnote": q2_full["districtFootnote"],
    "partners": P.PARTNERS,
    "about": {
        "purpose": ("This dashboard summarises the CCCM Cluster's quarterly site "
                    "monitoring round, so partners and donors can see where services are "
                    "missing and where sites need coordinated follow-up."),
        "severity": ("Each indicator is scored Green (standard met), Yellow (partially "
                     "met) or Red (gap). Not Applicable and missing responses are excluded "
                     "from the denominator and never counted as Red. A district's or "
                     "sector's \"gap\" percentage is its share of applicable indicators "
                     "scored Red."),
        "limits": P.LIMITATIONS,
    },
    "geo": GEO,
    "assets": assets,
}

# ---------------------------------------------------------------- operational layer
# This is now only the FALLBACK snapshot: the public page's primary source for the
# Operational Snapshot is the live /api/operational endpoint (queries Kobo/Zite at
# request time, see api/operational.py). Baked in here purely so the section still
# shows *something* — clearly labelled as a stale snapshot — if that endpoint is ever
# unreachable.
#
# Site-level records (names, GPS, per-sector scores) ARE part of the live payload —
# added at the Cluster Coordinator's explicit written instruction, matching the
# precedent of the published Q1 2026 report whose annex lists every assessed site
# with name and severity. They are STRIPPED from this embedded fallback: keeps the
# page ~550 KB lighter, and if the live endpoint is down the map simply shows no
# site points rather than months-stale ones.
OP_PATH = "operational.json"
if os.path.exists(OP_PATH):
    op = json.load(open(OP_PATH, encoding="utf-8"))
    fallback_quarters = {}
    for qk, qv in op["quarters"].items():
        fallback_quarters[qk] = {k: v for k, v in qv.items() if k != "sites"}
    if any("sites" in q for q in fallback_quarters.values()):
        print("QA FAILED: embedded operational fallback must stay aggregate-only")
        sys.exit(1)
    data["operational"] = {"available": True, "note": op["generatedNote"],
                           "quarters": fallback_quarters}
else:
    data["operational"] = {"available": False, "note": "", "quarters": {}}

# ---------------------------------------------------------------- QA: internal reconciliation
errs = []
def check(cond, msg):
    if not cond: errs.append(msg)

check(data["kpi"]["sites"] == 1275, "KPI sites != 1275")
check(data["kpi"]["hhs"] == 131520, "KPI hhs != 131520")
check(data["kpi"]["individuals"] == 719747, "KPI individuals != 719747")
check(data["kpi"]["partners"] == 7, "KPI partners != 7")
check(data["kpi"]["catchments"] == 36, "KPI catchments != 36")
check(data["kpi"]["districts"] == 16, "KPI districts != 16")
check(len(data["partners"]) == 7, "partner list length != 7")
check(data["q1"]["sites"] == 1902, "Q1 sites != 1902")
# Every period must carry a complete published payload that reconciles to its own KPI.
_byid = {p["id"]: p for p in data["periods"]}
check(_byid.get("Q2 2026", {}).get("kpi", {}).get("sites") == 1275, "Q2 period sites != 1275")
check(_byid.get("Q1 2026", {}).get("kpi", {}).get("sites") == 1902, "Q1 period sites != 1902")
check(_byid.get("Q1 2026", {}).get("kpi", {}).get("districts") == 17, "Q1 districts != 17")
for _p in data["periods"]:
    check(_p["kpi"]["sites"] > 0, f"period {_p['id']} has no site count")
    check(len(_p.get("sectors", [])) == 12, f"period {_p['id']} does not have 12 sectors")
    check(len(_p.get("districts", [])) >= 1, f"period {_p['id']} has no districts")
    for _s in _p["sectors"]:
        check(0 <= _s["gap"] <= 100 and 0 <= _s["cov"] <= 100, f"{_p['id']} sector {_s['name']} pct out of range")
    if _p.get("partners") is not None:
        check(len(_p["partners"]) == _p["kpi"]["partners"], f"{_p['id']} partner list != partner count")
    if _p.get("key"):                                  # pipeline quarter: bands and site totals must reconcile
        for _d in _p["districts"]:
            check(sum(_d["bands"].values()) == _d["n"], f"{_p['id']} {_d['district']} bands != site count")
            check(bool(_d["pc"]), f"{_p['id']} {_d['district']} has no p-code for the map")
    # Q1's district union must equal its 17-district KPI.
    if _p["id"] == "Q1 2026":
        check(len(_p["districts"]) == _p["kpi"]["districts"],
              "Q1 district-ranking count does not equal the 17-district KPI")
for d in districts:
    if d["bands"]:
        check(sum(d["bands"].values()) == d["n"],
              f"{d['district']} severity bands do not sum to site count")
check(sum(d["n"] for d in districts) + P.DISTRICTS_BELOW_THRESHOLD_SITES == 1275,
      "ranked + below-threshold site counts do not sum to 1,275")
for s in data["sectors"]:
    check(0 <= s["gap"] <= 100 and 0 <= s["cov"] <= 100, f"sector {s['name']} pct out of range")
if errs:
    print("QA FAILED:"); [print("  -", e) for e in errs]
    sys.exit(1)
print(f"  QA: periods {', '.join(p['id'] for p in data['periods'])} — all reconcile")

# ---------------------------------------------------------------- render
tpl = open("public_template.html", encoding="utf-8").read()
app = open("public_app.js", encoding="utf-8").read()

for ph, path in (("/*LEAFLET_JS*/", os.path.join("vendor", "leaflet.js")),):
    if ph in tpl:
        tpl = tpl.replace(ph, open(path, encoding="utf-8").read()
                          if os.path.exists(path) else "/* leaflet missing */")
# Leaflet CSS is only referenced by the internal build's <style> injection point;
# the public template loads it inline too, via the same placeholder convention.
leaflet_css = os.path.join("vendor", "leaflet.css")
if os.path.exists(leaflet_css):
    css_body = re.sub(r"/\*.*?\*/", "", open(leaflet_css, encoding="utf-8").read(), flags=re.S)
    tpl = tpl.replace("<style>\n/*INTER_CSS*/", f"<style>\n{css_body}\n/*INTER_CSS*/", 1) \
        if "/*INTER_CSS*/" in tpl else tpl
inter_css = os.path.join("vendor", "inter.css")
if os.path.exists(inter_css) and "/*INTER_CSS*/" in tpl:
    tpl = tpl.replace("/*INTER_CSS*/", open(inter_css, encoding="utf-8").read())

fav32 = os.path.join("public", "favicon-32x32.png")
if os.path.exists(fav32):
    tpl = tpl.replace("/*FAVICON_INLINE*/", "data:image/png;base64," + b64(fav32).split(",", 1)[1])
else:
    tpl = tpl.replace('<link rel="icon" href="/*FAVICON_INLINE*/">', "")

tpl = tpl.replace("/*DATA_PLACEHOLDER*/", "const DATA = " + json.dumps(data, ensure_ascii=False) + ";")
tpl = tpl.replace("/*APP_PLACEHOLDER*/", app)

os.makedirs("public", exist_ok=True)
OUT = os.path.join("public", "index.html")
open(OUT, "w", encoding="utf-8").write(tpl)
print(f"  wrote {OUT} ({os.path.getsize(OUT)/1024:.0f} KB)")

# ---------------------------------------------------------------- scrub
# Bounded number checks (\b) so "1315" doesn't false-positive inside "131520";
# plain substrings only for strings that are unambiguous regardless of context.
blob = open(OUT, "rb").read().decode("latin-1")
low = blob.lower()
hits = []
for num in ("1315", "1,315", "174351", "174,351", "975417", "975,417"):
    if re.search(r"(?<!\d)" + re.escape(num) + r"(?!\d)", low):
        hits.append(f"draft-figure:{num}")
for lit in ("zitemanager", "kf.kobo.iom.int", "/api/v2/", "reports-file",
           "draft-chip", "draft-banner", "pending im validation", "review queue",
           "priority score", "50% severity + 25%", "site explorer tab",
           "reconciliation", "matching-method", "name-pending"):
    if lit in low:
        hits.append(f"internal-term:{lit}")
ok_urls = ("https://www.w3.org", "http://www.w3.org", "https://{s}.tile.openstreetmap.org",
          "https://www.openstreetmap.org", "https://leafletjs.com",
          "https://site-monitoring.cccmclustersomalia.org", "https://github.com/leaflet")
low2 = low
for u in ok_urls: low2 = low2.replace(u, "")
if re.search(r"https?://", low2): hits.append("external_url")
if hits:
    print("SCRUB FAILED:", hits); sys.exit(1)
print("  scrub: clean — no draft-dataset figures, no internal-only terms, no stray external URLs")
