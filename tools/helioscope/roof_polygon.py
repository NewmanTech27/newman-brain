#!/usr/bin/env python3
"""Usable-roof polygons from keyless satellite imagery — the no-API-key leg
between geocode_verify.py and the HelioScope design.

While the Google Solar API key is pending, this step answers "which part of
the roof is actually installable" with geometry, not just a m2 summary:

  1. --fetch    stitch Esri World Imagery tiles (free, no key) around the
                verified point into out/roof/<RPU>_z<Z>.png + a georef sidecar
                (Web Mercator tile origin), so any pixel maps to lat/lng.
  2. (human/LLM) look at the image, digitize the usable planes and obstacles
                into out/roof/<RPU>_polygons.json (pixel coordinates).
  3. --export   geodesic area per polygon, module packing estimate
                (same constants as design_pack.py), and emits:
                  out/roof/<RPU>.kml            Google Earth overlay
                  out/roof/<RPU>.geojson        HelioScope/GIS import
                  out/roof/<RPU>_annotated.png  polygon burned into the image

When the Solar/HelioScope keys land, the same polygons paste into a HelioScope
field segment; nothing here is throwaway.

Usage:
  .venv/bin/python roof_polygon.py --site 016040800020 --fetch [--zoom 19] [--grid 5]
  .venv/bin/python roof_polygon.py --site 016040800020 --export
"""
import argparse
import json
import math
import os
import sys
import time
import urllib.request

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOF_DIR = os.path.join(HERE, "out", "roof")
TILE_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
TILE = 256

# keep in sync with design_pack.py
MODULE_WP = 575
MODULE_M2 = 2.69
PACKING = 0.75  # on an already-digitized clear plane (rows + walkways), vs 0.55 on gross roof


def latlng_to_tile(lat, lng, z):
    n = 2 ** z
    x = (lng + 180.0) / 360.0 * n
    y = (1.0 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2.0 * n
    return x, y


def pixel_to_latlng(px, py, georef):
    z, x0, y0 = georef["zoom"], georef["tile_x0"], georef["tile_y0"]
    n = 2 ** z
    gx = x0 + px / TILE
    gy = y0 + py / TILE
    lng = gx / n * 360.0 - 180.0
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * gy / n))))
    return lat, lng


def polygon_area_m2(latlngs):
    """Shoelace on a local equirectangular projection — exact enough for roofs."""
    lat0 = sum(p[0] for p in latlngs) / len(latlngs)
    mx = 111320.0 * math.cos(math.radians(lat0))
    my = 110574.0
    pts = [((p[1]) * mx, (p[0]) * my) for p in latlngs]
    s = 0.0
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
        s += x1 * y2 - x2 * y1
    return abs(s) / 2.0


def fetch(site, zoom, grid):
    lat, lng = site["lat"], site["lng"]
    xf, yf = latlng_to_tile(lat, lng, zoom)
    half = grid // 2
    x0, y0 = int(xf) - half, int(yf) - half
    img = Image.new("RGB", (grid * TILE, grid * TILE))
    for dy in range(grid):
        for dx in range(grid):
            url = TILE_URL.format(z=zoom, x=x0 + dx, y=y0 + dy)
            for attempt in range(3):
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": "newman-brain/roof_polygon"})
                    with urllib.request.urlopen(req, timeout=30) as r:
                        tile = Image.open(r).convert("RGB")
                    break
                except Exception as e:
                    if attempt == 2:
                        sys.exit(f"tile {zoom}/{y0+dy}/{x0+dx} failed: {e}")
                    time.sleep(1)
            img.paste(tile, (dx * TILE, dy * TILE))

    georef = {"rpu": site["rpu"], "zoom": zoom, "tile_x0": x0, "tile_y0": y0,
              "width": grid * TILE, "height": grid * TILE,
              "center_lat": lat, "center_lng": lng}
    os.makedirs(ROOF_DIR, exist_ok=True)
    base = os.path.join(ROOF_DIR, f"{site['rpu']}_z{zoom}")
    img.save(base + ".png")

    # marked copy: crosshair on the verified point + 100 px grid for digitizing
    marked = img.copy()
    d = ImageDraw.Draw(marked)
    cx, cy = (xf - x0) * TILE, (yf - y0) * TILE
    for gx in range(0, marked.width, 100):
        d.line([(gx, 0), (gx, marked.height)], fill=(255, 255, 0, 60), width=1)
        d.text((gx + 2, 2), str(gx), fill="yellow")
    for gy in range(0, marked.height, 100):
        d.line([(0, gy), (marked.width, gy)], fill=(255, 255, 0, 60), width=1)
        d.text((2, gy + 2), str(gy), fill="yellow")
    d.line([(cx - 25, cy), (cx + 25, cy)], fill="red", width=3)
    d.line([(cx, cy - 25), (cx, cy + 25)], fill="red", width=3)
    marked.save(base + "_grid.png")

    json.dump(georef, open(base + "_georef.json", "w"), indent=1)
    mpp = 156543.03392 * math.cos(math.radians(lat)) / (2 ** zoom)
    print(f"{base}.png  ({grid}x{grid} tiles, {mpp:.2f} m/px, verified point at pixel {cx:.0f},{cy:.0f})")


def kml_coords(latlngs):
    return " ".join(f"{lng:.7f},{lat:.7f},0" for lat, lng in latlngs + latlngs[:1])


def export(site, zoom):
    base = os.path.join(ROOF_DIR, f"{site['rpu']}_z{zoom}")
    georef = json.load(open(base + "_georef.json"))
    spec = json.load(open(os.path.join(ROOF_DIR, f"{site['rpu']}_polygons.json")))

    img = Image.open(base + ".png").convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Off-nadir imagery displaces tall roofs from their ground position ("lean").
    # spec["lean_px"] = [dx, dy] measured against a ground-truth footprint (OSM);
    # applied only to geographic outputs (KML/GeoJSON), not the annotated image.
    lean = spec.get("lean_px", [0, 0])

    def to_latlng(px, py):
        return pixel_to_latlng(px + lean[0], py + lean[1], georef)

    features, kml_parts, total_m2, total_n = [], [], 0.0, 0
    for poly in spec.get("usable", []):
        latlngs = [to_latlng(px, py) for px, py in poly["pixels"]]
        m2 = polygon_area_m2(latlngs)
        n = int(m2 * PACKING / MODULE_M2)
        kwp = round(n * MODULE_WP / 1000, 1)
        total_m2 += m2
        total_n += n
        poly.update({"latlngs": latlngs, "area_m2": round(m2, 1), "modules": n, "kwp": kwp})
        draw.polygon([tuple(p) for p in poly["pixels"]], fill=(46, 204, 113, 90), outline=(46, 204, 113, 255), width=4)
        features.append({"type": "Feature", "properties": {"name": poly["name"], "area_m2": round(m2, 1),
                                                           "modules": n, "kwp": kwp, "kind": "usable"},
                         "geometry": {"type": "Polygon", "coordinates": [[[lng, lat] for lat, lng in latlngs + latlngs[:1]]]}})
        kml_parts.append(f"""  <Placemark><name>{poly['name']} — {m2:.0f} m2, ~{n} mod / {kwp} kWp</name>
   <styleUrl>#usable</styleUrl>
   <Polygon><outerBoundaryIs><LinearRing><coordinates>{kml_coords(latlngs)}</coordinates></LinearRing></outerBoundaryIs></Polygon>
  </Placemark>""")

    for obs in spec.get("obstacles", []):
        if "pixels" in obs:
            latlngs = [to_latlng(px, py) for px, py in obs["pixels"]]
            draw.polygon([tuple(p) for p in obs["pixels"]], fill=(231, 76, 60, 110), outline=(231, 76, 60, 255), width=3)
            kml_parts.append(f"""  <Placemark><name>Obstáculo: {obs['name']}</name><styleUrl>#obstacle</styleUrl>
   <Polygon><outerBoundaryIs><LinearRing><coordinates>{kml_coords(latlngs)}</coordinates></LinearRing></outerBoundaryIs></Polygon>
  </Placemark>""")
            features.append({"type": "Feature", "properties": {"name": obs["name"], "kind": "obstacle"},
                             "geometry": {"type": "Polygon", "coordinates": [[[lng, lat] for lat, lng in latlngs + latlngs[:1]]]}})
        else:
            lat, lng = to_latlng(*obs["pixel"])
            px, py = obs["pixel"]
            draw.ellipse([px - 8, py - 8, px + 8, py + 8], outline=(231, 76, 60, 255), width=3)
            kml_parts.append(f"""  <Placemark><name>Obstáculo: {obs['name']}</name><styleUrl>#obstaclePt</styleUrl>
   <Point><coordinates>{lng:.7f},{lat:.7f},0</coordinates></Point></Placemark>""")
            features.append({"type": "Feature", "properties": {"name": obs["name"], "kind": "obstacle"},
                             "geometry": {"type": "Point", "coordinates": [lng, lat]}})

    kml = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
 <Document>
  <name>{spec.get('title', site['rpu'])} — área instalable (Newman)</name>
  <Style id="usable"><LineStyle><color>ff71cc2e</color><width>3</width></LineStyle>
   <PolyStyle><color>5971cc2e</color></PolyStyle></Style>
  <Style id="obstacle"><LineStyle><color>ff3c4ce7</color><width>2</width></LineStyle>
   <PolyStyle><color>6e3c4ce7</color></PolyStyle></Style>
  <Style id="obstaclePt"><IconStyle><color>ff3c4ce7</color></IconStyle></Style>
{chr(10).join(kml_parts)}
 </Document>
</kml>
"""
    open(os.path.join(ROOF_DIR, f"{site['rpu']}.kml"), "w").write(kml)
    json.dump({"type": "FeatureCollection", "features": features},
              open(os.path.join(ROOF_DIR, f"{site['rpu']}.geojson"), "w"), indent=1)

    Image.alpha_composite(img, overlay).convert("RGB").save(os.path.join(ROOF_DIR, f"{site['rpu']}_annotated.png"))
    json.dump(spec, open(os.path.join(ROOF_DIR, f"{site['rpu']}_polygons.json"), "w"), ensure_ascii=False, indent=1)
    print(f"usable {total_m2:.0f} m2 -> ~{total_n} x {MODULE_WP} W = {total_n * MODULE_WP / 1000:.1f} kWp "
          f"(packing {PACKING} on clear planes)")
    for ext in (".kml", ".geojson", "_annotated.png"):
        print("  " + os.path.join(ROOF_DIR, site["rpu"] + ext))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", required=True)
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--export", action="store_true")
    ap.add_argument("--zoom", type=int, default=19)
    ap.add_argument("--grid", type=int, default=5, help="tiles per side (odd)")
    ap.add_argument("--verified", default=os.path.join(HERE, "out", "verified_sites.json"))
    args = ap.parse_args()

    sites = {s["rpu"]: s for s in json.load(open(args.verified))["results"]}
    site = sites.get(args.site) or sys.exit(f"RPU {args.site} not in {args.verified}")
    if not site.get("lat"):
        sys.exit(f"RPU {args.site} has no verified location (tier {site.get('tier')})")

    if args.fetch:
        fetch(site, args.zoom, args.grid)
    if args.export:
        export(site, args.zoom)
    if not (args.fetch or args.export):
        sys.exit("nothing to do: pass --fetch and/or --export")


if __name__ == "__main__":
    main()
