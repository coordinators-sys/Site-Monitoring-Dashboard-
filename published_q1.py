"""Published Q1 2026 facts, hand-transcribed and page-verified from the officially
released CCCM Cluster Somalia Site Monitoring Report Q1 2026 (national),
source: SiteMonitoringReport_National_Q12026_CCCMClusterSomalia.pdf, page 1
(the summary dashboard page). Every figure here is printed on that page.

Q1 is presented here at the same "published" status as Q2. The report's national
summary page discloses sector-level gap/coverage rankings, the top-10 red and green
indicators (as counts of camps), and the top-10 districts by gap and by coverage —
so Q1 gets a real Overview, Sector Analysis and District ranking, all reconciling to
the published 1,902 assessed sites.

NOT taken from the site-level annex: the annex (pages 2-52) lists every site with a
severity dot grid, but OCR of 1,902 rows does not reconcile exactly to 1,902, so the
annex is NOT used for any headline figure. Only the exact page-1 numbers are used.
"""

SOURCE = "CCCM Cluster Somalia Site Monitoring Report Q1 2026 (national)"
PERIOD = "Q1 2026 (January–March)"

# p.1 KPI panel
KPI = {"sites": 1902, "catchments": 42, "hhs": 281962, "individuals": 1647023,
       "partners": 9, "districts": 17, "severity": None}
CATCHMENTS_TOTAL = 53          # "42 catchments assessed out of 53 CCCM covered CAs"
HH_TOTAL = 614590
IND_TOTAL = 3300000            # "out of total 3.3 million individuals"

PARTNERS_NOTE = "9 partners assessed sites in Q1 2026."

# p.1 "SECTORS RANKED BY % OF CAMPS WITH MOST SERVICE GAPS" and "...MOST SERVICE
# COVERAGE" — two separate rankings on the page, paired here by sector. As in the
# Q2 report, gap% and coverage% are independent "% of camps" metrics and do not
# necessarily sum to 100.
SECTORS = [
    {"name": "Non-Food Items",              "code": "NFI",  "gap": 90, "cov": 10},
    {"name": "Shelter",                      "code": "Shel", "gap": 70, "cov": 30},
    {"name": "Housing, Land & Property",     "code": "HLP",  "gap": 52, "cov": 48},
    {"name": "WASH",                         "code": "WASH", "gap": 50, "cov": 32},
    {"name": "Food Security & Livelihoods",  "code": "FSL",  "gap": 49, "cov": 44},
    {"name": "Child Protection",             "code": "CP",   "gap": 45, "cov": 55},
    {"name": "Protection",                   "code": "Prot", "gap": 42, "cov": 58},
    {"name": "Health",                       "code": "Hlth", "gap": 41, "cov": 54},
    {"name": "Nutrition",                    "code": "Nutr", "gap": 37, "cov": 54},
    {"name": "GBV",                          "code": "GBV",  "gap": 35, "cov": 35},
    {"name": "CCCM",                         "code": "CCCM", "gap": 32, "cov": 64},
    {"name": "Education",                    "code": "Educ", "gap": 15, "cov": 33},
]

# p.1 "Top 10 Indicators for which most camps indicated service gaps (Scored Red)".
# The page prints COUNTS of camps; pct is that count over the 1,902 assessed sites.
_N = 1902
def _pct(c): return round(c / _N * 100)
TOP_RED = [
    {"rank": 1,  "indicator": "Insufficient or non-functional latrines",           "n": 1845, "sector": "WASH"},
    {"rank": 2,  "indicator": "Shelter provided not adequate",                      "n": 1738, "sector": "Shel"},
    {"rank": 3,  "indicator": "No household participation in income-generating activities", "n": 1689, "sector": "FSL"},
    {"rank": 4,  "indicator": "No feedback collected on NFI quality/usefulness",    "n": 1688, "sector": "NFI"},
    {"rank": 5,  "indicator": "Vulnerable households not prioritized for NFI",      "n": 1655, "sector": "NFI"},
    {"rank": 6,  "indicator": "Lack of gender-separated WASH facilities",           "n": 1542, "sector": "WASH"},
    {"rank": 7,  "indicator": "No hygiene kits distributed",                        "n": 1532, "sector": "WASH"},
    {"rank": 8,  "indicator": "Lack of cash assistance provision",                  "n": 1526, "sector": "FSL"},
    {"rank": 9,  "indicator": "No on-site food distribution (when needed)",         "n": 1526, "sector": "FSL"},
    {"rank": 10, "indicator": "Lack of ambulance service",                          "n": 1525, "sector": "Hlth"},
]
# p.1 "Top 10 Indicators for which most camps indicated service sufficiency (Scored Green)"
TOP_GREEN = [
    {"rank": 1,  "indicator": "Functioning & inclusive CMC",                        "n": 1859, "sector": "CCCM"},
    {"rank": 2,  "indicator": "Accessible & functioning CFM",                       "n": 1825, "sector": "CCCM"},
    {"rank": 3,  "indicator": "CMC actively resolving issues",                      "n": 1731, "sector": "CCCM"},
    {"rank": 4,  "indicator": "Community sessions held on risks/needs",             "n": 1520, "sector": "Prot"},
    {"rank": 5,  "indicator": "Engagement on aid diversion",                        "n": 1514, "sector": "CCCM"},
    {"rank": 6,  "indicator": "Access to market available",                         "n": 1465, "sector": "FSL"},
    {"rank": 7,  "indicator": "GBV information/feedback mechanism available",        "n": 1428, "sector": "GBV"},
    {"rank": 8,  "indicator": "Coordination meetings conducted",                    "n": 1424, "sector": "CCCM"},
    {"rank": 9,  "indicator": "Community aware of & using GBV referral",            "n": 1409, "sector": "GBV"},
    {"rank": 10, "indicator": "GBV awareness campaigns conducted",                  "n": 1362, "sector": "GBV"},
]
for _r in TOP_RED + TOP_GREEN:
    _r["pct"] = _pct(_r["n"])
    _r["lc"] = False

# p.1 "Top 10 Districts Ranked by % of Camps With Most Service Gaps" and "...Most
# Service Coverage". The union of the two lists is 17 districts — exactly the "17
# districts covered" KPI. Region is mapped from the district. gap/cov are shown only
# where the district appears in the corresponding ranking (a dash otherwise); the
# Q1 report did not publish per-district site counts on this page.
_REGION = {"Laas Caanood": "Sool", "Luuq": "Gedo", "Baardheere": "Gedo", "Baraawe": "Lower Shabelle",
           "Afgooye": "Lower Shabelle", "Xudur": "Bakool", "Garbahaarey": "Gedo", "Diinsoor": "Bay",
           "Afmadow": "Lower Juba", "Kahda": "Banadir", "Doolow": "Gedo", "Gaalkacyo": "Mudug",
           "Kismaayo": "Lower Juba", "Belet Weyne": "Hiraan", "Daynile": "Banadir",
           "Baydhaba": "Bay", "Jamaame": "Lower Juba"}
_GAP = {"Laas Caanood": 71, "Luuq": 63, "Baardheere": 63, "Baraawe": 61, "Afgooye": 61,
        "Xudur": 60, "Garbahaarey": 60, "Diinsoor": 57, "Afmadow": 53, "Kahda": 51}
_COV = {"Doolow": 67, "Gaalkacyo": 61, "Kismaayo": 58, "Belet Weyne": 55, "Daynile": 48,
        "Baydhaba": 48, "Jamaame": 41, "Kahda": 40, "Afmadow": 40, "Afgooye": 36}
DISTRICTS_RANKED = [
    {"district": d, "region": _REGION[d], "gap": _GAP.get(d), "cov": _COV.get(d),
     "n": None, "bands": None}
    for d in sorted(_REGION, key=lambda d: (-(_GAP.get(d) if _GAP.get(d) is not None else -1),
                                            -(_COV.get(d) if _COV.get(d) is not None else -1)))
]

KEY_FINDINGS = [
    ("Widest service gap", "Non-Food Items (NFI)",
     "90% of assessed camps indicated a service gap — the highest of any sector"),
    ("Highest-priority district", "Laas Caanood",
     "71% of camps indicated service gaps — the highest of any district"),
    ("Strongest service coverage", "Functioning & inclusive CMC",
     "1,859 of 1,902 assessed camps (98%) reported this in place"),
    ("Assessment scope", "1,902 sites · 17 districts",
     "42 of 53 CCCM-covered catchment areas were assessed this quarter"),
]

LIMITATIONS = [
    "Results represent assessed sites, not every displacement site in Somalia.",
    "Q1 2026 figures are the officially published national report totals; per-district "
    "site counts and per-sector indicator breakdowns were not published at that "
    "granularity, and appear as a dash where unavailable.",
    "Missing and Not Applicable responses are excluded from the denominator and are "
    "never counted as Red.",
    "Direct quarter-to-quarter comparison may be affected by changing coverage: "
    "1,902 sites were assessed in Q1 2026 versus 1,275 in Q2 2026.",
]
