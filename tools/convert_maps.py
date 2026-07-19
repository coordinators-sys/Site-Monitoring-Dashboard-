#!/usr/bin/env python3
"""Convert the UNDP Admin2 + CCCM catchment shapefiles into a compact JSON the
dashboard embeds (data/geo.json). Coordinates rounded to 3 dp (~110 m) — far below
the visual resolution of a national SVG map — which keeps the payload small enough
for the self-contained file. Run manually when boundary files change; the output
is committed, so CI never needs the shapefiles."""
import json, os
import shapefile

B    = r"Somali Maps"
OUT  = os.path.join("data", "geo.json")
ADM2 = os.path.join(B, "somalia_admin2", "Som_Admbnda_Adm2_UNDP.shp")
CA   = os.path.join(B, "catchments", "2025_CA_Shapefiles_V01", "2025_CA_Shapefiles_V01.shp")

def rings(shape, nd=3):
    """Shapefile polygon -> list of rings, deduplicating consecutive rounded points."""
    parts = list(shape.parts) + [len(shape.points)]
    out = []
    for a, b in zip(parts[:-1], parts[1:]):
        ring, last = [], None
        for x, y in shape.points[a:b]:
            p = (round(x, nd), round(y, nd))
            if p != last:
                ring.append([p[0], p[1]]); last = p
        if len(ring) >= 4:
            out.append(ring)
    return out

sf = shapefile.Reader(ADM2)
fields = [f[0] for f in sf.fields[1:]]
districts = []
for sr in sf.iterShapeRecords():
    rec = dict(zip(fields, list(sr.record)))
    districts.append({"pc": rec["admin2Pcod"], "n": rec["admin2Name"],
                      "r": rec["admin1Name"], "rings": rings(sr.shape)})

sf = shapefile.Reader(CA)
fields = [f[0] for f in sf.fields[1:]]
catchments = []
for sr in sf.iterShapeRecords():
    rec = dict(zip(fields, list(sr.record)))
    catchments.append({"ca": rec["Catchment"], "pc": rec["ADM2_Pcode"],
                       "d": rec["ADM2_Dis"], "agency": rec["CCCM_Agenc"],
                       "hh": int(rec["HHs"] or 0), "ind": int(rec["INDs"] or 0),
                       "rings": rings(sr.shape)})

geo = {"districts": districts, "catchments": catchments,
       # our monitoring splits Banadir into Kahda/Daynile sub-districts that the UNDP
       # Admin2 layer does not carry — both render onto the Banadir polygon
       "pcodeAlias": {"SO2210": "SO2201", "SO2203": "SO2201"}}
os.makedirs("data", exist_ok=True)
json.dump(geo, open(OUT, "w", encoding="utf-8"), ensure_ascii=False,
          separators=(",", ":"))
print(f"wrote {OUT}: {len(districts)} districts, {len(catchments)} catchments, "
      f"{os.path.getsize(OUT)/1024:.0f} KB")
