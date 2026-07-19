#!/usr/bin/env python3
"""
CCCM Somalia — Q2 2026 Site Monitoring dashboard build.

Union of:
  Source A  Kobo submissions   (all partners except IOM)  -> _cache_kobo.json
  Source B  Zite Manager       (IOM only)                 -> _cache_zite.json

Both are filtered to the Q2 2026 assessment window, normalised onto the XLSForm
machine-name schema, deduplicated to one row per site, then scored, aggregated
and rendered by build_dashboard_from_live_data.py.

Writes no URL, token or key to any output.
"""
import json, re, csv, unicodedata, importlib.util, sys, os
from difflib import SequenceMatcher
from collections import Counter, defaultdict
import pandas as pd

Q_START, Q_END, QLABEL = "2026-04-01", "2026-06-30", "Q2 2026"
FORM  = os.environ.get("XLSFORM_PATH", os.path.join("data", "xlsform.xlsx"))
BAD   = ["zitemanager", "http", "/api/", "key=", "token"]

# ---------------------------------------------------------------- load the scorer module
spec = importlib.util.spec_from_file_location("bd", "build_dashboard_from_live_data.py")
bd = importlib.util.module_from_spec(spec); spec.loader.exec_module(bd)
INDICATORS, SECTORS = bd.INDICATORS, bd.SECTORS

def norm(s):
    s = re.sub(r"<[^>]+>", " ", str(s)).replace("#", " ")
    s = unicodedata.normalize("NFKD", s).lower()
    s = re.sub(r"\[most recent value\]", " ", s)
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s).split())

# ---------------------------------------------------------------- XLSForm: choices
survey  = pd.read_excel(FORM, sheet_name="survey").fillna("")
choices = pd.read_excel(FORM, sheet_name="choices").fillna("")

qlist = {}                                    # machine name -> choice list_name
for _, r in survey.iterrows():
    t = str(r["type"]).strip()
    if t.startswith("select_one ") or t.startswith("select_multiple "):
        qlist[str(r["name"]).strip()] = t.split()[1]

lab2code = defaultdict(dict)                  # list_name -> {normalised label: code}
code_ok  = defaultdict(set)
for _, r in choices.iterrows():
    ln, cd, lb = str(r["list_name"]).strip(), str(r["name"]).strip(), r["label::English"]
    if ln and cd:
        code_ok[ln].add(cd)
        if str(lb).strip():
            lab2code[ln][norm(lb)] = cd

def to_code(machine_name, value):
    """Zite exports LABELS; Kobo exports CODES. Normalise everything to codes."""
    if value is None or str(value).strip() == "":
        return ""
    v = str(value).strip()
    ln = qlist.get(machine_name)
    if not ln:
        return v
    if v in code_ok[ln]:
        return v
    return lab2code[ln].get(norm(v), v)

# ---------------------------------------------------------------- admin lookups
dist_label, dist_region = {}, {}
for _, r in choices.iterrows():
    if str(r["list_name"]).strip() == "district":
        dist_label[str(r["name"]).strip()] = str(r["label::English"]).strip()
        dist_region[str(r["name"]).strip()] = str(r.get("regionfilter", "")).strip()
region_label = {str(r["name"]).strip(): str(r["label::English"]).strip()
                for _, r in choices.iterrows() if str(r["list_name"]).strip() == "region"}

site_label = {str(r["name"]).strip(): str(r["label::English"]).strip()
              for _, r in choices.iterrows()
              if str(r["list_name"]).strip() == "site" and str(r["name"]).strip() != "other"}
org_label  = {str(r["name"]).strip(): str(r["label::English"]).strip()
              for _, r in choices.iterrows() if str(r["list_name"]).strip() == "organization"}

by_norm_label = {norm(v): k for k, v in dist_label.items()}
ZITE_DISTRICT_ALIAS = {           # Zite operational name -> XLSForm district label
    "baidoa": "baydhaba", "banadir mogadishu khada": "kahda",
    "banadir mogadishu dayniile": "daynile", "kismaayo": "kismaayo",
    "xudur": "xudur", "baardheere": "baardheere", "luuq": "luuq", "doolow": "doolow",
}
def zite_district_to_pcode(name):
    n = norm(name)
    n = ZITE_DISTRICT_ALIAS.get(n, n)
    if n in by_norm_label:
        return by_norm_label[n]
    for cand, pc in by_norm_label.items():          # tolerate spelling drift
        if cand.startswith(n[:5]) or n.startswith(cand[:5]):
            return pc
    return ""

# ---------------------------------------------------------------- Source A: Kobo
KD, KSITE, KSITE2 = ("group_incident_basic/date_entry",
                     "group_general_info/final_site_name", "group_general_info/site_name")
KNEW, KOTH = "group_general_info/site_name_new", "group_general_info/site_name_other"

ko = pd.DataFrame(json.load(open("_cache_kobo.json", encoding="utf-8")))
kd = pd.to_datetime(ko[KD], errors="coerce")
ko_q2 = ko[(kd >= Q_START) & (kd <= Q_END)].copy()
ko_q2["_date"] = kd[(kd >= Q_START) & (kd <= Q_END)]

raw_id = ko_q2[KSITE].fillna(ko_q2[KSITE2]).astype(str).str.strip()
is_other = raw_id.str.lower().isin(["other", "nan", ""])
alt = ko_q2.get(KNEW, pd.Series("", index=ko_q2.index)).astype(str).str.strip()
alt = alt.where(alt.ne("") & alt.ne("nan"),
                ko_q2.get(KOTH, pd.Series("", index=ko_q2.index)).astype(str).str.strip())
ko_q2["_site_id"] = raw_id.where(~is_other, alt)
ko_q2["_name_unresolved"] = is_other
ko_q2["__source"] = "Kobo"
ko_q2["_partner"] = ko_q2["group_incident_basic/organization_updating"].astype(str)
ko_q2["_lat"] = pd.to_numeric(ko_q2.get("group_general_info/final_latitude"), errors="coerce")
ko_q2["_lon"] = pd.to_numeric(ko_q2.get("group_general_info/final_longitude"), errors="coerce")

# completeness = non-null scored indicators; dedupe keeps most recent, then most complete
ind_cols_k = [c for c in INDICATORS if c in ko_q2.columns]
ko_q2["_complete"] = ko_q2[ind_cols_k].notna().sum(axis=1)
before = len(ko_q2)
ko_q2 = (ko_q2.sort_values(["_date", "_complete"], ascending=[False, False])
              .drop_duplicates("_site_id", keep="first"))
collisions = before - len(ko_q2)

# ---------------------------------------------------------------- Source B: Zite (IOM)
zi = pd.DataFrame(json.load(open("_cache_zite.json", encoding="utf-8")))
zd = pd.to_datetime(zi["Date of Assessment"], errors="coerce")
zi_q2 = zi[(zd >= Q_START) & (zd <= Q_END)].copy()
zi_q2["_date"] = zd[(zd >= Q_START) & (zd <= Q_END)]

zmap = json.load(open("zite_map.json", encoding="utf-8"))
short2path = {k.split("/")[-1]: k for k in INDICATORS}
zrows = {}
for zcol, mname in zmap.items():
    path = short2path.get(mname)
    if path and zcol in zi_q2.columns:
        zrows[path] = zi_q2[zcol].map(lambda v, m=mname: to_code(m, v))
zn = pd.DataFrame(zrows, index=zi_q2.index)

zn["group_general_info/district"]  = zi_q2["Region Information/Region Name"].map(zite_district_to_pcode)
zn["group_general_info/region"]    = zn["group_general_info/district"].map(lambda d: dist_region.get(d, ""))
zn["group_general_info/subdistrict"] = zi_q2["Site Information/Primary Parent Site"]
zn["group_general_info/final_site_name"] = zi_q2["Site ID"]
zn["group_demographic_info/hhs"]   = zi_q2["DEMOGRAPHIC INFO/How many families are currently residing at the site? [Most Recent Value]"]
zn["group_demographic_info/inds"]  = zi_q2["DEMOGRAPHIC INFO/How many individuals are currently residing at the site? [Most Recent Value]"]
zn["group_incident_basic/organization_updating"] = "IOM"
zn["_site_id"] = zi_q2["Site ID"]
zn["_zite_name"] = zi_q2["Site Name"]
# Zite ships WKT "POINT(lon lat)" — longitude first. (The IOM Excel's own latitude/
# longitude columns are transposed: they hold 42-45 in 'latitude', which is a Somali
# longitude. Verified against Somalia's bounds; we take GPS from the API instead.)
_pt = zi_q2["Region Information/Location"].astype(str).str.extract(
        r"POINT\s*\(\s*([-\d.]+)\s+([-\d.]+)\s*\)")
zn["_lon"] = pd.to_numeric(_pt[0], errors="coerce")
zn["_lat"] = pd.to_numeric(_pt[1], errors="coerce")
zn["_name_unresolved"] = False
zn["__source"] = "Zite/IOM"
zn["_partner"] = "IOM"
zn["_date"] = zi_q2["_date"]
zn = zn.drop_duplicates("_site_id", keep="first")   # feed is already site-grain

# ---------------------------------------------------------------- union
df = pd.concat([ko_q2, zn], ignore_index=True, sort=False)
for c in ("Url",):   # Location already parsed into _lat/_lon above
    if c in df.columns: df = df.drop(columns=[c])

# pcodes -> OCHA/XLSForm admin names, so the dashboard reads as names not codes
DCOL, RCOL = "group_general_info/district", "group_general_info/region"
df["_dist_pcode"] = df[DCOL]
df[DCOL] = df[DCOL].map(lambda v: dist_label.get(str(v).strip(), str(v).strip()))
df[RCOL] = df[RCOL].map(lambda v: region_label.get(str(v).strip(), str(v).strip()))
# strip stray spaces in catchment codes (e.g. "CA03_G S" -> "CA03_GS")
CCOL = "group_general_info/subdistrict"
df[CCOL] = df[CCOL].astype(str).str.replace(r"_G\s+([NS])", r"_G\1", regex=True).replace("nan","")
still_code = df[DCOL].astype(str).str.match(r"^SO\d+$", case=False).sum()
if still_code:
    print(f"  WARNING: {still_code} rows kept a district pcode (no label in XLSForm)")

# Human-readable site names. Kobo stores the CCCM code in the site select_one; the
# XLSForm `site` choice list carries the actual name. Zite already sends a name.
# The code is kept in _site_id for export and matching.
SCOL = "group_general_info/final_site_name"
def display_name(r):
    code = str(r.get("_site_id", "")).strip()
    if r.get("__source") == "Zite/IOM":
        return str(r.get("_zite_name") or code).strip()
    nm = site_label.get(code)
    if nm:
        return nm
    return code            # 'other' rows already carry their free-text name here
df[SCOL] = df.apply(display_name, axis=1)
df["_partner"] = df["_partner"].map(lambda p: org_label.get(str(p).strip().lower(),
                                                            str(p).strip().upper()))
df["group_incident_basic/organization_updating"] = df["_partner"]
resolved = df[SCOL].ne(df["_site_id"]).sum()
print(f"  site names resolved to labels: {resolved} of {len(df)}")


print(f"Kobo   {QLABEL}: {before} submissions -> {len(ko_q2)} sites "
      f"({collisions} duplicate submissions collapsed)")
print(f"Zite   {QLABEL}: {len(zi_q2)} IOM sites")
print(f"UNION            : {len(df)} sites   "
      f"(name-unresolved: {int(df['_name_unresolved'].sum())})")
unmapped = zn["group_general_info/district"].eq("").sum()
if unmapped:
    print(f"  WARNING: {unmapped} IOM rows with unmapped district")

# ------------------------------------------- Master List Q2 + Site Verification join
# HH / individuals come from the CCCM Master List Q2 (authoritative population figures);
# age/sex comes from the Site Verification file. Neither is collected by the monitoring
# form. Join on CCCM site code first, then normalised district|site-name.
MLP = os.environ.get("MASTERLIST_PATH", os.path.join("data", "masterlist_q2.xlsx"))
SVP = os.environ.get("SITEVERIF_PATH", os.path.join("data", "site_verification.xlsx"))

def nm(s):
    s = unicodedata.normalize("NFKD", str(s)).lower()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s).split())

# The three sources spell the same districts differently. Left unmapped, the name stage
# silently fails for 932 of our sites (Baydhaba 565, Kahda 209, Daynile 158) because the
# Master List calls them Baidoa / Mogadishu Khada / Mogadishu Dayniile.
DISTRICT_CANON = {
    "baidoa": "baydhaba", "baydhabo": "baydhaba",
    "mogadishu khada": "kahda", "khada": "kahda", "kaxda": "kahda",
    "mogadishu dayniile": "daynile", "dayniile": "daynile", "deynile": "daynile",
    "kismayo": "kismaayo", "beled weyne": "belet weyne", "beletweyne": "belet weyne",
    "bardhere": "baardheere", "bardheere": "baardheere",
    "garbaharey": "garbahaarey", "las anod": "laas caanood",
}
def dcanon(s):
    n = nm(s)
    return DISTRICT_CANON.get(n, n)

ml = pd.read_excel(MLP, sheet_name="CCCM IDP Site List (Verified)", header=1)
ml.columns = [str(c).strip() for c in ml.columns]
MC, MH, MI = "CCCM IDP Site Code", "HH (Q2-2026)", "Individual (Q2-2026)"
n_all = len(ml)
ml = ml[ml[MC].astype(str).str.upper().str.startswith("CCCM")].copy()   # drop totals row
print(f"  Master List: {n_all} rows -> {len(ml)} sites (dropped {n_all-len(ml)} totals row)")
ml["_hh"]  = pd.to_numeric(ml[MH], errors="coerce")
ml["_ind"] = pd.to_numeric(ml[MI], errors="coerce")
ml["_k"]   = ml["District"].map(dcanon) + "|" + ml["IDP Site"].map(nm)

sv = pd.read_excel(SVP, sheet_name="Cleaned Site Verification")
AGE = ["Male <5","Female <5","Male 5-17","Female 5-17",
       "Male 18-59","Female 18-59","Male 60+","Female 60+"]
for c in AGE:
    sv[c] = pd.to_numeric(sv[c], errors="coerce")
sv["_k"] = sv["District Name"].map(dcanon) + "|" + sv["IDP Site Name"].map(nm)
sv["_c"] = sv["IDP Site Code"].astype(str).str.strip().str.upper()
sv["_lat"] = pd.to_numeric(sv["Latitude"], errors="coerce")
sv["_lon"] = pd.to_numeric(sv["Longitude"], errors="coerce")
sv = sv.dropna(subset=AGE, how="all").reset_index(drop=True)
sv["_dist_nm"] = sv["District Name"].map(dcanon)
sv["_name_nm"] = sv["IDP Site Name"].map(nm)

ml["_lat"] = pd.to_numeric(ml["Latitude"], errors="coerce")
ml["_lon"] = pd.to_numeric(ml["Longitude"], errors="coerce")
ml["_c"]   = ml[MC].astype(str).str.strip().str.upper()
ml["_k"]   = ml["District"].map(dcanon) + "|" + ml["IDP Site"].map(nm)
ml = ml.reset_index(drop=True)
ml["_dist_nm"] = ml["District"].map(dcanon)
ml["_name_nm"] = ml["IDP Site"].map(nm)

df["_k"]  = df[DCOL].map(dcanon) + "|" + df[SCOL].map(nm)
df["_cu"] = df["_site_id"].astype(str).str.strip().str.upper()
df["_dist_nm"] = df[DCOL].map(dcanon)
df["_name_nm"] = df[SCOL].map(nm)


# GPS is a TIE-BREAKER ONLY, never a primary key. Measured on these datasets, the median
# distance from a site to its nearest same-district neighbour is 46 m (Master List) and
# 34 m (Site Verification) — the same order as handheld GPS error. At 250 m tolerance 86%
# of Master List sites are ambiguous; even at 25 m, 22% are. A nearest-point match
# therefore picks the wrong site more often than not, so a GPS candidate is only accepted
# when district and site name independently agree.
GPS_TOL_M = 250.0

def match_rows(left, right, tol_m=GPS_TOL_M):
    """Resolve each left row to a right-row index: CCCM code, then district|name, then
    nearest GPS within tol_m. Returns (idx array, method array); idx -1 = unmatched."""
    import numpy as np
    by_code = {}
    for i, c in enumerate(right["_c"]):
        if isinstance(c, str) and c.startswith("CCCM"):
            by_code.setdefault(c, i)
    by_name = {}
    for i, k in enumerate(right["_k"]):
        by_name.setdefault(k, i)

    rdist_nm = right["_dist_nm"].tolist()
    rname_nm = right["_name_nm"].tolist()
    rlat = right["_lat"].to_numpy(dtype="float64")
    rlon = right["_lon"].to_numpy(dtype="float64")
    have = ~(np.isnan(rlat) | np.isnan(rlon))
    rlat_v, rlon_v = rlat[have], rlon[have]
    ridx_v = np.nonzero(have)[0]

    idx = np.full(len(left), -1, dtype="int64")
    how = np.array(["none"] * len(left), dtype=object)
    llat = left["_lat"].to_numpy(dtype="float64")
    llon = left["_lon"].to_numpy(dtype="float64")

    for i, (c, k) in enumerate(zip(left["_cu"], left["_k"])):
        j = by_code.get(c)
        if j is not None:
            idx[i], how[i] = j, "code"; continue
        j = by_name.get(k)
        if j is not None:
            idx[i], how[i] = j, "name"; continue
        la, lo = llat[i], llon[i]
        if np.isnan(la) or np.isnan(lo) or not len(ridx_v):
            continue
        # equirectangular approximation — accurate well below 1 km at these latitudes
        x = np.radians(rlon_v - lo) * np.cos(np.radians(la))
        y = np.radians(rlat_v - la)
        dist = 6371000.0 * np.sqrt(x * x + y * y)
        near = np.nonzero(dist <= tol_m)[0]
        if not len(near):
            continue
        # GPS ALONE IS NOT SAFE HERE: 86% of Master List sites have another site within
        # 250 m, so "nearest wins" picks the wrong site more often than not. Require the
        # candidate to agree on district AND on site name before accepting.
        ldist = left["_dist_nm"].iloc[i]
        lname = left["_name_nm"].iloc[i]
        best, best_score = None, 0.0
        for c in near:
            j = int(ridx_v[c])
            if rdist_nm[j] and ldist and rdist_nm[j] != ldist:
                continue
            score = SequenceMatcher(None, lname, rname_nm[j]).ratio() if lname else 0.0
            if score > best_score:
                best, best_score = j, score
        if best is not None and best_score >= 0.86:
            idx[i], how[i] = best, "gps+name"
    return idx, how

ml_idx, ml_how = match_rows(df, ml)
sv_idx, sv_how = match_rows(df, sv)

df["_ml_hh"]  = [float(ml["_hh"].iloc[j])  if j >= 0 and pd.notna(ml["_hh"].iloc[j])  else None for j in ml_idx]
df["_ml_ind"] = [float(ml["_ind"].iloc[j]) if j >= 0 and pd.notna(ml["_ind"].iloc[j]) else None for j in ml_idx]
df["_ml_matched"] = [j >= 0 for j in ml_idx]
df["_sv_matched"] = [j >= 0 for j in sv_idx]
df["_sv_idx"] = sv_idx          # kept on the frame so it survives the dedup below

n_ml, n_sv = int(df["_ml_matched"].sum()), int(df["_sv_matched"].sum())
print(f"  Master List Q2 matched   : {n_ml} of {len(df)}  " + str(dict(Counter(ml_how))))
print(f"  Site Verification matched: {n_sv} of {len(df)}  " + str(dict(Counter(sv_how))))

# ------------------------------------------- canonical site identity + cross-source dedup
# A Master List match gives a site its canonical CCCM code — including free-text "other"
# rows and IOM rows (whose CCCM-BDA-* codes never reconcile directly). Two rows resolving
# to the same canonical code are the same site reported twice (two partners, or a
# free-text duplicate of a coded submission): keep the most recent/most complete, log the
# rest. This is the resolution step the published round applied; without it we carried
# 1,321 sites against its 1,275.
df["_canon"] = [ml["_c"].iloc[j] if j >= 0 else None for j in ml_idx]
resolved_other = int((df["_canon"].notna() & df["_name_unresolved"]).sum())
df.loc[df["_canon"].notna(), "_name_unresolved"] = False
df["_key"] = df["_canon"].fillna(df["_cu"])
df.loc[df["_canon"].notna(), "_site_id"] = df.loc[df["_canon"].notna(), "_canon"]

_indcols = [c for c in INDICATORS if c in df.columns]
df["_complete"] = df["_complete"].fillna(df[_indcols].notna().sum(axis=1))
before_dd = len(df)
dup_mask = df.duplicated("_key", keep=False)
xsrc = df.loc[dup_mask].groupby("_key")["__source"].nunique()
df = (df.sort_values(["_date", "_complete"], ascending=[False, False])
        .drop_duplicates("_key", keep="first").reset_index(drop=True))
site_collisions = before_dd - len(df)
print(f"  canonical resolution     : {resolved_other} free-text names resolved to CCCM codes")
print(f"  cross-source dedup       : {before_dd} -> {len(df)} sites "
      f"({site_collisions} duplicates collapsed, {(xsrc > 1).sum()} across two sources)")
print(f"  vs published Q2 (1,275)  : {len(df) - 1275:+d}")

demo_rows = [sv.iloc[int(j)][AGE].to_dict() if j >= 0 else None for j in df["_sv_idx"]]
n_ml = int(df["_ml_matched"].sum()); n_sv = int(df["_sv_matched"].sum())

# Population: prefer the Master List figure; fall back to the monitoring form.
HHC, INDC = "group_demographic_info/hhs", "group_demographic_info/inds"
form_hh  = pd.to_numeric(df[HHC], errors="coerce")
form_ind = pd.to_numeric(df[INDC], errors="coerce")
df[HHC]  = pd.Series(df["_ml_hh"]).fillna(form_hh)
df[INDC] = pd.Series(df["_ml_ind"]).fillna(form_ind)
print(f"  population: Master List for {n_ml} sites, monitoring form for {len(df)-n_ml}")

# Age/sex totals across SV-matched sites only
bands = [("0-4","Male <5","Female <5"), ("5-17","Male 5-17","Female 5-17"),
         ("18-59","Male 18-59","Female 18-59"), ("60+","Male 60+","Female 60+")]
tot = {c: 0.0 for c in AGE}
for v in demo_rows:
    if v is None: continue
    for c in AGE:
        x = v.get(c)
        if x is not None and pd.notna(x): tot[c] += float(x)
grand = sum(tot.values())
print(f"  age/sex total across matched sites: {grand:,.0f} individuals")

# ---------------------------------------------------------------- score / aggregate
sites, review, present = bd.transform(df)
if not sites:
    raise SystemExit("no scorable sites")
data = bd.aggregate(sites, present, df)
data["kpi"]["quarter"] = QLABEL
data["kpi"]["partners"] = int(df["_partner"].nunique())
data["kpi"]["regions"] = int(df[RCOL].astype(str).str.strip().replace("", pd.NA).nunique())
# No prior-quarter dataset is present in this working directory. aggregate() defaults q1
# to a copy of q2, which would render as "coverage unchanged" — a claim we cannot make.
data["generated"] = pd.Timestamp.now().strftime("%d %B %Y")

# ---------------------------------------------------------------- Q1 2026 baseline
# Published figures, CCCM Cluster Somalia Site Monitoring Report, Q1 2026 (p.1) and the
# Q2 2026 report's "Coverage change Q1 -> Q2" table (p.5). Entered from the published
# reports — NOT recomputed here, because no Q1 dataset exists in this directory.
Q1_PUBLISHED = {"Sites": 1902, "Catchments": 42, "HHs": 281962,
                "Individuals": 1647023, "Partners": 9, "Districts": 17}
Q2_PUBLISHED = {"Sites": 1275, "Catchments": 36, "HHs": 131520,
                "Individuals": 719747, "Partners": 7, "Districts": 16}
data["q1"] = {k: [Q2_PUBLISHED[k], Q1_PUBLISHED[k]] for k in Q1_PUBLISHED}
data["hasQ1Baseline"] = True
data["q1Source"] = ("Baseline: published CCCM Cluster Somalia Q1 2026 figures. "
                    "Coverage narrowed: 14 of Mogadishu's 26 catchments were not assessed "
                    "in Q2. Severity is not like-for-like across quarters.")

# ---------------------------------------------------------------- demographics (computed)
# Computed from IDP_Site_Verification_CLEANED_Q1-2026.xlsx, summed over the sites in this
# quarter that matched by CCCM code or district|site-name. Age/sex is not captured by the
# monitoring form or the Q2 Master List, so this is the only source for it.
male   = sum(tot[c] for c in AGE if c.startswith("Male"))
female = sum(tot[c] for c in AGE if c.startswith("Female"))
pct = lambda v: round(100.0 * v / grand, 1) if grand else 0.0
data["demographics"] = {
  "total": int(grand), "matchedSites": n_sv,
  "malePct": pct(male), "femalePct": pct(female),
  "source": (f"Age/sex computed from the IDP Site Verification dataset, summed over the "
             f"{n_sv} of {len(df)} sites in this quarter that matched by CCCM site code or "
             f"district + site name. Not collected by the monitoring form or the Q2 Master "
             f"List. Verification totals are Q1-2026 vintage."),
  "bands": [{"age": lab,
             "mN": int(tot[mc]), "mP": pct(tot[mc]),
             "fN": int(tot[fc]), "fP": pct(tot[fc])} for lab, mc, fc in reversed(bands)]}

# ---------------------------------------------------------------- branding assets
# Embedded base64 so the dashboard stays a single self-contained offline file.
import base64, glob
def _b64(path):
    with open(path, "rb") as fh:
        return "data:image/png;base64," + base64.b64encode(fh.read()).decode()

ICON_FOR = {"CCCM": "CCCM icon.png", "Prot": "Protection.png", "CP": "CP.png",
            "GBV": "GBV.png", "HLP": "HLP.png", "NFI": "Shelter SNFI.png",
            "Shel": "Shelter SNFI.png", "WASH": "WASH.png", "Hlth": "Health .png",
            "FSL": "Food Security .png", "Nutr": "Natrution .png", "Educ": "Eduction.png"}
icons, missing = {}, []
for code, fn in ICON_FOR.items():
    p = os.path.join("icons", fn)
    if os.path.exists(p):
        icons[code] = _b64(p)
    else:
        missing.append(fn)
logo_p = os.path.join("logo", "CCCMCluster_Somalia.png")
data["assets"] = {"logo": _b64(logo_p) if os.path.exists(logo_p) else "", "icons": icons}
print(f"  assets embedded: logo={'yes' if data['assets']['logo'] else 'NO'}, "
      f"icons={len(icons)}/12" + (f"  MISSING: {missing}" if missing else ""))

# short keys for the front-end payload
for s in data["sites"]:
    s["p"]    = s.pop("_partner", "")
    s["code"] = s.pop("_code", "")
    s["src"]  = s.pop("_src", "")
    s["hh"]   = s.pop("_hh", None)
    s["ind"]  = s.pop("_ind", None)
data["partners"] = sorted({s["p"] for s in data["sites"] if s["p"]})
data["provenance"] = {"kobo_sites": int(len(ko_q2)), "iom_sites": int(len(zn)),
                      "quarter": QLABEL, "window": [Q_START, Q_END]}

json.dump(data, open("dashboard_data.json", "w", encoding="utf-8"), ensure_ascii=False)

SEC_ORDER = ["CCCM","Protection","CP","GBV","HLP","NFI","Shelter","WASH","Health",
             "FSL","Nutrition","Education"]
# built AFTER the short-key rename above, so read the short keys — not the popped ones
out = [{"region": s["r"], "district": s["d"], "ca": s["c"], "site": s["s"],
        "code": s.get("code",""), "partner": s.get("p",""),
        "source": s.get("src",""), "hh": s.get("hh"), "individuals": s.get("ind"),
        "severity": s["v"], "band": s["b"],
        "scores": dict(zip(SEC_ORDER, s["sc"]))} for s in sites]
json.dump(out, open("sites.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

with open("review_queue.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["reason","site_id","district","partner","source"])
    for _, r in df[df["_name_unresolved"]].iterrows():
        w.writerow(["name_pending_verification", r.get("_site_id",""),
                    r.get("group_general_info/district",""), r.get("_partner",""),
                    r.get("__source","")])
    for r in review:
        w.writerow(["no_assessed_sector", r.get("_site_id",""),
                    r.get("group_general_info/district",""), r.get("_partner",""),
                    r.get("__source","")])

bd.render(data)

# ---------------------------------------------------------------- scrub
# Precise patterns. A bare "http"/"key=" substring test false-positives on the SVG
# xmlns namespace and on JS arrow params (`key=>{}`), which trains people to ignore
# the check. Match the actual secrets and real endpoint shapes instead.
def scrub(path):
    blob = open(path, "rb").read().decode("latin-1")
    low  = blob.lower()
    hits = []
    for name, val in (("ZITE_FULL_KEY", os.environ.get("ZITE_FULL_KEY","")),
                      ("KOBO_API_TOKEN", os.environ.get("KOBO_API_TOKEN",""))):
        if val and val in blob:
            hits.append(f"{name}_VALUE")
    for lit in ("zitemanager", "kf.kobo.iom.int", "/api/v2/", "reports-file"):
        if lit in low:
            hits.append(lit)
    if re.search(r"[?&]key=", low):        hits.append("query_param_key")
    if re.search(r"authorization\s*:\s*token", low): hits.append("auth_header")
    if re.search(r"https?://(?!www\.w3\.org)", low): hits.append("external_url")
    return hits

leaks = {a: h for a in ("dashboard_data.json","sites.json","review_queue.csv",
                        "CCCM_Site_Monitoring_Dashboard.html")
         if os.path.exists(a) and (h := scrub(a))}
print("\nscrub:", "clean" if not leaks else f"LEAK {leaks}")
if leaks:
    raise SystemExit("sensitive string in published artefact")
_src_n = df["__source"].value_counts()
json.dump({"union": len(df), "kobo": int(_src_n.get("Kobo", 0)),
           "iom": int(_src_n.get("Zite/IOM", 0)),
           "scored": len(sites), "review": len(review),
           "unresolved": int(df["_name_unresolved"].sum()),
           "collisions": collisions, "site_collisions": site_collisions,
           "resolved_other": resolved_other, "leaks": leaks},
          open("_build_stats.json","w",encoding="utf-8"))
