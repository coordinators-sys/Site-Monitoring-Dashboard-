#!/usr/bin/env python3
"""Fetch the Kobo Site Monitoring submissions once and cache to disk.
Prints no token. Re-pull only with --refresh."""
import os, sys, json

try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

from live_fetch import fetch_kobo_live

CACHE = "_cache_kobo.json"

def main():
    if os.path.exists(CACHE) and "--refresh" not in sys.argv:
        print(f"cache present: {CACHE} (use --refresh to re-pull)")
        return
    if not os.environ.get("KOBO_API_TOKEN"):
        raise SystemExit("KOBO_API_TOKEN missing from .env")
    print("token loaded: yes")
    try:
        rows = fetch_kobo_live()
    except RuntimeError as e:
        raise SystemExit(str(e))
    json.dump(rows, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"cached {len(rows)} records -> {CACHE}")

if __name__ == "__main__":
    main()
