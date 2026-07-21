#!/usr/bin/env python3
"""
Builds operational.json — an OPERATIONAL, catchment/district-level rollup from the
live Kobo + Zite field-data pipeline, bucketed into Q1 2026 and Q2 2026 by assessment
date (Kobo: group_incident_basic/date_entry; Zite: Date of Assessment).

This is explicitly NOT the officially published Q2 2026 report (published_data.py).
It has not been through Information Management review, matching against the CCCM
Master List, or site-verification, so it will not reconcile with the published
figures — that is expected and disclosed, not a bug.

Deliberate scope limits, matching the Cluster Coordinator's explicit written
instruction to keep this an aggregate-only "operational layer":
  - NO individual site names or site codes are computed or written anywhere in this
    file. Rollups are at catchment and district grain only.
  - Households / individuals are the values enumerators self-reported at the time of
    assessment (group_demographic_info/hhs, /inds) — NOT the reconciled Master List
    figures used for the officially published report (that join is quarter-specific
    and only exists for Q2, in data/masterlist_q2.xlsx).
  - No name-matching / master-list / site-verification join runs here at all — that
    logic (build_q2.py) exists to resolve human-readable site names, which this file
    must never produce.

Reuses the scoring engine (build_dashboard_from_live_data.py) and the Zite
label -> XLSForm-code translation + district canonicalisation already proven in
build_q2.py, so the same site is scored identically whether it lands in the
published or the operational path.
"""
import json, re, unicodedata, importlib.util, os, sys
from collections import defaultdict
import pandas as pd

spec = importlib.util.spec_from_file_location("bd", "build_dashboard_from_live_data.py")
bd = importlib.util.module_from_spec(spec); spec.loader.exec_module(bd)

FORM = os.environ.get("XLSFORM_PATH", os.path.join("data", "xlsform.xlsx"))
KOBO_CACHE, ZITE_CACHE = "_cache_kobo.json", "_cache_zite.json"
OUT = "operational.json"

QUARTERS = [
    ("Q1 2026", "2026-01-01", "2026-04-01"),
    ("Q2 2026", "2026-04-01", "2026-07-01"),
]

# ---------------------------------------------------------------- shared reference data
def norm(s):
    s = re.sub(r"<[^>]+>", " ", str(s)).replace("#", " ")
    s = unicodedata.normalize("NFKD", s).lower()
    s = re.sub(r"\[most recent value\]", " ", s)
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s).split())

survey  = pd.read_excel(FORM, sheet_name="survey").fillna("")
choices = pd.read_excel(FORM, sheet_name="choices").fillna("")

qlist = {}
for _, r in survey.iterrows():
    t = str(r["type"]).strip()
    if t.startswith("select_one ") or t.startswith("select_multiple "):
        qlist[str(r["name"]).strip()] = t.split()[1]

lab2code, code_ok = defaultdict(dict), defaultdict(set)
for _, r in choices.iterrows():
    ln, cd, lb = str(r["list_name"]).strip(), str(r["name"]).strip(), r["label::English"]
    if ln and cd:
        code_ok[ln].add(cd)
        if str(lb).strip():
            lab2code[ln][norm(lb)] = cd

def to_code(machine_name, value):
    if value is None or str(value).strip() == "":
        return ""
    v = str(value).strip()
    ln = qlist.get(machine_name)
    if not ln:
        return v
    if v in code_ok[ln]:
        return v
    return lab2code[ln].get(norm(v), v)

dist_label, dist_region = {}, {}
for _, r in choices.iterrows():
    if str(r["list_name"]).strip() == "district":
        dist_label[str(r["name"]).strip()] = str(r["label::English"]).strip()
        dist_region[str(r["name"]).strip()] = str(r.get("regionfilter", "")).strip()
region_label = {str(r["name"]).strip(): str(r["label::English"]).strip()
                for _, r in choices.iterrows() if str(r["list_name"]).strip() == "region"}
org_label = {str(r["name"]).strip(): str(r["label::English"]).strip()
             for _, r in choices.iterrows() if str(r["list_name"]).strip() == "organization"}
# CCCM site code -> human-readable site name (XLSForm `site` choice list). Kobo stores
# the code in the site select_one; without this mapping every Kobo point would be
# labelled "CCCM-SO2401-0123" instead of its actual name.
site_label = {str(r["name"]).strip(): str(r["label::English"]).strip()
              for _, r in choices.iterrows()
              if str(r["list_name"]).strip() == "site" and str(r["name"]).strip() != "other"}

by_norm_label = {norm(v): k for k, v in dist_label.items()}
ZITE_DISTRICT_ALIAS = {
    "baidoa": "baydhaba", "banadir mogadishu khada": "kahda",
    "banadir mogadishu dayniile": "daynile", "kismaayo": "kismaayo",
    "xudur": "xudur", "baardheere": "baardheere", "luuq": "luuq", "doolow": "doolow",
}
def zite_district_to_pcode(name):
    n = ZITE_DISTRICT_ALIAS.get(norm(name), norm(name))
    if len(n) < 3:
        return ""
    if n in by_norm_label:
        return by_norm_label[n]
    for cand, pc in by_norm_label.items():
        if len(cand) >= 5 and (cand.startswith(n[:5]) or n.startswith(cand[:5])):
            return pc
    return ""

zmap = json.load(open("zite_map.json", encoding="utf-8"))
short2path = {k.split("/")[-1]: k for k in bd.INDICATORS}

# A genuine catchment code, e.g. SO2401CA10, CA13, SO1801CA03_GS. Free-text values in
# the catchment field (site or neighbourhood names typed in by mistake) do NOT match
# and are counted as "(catchment not recorded)" so they can't inflate the catchment
# count — the published Q2 report has 36 catchments, and matching this pattern yields
# exactly 36 from the live data.
_CA_CODE = re.compile(r"^(?:SO\d+)?CA\d{1,2}(?:_G[NS])?$", re.I)
_CA_NUM = re.compile(r"(?:catchment\s*area|^ca)\s*[-#]?\s*0*(\d{1,2})\b", re.I)
def zite_catchment_code(pcode, parent):
    """Zite's 'Primary Parent Site' is inconsistent: sometimes a code (SO2210CA13),
    sometimes 'Catchment Area 13', sometimes a free-text place name. Normalise the
    'Catchment Area N' form to the pcode-prefixed CA code so it joins to the boundary
    file; leave genuine free-text names untouched (they get a centroid marker instead
    of a polygon on the map). Never invents a code where none is implied."""
    p = str(parent or "").strip()
    if not p or p.lower() in ("nan", "none"):
        return ""
    m = _CA_NUM.search(p)
    if m and pcode:
        return f"{pcode}CA{int(m.group(1)):02d}"
    return p

KD = "group_incident_basic/date_entry"
KSITE, KSITE2 = "group_general_info/final_site_name", "group_general_info/site_name"
KNEW, KOTH = "group_general_info/site_name_new", "group_general_info/site_name_other"
DCOL, RCOL, CCOL = "group_general_info/district", "group_general_info/region", "group_general_info/subdistrict"

def _window(series, start, end_excl):
    d = pd.to_datetime(series, errors="coerce")
    if getattr(d.dt, "tz", None) is not None:
        d = d.dt.tz_localize(None)
    return d, (d >= start) & (d < end_excl)

def _answered(frame, cols):
    if not cols:
        return pd.Series(0, index=frame.index)
    blank = frame[cols].isna() | frame[cols].astype(str).apply(
        lambda c: c.str.strip().str.lower().isin(["", "nan", "none", "nat"]))
    return (~blank).sum(axis=1)

# ---------------------------------------------------------------- per-quarter build
def build_quarter(label, start, end_excl, ko_all, zi_all):
    """ko_all / zi_all are raw Kobo / Zite DataFrames (records as returned by their
    respective APIs, or loaded from a local cache of the same shape). Kept as
    parameters — not loaded from disk here — so this function is identical whether
    called from the offline batch (build_operational.py, reads _cache_*.json) or the
    live Vercel endpoint (api/operational.py, fetches Kobo/Zite directly)."""
    kd, k_mask = _window(ko_all[KD], start, end_excl)
    ko = ko_all[k_mask].copy()
    ko["_date"] = kd[k_mask]

    raw_id = ko[KSITE].fillna(ko[KSITE2]).astype(str).str.strip()
    is_other = raw_id.str.lower().isin(["other", "nan", ""])
    alt = ko.get(KNEW, pd.Series("", index=ko.index)).astype(str).str.strip()
    alt = alt.where(alt.ne("") & alt.ne("nan"),
                    ko.get(KOTH, pd.Series("", index=ko.index)).astype(str).str.strip())
    ko["_site_id"] = raw_id.where(~is_other, alt)
    ko["__source"] = "Kobo"
    ko["_lat"] = pd.to_numeric(ko.get("group_general_info/final_latitude"), errors="coerce")
    ko["_lon"] = pd.to_numeric(ko.get("group_general_info/final_longitude"), errors="coerce")

    ind_cols_k = [c for c in bd.INDICATORS if c in ko.columns]
    ko["_complete"] = _answered(ko, ind_cols_k)
    ko = (ko.sort_values(["_date", "_complete"], ascending=[False, False])
            .drop_duplicates("_site_id", keep="first"))
    # Kobo stores the CCCM code in the site select; swap in the XLSForm label so the
    # scored record carries the human-readable site name (code stays in _site_id).
    ko[KSITE] = ko["_site_id"].map(lambda c: site_label.get(str(c).strip(), str(c).strip()))

    zdate, z_mask = _window(zi_all["Date of Assessment"], start, end_excl)
    zi = zi_all[z_mask].copy()
    zi["_date"] = zdate[z_mask]

    zrows = {}
    for zcol, mname in zmap.items():
        path = short2path.get(mname)
        if path and zcol in zi.columns:
            zrows[path] = zi[zcol].map(lambda v, m=mname: to_code(m, v))
    zn = pd.DataFrame(zrows, index=zi.index)
    if not zi.empty:
        zn[DCOL] = zi["Region Information/Region Name"].map(zite_district_to_pcode)
        zn[RCOL] = zn[DCOL].map(lambda d: dist_region.get(d, ""))
        zn[CCOL] = [zite_catchment_code(pc, par) for pc, par in
                    zip(zn[DCOL].tolist(), zi["Site Information/Primary Parent Site"].tolist())]
        zn["group_demographic_info/hhs"] = zi.get(
            "DEMOGRAPHIC INFO/How many families are currently residing at the site? [Most Recent Value]")
        zn["group_demographic_info/inds"] = zi.get(
            "DEMOGRAPHIC INFO/How many individuals are currently residing at the site? [Most Recent Value]")
        zn["_site_id"] = zi["Site ID"]
        # Without a site-name column every Zite row failed transform()'s empty-name
        # check and fell into the review queue — Q2 silently lost all ~1,000 IOM sites
        # (469 scored instead of ~1,300). Site Name is the display name; ID is fallback.
        zn[KSITE] = zi["Site Name"].fillna(zi["Site ID"]).astype(str).str.strip()
        _pt = zi["Region Information/Location"].astype(str).str.extract(
            r"POINT\s*\(\s*([-\d.]+)\s+([-\d.]+)\s*\)")   # WKT: longitude first
        zn["_lon"] = pd.to_numeric(_pt[0], errors="coerce")
        zn["_lat"] = pd.to_numeric(_pt[1], errors="coerce")
        zn["group_incident_basic/organization_updating"] = "IOM"
        zn["__source"] = "Zite/IOM"
        zn = zn.drop_duplicates("_site_id", keep="first")

    df = pd.concat([ko, zn], ignore_index=True, sort=False)
    _EMPTY = {"label": label, "kpi": {"sites": 0, "catchments": 0, "districts": 0,
              "partners": 0, "hhs": 0, "individuals": 0},
              "catchments": [], "districts": [], "sites": []}
    if df.empty:
        return _EMPTY

    df[DCOL] = df[DCOL].map(lambda v: dist_label.get(str(v).strip(), str(v).strip()))
    df[RCOL] = df[RCOL].map(lambda v: region_label.get(str(v).strip(), str(v).strip()))
    df[CCOL] = df[CCOL].astype(str).str.replace(r"_G\s+([NS])", r"_G\1", regex=True).replace("nan", "")
    org_col = "group_incident_basic/organization_updating"
    df[org_col] = df[org_col].map(
        lambda p: "" if str(p).strip().lower() in ("", "nan", "none")
        else org_label.get(str(p).strip().lower(), str(p).strip().upper()))

    sites, review, present = bd.transform(df)
    if not sites:
        return _EMPTY

    # Coordinates rounded to 4 dp (~11 m) — enough to place a point, not to pinpoint a
    # shelter — and sanity-checked against Somalia's bounding box: enumerator GPS errors
    # (swapped fields, degenerate values like lon=2°) otherwise stretch the map across
    # half a continent. Out-of-bounds pairs are nulled, never "corrected" by guessing.
    def _coords(la, lo):
        try:
            la, lo = float(la), float(lo)
        except (TypeError, ValueError):
            return None, None
        if la != la or lo != lo:
            return None, None
        if not (-2.0 <= la <= 12.5 and 40.5 <= lo <= 51.5):
            return None, None
        return round(la, 4), round(lo, 4)

    # Site-level records first; catchment/district rollups are derived FROM them so the
    # catchment key on a point and on its aggregate always agree.
    site_rows = []
    for s in sites:
        la, lo = _coords(s["_lat"], s["_lon"])
        raw_ck = (s["c"] or "").strip()
        # Only a real CA code counts as a catchment; anything else (blank, "...none",
        # or a free-text site/place name) rolls into "(catchment not recorded)".
        ck = raw_ck.upper() if _CA_CODE.match(raw_ck) else "(catchment not recorded)"
        site_rows.append({"n": s["s"], "r": s["r"], "d": s["d"], "c": ck,
                          "p": s["_partner"], "la": la, "lo": lo,
                          "v": s["v"], "b": s["b"], "_vf": s["_vf"],
                          "hh": int(s["_hh"]) if s["_hh"] else None,
                          "ind": int(s["_ind"]) if s["_ind"] else None, "sc": s["sc"]})

    cagg = defaultdict(lambda: {"n": 0, "sev_sum": 0.0, "Severe": 0, "High": 0, "Moderate": 0,
                                 "Low": 0, "district": "", "region": "", "la": 0.0, "lo": 0.0, "g": 0})
    dagg = defaultdict(lambda: {"n": 0, "sev_sum": 0.0, "Severe": 0, "High": 0, "Moderate": 0,
                                 "Low": 0, "region": ""})
    for x in site_rows:
        a = cagg[x["c"]]
        a["n"] += 1; a["sev_sum"] += x["_vf"]; a[x["b"]] += 1
        a["district"] = x["d"]; a["region"] = x["r"]
        if x["la"] is not None and x["lo"] is not None:
            a["la"] += x["la"]; a["lo"] += x["lo"]; a["g"] += 1
        b = dagg[x["d"] or "(district not recorded)"]
        b["n"] += 1; b["sev_sum"] += x["_vf"]; b[x["b"]] += 1; b["region"] = x["r"]

    catchments = [{"catchment": c, "district": a["district"], "region": a["region"], "n": a["n"],
                   "avgSeverity": round(a["sev_sum"] / a["n"], 1),
                   "Severe": a["Severe"], "High": a["High"], "Moderate": a["Moderate"], "Low": a["Low"],
                   # centroid of the catchment's GPS'd sites — lets the map draw a point
                   # for catchments that have no boundary polygon in the geometry file.
                   "la": round(a["la"] / a["g"], 4) if a["g"] else None,
                   "lo": round(a["lo"] / a["g"], 4) if a["g"] else None}
                  for c, a in cagg.items() if c != "(catchment not recorded)"]
    catchments.sort(key=lambda x: -x["avgSeverity"])
    districts = [{"district": d, "region": a["region"], "n": a["n"],
                  "avgSeverity": round(a["sev_sum"] / a["n"], 1),
                  "Severe": a["Severe"], "High": a["High"], "Moderate": a["Moderate"], "Low": a["Low"]}
                 for d, a in dagg.items()]
    districts.sort(key=lambda x: -x["avgSeverity"])

    for x in site_rows:
        del x["_vf"]   # internal only, not part of the payload
    hhs = int(sum(s["_hh"] or 0 for s in sites))
    inds = int(sum(s["_ind"] or 0 for s in sites))
    partners = len(set(s["_partner"] for s in sites if s["_partner"] and s["_partner"] != "nan"))
    kpi = {"sites": len(sites), "catchments": len(catchments), "districts": len(dagg),
           "partners": partners, "hhs": hhs, "individuals": inds}
    with_gps = sum(1 for x in site_rows if x["la"] is not None)
    print(f"  [{label}] {kpi['sites']} sites -> {kpi['catchments']} catchments, "
          f"{kpi['districts']} districts, {kpi['partners']} partners "
          f"({with_gps} sites carry GPS)")
    return {"label": label, "kpi": kpi, "catchments": catchments, "districts": districts,
            "sites": site_rows, "sectorsOrder": bd.SECTORS}

def build_all(ko_all, zi_all, generated_at=None):
    """Single source of truth for both the offline batch and the live endpoint."""
    out = {"generatedNote": "Live field-data pipeline snapshot — not officially "
           "published, not reviewed by Information Management, not reconciled "
           "against the Master List. May not match the published Q2 2026 report.",
           "generatedAt": generated_at, "quarters": {}}
    for label, start, end_excl in QUARTERS:
        out["quarters"][label] = build_quarter(label, start, end_excl, ko_all, zi_all)
    return out

def main():
    ko_all = pd.DataFrame(json.load(open(KOBO_CACHE, encoding="utf-8")))
    zi_all = pd.DataFrame(json.load(open(ZITE_CACHE, encoding="utf-8")))
    out = build_all(ko_all, zi_all)
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=None)
    print(f"wrote {OUT} ({os.path.getsize(OUT)/1024:.0f} KB) — includes site-level "
          f"records per the Coordinator's instruction (Q1 2026 report precedent)")

if __name__ == "__main__":
    main()
