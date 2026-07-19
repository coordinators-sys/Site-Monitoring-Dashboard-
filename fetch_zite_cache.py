#!/usr/bin/env python3
"""Fetch the Zite Manager (IOM) site-monitoring feed once and cache to disk.
Prints no key or URL. Re-pull only with --refresh."""
import os, sys, json
import requests

try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

CACHE = "_cache_zite.json"

def main():
    if os.path.exists(CACHE) and "--refresh" not in sys.argv:
        print(f"cache present: {CACHE} (use --refresh to re-pull)")
        return
    key    = os.environ.get("ZITE_FULL_KEY", "")
    base   = os.environ.get("ZITE_API_URL", "https://app.zitemanager.org/api/v2/reports-file/")
    report = os.environ.get("ZITE_REPORT_ID", "4001")
    if not key:
        raise SystemExit("ZITE_FULL_KEY missing from .env")
    print("key loaded: yes")
    url = base.rstrip("/") + "/?report_id=" + str(report) + "&key=" + key

    r = requests.get(url, timeout=300)
    r.raise_for_status()
    body = r.content
    if b"No data" in body[:200] or b"switch off" in body[:200]:
        raise SystemExit("Zite Manager returned 'No data' — the IOM feed is off at "
                         "source. Not proceeding without IOM sites.")
    rows = r.json()
    if not isinstance(rows, list) or not rows:
        raise SystemExit(f"Zite returned 0 rows — check report_id/key. "
                         f"Response type: {type(rows).__name__}")
    json.dump(rows, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"cached {len(rows)} records -> {CACHE}")

if __name__ == "__main__":
    main()
