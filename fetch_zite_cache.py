#!/usr/bin/env python3
"""Fetch the Zite Manager (IOM) site-monitoring feed once and cache to disk.
Prints no key or URL. Re-pull only with --refresh."""
import os, sys, json

try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

from live_fetch import fetch_zite_live

CACHE = "_cache_zite.json"

def main():
    if os.path.exists(CACHE) and "--refresh" not in sys.argv:
        print(f"cache present: {CACHE} (use --refresh to re-pull)")
        return
    if not os.environ.get("ZITE_FULL_KEY"):
        raise SystemExit("ZITE_FULL_KEY missing from .env")
    print("key loaded: yes")
    try:
        rows = fetch_zite_live()
    except RuntimeError as e:
        raise SystemExit(str(e))
    json.dump(rows, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"cached {len(rows)} records -> {CACHE}")

if __name__ == "__main__":
    main()
