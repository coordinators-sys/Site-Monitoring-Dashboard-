#!/usr/bin/env python3
"""
CCCM Somalia — Site Monitoring Dashboard: live-data pipeline
============================================================
Fetch KoboToolbox (all partners except IOM) + Zite Manager (IOM sites),
union + clean + score per the cluster methodology, then regenerate the
self-contained interactive dashboard.

USAGE
-----
    export KOBO_API_TOKEN="xxxxxxxxxxxxxxxxxxxx"      # kf.kobo.iom.int API token
    export ZITE_FULL_KEY="rraXTem6O2XStIGd1DzNm6QTZBY2581...FULL_KEY"
    pip install requests pandas openpyxl
    python build_dashboard_from_live_data.py

Requires, in the same folder:
    dashboard_template.html   (ships with <!--DATA/APP placeholders-->)
    app.js                    (the dashboard front-end)
Both are produced by the dashboard build and are reused unchanged for rendering.

NOTE ON SCORING: the raw→Green/Yellow/Red logic in SCORE_RULES below reproduces the
Q2 2026 published tables. Confirm the exact choice values / thresholds against the
cluster's XLSForm before trusting a new quarter — they are the one place a form change
would bite. Everything marked  # <<< CONFIRM  is a business rule, not code.
"""
import os, io, json, sys, re
from collections import Counter, defaultdict

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ----------------------------------------------------------------------------- CONFIG
KOBO_XLSX   = "https://kf.kobo.iom.int/api/v2/assets/aRQhLp3M6yhXzAPtVTafRW/export-settings/esDuRJwnEiArZid4sdfPjxP/data.xlsx"
KOBO_JSON   = "https://kf.kobo.iom.int/api/v2/assets/aRQhLp3M6yhXzAPtVTafRW/data.json"
KOBO_TOKEN  = os.environ.get("KOBO_API_TOKEN", "")
ZITE_KEY    = os.environ.get("ZITE_FULL_KEY", "")
ZITE_BASE   = os.environ.get("ZITE_API_URL", "https://app.zitemanager.org/api/v2/reports-file/")
ZITE_REPORT = os.environ.get("ZITE_REPORT_ID", "4001")
ZITE_URL    = ZITE_BASE.rstrip("/") + "/?report_id=" + str(ZITE_REPORT) + "&key={key}"
OUT_HTML    = "CCCM_Site_Monitoring_Dashboard.html"

SECTORS = ["CCCM","Prot","CP","GBV","HLP","NFI","Shel","WASH","Hlth","FSL","Nutr","Educ"]
IS_KEY  = {"CCCM":"CCCM","Prot":"Protection","CP":"CP","GBV":"GBV","HLP":"HLP","NFI":"NFI",
           "Shel":"Shelter","WASH":"WASH","Hlth":"Health","FSL":"FSL","Nutr":"Nutrition","Educ":"Education"}
SECTOR_META = {  # code: [short, long, indicator_count]
 "CCCM":["CCCM","Camp Coordination & Camp Mgmt",10],"Prot":["Protection","Protection",6],
 "CP":["CP","Child Protection",2],"GBV":["GBV","Gender-Based Violence",6],
 "HLP":["HLP","Housing, Land & Property",4],"NFI":["NFI","Non-Food Items",2],
 "Shel":["Shelter","Shelter",4],"WASH":["WASH","Water, Sanitation & Hygiene",10],
 "Hlth":["Health","Health",11],"FSL":["FSL","Food Security & Livelihoods",5],
 "Nutr":["Nutrition","Nutrition",5],"Educ":["Education","Education",11]}

# ---------------------------------------------------------------- FORM-DERIVED MAPPING
# Keys are the *actual Kobo column paths* from XLSForm aRQhLp3M6yhXzAPtVTafRW
# (survey sheet, 167 rows). Derived 2026-07-19 — not guessed. '(LC)' = learning-centre-
# only, relevant-gated on access_education='yes'; blank at non-LC sites => not applicable.
#
# Divergences from the published methodology, all recorded in run_report.md:
#   1. The `yesno` choice list is binary (yes/no) — it has NO 'partial' option. The
#      methodology's "partial/in progress -> Yellow" rule therefore cannot fire on any
#      binary indicator. Yellow arises only from the 6 value/threshold lists below.
#   2. WASH scores on 10 indicators, not 11. The published "Latrines functional &
#      sufficient" has no yes/no field in this form — only the integers
#      functional_latrines / non_functional_latrines. Per cluster decision those are
#      carried as a breakdown table only; no derived rule invented.
#   3. FSL income_generating cut-offs (6 bands -> G/Y/R) are a cluster decision, not a
#      form constraint. Applied: 0%=Red, 1-50%=Yellow, >50%=Green.
#   4. The form has no site_code field; master-list matching is by name + GPS only.
INDICATORS = {
 "group_cccm_cluster/site_decongestion":("CCCM","Decongestion activities conducted at the site"),
 "group_cccm_cluster/cmc_training":("CCCM","CMC received trainings this month"),
 "group_cccm_cluster/cmc_rotation":("CCCM","Regular rotation or election process for CMC members"),
 "group_cccm_cluster/hlp_due":("CCCM","HLP due diligence conducted prior to infrastructure work"),
 "group_cccm_cluster/coord_meeting":("CCCM","Coordination meeting conducted at site/catchment this month"),
 "group_cccm_cluster/community_engagement":("CCCM","Engagement with committees/IDPs on aid-diversion patterns"),
 "group_cccm_cluster/community_led":("CCCM","Community-led sessions/forums held this month"),
 "group_cccm_cluster/cmc_resolving":("CCCM","CMC actively resolves issues & coordinates with providers"),
 "group_cccm_cluster/cmc":("CCCM","Functioning & inclusive Camp Management Committee (CMC)"),
 "group_cccm_cluster/cfrm":("CCCM","Accessible & functioning CFM mechanism"),
 "group_protection_cluster/psychosocial":("Prot","Psychosocial support for trauma-affected population"),
 "group_protection_cluster/protection_desk":("Prot","Residents access & use protection desks"),
 "group_protection_cluster/referral_protection":("Prot","Functional referral to specialized protection services"),
 "group_protection_cluster/protection_service":("Prot","Protection services accessible to at-risk groups (PWD, older)"),
 "group_protection_cluster/mobile_protection":("Prot","Mobile protection mechanism on defined schedule"),
 "group_protection_cluster/awareness_protection":("Prot","Awareness-raising campaigns on protection services"),
 "group_cp_aor/uasc":("CP","Unaccompanied/separated children identified within site"),
 "group_cp_aor/referral_cp":("CP","Child Protection referral pathway functional & used"),
 "group_gbv_aor/safespace":("GBV","Safe spaces on-site for women/girls"),
 "group_gbv_aor/safespaces_confidentiality":("GBV","Designated confidential GBV safe spaces"),
 "group_gbv_aor/referral_gbv":("GBV","Referral system for GBV cases working"),
 "group_gbv_aor/awareness_gbv":("GBV","GBV prevention/awareness campaigns this month"),
 "group_gbv_aor/hotline":("GBV","Hotline/helpdesk feedback for GBV users"),
 "group_gbv_aor/referral_access":("GBV","Community knows/accesses GBV referral pathway"),
 "Damages_Destructions/transition_support":("HLP","Support to transition to long-term tenure"),
 "Damages_Destructions/hlp_support":("HLP","Support to obtain legal tenancy documentation"),
 "Damages_Destructions/awareness_hlp":("HLP","Awareness campaigns on HLP rights"),
 "Damages_Destructions/hlp_mechanism":("HLP","Active mechanisms to resolve HLP disputes"),
 "group_snfi/usefulness":("NFI","Feedback collected on NFI item quality/usefulness"),
 "group_snfi/prioritized":("NFI","Vulnerable HHs prioritized for NFI distribution"),
 "group_snfi/shelter_repair_kits":("Shel","Shelter repair kits available for HHs in need"),
 "group_snfi/adequate_shelter":("Shel","Shelter adequate to meet basic HH needs"),
 "group_snfi/shelter_safe":("Shel","Shelter environment safe/secure (esp. women & children)"),
 "group_snfi/vulnerable_identified":("Shel","Vulnerable HHs identified needing emergency shelter"),
 "group_wash/gender_seggregated_wash":("WASH","WASH facilities separated by gender"),
 "group_wash/hygiene_kits":("WASH","Hygiene kits distributed to households"),
 "group_wash/waste_management_toolkit":("WASH","Waste management kits/tools available"),
 "group_wash/waste_management":("WASH","Effective waste management system in place"),
 "group_wash/water_user_committees":("WASH","Functional water user committees"),
 "group_wash/open_defecation":("WASH","No open defecation observed"),  # reverse-coded
 "group_wash/primary_source_bh_sw":("WASH","Water treatment conducted (shallow well/borehole)"),
 "group_wash/community_involved":("WASH","Community involved in WASH activities/maintenance"),
 "group_wash/water_availability":("WASH","Average litres of water per person per day"),   # value
 "group_wash/water_distance":("WASH","Time to walk to nearest water point"),              # value
 "group_health/ambulance":("Hlth","Ambulance service available to residents"),
 "group_health/health_monitor_disease_outbreak":("Hlth","System to monitor/report disease outbreaks"),
 "group_health/health_vaccines":("Hlth","Vaccination campaigns regularly conducted"),
 "group_health/maternal_health":("Hlth","Maternal & delivery health services available"),
 "group_health/health_emergency_medical":("Hlth","Emergency medical services available nearby"),
 "group_health/health_referral":("Hlth","Referral pathways for specialized medical care"),
 "group_health/health_vulnerable_targeted":("Hlth","Vulnerable groups access appropriate health services"),
 "group_health/health_facilties_number":("Hlth","Functioning health facility accessible"),
 "group_health/health_medicine_sufficient":("Hlth","Essential medicines available"),
 "group_health/health_campaigns":("Hlth","Awareness campaigns on health services"),
 "group_health/health_distance":("Hlth","Distance of nearest health facility"),           # value
 "group_foodsecurity/food_distribution":("FSL","Last time food or cash distributed on-site"),  # recency
 "group_foodsecurity/income_generating":("FSL","% HHs in income-generating activities"),  # value
 "group_foodsecurity/households_prioritized":("FSL","Most vulnerable HHs prioritized for food assistance"),
 "group_foodsecurity/market_access":("FSL","IDPs have market access for essential goods"),
 "group_foodsecurity/cash_assitance_restrictions":("FSL","Cash assistance usable without restrictions"),
 "group_nutrition/muac_screening":("Nutr","MUAC screening conducted in the site"),
 "group_nutrition/nutritional_screening":("Nutr","Regular nutrition screenings for under-5"),
 "group_nutrition/referral_protection_001":("Nutr","Functional referral for acute malnutrition"),
 "group_nutrition/awareness_nutrition":("Nutr","Nutrition education/awareness sessions"),
 "group_nutrition/commmunity_access":("Nutr","Community access to nutrition services (under-5, PLW)"),  # value
 "group_education/school_feeding":("Educ","School feeding programs available (LC)"),
 "group_education/access_education":("Educ","Resident children have access to a learning center"),
 "group_education/learning_supplies":("Educ","Children receive individual learning supplies (LC)"),
 "group_education/incentive_teacher":("Educ","Teachers receiving a cash incentive (LC)"),
 "group_education/functional_handwashing_edu":("Educ","Functioning handwashing stations with water (LC)"),
 "group_education/trained_teachers":("Educ","Enough trained teachers available (LC)"),
 "group_education/enough_space":("Educ","Enough space to accommodate all students (LC)"),
 "group_education/community_activities":("Educ","Community participates in school management (LC)"),
 "group_education/committees_education":("Educ","Established committees to support schools (LC)"),
 "group_education/functional_latrines_edu":("Educ","Learning centers have functional latrines (LC)"),
 "group_education/access_education_distance":("Educ","Distance to nearest learning center"),  # value
}
_OLD_INDICATORS_UNUSED = {
 "CCCM_SiteDecongestion":("CCCM","Decongestion activities conducted at the site"),
 "CCCM_CMC_Training":("CCCM","CMC received trainings this month"),
 "CCCM_CMC_Election":("CCCM","Regular rotation or election process for CMC members"),
 "CCCM_HLP_DueDiligence":("CCCM","HLP due diligence conducted prior to infrastructure work"),
 "CCCM_CoordinationMeetings":("CCCM","Coordination meeting conducted at site/catchment this month"),
 "CCCM_Engagement_AidDiversion":("CCCM","Engagement with committees/IDPs on aid-diversion patterns"),
 "CCCM_CommunityLedSessions_Risk":("CCCM","Community-led sessions/forums held this month"),
 "CCCM_CMC_ResolvingIssues":("CCCM","CMC actively resolves issues & coordinates with providers"),
 "CCCM_Functioning_CMC":("CCCM","Functioning & inclusive Camp Management Committee (CMC)"),
 "CCCM_Operational_CFM":("CCCM","Accessible & functioning CFM mechanism"),
 "PRO_PsychosocialSupportServices":("Prot","Psychosocial support for trauma-affected population"),
 "PRO_ProtectionDesk":("Prot","Residents access & use protection desks"),
 "PRO_FunctionalReferralMechanism":("Prot","Functional referral to specialized protection services"),
 "PRO_ProtectionServices":("Prot","Protection services accessible to at-risk groups (PWD, older)"),
 "PRO_MobileProtectionAvailable":("Prot","Mobile protection mechanism on defined schedule"),
 "PRO_AwarenessCampaigns":("Prot","Awareness-raising campaigns on protection services"),
 "CP_UASC":("CP","Unaccompanied/separated children identified within site"),
 "CP_ReferralPathway":("CP","Child Protection referral pathway functional & used"),
 "GBV_SafeSpaces":("GBV","Safe spaces on-site for women/girls"),
 "GBV_SafeSpaces_Confidential":("GBV","Designated confidential GBV safe spaces"),
 "GBV_ReferralPathway":("GBV","Referral system for GBV cases working"),
 "GBV_AwarenessCampaigns":("GBV","GBV prevention/awareness campaigns this month"),
 "GBV_HelpDesk":("GBV","Hotline/helpdesk feedback for GBV users"),
 "GBV_ReferralPathway_CommunityAware":("GBV","Community knows/accesses GBV referral pathway"),
 "HLP_TransitionDurableSolutions":("HLP","Support to transition to long-term tenure"),
 "HLP_Support":("HLP","Support to obtain legal tenancy documentation"),
 "HLP_AwarenessCampaigns":("HLP","Awareness campaigns on HLP rights"),
 "HLP_Mechanism":("HLP","Active mechanisms to resolve HLP disputes"),
 "NFI_Feedback_Collected":("NFI","Feedback collected on NFI item quality/usefulness"),
 "NFI_VulnerablePrioritized":("NFI","Vulnerable HHs prioritized for NFI distribution"),
 "SHELTER_ShelterKits":("Shel","Shelter repair kits available for HHs in need"),
 "SHELTER_Adequate":("Shel","Shelter adequate to meet basic HH needs"),
 "SHELTER_ShelterSafe":("Shel","Shelter environment safe/secure (esp. women & children)"),
 "SHELTER_VulnerablePrioritized":("Shel","Vulnerable HHs identified needing emergency shelter"),
 "WASH_Facilities_GenderSeparated":("WASH","WASH facilities separated by gender"),
 "WASH_HygieneKits_Distributions":("WASH","Hygiene kits distributed to households"),
 "WASH_WasteManagement_Kits":("WASH","Waste management kits/tools available"),
 "WASH_WashManagementSystem":("WASH","Effective waste management system in place"),
 "WASH_WaterUserCommittees":("WASH","Functional water user committees"),
 "WASH_OpenDefecation":("WASH","No open defecation observed"),  # reverse-coded
 "WASH_WaterSource_Borehole_Treated":("WASH","Water treatment conducted (shallow well/borehole)"),
 "WASH_CommunitiesInvolved":("WASH","Community involved in WASH activities/maintenance"),
 "WASH_LatrineEnough":("WASH","Latrines functional & sufficient"),
 "WASH_WaterAvailability":("WASH","Average litres of water per person per day"),   # value
 "WASH_DistanceTime_WaterSource":("WASH","Time to walk to nearest water point"),   # value
 "HEALTH_Ambulance":("Hlth","Ambulance service available to residents"),
 "HEALTH_MonitoringSystem":("Hlth","System to monitor/report disease outbreaks"),
 "HEALTH_Vaccination":("Hlth","Vaccination campaigns regularly conducted"),
 "HEALTH_MaternalHealthServices":("Hlth","Maternal & delivery health services available"),
 "HEALTH_EmergencyServices":("Hlth","Emergency medical services available nearby"),
 "HEALTH_ReferralPathways":("Hlth","Referral pathways for specialized medical care"),
 "HEALTH_VulnerablePrioritized":("Hlth","Vulnerable groups access appropriate health services"),
 "HEALTH_FunctioningHealthFacilities":("Hlth","Functioning health facility accessible"),
 "HEALTH_EssentialMedicines":("Hlth","Essential medicines available"),
 "HEALTH_AwarenessCampaigns":("Hlth","Awareness campaigns on health services"),
 "HEALTH_Distance_HealthFacility":("Hlth","Distance of nearest health facility"),  # value
 "FSL_LastDistribution":("FSL","Last time food or cash distributed on-site"),       # recency
 "FSL_PercentageHHs_IncomeGenerating":("FSL","% HHs in income-generating activities"),# value
 "FSL_VulnerablePrioritized":("FSL","Most vulnerable HHs prioritized for food assistance"),
 "FSL_MarketAccess":("FSL","IDPs have market access for essential goods"),
 "FSL_UseCas_WORestrictions":("FSL","Cash assistance usable without restrictions"),
 "NUT_MUAC_Screening":("Nutr","MUAC screening conducted in the site"),
 "NUT_Screening_Under5":("Nutr","Regular nutrition screenings for under-5"),
 "NUT_ReferralPathway":("Nutr","Functional referral for acute malnutrition"),
 "NUT_Awareness":("Nutr","Nutrition education/awareness sessions"),
 "NUT_Access_Level":("Nutr","Community access to nutrition services (under-5, PLW)"),  # value
 "EDU_SchoolFeeding":("Educ","School feeding programs available (LC)"),
 "EDU_Education_Access":("Educ","Resident children have access to a learning center"),
 "EDU_Learning_Supplies":("Educ","Children receive individual learning supplies (LC)"),
 "EDU_TeachersIncentive":("Educ","Teachers receiving a cash incentive (LC)"),
 "EDU_HandwashingStation":("Educ","Functioning handwashing stations with water (LC)"),
 "EDU_TeachersEnough":("Educ","Enough trained teachers available (LC)"),
 "EDU_EnoughSpace":("Educ","Enough space to accommodate all students (LC)"),
 "EDU_CommunityParticipation":("Educ","Community participates in school management (LC)"),
 "EDU_SchoolCommittee":("Educ","Established committees to support schools (LC)"),
 "EDU_Latrines":("Educ","Learning centers have functional latrines (LC)"),
 "EDU_Distance":("Educ","Distance to nearest learning center"),                      # value
}
REVERSE = {"group_wash/open_defecation"}   # 'yes' (observed) => Red

# Value/threshold scorers. Keyed to the EXACT choice codes in the XLSForm `choices`
# sheet — no numeric parsing, no substring guessing. A code not in the map => None
# (not assessed), never a silent Red.
VALUE_MAPS = {
 # group_wash/water_availability -> list `water`   (spec: >=15 G / 10-15 Y / <10 R)
 "group_wash/water_availability": {
    "water_1":"R",   # Less than 10 Liters
    "water_2":"Y",   # 10-15 Liters
    "water_3":"G",   # 15-20 Liters
    "water_4":"G"},  # More than 20 Liters
 # group_wash/water_distance -> list `time`        (spec: <30 G / 30-60 Y / >60 R)
 "group_wash/water_distance": {
    "time_1":"G",    # Less than 30 Minutes
    "time_2":"Y",    # 30-60 Minutes
    "time_3":"R"},   # More than 60 Minutes
 # group_health/health_distance -> list `distance` (spec: <1km G / 1-5 Y / >5 R)
 "group_health/health_distance": {
    "distance_1":"G","distance_2":"Y","distance_3":"R"},
 # group_education/access_education_distance -> `distance_edu` (spec: <1 G / 1-3 Y / >3 R)
 "group_education/access_education_distance": {
    "distance_edu_1":"G","distance_edu_2":"Y","distance_edu_3":"R"},
 # group_nutrition/commmunity_access -> list `access_level`
 "group_nutrition/commmunity_access": {
    "easy":"G","moderate":"Y","difficult":"R"},
 # group_foodsecurity/food_distribution -> list `food_distribution`
 # (spec: <1mo G / 1-6mo Y / >6mo, never, don't know R)
 "group_foodsecurity/food_distribution": {
    "distribution_1":"G",   # Less than a month
    "distribution_2":"Y",   # Between 1 to 6 months
    "distribution_3":"R",   # More than 6 months
    "distribution_4":"R",   # Don't know
    "distribution_5":"R"},  # Never
 # group_foodsecurity/income_generating -> list `income`
 # CLUSTER DECISION (not a form constraint): 0%=R, 1-50%=Y, >50%=G. See run_report.md.
 "group_foodsecurity/income_generating": {
    "income_1":"R",   # 0%
    "income_2":"Y",   # 1%-25%
    "income_3":"Y",   # 25%-50%
    "income_4":"G",   # 51%-75%
    "income_5":"G",   # 75%-90%
    "income_6":"G"},  # 91%-100%
}
VALUE_INDS = set(VALUE_MAPS)

def _blank(v):
    return v is None or str(v).strip().lower() in ("","nan","none","n/a","na","not applicable","-")

def _num(v):
    """Numeric coercion for HH / individuals counts. Missing -> None, never 0."""
    if _blank(v): return None
    try: return float(re.sub(r"[^0-9.\-]", "", str(v)))
    except Exception: return None

def score_value(ind, v):
    if _blank(v): return None
    return VALUE_MAPS.get(ind, {}).get(str(v).strip())

def norm_binary(v):
    """XLSForm list `yesno` is binary: yes / no. There is no 'partial' choice, so this
    never returns 'Y'. Anything unrecognised is not-assessed, not Red."""
    if _blank(v): return None
    s = str(v).strip().lower()
    if s == "yes": return "G"
    if s == "no":  return "R"
    return None

# admin / identity columns — exact paths from the XLSForm survey sheet.
COL = {
 "region":   ["region"],
 "district": ["district"],
 "ca":       ["subdistrict"],          # label: "Sub-District/Catchment/Neighbourhood"
 "site":     ["final_site_name","site_name"],   # final_site_name is the calculated resolver
 "site_code":["site_code"],            # NOT PRESENT in this form — match by name+GPS
 "hh":       ["hhs"],
 "ind":      ["inds"],
 "partner":  ["organization_updating"],
 "lat":      ["final_latitude","latitude"],
 "lon":      ["final_longitude","longitude"],
}

# ----------------------------------------------------------------------------- FETCH
def die(msg):
    print("\nSTOP:", msg); sys.exit(1)

def fetch():
    import requests
    if not KOBO_TOKEN: die("Set KOBO_API_TOKEN (kf.kobo.iom.int ▸ Account ▸ Security ▸ API token).")
    import pandas as pd
    # --- Source A: Kobo xlsx (fall back to data.json) ---
    print("Fetching Kobo export …")
    hdr = {"Authorization": f"Token {KOBO_TOKEN}"}
    try:
        r = requests.get(KOBO_XLSX, headers=hdr, timeout=120)
        r.raise_for_status()
        dfA = pd.read_excel(io.BytesIO(r.content))
    except Exception as e:
        print("  xlsx export failed (%s); trying data.json …" % e)
        # Kobo caps page size server-side (typically 1000) REGARDLESS of the requested
        # limit. Paginate on the actual batch size and reconcile against the reported
        # total, or we silently truncate. (This bit us: 1000 of 6086 rows, no error.)
        PAGE = 1000
        rows, start, expected = [], 0, None
        while True:
            r = requests.get(KOBO_JSON, headers=hdr,
                             params={"start":start,"limit":PAGE,"format":"json"}, timeout=120)
            r.raise_for_status(); js = r.json()
            batch = js.get("results", js if isinstance(js,list) else [])
            if expected is None and isinstance(js, dict) and js.get("count") is not None:
                expected = js["count"]
                print(f"  Kobo reports {expected} submissions; paginating at {PAGE}/page …")
            rows += batch
            if not batch or len(batch) < PAGE: break
            start += len(batch)
            print(f"    fetched {len(rows)}…")
        if not rows: die("Kobo returned no rows — check token / asset permissions.")
        if expected is not None and len(rows) != expected:
            die(f"Kobo pagination incomplete: got {len(rows)} of {expected} submissions. "
                "Refusing to score a truncated dataset.")
        dfA = pd.json_normalize(rows)
    dfA["__source"] = "Kobo"
    print(f"  Kobo rows: {len(dfA)}")
    # --- Source B: Zite Manager (IOM) ---
    dfB = None
    if ZITE_KEY:
        print("Fetching Zite Manager (IOM) …")
        r = requests.get(ZITE_URL.format(key=ZITE_KEY), timeout=120)
        body = r.content
        if b"No data" in body[:200] or b"switch off" in body[:200]:
            die("Zite Manager returned 'No data; may be owner switch off the data' — IOM feed is off. "
                "Enable it or supply the IOM Excel manually, then re-run. Not proceeding without IOM sites.")
        try:    dfB = pd.read_excel(io.BytesIO(body))
        except Exception:
            try: dfB = pd.read_csv(io.BytesIO(body))
            except Exception as e:
                die(f"Zite response is neither XLSX nor CSV ({e}); first bytes: {body[:120]!r}")
        dfB["__source"] = "Zite/IOM"
        print(f"  Zite rows: {len(dfB)}")
        # A zero-row payload is NOT a valid 'no IOM sites this quarter' signal — it means
        # the feed is off or the report/key is wrong. Proceeding would understate coverage
        # and bias every aggregate. Stop, per the methodology guardrail.
        if len(dfB) == 0:
            die("Zite Manager returned 0 rows — the IOM feed is empty. Check report_id/key "
                "or whether the owner has enabled the data. Not proceeding without IOM sites.")
    else:
        print("  ZITE_FULL_KEY not set — proceeding WITHOUT IOM sites (coverage will be understated).")
    df = pd.concat([d for d in (dfA,dfB) if d is not None], ignore_index=True)
    return df

# ----------------------------------------------------------------------------- TRANSFORM
def pick(df, keys):
    low = {c.lower(): c for c in df.columns}
    for k in keys:
        for c in df.columns:
            if c.lower()==k or c.lower().endswith("/"+k) or c.lower().endswith("."+k):
                return c
    return None

def band(s):
    return "Severe" if s>=55 else "High" if s>=40 else "Moderate" if s>=25 else "Low"

def transform(df):
    cmap = {k: pick(df, v) for k,v in COL.items()}
    print("Column map:", {k:v for k,v in cmap.items() if v})
    # locate the indicator columns present in this export
    present = {}
    for ind in INDICATORS:
        col = None
        for c in df.columns:
            cl=c.lower()
            if cl==ind.lower() or cl.endswith("/"+ind.lower()) or cl.endswith("."+ind.lower()):
                col=c; break
        if col: present[ind]=col
    print(f"Indicator columns found: {len(present)} / {len(INDICATORS)}")

    sites=[]; review=[]
    for _,row in df.iterrows():
        site = str(row.get(cmap["site"] or "", "")).strip()
        if not site or site.lower()=="nan":
            review.append(row); continue
        # per-sector red counts
        red=defaultdict(int); assessed=defaultdict(int)
        lc = norm_binary(row.get(present.get("EDU_Education_Access",""))) in ("G","Y")  # learning-centre?
        for ind,(sec,_lab) in INDICATORS.items():
            col = present.get(ind)
            if col is None: continue
            if "(LC)" in _lab and not lc:  # LC indicator at non-LC site -> not applicable
                continue
            raw = row.get(col)
            sc = score_value(ind,raw) if ind in VALUE_INDS else norm_binary(raw)
            if sc is None: continue
            if ind in REVERSE and sc in ("G","R"): sc = "R" if sc=="G" else "G"
            assessed[sec]+=1
            if sc=="R": red[sec]+=1
        # sector dot + severity
        dots=[]; pcts=[]
        for sec in SECTORS:
            a=assessed[sec]
            if a==0: dots.append("NA"); continue
            p=red[sec]/a*100; pcts.append(p)
            dots.append("G" if p<=25 else "Y" if p<=50 else "R" if p<=90 else "K")
        if not pcts:
            review.append(row); continue
        sev=round(sum(pcts)/len(pcts))
        sites.append({"r":str(row.get(cmap["region"] or "","")).strip(),
                      "d":str(row.get(cmap["district"] or "","")).strip(),
                      "c":re.sub(r"_G\s+([NS])",r"_G\1",str(row.get(cmap["ca"] or "","")).strip()).replace("nan",""),
                      "s":site,"v":sev,"b":band(sev),"sc":dots,
                      "_hh":_num(row.get(cmap["hh"] or "")),"_ind":_num(row.get(cmap["ind"] or "")),
                      "_partner":str(row.get(cmap["partner"] or "","")).strip(),
                      "_code":str(row.get("_site_id","")).strip(),
                      "_src":str(row.get("__source","")).strip()})
    print(f"Scored sites: {len(sites)} | review-queue rows: {len(review)}")
    return sites, review, present

# ----------------------------------------------------------------------------- AGGREGATE
def aggregate(sites, present, df):
    n=len(sites)
    # district severity
    dsev=defaultdict(lambda:Counter()); dreg={}
    for s in sites:
        dsev[s["d"]][s["b"]]+=1; dsev[s["d"]]["n"]+=1; dreg.setdefault(s["d"],s["r"])
    districtSev=[]
    for d,c in dsev.items():
        avg=round(sum(x["v"] for x in sites if x["d"]==d)/c["n"],1)
        districtSev.append({"district":d,"region":dreg[d],"n":c["n"],"avg":avg,
            "Severe":c["Severe"],"High":c["High"],"Moderate":c["Moderate"],"Low":c["Low"]})
    districtSev.sort(key=lambda x:-x["avg"])
    # sector dots distribution
    sectorDots={}
    for i,code in enumerate(SECTORS):
        cc=Counter(s["sc"][i] for s in sites); sectorDots[code]={x:cc.get(x,0) for x in ["G","Y","R","K","NA"]}
    # indicator-level scoring across all sites  (needs raw again → recompute per indicator)
    indScore=defaultdict(list)  # sector_key -> [[label,g,y,r]]
    # sector gap/coverage (indicator-level)
    sec_g=Counter(); sec_r=Counter(); sec_tot=Counter()
    # (recompute from df using present cols)
    per_ind = {}
    for ind,col in present.items():
        sec,label=INDICATORS[ind]
        g=y=r=0
        for _,row in df.iterrows():
            raw=row.get(col)
            sc=score_value(ind,raw) if ind in VALUE_INDS else norm_binary(raw)
            if sc is None: continue
            if ind in REVERSE and sc in ("G","R"): sc="R" if sc=="G" else "G"
            if sc=="G":g+=1
            elif sc=="Y":y+=1
            elif sc=="R":r+=1
        tot=g+y+r
        if tot==0: continue
        gp,yp,rp=round(g/tot*100),round(y/tot*100),round(r/tot*100)
        per_ind[ind]=(label,gp,yp,rp)
        indScore[IS_KEY[sec]].append([label,gp,yp,rp])
        sec_g[sec]+=g; sec_r[sec]+=r; sec_tot[sec]+=tot
    sectors=[]
    for code in SECTORS:
        t=sec_tot[code]
        if t==0: continue
        sectors.append({"name":SECTOR_META[code][1],"gap":round(sec_r[code]/t*100),"cov":round(sec_g[code]/t*100)})
    sectors.sort(key=lambda x:-x["gap"])
    # top red / green individual indicators
    allind=[(v[0],v[3]) for v in per_ind.values()]
    topRed=sorted(allind,key=lambda x:-x[1])[:10]
    topGreen=sorted([(v[0],v[1]) for v in per_ind.values()],key=lambda x:-x[1])[:10]
    # district gap (>=10 sites) using site-dot share
    districtGap=[]
    for d in districtSev:
        if d["n"]<10: continue
        # indicator-level gap not per-district here without re-scan; approx via avg severity
        districtGap.append([d["district"],d["n"],round(d["avg"]),round(100-d["avg"])])
    districtGap.sort(key=lambda x:-x[2]); districtGap=districtGap[:10]
    # KPIs
    hhs=int(sum(s["_hh"] or 0 for s in sites)); inds=int(sum(s["_ind"] or 0 for s in sites))
    partners=len(set(s["_partner"] for s in sites if s["_partner"] and s["_partner"]!="nan"))
    natSev=round(sum(s["v"] for s in sites)/n,1) if n else 0
    kpi={"sites":n,"sitesAnnex":n,"catchments":len(set(s["c"] for s in sites if s["c"])),
         "hhs":hhs,"individuals":inds,"partners":partners or 0,"districts":len(dsev),"severity":natSev}
    # key findings (auto)
    worst=topRed[0] if topRed else ("—",0)
    findings=[f"Widest indicator gap: {worst[0]} — {worst[1]}% of sites scored Red.",
              f"Highest-severity districts: "+", ".join(f"{d['district']} {round(d['avg'])}%" for d in districtSev[:3] if d['n']>=10)+".",
              f"Strongest coverage: {topGreen[0][0]} {topGreen[0][1]}% Green." if topGreen else ""]
    strip=lambda s: [x for x in s if x]
    clean = lambda arr:[[a,b] for a,b in arr]
    # Private fields are RETAINED: the Site Explorer filters by partner and the CSV export
    # carries HH/individuals per site. (These used to be dropped here to shrink the payload,
    # which silently emptied the Partner column and the export's population columns.)
    return {
      "meta":{"title":"CCCM Cluster Somalia — Site Monitoring","subtitle":"National · live rebuild",
              "published":"auto-generated","source":"CCCM Cluster Site Monitoring"},
      "kpi":kpi,
      "q1":{k:[v, v] for k,v in [("Sites",kpi["sites"]),("Catchments",kpi["catchments"]),("HHs",kpi["hhs"]),
             ("Individuals",kpi["individuals"]),("Partners",kpi["partners"]),("Districts",kpi["districts"])]},
      "keyFindings":strip(findings),
      "coverageNotes":"CCCM Cluster Site Monitoring — all reporting partners, including IOM.",
      "partnersList":sorted(set(s.get("_partner","") for s in sites)) if False else [],
      "sectors":sectors,
      "topRed":clean(topRed),"topGreen":clean(topGreen),
      "districtGap":[[d[0],d[1],d[2],d[3]] for d in districtGap],
      "demographics":{"total":0,"malePct":0,"femalePct":0,"matchedSites":0,"bands":[]},  # fill if sex/age cols exist
      "sectorMeta":{c:[SECTOR_META[c][0],SECTOR_META[c][1],SECTOR_META[c][2]] for c in SECTORS},
      "indicatorScoring":{k:sorted(v,key=lambda x:-x[3]) for k,v in indScore.items()},
      "breakdowns":{},          # populate from multi-select columns as needed
      "aggregates":{},
      "sectorDots":sectorDots,
      "districtSev":districtSev,
      "sectors_order":SECTORS,
      "sites":sites,
    }

# ----------------------------------------------------------------------------- RENDER
def render(data):
    if not (os.path.exists("dashboard_template.html") and os.path.exists("app.js")):
        die("Place dashboard_template.html and app.js next to this script (they ship with the dashboard).")
    tpl=open("dashboard_template.html",encoding="utf-8").read()
    app=open("app.js",encoding="utf-8").read()
    tpl=tpl.replace("/*DATA_PLACEHOLDER*/","const DATA = "+json.dumps(data,ensure_ascii=False)+";")
    tpl=tpl.replace("/*APP_PLACEHOLDER*/",app)
    open(OUT_HTML,"w",encoding="utf-8").write(tpl)
    try:
        print(f"\n✅ Wrote {OUT_HTML}  ({round(os.path.getsize(OUT_HTML)/1024)} KB)  ·  {data['kpi']['sites']} sites")
    except UnicodeEncodeError:   # some Windows consoles default to a non-UTF-8 codepage
        print(f"\nWrote {OUT_HTML}  ({round(os.path.getsize(OUT_HTML)/1024)} KB)  - {data['kpi']['sites']} sites")

def main():
    df = fetch()
    sites, review, present = transform(df)
    if not sites: die("No scorable sites — check column mapping (COL/INDICATORS) against the export headers.")
    data = aggregate(sites, present, df)
    json.dump(data, open("dashboard_data.json","w",encoding="utf-8"), ensure_ascii=False)
    if review:
        import csv
        with open("review_queue.csv","w",newline="",encoding="utf-8") as f:
            w=csv.writer(f); w.writerow(["reason","raw_row_index"]); [w.writerow(["unmatched_or_no_site",i]) for i,_ in enumerate(review)]
    render(data)
    print("Next: open the HTML, and verify totals in run_report.md against the cluster's expectations.")

if __name__ == "__main__":
    main()
