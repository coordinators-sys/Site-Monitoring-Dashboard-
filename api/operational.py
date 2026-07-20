"""
Live "Operational Snapshot" endpoint — the one piece of the public dashboard that
queries Kobo + Zite directly, at request time, from server-side code. The
KOBO_API_TOKEN / ZITE_FULL_KEY environment variables live only in Vercel's project
settings; they are read here and never appear in the response, in a log line, or
anywhere the browser can see.

Cached at the CDN edge for ~10 minutes (Cache-Control: s-maxage) so a burst of
visitors — or a Coordinator refreshing the page repeatedly — doesn't hammer Kobo's
API or add multi-second latency to every single page view. That is standard
practice for a "live but public" data feed, not a shortcut around freshness: the
data behind it is at most ~10 minutes old, which for a quarterly-cadence indicator
set is effectively real-time.

Scope is identical to the offline batch (build_operational.py): catchment/district
aggregates only, bucketed into Q1 2026 / Q2 2026 by assessment date. No site name or
site code is ever computed here — build_operational.build_all() asserts this on
itself before returning, and this handler treats that assertion failing as a hard
500, never a partial/best-effort response.

This endpoint has no connection to PUBLISHED RESULTS (published_data.py) at all —
those stay static, changing only when Information Management approves a new
quarterly report.
"""
import json
import os
import sys
import traceback
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from live_fetch import fetch_kobo_live, fetch_zite_live
import build_operational as bo


def _build():
    if not os.environ.get("KOBO_API_TOKEN") or not os.environ.get("ZITE_FULL_KEY"):
        raise RuntimeError("operational data source not configured")
    ko_rows = fetch_kobo_live()
    zi_rows = fetch_zite_live()
    ko_all = pd.DataFrame(ko_rows)
    zi_all = pd.DataFrame(zi_rows)
    generated_at = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    return bo.build_all(ko_all, zi_all, generated_at=generated_at)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            payload = _build()
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "public, s-maxage=600, stale-while-revalidate=120")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)
        except AssertionError as e:
            # A site-identifying key almost made it into a public response. Never
            # serve a partial/best-effort payload here — fail loudly instead.
            print("OPERATIONAL ENDPOINT BLOCKED — leak-check failed:", str(e), file=sys.stderr)
            self._error(500, "internal error")
        except Exception as e:
            print("operational endpoint error:", type(e).__name__, str(e), file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            self._error(502, "operational data source temporarily unavailable")

    def _error(self, code, message):
        body = json.dumps({"error": message}).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)
