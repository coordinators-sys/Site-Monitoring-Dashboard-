#!/usr/bin/env python3
"""STEP 3 profile of the Kobo submissions cache — the checks that caught the
scope and grain problems in the Zite feed, applied to the larger source."""
import json
import pandas as pd

df = pd.DataFrame(json.load(open("_cache_kobo.json", encoding="utf-8")))
print(f"records : {len(df)}")
print(f"columns : {df.shape[1]}")

DATE   = "group_incident_basic/date_entry"
SUBMIT = "_submission_time"
SITE   = "group_general_info/final_site_name"
SITE2  = "group_general_info/site_name"
DIST   = "group_general_info/district"
REG    = "group_general_info/region"
CA     = "group_general_info/subdistrict"
ORG    = "group_incident_basic/organization_updating"
HH     = "group_demographic_info/hhs"
IND    = "group_demographic_info/inds"

for c in (DATE, SUBMIT, SITE, SITE2, DIST, ORG):
    print(f"  {'OK ' if c in df.columns else 'MISSING'}  {c}")

# ---- dates -----------------------------------------------------------------
d = pd.to_datetime(df[DATE], errors="coerce")
print(f"\nDATE OF ASSESSMENT: min={d.min()}  max={d.max()}  unparsed={d.isna().sum()}")
q = d.dt.to_period("Q").astype(str)
print("\nby quarter (date_entry):")
for k, v in sorted(q.value_counts().items()):
    print(f"   {k}: {v}")

s = pd.to_datetime(df[SUBMIT], errors="coerce", utc=True)
print(f"\nSUBMISSION TIME: min={s.min()}  max={s.max()}")
print("by quarter (_submission_time):")
for k, v in sorted(s.dt.to_period("Q").astype(str).value_counts().items()):
    print(f"   {k}: {v}")

q2 = q == "2026Q2"
print(f"\nIN Q2 2026 by date_entry: {q2.sum()} of {len(df)}   OUT: {(~q2).sum()}")

# ---- grain -----------------------------------------------------------------
site = df[SITE].fillna(df[SITE2]) if SITE in df.columns else df[SITE2]
print(f"\nGRAIN (all records): {len(df)} rows vs {site.nunique()} distinct site names")
sub = df[q2]
site_q2 = site[q2]
print(f"GRAIN (Q2 only)    : {len(sub)} rows vs {site_q2.nunique()} distinct site names")
dup = site_q2.value_counts()
print(f"  sites with >1 Q2 submission: {(dup > 1).sum()}   max submissions/site: {dup.max()}")

# ---- admin -----------------------------------------------------------------
print(f"\nregions (Q2): {sub[REG].nunique()}   districts (Q2): {sub[DIST].nunique()}   "
      f"catchments (Q2): {sub[CA].nunique()}")
print("\ntop districts (Q2):")
for k, v in sub[DIST].value_counts().head(12).items():
    print(f"   {k}: {v}")
print(f"\npartners (Q2): {sub[ORG].nunique()}")
for k, v in sub[ORG].value_counts().head(12).items():
    print(f"   {k}: {v}")

# ---- IOM present in Kobo? --------------------------------------------------
iom = sub[ORG].astype(str).str.contains("iom", case=False, na=False)
print(f"\nrows in Q2 Kobo whose partner looks like IOM: {iom.sum()}")

# ---- demographics ----------------------------------------------------------
for lab, c in (("households", HH), ("individuals", IND)):
    v = pd.to_numeric(sub[c], errors="coerce")
    print(f"{lab} (Q2): total={v.sum():,.0f}  n={v.notna().sum()}  null={v.isna().sum()}")
