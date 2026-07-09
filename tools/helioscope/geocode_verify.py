#!/usr/bin/env python3
"""Resolve fuzzy CFE service addresses to a real rooftop, with a confidence score.

CFE addresses are "between streets" style and often name a landmark instead of a
street number ("HOTEL FIESTA INN", "FTE A SUZUKI"). Strategy per site:

  1. Places Text Search — query built from the landmark/brand + municipio.
     Branded POIs (hotels, plazas) are the strongest signal for this portfolio.
  2. Geocoding API — the literal address (calle1, colonia, cp, municipio) as
     an independent cross-check.
  3. Google Solar API buildingInsights — confirms there is a real building at
     the chosen point and returns roof segments + max panel count, which
     pre-fills the HelioScope field segment and sanity-checks its module count.

Confidence (0-100), tiered:
  >= 80 HIGH    auto-create the HelioScope design
  50-79 MEDIUM  create design but flag for human confirmation of the roof
  <  50 LOW     do not design; queue for manual location pinning

Requires GOOGLE_MAPS_API_KEY (Places API (New), Geocoding API, Solar API enabled).
Usage: geocode_verify.py [--site RPU] [--in sites.json] [--out out/verified_sites.json]
"""
import argparse
import json
import math
import os
import re
import sys
import urllib.parse
import urllib.request

PLACES_URL = "https://places.googleapis.com/v1/places:searchText"
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
SOLAR_URL = "https://solar.googleapis.com/v1/buildingInsights:findClosest"

# Landmark/brand tokens seen in this portfolio (Grupo Posadas trust + franchises).
BRAND_HINTS = [
    (re.compile(r"FIESTA AMERICANA", re.I), "Fiesta Americana"),
    (re.compile(r"FIESTA INN LOFT|HOTEL ONE|EL HOTEL ONE", re.I), "One Hotel"),
    (re.compile(r"FIESTA INN|FIESTA I\b", re.I), "Fiesta Inn"),
    (re.compile(r"GRUPO POSADAS|FIDEICOMISO.*1596", re.I), "Fiesta Inn"),  # trust default: Posadas brand
]
JUNK = re.compile(r"\b(CALLE2|S N|SSE\.|DP\w*|SE\d+|\d{3,}KVA|ORDEN L\d+|\d{6,})\b", re.I)


def http_json(url, headers=None, body=None):
    req = urllib.request.Request(url, headers=headers or {}, method="POST" if body else "GET",
                                 data=json.dumps(body).encode() if body else None)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def clean(text):
    return re.sub(r"\s{2,}", " ", JUNK.sub("", text or "")).strip()


def brand_of(site):
    blob = " ".join([site.get("calle1", ""), site.get("calle2", ""), site.get("client_name", "")])
    for rx, brand in BRAND_HINTS:
        if rx.search(blob):
            return brand
    return None


def places_search(key, query, region_bias=None):
    body = {"textQuery": query, "languageCode": "es", "regionCode": "MX"}
    if region_bias:
        body["locationBias"] = {"circle": {"center": region_bias, "radius": 30000.0}}
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.types,places.id",
    }
    return http_json(PLACES_URL, headers, body).get("places", [])


def geocode(key, address):
    url = f"{GEOCODE_URL}?address={urllib.parse.quote(address)}&region=mx&key={key}"
    res = http_json(url).get("results", [])
    return res[0] if res else None


def solar_insights(key, lat, lng):
    url = f"{SOLAR_URL}?location.latitude={lat}&location.longitude={lng}&requiredQuality=MEDIUM&key={key}"
    try:
        return http_json(url)
    except Exception:
        return None  # Solar API coverage in MX is partial; absence is not disqualifying


def haversine_m(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 6371000 * 2 * math.asin(math.sqrt(h))


def verify_site(key, site):
    brand = brand_of(site)
    landmark = clean(site["calle1"])
    place_q = f"{brand or landmark} {site['municipio']} {site['estado']}"
    addr_q = ", ".join(filter(None, [clean(site["calle1"]), clean(site["colonia"]),
                                     f"{site['cp']} {site['municipio']}", site["estado"], "México"]))

    geo = geocode(key, addr_q)
    bias = None
    if geo:
        loc = geo["geometry"]["location"]
        bias = {"latitude": loc["lat"], "longitude": loc["lng"]}
    places = places_search(key, place_q, bias)
    place = places[0] if places else None

    score, evidence = 0, []
    chosen = None

    if place:
        chosen = (place["location"]["latitude"], place["location"]["longitude"])
        if "lodging" in place.get("types", []) or brand:
            score += 40
            evidence.append(f"POI match: {place['displayName']['text']} ({place['formattedAddress']})")
        else:
            score += 25
            evidence.append(f"Place found (non-lodging): {place['displayName']['text']}")
        if site["cp"] in place.get("formattedAddress", ""):
            score += 15
            evidence.append(f"CP {site['cp']} matches POI address")
        if site["municipio"].lower() in place.get("formattedAddress", "").lower():
            score += 10
            evidence.append("municipio matches POI address")

    if geo:
        gloc = (geo["geometry"]["location"]["lat"], geo["geometry"]["location"]["lng"])
        lt = geo["geometry"].get("location_type", "APPROXIMATE")
        score += {"ROOFTOP": 20, "RANGE_INTERPOLATED": 10}.get(lt, 0)
        evidence.append(f"geocode {lt}: {geo.get('formatted_address', '')}")
        if chosen and haversine_m(chosen, gloc) < 800:
            score += 15
            evidence.append(f"POI and geocode agree within {haversine_m(chosen, gloc):.0f} m")
        chosen = chosen or gloc

    solar = None
    if chosen:
        solar = solar_insights(key, *chosen)
        if solar and solar.get("solarPotential"):
            sp = solar["solarPotential"]
            evidence.append(f"Solar API: building found, roof {sp.get('wholeRoofStats', {}).get('areaMeters2', 0):.0f} m2, "
                            f"max {sp.get('maxArrayPanelsCount', '?')} panels")
            score = min(100, score + 10)

    tier = "HIGH" if score >= 80 else "MEDIUM" if score >= 50 else "LOW"
    return {**site, "brand_guess": brand, "place_query": place_q, "geocode_query": addr_q,
            "lat": chosen[0] if chosen else None, "lng": chosen[1] if chosen else None,
            "confidence": min(score, 100), "tier": tier, "evidence": evidence,
            "place_id": place.get("id") if place else None,
            "solar_max_panels": (solar or {}).get("solarPotential", {}).get("maxArrayPanelsCount"),
            "solar_roof_m2": (solar or {}).get("solarPotential", {}).get("wholeRoofStats", {}).get("areaMeters2")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default=os.path.join(os.path.dirname(__file__), "sites.json"))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "out", "verified_sites.json"))
    ap.add_argument("--site", help="verify a single RPU")
    args = ap.parse_args()

    key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not key:
        sys.exit("GOOGLE_MAPS_API_KEY not set (needs Places API (New) + Geocoding API + Solar API)")

    sites = json.load(open(args.inp))["sites"]
    if args.site:
        sites = [s for s in sites if s["rpu"] == args.site]

    results = []
    for s in sites:
        r = verify_site(key, s)
        print(f"{r['rpu']}  {r['tier']:6} {r['confidence']:3}%  {r['evidence'][0] if r['evidence'] else 'no match'}")
        results.append(r)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    json.dump({"results": results}, open(args.out, "w"), ensure_ascii=False, indent=1)
    print(f"\n{len(results)} sites -> {args.out}")


if __name__ == "__main__":
    main()
