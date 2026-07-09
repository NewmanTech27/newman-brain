#!/usr/bin/env python3
"""Route: Supabase CFE sites -> verified rooftop -> HelioScope project + design.

  1. sites.json          extracted from Supabase (refresh with extract_sites.sql)
  2. geocode_verify.py   Google Places/Geocoding/Solar -> lat/lng + confidence tier
  3. this script         for each site >= --min-confidence: create HelioScope
                         project + seed design, record everything to out/designs.json
                         (load into client.helioscope_site on the dev branch via schema.sql)

Dry-run by default; pass --live to hit the HelioScope API.
Env: HELIOSCOPE_API_KEY (live mode). GOOGLE_MAPS_API_KEY is used by step 2, not here.
"""
import argparse
import json
import os

HERE = os.path.dirname(__file__)


def rectangle_around(lat, lng, meters=40):
    # ~degrees per meter; seed square field segment centered on the verified roof,
    # to be trimmed to the parapet in the HelioScope UI (or replaced by Solar API
    # roof-segment polygons when solar_roof_m2 is present).
    dlat = meters / 111320.0
    dlng = meters / (111320.0 * max(0.2, abs(__import__("math").cos(__import__("math").radians(lat)))))
    return [[lat + dlat, lng - dlng], [lat + dlat, lng + dlng],
            [lat - dlat, lng + dlng], [lat - dlat, lng - dlng]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verified", default=os.path.join(HERE, "out", "verified_sites.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "out", "designs.json"))
    ap.add_argument("--min-confidence", type=int, default=50)
    ap.add_argument("--site", help="single RPU")
    ap.add_argument("--live", action="store_true", help="actually call the HelioScope API")
    args = ap.parse_args()

    sites = json.load(open(args.verified))["results"]
    if args.site:
        sites = [s for s in sites if s["rpu"] == args.site]

    hs = None
    if args.live:
        from helioscope_client import HelioScope
        hs = HelioScope()

    cfg = json.load(open(os.path.join(HERE, "helioscope_config.json")))
    out = []
    for s in sites:
        rec = {"rpu": s["rpu"], "client_name": s["client_name"], "tier": s["tier"],
               "confidence": s["confidence"], "evidence": s["evidence"],
               "lat": s["lat"], "lng": s["lng"], "status": None}
        if s["lat"] is None or s["confidence"] < args.min_confidence:
            rec["status"] = "skipped_low_confidence"
            out.append(rec)
            print(f"{s['rpu']}  SKIP ({s['tier']} {s['confidence']}%)")
            continue

        name = f"{s['rpu']} - {(s.get('brand_guess') or s['client_name'])[:40]} {s['municipio']}"
        segment = {"geometry": rectangle_around(s["lat"], s["lng"]),
                   "racking": cfg["default_racking"], "tilt": cfg["default_tilt_deg"],
                   "azimuth": cfg["default_azimuth_deg"]}
        if args.live:
            proj = hs.create_project(name, s["lat"], s["lng"], s.get("geocode_query", ""))
            design = hs.create_design(proj["id"], "auto-seed v1", [segment])
            rec.update(status="created", helioscope_project_id=proj["id"],
                       helioscope_design_id=design["id"])
            print(f"{s['rpu']}  CREATED project {proj['id']} design {design['id']} ({s['tier']} {s['confidence']}%)")
        else:
            rec.update(status="dry_run", would_create={"project": name, "field_segment": segment,
                                                       "solar_max_panels": s.get("solar_max_panels")})
            print(f"{s['rpu']}  DRY-RUN {name} ({s['tier']} {s['confidence']}%)")
        out.append(rec)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    json.dump({"designs": out}, open(args.out, "w"), ensure_ascii=False, indent=1)
    print(f"\n{sum(1 for r in out if r['status'] != 'skipped_low_confidence')} designed / "
          f"{len(out)} total -> {args.out}")


if __name__ == "__main__":
    main()
