#!/usr/bin/env python3
"""Minimal HelioScope API client.

HelioScope's API is Enterprise-gated and its endpoint spec ships with the API
key (docs on request from sales@helioscope.com / your account manager), so the
paths below live in helioscope_config.json and MUST be validated against the
docs that come with the key. The flow they document publicly:
Project (location) -> Design (field segments + modules) -> Simulation.

Auth: token in the Authorization header. Set HELIOSCOPE_API_KEY.
"""
import json
import os
import urllib.request

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "helioscope_config.json")


class HelioScope:
    def __init__(self, api_key=None, config=None):
        self.key = api_key or os.environ["HELIOSCOPE_API_KEY"]
        self.cfg = config or json.load(open(CONFIG_PATH))

    def _call(self, method, path, body=None):
        req = urllib.request.Request(
            self.cfg["base_url"].rstrip("/") + path,
            data=json.dumps(body).encode() if body else None,
            method=method,
            headers={"Authorization": self.cfg["auth_scheme"].format(key=self.key),
                     "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)

    def create_project(self, name, lat, lng, address=""):
        return self._call("POST", self.cfg["paths"]["projects"], {
            "name": name, "latitude": lat, "longitude": lng, "address": address,
            "project_type": self.cfg.get("project_type", "commercial")})

    def create_design(self, project_id, name, field_segments, module_id=None):
        """field_segments: list of {geometry: [[lat,lng],...], racking, tilt, azimuth}.
        Geometry from Solar API roof segments when available, else a rectangle
        seeded around the verified point for manual adjustment in the UI."""
        return self._call("POST", self.cfg["paths"]["designs"].format(project_id=project_id), {
            "name": name,
            "field_segments": field_segments,
            "module_id": module_id or self.cfg.get("default_module_id")})

    def run_simulation(self, design_id):
        return self._call("POST", self.cfg["paths"]["simulations"].format(design_id=design_id), {})

    def get_simulation(self, simulation_id):
        return self._call("GET", self.cfg["paths"]["simulation"].format(simulation_id=simulation_id))
