#!/usr/bin/env python3
"""Generate the favicon / touch-icon set from the CCCM Cluster logo.

The source logo is a wide lockup (figure mark above a "CCCM CLUSTER / SOMALIA"
wordmark). At 16px the wordmark is an unreadable smear, so the icon uses the figure
mark alone — the part of the lockup that is actually recognisable at tab size.

Run: python tools/make_icons.py     (writes into public/)
Re-run whenever logo/CCCMCluster_Somalia.png changes.
"""
import json, os
from PIL import Image, ImageFilter, ImageDraw

SRC = os.path.join("logo", "CCCMCluster_Somalia.png")
OUT = "public"
TEAL = (31, 107, 114)          # --teal-d, matches the dashboard header

os.makedirs(OUT, exist_ok=True)
logo = Image.open(SRC).convert("RGBA")
W, H = logo.size

# The figure mark sits above the wordmark. Take the top band, then tighten to whatever
# is actually inked so the crop survives a re-export of the logo at a different size.
band = logo.crop((0, 0, W, int(H * 0.60)))
bbox = band.getbbox()          # alpha-based bounds of the mark + its baseline rule
mark = band.crop(bbox)
mw, mh = mark.size


def square(px, bg=None, pad=0.12):
    """Fit the mark on a square canvas, centred, without distorting its aspect."""
    canvas = Image.new("RGBA", (px, px), bg if bg else (0, 0, 0, 0))
    inner = int(px * (1 - 2 * pad))
    scale = min(inner / mw, inner / mh)
    w, h = max(1, int(mw * scale)), max(1, int(mh * scale))
    canvas.paste(mark.resize((w, h), Image.LANCZOS),
                 ((px - w) // 2, (px - h) // 2),
                 mark.resize((w, h), Image.LANCZOS))
    return canvas


def _figures():
    """Split the mark into individual figures by vertical gaps in the ink profile.

    The baseline rule runs the full width and would bridge every figure, so it is
    excluded from the profile before segmenting.
    """
    a = mark.split()[3]
    body = a.crop((0, 0, mw, int(mh * 0.92)))          # drop the baseline rule
    cols = [sum(body.crop((x, 0, x + 1, body.height)).getdata()) for x in range(mw)]
    thresh = max(cols) * 0.02
    spans, run = [], None
    for x, v in enumerate(cols):
        if v > thresh and run is None:
            run = x
        elif v <= thresh and run is not None:
            if x - run > mw * 0.03:
                spans.append((run, x))
            run = None
    if run is not None:
        spans.append((run, mw))
    return spans


def _pick_small_fig():
    """Choose one figure for the tab-sized icon.

    Adjacent figures in the lockup overlap, so a gap-based span can cover two of them
    (the child and the standing adult come through as one 278px-wide span). A single
    standing figure is tall and narrow, so among the near-tallest spans take the
    narrowest — that reliably lands on one body rather than a pair.
    """
    if not FIGS:
        return None
    def box(s):
        return mark.crop((s[0], 0, s[1], int(mh * 0.92))).getbbox()
    def h(s):
        b = box(s)
        return (b[3] - b[1]) if b else 0
    # Near-tallest, then narrowest. The tall-and-narrow spans are lone standing figures;
    # the broader ones are either two figures merged by the gap detector or a figure
    # holding a child, and both silhouette into an unreadable blob at 16px.
    tallest = max(h(s) for s in FIGS)
    return min((s for s in FIGS if h(s) >= tallest * 0.9), key=lambda s: s[1] - s[0])


FIGS = _figures()
SMALL_FIG = _pick_small_fig()


def _silhouette(span):
    """Solid white silhouette of one figure.

    The mark is outline art. Thickening the strokes at 16px just closes the interior
    into a blob, so instead the outline is filled deliberately: flood the background
    inwards from the border, then take everything it could not reach as the body. Done
    at full resolution and downscaled, so the edges stay smooth.
    """
    fig = mark.crop((span[0], 0, span[1], int(mh * 0.92)))
    fig = fig.crop(fig.getbbox())
    ink = fig.split()[3].point(lambda v: 255 if v > 40 else 0)
    # Pad by 1px so the flood has somewhere to start, then seal the bottom: the figure
    # was cropped above its baseline rule, leaving the outline open at the feet, and an
    # unsealed outline lets the flood straight into the body it is meant to fill.
    canvas = Image.new("L", (ink.width + 2, ink.height + 3), 0)
    canvas.paste(ink, (1, 1))
    ImageDraw.Draw(canvas).rectangle(
        [0, ink.height, canvas.width - 1, canvas.height - 1], fill=255)
    ImageDraw.floodfill(canvas, (0, 0), 128)           # 128 marks reachable background
    body = canvas.point(lambda v: 0 if v == 128 else 255)
    return Image.merge("RGBA", (body, body, body, body)).crop(
        (1, 1, ink.width + 1, ink.height + 1))


def tile(px, pad=0.06):
    """Icon at `px`: the full official lockup on a white ground, exactly as the
    Service Mapping dashboard's tab icon shows it (that site serves the raw logo
    PNG as its favicon). No derived silhouettes, no invented teal tile - the mark
    users already recognise, letterboxed on white."""
    canvas = Image.new("RGBA", (px, px), (255, 255, 255, 255))
    inner = int(px * (1 - 2 * pad))
    scale = min(inner / W, inner / H)
    w, h = max(1, int(W * scale)), max(1, int(H * scale))
    sized = logo.resize((w, h), Image.LANCZOS)
    canvas.paste(sized, ((px - w) // 2, (px - h) // 2), sized)
    return canvas


# --- favicons: full lockup on white, matching the Service Mapping tab ---------------
for px in (16, 32):
    tile(px).save(os.path.join(OUT, f"favicon-{px}x{px}.png"))

tile(48).save(os.path.join(OUT, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])

tile(180, pad=0.08).save(os.path.join(OUT, "apple-touch-icon.png"))
for px in (192, 512):
    tile(px, pad=0.08).save(os.path.join(OUT, f"android-chrome-{px}x{px}.png"))

# --- social preview: 1200x630, the full lockup on white ---------------------------
og = Image.new("RGBA", (1200, 630), (255, 255, 255, 255))
scale = min(1000 / W, 430 / H)
lw, lh = int(W * scale), int(H * scale)
sized = logo.resize((lw, lh), Image.LANCZOS)
og.paste(sized, ((1200 - lw) // 2, (630 - lh) // 2 - 20), sized)
og.convert("RGB").save(os.path.join(OUT, "og-image.png"), optimize=True)

with open(os.path.join(OUT, "site.webmanifest"), "w", encoding="utf-8") as f:
    json.dump({
        "name": "CCCM Somalia — Site Monitoring Dashboard",
        "short_name": "CCCM Somalia",
        "icons": [
            {"src": "/android-chrome-192x192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/android-chrome-512x512.png", "sizes": "512x512", "type": "image/png"},
        ],
        "theme_color": "#104E5D",
        "background_color": "#F5F5F1",
        "display": "standalone",
    }, f, indent=2)

print("icons written to", OUT + "/:")
for n in sorted(os.listdir(OUT)):
    if n != "index.html":
        print(f"   {n:32s} {os.path.getsize(os.path.join(OUT, n)):>8,} bytes")
