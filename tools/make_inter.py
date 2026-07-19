#!/usr/bin/env python3
"""Vendor the Inter font (latin subset, weights 400/600/700/800) as a single CSS file
with base64-embedded woff2, so the dashboard matches the Service Mapping design without
any external font request (CSP stays closed; file stays self-contained). Run once when
the design changes; vendor/inter.css is committed."""
import base64, re, urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")   # woff2-capable UA
CSS_URL = "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap"

req = urllib.request.Request(CSS_URL, headers={"User-Agent": UA})
css = urllib.request.urlopen(req, timeout=30).read().decode()

out = ["/* Inter (latin), vendored — © The Inter Project Authors, SIL OFL 1.1 */"]
# css2 emits one @font-face per unicode subset; keep only the latin block per weight
for block in re.findall(r"/\* latin \*/\s*@font-face\s*{[^}]+}", css):
    m = re.search(r"font-weight:\s*(\d+)", block)
    u = re.search(r"url\((https://[^)]+\.woff2)\)", block)
    if not (m and u):
        continue
    data = urllib.request.urlopen(
        urllib.request.Request(u.group(1), headers={"User-Agent": UA}), timeout=30).read()
    b64 = base64.b64encode(data).decode()
    out.append(
        "@font-face{font-family:'Inter';font-style:normal;font-weight:%s;"
        "font-display:swap;src:url(data:font/woff2;base64,%s) format('woff2');"
        "unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,"
        "U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}"
        % (m.group(1), b64))
    print(f"  weight {m.group(1)}: {len(data)/1024:.0f} KB")

open("vendor/inter.css", "w", encoding="utf-8").write("\n".join(out))
import os
print(f"wrote vendor/inter.css ({os.path.getsize('vendor/inter.css')/1024:.0f} KB, "
      f"{len(out)-1} weights)")
