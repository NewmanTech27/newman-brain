#!/usr/bin/env python3
"""Proof-of-concept mode: per-site design packs, no HelioScope API needed.

For each verified site this emits a markdown pack with everything required to
(a) answer "how many modules fit on this roof" and (b) recreate the design by
hand in the HelioScope browser UI in ~5 minutes:

  - verified location, confidence tier and the evidence behind it
  - Google Maps satellite / Street View deep links to eyeball the roof
  - Solar API roof stats when available (roof m2, maxArrayPanelsCount)
  - fallback packing estimate from roof area (flat-roof assumptions below)
  - a paste-ready HelioScope UI checklist (project name, coords, segment specs)

Usage: design_pack.py [--verified out/verified_sites.json] [--out out/packs/]
       [--site RPU] [--roof-m2 N]  (--roof-m2 overrides area for a single site)
"""
import argparse
import json
import os

# Flat commercial roof packing assumptions (match client.design conventions):
# 575 Wp module 2.38 x 1.13 m ≈ 2.69 m2; 10 deg ballasted south rows with
# walkways/setbacks => ~55% of usable roof covered by module area.
MODULE_WP = 575
MODULE_M2 = 2.69
USABLE_FRACTION = 0.55


def packing_estimate(roof_m2):
    n = int(roof_m2 * USABLE_FRACTION / MODULE_M2)
    return n, round(n * MODULE_WP / 1000, 1)


def pack_md(s, roof_m2_override=None):
    lat, lng = s.get("lat"), s.get("lng")
    maps = f"https://www.google.com/maps/@?api=1&map_action=map&center={lat},{lng}&zoom=20&basemap=satellite" if lat else None
    pin = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}" if lat else None
    street = f"https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={lat},{lng}" if lat else None

    roof_m2 = roof_m2_override or s.get("solar_roof_m2")
    fit = None
    if s.get("solar_max_panels"):
        fit = f"{s['solar_max_panels']} panels (Google Solar API maxArrayPanelsCount)"
    elif roof_m2:
        n, kwp = packing_estimate(roof_m2)
        fit = f"~{n} x {MODULE_WP} W = ~{kwp} kWp (packing estimate: {roof_m2:.0f} m2 x {USABLE_FRACTION} / {MODULE_M2} m2)"

    lines = [
        f"# {s['rpu']} — {s.get('brand_guess') or s['client_name']}",
        "",
        f"**Confidence: {s['tier']} ({s['confidence']}%)** — how sure we are this is the actual roof:",
        *[f"- {e}" for e in s.get("evidence", [])],
        "",
        f"- CFE address query: `{s.get('geocode_query', '')}`",
        f"- Location: {f'{lat}, {lng}' if lat else 'UNRESOLVED — manual pin needed'}",
    ]
    if maps:
        lines += [f"- [Satellite view]({maps}) · [Drop pin]({pin}) · [Street View]({street})"]
    lines += ["", f"**Module fit:** {fit or 'unknown — measure roof on the satellite view, rerun with --roof-m2'}", ""]
    if lat:
        lines += [
            "## HelioScope UI checklist (manual, ~5 min)",
            f"1. New Project → name `{s['rpu']} - {(s.get('brand_guess') or s['client_name'])[:40]} {s.get('municipio','')}`,"
            f" location `{lat}, {lng}` (paste coords in the address box).",
            "2. Confirm the satellite image matches the linked view above (same building!).",
            "3. New Design → draw field segment tracing the parapet; racking Fixed Tilt 10 deg,"
            " azimuth 180, row spacing ~0.5 m, module 570-580 W class.",
            f"4. Sanity-check module count vs estimate above{' (' + fit + ')' if fit else ''}.",
            "5. Add keepouts (HVAC, skylights) visible in satellite view; run simulation.",
            f"6. Record design + simulation IDs against RPU {s['rpu']} (client.helioscope_site).",
        ]
    return "\n".join(lines) + "\n"


def main():
    here = os.path.dirname(__file__)
    ap = argparse.ArgumentParser()
    ap.add_argument("--verified", default=os.path.join(here, "out", "verified_sites.json"))
    ap.add_argument("--out", default=os.path.join(here, "out", "packs"))
    ap.add_argument("--site")
    ap.add_argument("--roof-m2", type=float, help="manual roof area override (single --site)")
    args = ap.parse_args()

    sites = json.load(open(args.verified))["results"]
    if args.site:
        sites = [s for s in sites if s["rpu"] == args.site]
    os.makedirs(args.out, exist_ok=True)

    index = ["# Design packs", ""]
    for s in sorted(sites, key=lambda x: -x["confidence"]):
        path = os.path.join(args.out, f"{s['rpu']}.md")
        open(path, "w").write(pack_md(s, args.roof_m2 if args.site else None))
        index.append(f"- [{s['rpu']}]({s['rpu']}.md) — {s['tier']} {s['confidence']}% — "
                     f"{s.get('brand_guess') or s['client_name']} ({s.get('municipio','?')})")
    open(os.path.join(args.out, "INDEX.md"), "w").write("\n".join(index) + "\n")
    print(f"{len(sites)} packs -> {args.out}/")


if __name__ == "__main__":
    main()
