#!/usr/bin/env python3
"""
Live Kobo + Zite fetch, in-memory (no disk cache). Shared by:
  - fetch_kobo_cache.py / fetch_zite_cache.py (write the result to disk, for the
    offline GitHub Actions batch build)
  - api/operational.py (the live Vercel endpoint — fetches fresh on every
    cache-miss request, credentials read from environment variables that are
    never sent to the browser)

Never logs or returns the token/key themselves — only row counts.
"""
import os
import requests

KOBO_ASSET = "aRQhLp3M6yhXzAPtVTafRW"
KOBO_URL   = f"https://kf.kobo.iom.int/api/v2/assets/{KOBO_ASSET}/data.json"
KOBO_PAGE  = 1000

def fetch_kobo_live(token=None, timeout=180):
    tok = token or os.environ.get("KOBO_API_TOKEN")
    if not tok:
        raise RuntimeError("KOBO_API_TOKEN not set")
    hdr = {"Authorization": f"Token {tok}"}
    rows, start, expected = [], 0, None
    while True:
        r = requests.get(KOBO_URL, headers=hdr,
                          params={"start": start, "limit": KOBO_PAGE, "format": "json"},
                          timeout=timeout)
        r.raise_for_status()
        js = r.json()
        batch = js.get("results", js if isinstance(js, list) else [])
        if expected is None and isinstance(js, dict):
            expected = js.get("count")
        rows += batch
        if not batch or len(batch) < KOBO_PAGE:
            break
        start += len(batch)
    if expected is not None and len(rows) != expected:
        raise RuntimeError(f"Kobo pagination incomplete: got {len(rows)} of {expected}")
    return rows

def fetch_zite_live(key=None, base=None, report=None, timeout=180):
    key = key or os.environ.get("ZITE_FULL_KEY")
    base = base or os.environ.get("ZITE_API_URL", "https://app.zitemanager.org/api/v2/reports-file/")
    report = report or os.environ.get("ZITE_REPORT_ID", "4001")
    if not key:
        raise RuntimeError("ZITE_FULL_KEY not set")
    url = base.rstrip("/") + "/?report_id=" + str(report) + "&key=" + key
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    body = r.content
    if b"No data" in body[:200] or b"switch off" in body[:200]:
        raise RuntimeError("Zite Manager feed is off at source")
    rows = r.json()
    if not isinstance(rows, list) or not rows:
        raise RuntimeError(f"Zite returned 0 rows (type {type(rows).__name__})")
    return rows
