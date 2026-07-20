"""Published Q2 2026 facts, hand-transcribed and page-verified from the officially
released CCCM Cluster Somalia Site Monitoring Report Q2 2026 v1.1 (published 03 July
2026), source: SiteMonitoring_Report_Q2_2026_National_CCCM.pdf, pages 3-7.

This is the ONLY data source for the public dashboard. Nothing here is derived from
the live draft rebuild. Every figure is either a number printed in the PDF, or an
arithmetic combination of two numbers printed in the PDF (each such case is commented
with which page and which two source numbers it combines).

If a public visual needs a number not in this file, the answer is "not published at
this granularity" - it must not be filled in from the draft dataset.
"""

SOURCE = "CCCM Cluster Somalia Site Monitoring Report Q2 2026 v1.1, published 03 July 2026"
PERIOD = "Q2 2026 (April–June)"

KPI = {"sites": 1275, "catchments": 36, "hhs": 131520, "individuals": 719747,
       "partners": 7, "districts": 16, "severity": 44.6}

PARTNERS = ["ACTED", "AMARD", "DRC", "IOM", "NoFYL", "SCC", "SWCRI"]

# p.3: "14 of Mogadishu's 26 catchments were not assessed this quarter"
MOGADISHU_UNASSESSED_CAS = ["CA01", "CA02", "CA03", "CA04", "CA05", "CA07", "CA08",
                            "CA10", "CA11", "CA12", "CA16", "CA24", "CA25", "CA26"]
MOGADISHU_TOTAL_CAS = 26
MOGADISHU_UNASSESSED_N = 14

# p.3 "Coverage this quarter" table + p.5 "Coverage change Q1->Q2 2026" table
Q1 = {"sites": 1902, "catchments": 42, "hhs": 281962, "individuals": 1647023,
      "partners": 9, "districts": 17}

# p.3 Key Findings box. The "84% Red" (p.7 Top-10 Red chart) and "869 of 1,275" (p.3
# prose) are BOTH printed in the source report as if they reconcile - they do not
# (869/1275 = 68.2%, not 84%). 869 / 0.84 = 1034.5, so the chart's 84% is over an
# applicable base of ~1,034 sites (some sites are N/A for this indicator), not the
# full 1,275 - consistent with the report's own footnote "rows may not sum to 100%
# where indicators were not applicable." The exact applicable N is not separately
# disclosed, so it is shown as an approximation, not asserted as exact.
WIDEST_GAP = {"indicator": "On-site food or cash distribution", "redPct": 84,
              "nRed": 869, "approxApplicable": 1034,
              "note": ("The published 84% and the published count of 869 sites do not "
                       "share the same base: 869 ÷ 84% implies an applicable base of "
                       "about 1,034 sites (some sites are not applicable for this "
                       "indicator). The exact applicable count is not separately "
                       "disclosed in the published report.")}

# p.7 "Sectors - sorted by gap severity" (gap%, coverage%). Rows do not always sum to
# 100 - remainder is Yellow/partial or not-applicable, per the report's own footnote.
SECTORS = [
    {"name": "Child Protection",              "code": "CP",   "gap": 59, "cov": 41},
    {"name": "Shelter",                        "code": "Shel", "gap": 49, "cov": 51},
    {"name": "WASH",                           "code": "WASH", "gap": 49, "cov": 43},
    {"name": "Housing, Land & Property",       "code": "HLP",  "gap": 49, "cov": 51},
    {"name": "Food Security & Livelihoods",    "code": "FSL",  "gap": 47, "cov": 40},
    {"name": "Health",                         "code": "Hlth", "gap": 42, "cov": 54},
    {"name": "GBV",                            "code": "GBV",  "gap": 35, "cov": 65},
    {"name": "Protection",                     "code": "Prot", "gap": 34, "cov": 66},
    {"name": "Non-Food Items",                 "code": "NFI",  "gap": 34, "cov": 66},
    {"name": "CCCM",                           "code": "CCCM", "gap": 33, "cov": 67},
    {"name": "Education",                      "code": "Educ", "gap": 33, "cov": 64},
    {"name": "Nutrition",                      "code": "Nutr", "gap": 32, "cov": 59},
]

# p.7 "Top 10 Indicators - Red (Gaps)". learningCentre marks the report's own
# dagger-note "Learning-centre sites only (n=690)".
TOP_RED = [
    {"rank": 1,  "indicator": "On-site food/cash distribution",      "pct": 84, "lc": False, "sector": "FSL"},
    {"rank": 2,  "indicator": "Ambulance service available",         "pct": 81, "lc": False, "sector": "Hlth"},
    {"rank": 3,  "indicator": "Gender-separated WASH facilities",    "pct": 79, "lc": False, "sector": "WASH"},
    {"rank": 4,  "indicator": "School feeding programmes",           "pct": 78, "lc": True,  "sector": "Educ"},
    {"rank": 5,  "indicator": "Shelter repair kits available",       "pct": 75, "lc": False, "sector": "Shel"},
    {"rank": 6,  "indicator": "Hygiene kits distributed",            "pct": 73, "lc": False, "sector": "WASH"},
    {"rank": 7,  "indicator": "Site decongestion activities",        "pct": 70, "lc": False, "sector": "CCCM"},
    {"rank": 8,  "indicator": "Unaccompanied/separated children",    "pct": 70, "lc": False, "sector": "CP"},
    {"rank": 9,  "indicator": "WASH waste-management kits",          "pct": 64, "lc": False, "sector": "WASH"},
    {"rank": 10, "indicator": "CMC received training",               "pct": 63, "lc": False, "sector": "CCCM"},
]
# p.7 "Top 10 Indicators - Green (Coverage)"
TOP_GREEN = [
    {"rank": 1,  "indicator": "Accessible & functioning CFM",              "pct": 97, "lc": False, "sector": "CCCM"},
    {"rank": 2,  "indicator": "Functional & inclusive CMC",                "pct": 95, "lc": False, "sector": "CCCM"},
    {"rank": 3,  "indicator": "Cash used without restrictions",            "pct": 93, "lc": False, "sector": "FSL"},
    {"rank": 4,  "indicator": "Functional learning-centre latrines",       "pct": 91, "lc": True,  "sector": "Educ"},
    {"rank": 5,  "indicator": "CMC resolves issues",                       "pct": 88, "lc": False, "sector": "CCCM"},
    {"rank": 6,  "indicator": "School support committees",                 "pct": 80, "lc": True,  "sector": "Educ"},
    {"rank": 7,  "indicator": "Community in school management",           "pct": 79, "lc": True,  "sector": "Educ"},
    {"rank": 8,  "indicator": "Market access for goods",                  "pct": 79, "lc": False, "sector": "FSL"},
    {"rank": 9,  "indicator": "Enough learning-centre space",              "pct": 78, "lc": True,  "sector": "Educ"},
    {"rank": 10, "indicator": "Community-led risk sessions",               "pct": 77, "lc": False, "sector": "CCCM"},
]
LC_SAMPLE_NOTE = "Learning-centre sites only (n=690)"

# p.7 "Districts - >=10 assessed sites - sorted by gap severity" (exact gap/coverage %)
# p.4 map panels give exact severity-band COUNTS for 4 of these (Baydhaba, Gaalkacyo,
# Kismaayo, and the combined Mogadishu panel = Kahda + Daynile: 183+158=341, matching
# the map's stated total exactly). Bands for Kahda and Daynile individually are not
# separately published - only their combined total appears with bands.
DISTRICTS_RANKED = [
    {"district": "Afmadow",    "region": "Lower Juba",     "n": 11,  "gap": 67, "cov": 33, "bands": None},
    {"district": "Xudur",      "region": "Bakool",         "n": 71,  "gap": 61, "cov": 39, "bands": None},
    {"district": "Baardheere", "region": "Gedo",           "n": 31,  "gap": 60, "cov": 40, "bands": None},
    {"district": "Kahda",      "region": "Banadir",        "n": 183, "gap": 57, "cov": 43, "bands": None},
    {"district": "Daynile",    "region": "Banadir",        "n": 158, "gap": 53, "cov": 47, "bands": None},
    {"district": "Luuq",       "region": "Gedo",           "n": 39,  "gap": 51, "cov": 49, "bands": None},
    {"district": "Gaalkacyo",  "region": "Mudug",          "n": 41,  "gap": 49, "cov": 51,
     "bands": {"Severe": 10, "High": 20, "Moderate": 10, "Low": 1}},
    {"district": "Baydhaba",   "region": "Bay",            "n": 559, "gap": 38, "cov": 62,
     "bands": {"Severe": 108, "High": 148, "Moderate": 123, "Low": 180}},
    {"district": "Kismaayo",   "region": "Lower Juba",     "n": 133, "gap": 29, "cov": 71,
     "bands": {"Severe": 0, "High": 18, "Moderate": 64, "Low": 51}},
    {"district": "Belet Weyne","region": "Hiraan",         "n": 23,  "gap": 23, "cov": 77, "bands": None},
]
# The remaining 6 districts share the 16-10=6 slots and 1275-sum(above)=26 sites,
# each individually below the report's own 10-site ranking threshold.
DISTRICTS_BELOW_THRESHOLD_N = 16 - len(DISTRICTS_RANKED)
DISTRICTS_BELOW_THRESHOLD_SITES = KPI["sites"] - sum(d["n"] for d in DISTRICTS_RANKED)

MOGADISHU_COMBINED = {"district": "Mogadishu (Kahda + Daynile, combined)",
                      "n": 341, "bands": {"Severe": 153, "High": 150, "Moderate": 22, "Low": 16}}

# p.6 Demographic Profile - "Verified figures for 168,478 individuals; 205 matched sites"
DEMOGRAPHICS = {
    "total": 168478, "matchedSites": 205, "malePct": 46.4, "femalePct": 53.6,
    "bands": [
        {"age": "60+",   "mN": 6750,  "mP": 4.0,  "fN": 8269,  "fP": 4.9},
        {"age": "18-59", "mN": 25340, "mP": 15.0, "fN": 27591, "fP": 16.4},
        {"age": "5-17",  "mN": 22369, "mP": 13.3, "fN": 26150, "fP": 15.5},
        {"age": "0-4",   "mN": 23781, "mP": 14.1, "fN": 28228, "fP": 16.8},
    ]}

KEY_FINDINGS = [
    ("Widest service gap", "On-site food/cash distribution",
     "84% of applicable sites scored Red (869 sites; applicable base ≈ 1,034 of 1,275 assessed)"),
    ("Highest-priority district (≥10 sites)", "Afmadow",
     "67% Red — 11 assessed sites"),
    ("Strongest service coverage", "Accessible & functioning CFM",
     "97% of assessed sites scored Green"),
    ("Main assessment-coverage limitation", "Mogadishu catchment coverage",
     "14 of 26 Mogadishu catchment areas were not assessed this quarter"),
]

LIMITATIONS = [
    "Results represent assessed sites, not every displacement site in Somalia.",
    "Direct quarter-to-quarter comparison may be affected by changing coverage: "
    "1,902 sites were assessed in Q1 2026 versus 1,275 in Q2 2026.",
    "Missing and Not Applicable responses are excluded from the denominator and are "
    "never counted as Red.",
    "Districts with fewer than 10 assessed sites are not included in the national "
    "district ranking; results for small samples should be interpreted cautiously.",
]

CONTACT = {"im": "im@cccmclustersomalia.org",
           "coordination": "coordinators@cccmclustersomalia.org"}
