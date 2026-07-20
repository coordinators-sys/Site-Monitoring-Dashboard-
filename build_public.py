#!/usr/bin/env python3
"""
Builds the PUBLIC dashboard — the only artefact ever deployed to
site-monitoring.cccmclustersomalia.org.

Every reconciled figure (KPI totals, sector-gap %, district table, downloads) comes
from published_data.py ONLY (hand-transcribed, page-verified from the officially
released Q2 2026 PDF report) — this script has no code path from those figures to
the live draft rebuild (_cache_kobo.json, _cache_zite.json, sites.json).

One deliberate, narrow exception, added at the Cluster Coordinator's explicit written
request: operational.json (built by build_operational.py) supplies a catchment/
district-level "Operational Snapshot (unreconciled)" block — aggregate counts only,
never a site name or site code, never blended into the reconciled KPIs/downloads
above, and rendered under its own distinct badge and caveat so it can never be
mistaken for PUBLISHED RESULTS.

Writes: public/index.html
"""
import base64, json, os, re, sys
import pandas as pd
import published_data as P

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

districts = []
for d in P.DISTRICTS_RANKED:
    districts.append({"district": d["district"], "region": d["region"], "n": d["n"],
                       "gap": d["gap"], "cov": d["cov"], "bands": d["bands"], "pc": None})
# pcodes for map join — only needed for districts we can shade; others render grey.
PCODE_BY_NAME = {"Afmadow": "SO2801", "Xudur": "SO2501", "Baardheere": "SO2802",
                 "Kahda": "SO2210", "Daynile": "SO2203", "Luuq": "SO2803",
                 "Gaalkacyo": "SO1801", "Baydhaba": "SO2401", "Kismaayo": "SO2801",
                 "Belet Weyne": "SO2601"}
for d in districts:
    d["pc"] = PCODE_BY_NAME.get(d["district"])

data = {
    "kpi": P.KPI,
    "period": P.PERIOD,
    "source": P.SOURCE,
    "generated": pd.Timestamp.now().strftime("%d %B %Y"),
    "contact": P.CONTACT,
    "intro": ("The CCCM Cluster Somalia Site Monitoring provides a quarterly overview "
              "of service availability and priority gaps in displacement sites assessed "
              "by CCCM partners. Results represent assessed locations during Q2 2026 and "
              "should not be interpreted as a census of all displacement sites."),
    "keyFindings": P.KEY_FINDINGS,
    "q1": P.Q1,
    "coverageNote": ("Direct trend comparison is not recommended because the sites assessed "
                     "in Q1 and Q2 2026 were not the same locations — fewer sites and "
                     "catchments were assessed this quarter than last."),
    "sectors": P.SECTORS,
    "topRed": P.TOP_RED,
    "topGreen": P.TOP_GREEN,
    "lcNote": P.LC_SAMPLE_NOTE,
    "districts": districts,
    "districtFootnote": (
        f"{len(districts)} districts had at least 10 assessed sites this quarter and are "
        f"eligible for national comparison. {P.DISTRICTS_BELOW_THRESHOLD_N} further "
        f"districts ({P.DISTRICTS_BELOW_THRESHOLD_SITES} sites combined) fell below that "
        f"threshold and are not individually ranked. Severity band counts (Severe/High/"
        f"Moderate/Low) are shown only where published at district level; a dash means "
        f"the published report did not disclose that breakdown for this district. "
        f"Kahda and Daynile are reported jointly as \"Mogadishu\" for severity bands in "
        f"the published map (341 sites: 153 Severe · 150 High · 22 Moderate · 16 Low)."),
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
    "geo": json.load(open(os.path.join("data", "geo.json"), encoding="utf-8"))
           if os.path.exists(os.path.join("data", "geo.json")) else None,
    "assets": assets,
}

# ---------------------------------------------------------------- operational layer
# Aggregate-only (catchment/district), unreconciled, from the live pipeline. See the
# module docstring above and build_operational.py for the scope this is limited to.
OP_PATH = "operational.json"
if os.path.exists(OP_PATH):
    op = json.load(open(OP_PATH, encoding="utf-8"))
    op_blob = json.dumps(op)
    for forbidden in ("_site_id", '"s":', '"site":', "final_site_name"):
        if forbidden in op_blob:
            print(f"QA FAILED: operational.json appears to carry site-identifying key {forbidden!r}")
            sys.exit(1)
    data["operational"] = {"available": True, "note": op["generatedNote"], "quarters": op["quarters"]}
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
print(f"  QA: {len(districts)} districts, {len(data['sectors'])} sectors, "
      f"{len(data['topRed'])} top-red, {len(data['topGreen'])} top-green — all reconcile")

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
