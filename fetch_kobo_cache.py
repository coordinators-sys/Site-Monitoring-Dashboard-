#!/usr/bin/env python3
"""Fetch the Kobo Site Monitoring submissions once and cache to disk.
Prints no token. Re-pull only with --refresh."""
import os, sys, json
import requests

try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

CACHE = "_cache_kobo.json"
ASSET = "aRQhLp3M6yhXzAPtVTafRW"
URL   = f"https://kf.kobo.iom.int/api/v2/assets/{ASSET}/data.json"
PAGE  = 1000

def main():
    if os.path.exists(CACHE) and "--refresh" not in sys.argv:
        print(f"cache present: {CACHE} (use --refresh to re-pull)")
        return
    tok = os.environ.get("KOBO_API_TOKEN")
    if not tok:
        raise SystemExit("KOBO_API_TOKEN missing from .env")
    print("token loaded: yes")
    hdr = {"Authorization": f"Token {tok}"}

    rows, start, expected = [], 0, None
    while True:
        r = requests.get(URL, headers=hdr,
                         params={"start": start, "limit": PAGE, "format": "json"},
                         timeout=180)
        r.raise_for_status()
        js = r.json()
        batch = js.get("results", js if isinstance(js, list) else [])
        if expected is None and isinstance(js, dict):
            expected = js.get("count")
            print(f"reported total: {expected}")
        rows += batch
        print(f"  fetched {len(rows)}")
        if not batch or len(batch) < PAGE:
            break
        start += len(batch)

    if expected is not None and len(rows) != expected:
        raise SystemExit(f"incomplete: got {len(rows)} of {expected}")
    json.dump(rows, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"cached {len(rows)} records -> {CACHE}")

if __name__ == "__main__":
    main()
