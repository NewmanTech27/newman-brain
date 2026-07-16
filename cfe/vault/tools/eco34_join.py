#!/usr/bin/env python3
"""ECO-3 / ECO-4 join: token_audit (--json) x cto-verdict-log.jsonl.

ECO-3 tokens_per_point = total context-in tokens / Σ numeric CTO score points
ECO-4 rework_rate      = CTO rejections / submissions reviewed

Log schema is freeform: score fields are inconsistently named (*_score),
verdict is prose. A "rejection" = verdict not opening GO/CONFIRMED.

Usage: python3 eco34_join.py AUDIT.json cto-verdict-log.jsonl
"""
import json, re, sys

audit = json.load(open(sys.argv[1]))
log = [json.loads(l) for l in open(sys.argv[2])]

g = audit["global"]
total_ctx = g["input"] + g["cache_read"] + g["cache_creation"]

pts = 0
scored = []
for o in log:
    for k, v in o.items():
        if re.search("score", k, re.I) and isinstance(v, (int, float)):
            pts += v
            scored.append((o["id"], k, v))

subs = len(log)
rejects = sum(0 if re.match(r"(GO|CONFIRMED)", o.get("verdict", ""), re.I) else 1
              for o in log)

print(f"ECO-3 tokens_per_point = {total_ctx:,} / {pts} = {total_ctx/max(pts,1):,.0f} tokens/point")
print(f"       (scored entries: {scored}; {subs-len(scored)}/{subs} entries carry NO numeric score)")
print(f"ECO-4 rework_rate      = {rejects}/{subs} = {100*rejects/max(subs,1):.0f}%")

# CTO-attributed spend, for the honest per-point-of-CTO-work variant
cto = audit["per_agent"].get("cto", {})
cto_ctx = cto.get("input", 0) + cto.get("cache_read", 0) + cto.get("cache_creation", 0)
print(f"\naside: CTO-agent context-in = {cto_ctx:,} over {cto.get('turns',0)} turns, ${cto.get('cost',0):,.2f}")
