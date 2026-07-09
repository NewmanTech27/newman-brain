#!/usr/bin/env python3
"""token_audit.py — Phase 0 measurement of Claude Code transcript token cost.

Reads every .jsonl transcript under a projects dir (one JSON object per line),
sums the exact token accounting the API returns on each assistant turn, and
reports where the money goes. Measure before optimizing.

Usage:
    python3 token_audit.py [PROJECTS_DIR] [--json OUT.json] [--top N]

Default PROJECTS_DIR = ~/.claude/projects/-home-jesus/

Token fields (per assistant message.usage) are EXACT from the API:
    input_tokens               — fresh input, billed at input rate
    cache_creation_input_tokens— prefix written to cache (5m/1h split available)
    cache_read_input_tokens    — prefix served from cache (0.1x input)
    output_tokens              — generated tokens (incl. reasoning)

Tool-result payload sizes are APPROXIMATE (chars/4), since the transcript
stores the rendered text, not its exact token count.
"""
import json, glob, os, sys, collections, re, argparse

# ---- Opus 4.8 pricing, USD per 1M tokens (standard tier) --------------------
PRICE = {
    "input":       15.00,
    "output":      75.00,
    "cache_5m":    18.75,   # 1.25x input
    "cache_1h":    30.00,   # 2.00x input
    "cache_read":   1.50,   # 0.10x input
}
CHARS_PER_TOK = 4  # rough approximation for payload sizing only

# ---- agent attribution via dominant content marker --------------------------
MARKERS = {
    "cfe":      r"cfe-bill-parser|cfe-collector|bill.?parser",
    "tuesday":  r"tuesday\.newman\.re|tuesday-inputs",
    "data":     r"\bdata agent\b|load.?curve|load.?curva",
    "ppa":      r"ppa_pricer|\bppa agent\b",
    "cto":      r"merge veto|CTO (?:review|verdict|session)",
    "devops":   r"supabase-devops|branch audit",
    "research": r"ai.?research|token_audit|_practices",
}
MARKERS_C = {k: re.compile(v, re.I) for k, v in MARKERS.items()}


def label_agent(raw_text):
    counts = collections.Counter()
    for k, c in MARKERS_C.items():
        n = len(c.findall(raw_text))
        if n:
            counts[k] = n
    if not counts:
        return "unknown"
    return counts.most_common(1)[0][0]


def content_blocks(msg):
    c = msg.get("content")
    if isinstance(c, list):
        return c
    return []


def block_text_len(block):
    """Approx char length of a tool_result / text block content."""
    cont = block.get("content")
    if isinstance(cont, str):
        return len(cont)
    if isinstance(cont, list):
        total = 0
        for b in cont:
            if isinstance(b, dict):
                total += len(b.get("text", "") or "")
        return total
    return 0


def analyze(files):
    sessions = {}          # sid -> dict
    tool_payload = collections.defaultdict(lambda: {"calls": 0, "chars": 0, "max": 0})
    turns = []             # list of per-turn records for top-N
    tool_use_names = {}    # tool_use_id -> tool name (to attribute result payloads)

    for f in files:
        sid = os.path.basename(f)
        try:
            with open(f, encoding="utf-8") as fh:
                lines = fh.readlines()
        except Exception:
            continue
        raw = "".join(lines)
        agent = label_agent(raw)

        s = sessions.setdefault(sid, {
            "agent": agent, "input": 0, "output": 0, "cache_read": 0,
            "cache_5m": 0, "cache_1h": 0, "cache_creation": 0, "turns": 0,
            "sidechain_turns": 0, "models": collections.Counter(),
            "first_ts": None, "last_ts": None,
        })

        # first pass: map tool_use ids -> names (for payload attribution)
        for line in lines:
            try:
                o = json.loads(line)
            except Exception:
                continue
            for b in content_blocks(o.get("message", {})):
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    tool_use_names[b.get("id")] = b.get("name", "?")

        pending_result_chars = 0   # payload fed into the NEXT assistant turn
        pending_result_top = ("", 0)
        seen_ids = set()           # dedupe: harness writes each msg.id on N lines

        for line in lines:
            try:
                o = json.loads(line)
            except Exception:
                continue
            typ = o.get("type")
            msg = o.get("message", {})
            ts = o.get("timestamp")
            if ts:
                s["first_ts"] = s["first_ts"] or ts
                s["last_ts"] = ts

            if typ == "user":
                # accumulate tool_result payloads sitting between assistant turns
                for b in content_blocks(msg):
                    if isinstance(b, dict) and b.get("type") == "tool_result":
                        tuid = b.get("tool_use_id")
                        if tuid in seen_ids:
                            continue   # re-logged tool_result, count once
                        seen_ids.add(tuid)
                        n = block_text_len(b)
                        name = tool_use_names.get(tuid, "?")
                        tp = tool_payload[name]
                        tp["calls"] += 1
                        tp["chars"] += n
                        tp["max"] = max(tp["max"], n)
                        pending_result_chars += n
                        if n > pending_result_top[1]:
                            pending_result_top = (name, n)

            elif typ == "assistant":
                u = msg.get("usage")
                if not u:
                    continue
                mid = msg.get("id")
                if mid is not None:
                    if mid in seen_ids:
                        continue   # same API message, re-logged per content block
                    seen_ids.add(mid)
                inp = u.get("input_tokens", 0)
                out = u.get("output_tokens", 0)
                cr = u.get("cache_read_input_tokens", 0)
                cc = u.get("cache_creation_input_tokens", 0)
                cc_split = u.get("cache_creation", {}) or {}
                c5 = cc_split.get("ephemeral_5m_input_tokens", cc)
                c1 = cc_split.get("ephemeral_1h_input_tokens", 0)
                model = msg.get("model", "?")
                is_side = o.get("isSidechain", False)

                s["input"] += inp
                s["output"] += out
                s["cache_read"] += cr
                s["cache_creation"] += cc
                s["cache_5m"] += c5
                s["cache_1h"] += c1
                s["turns"] += 1
                if is_side:
                    s["sidechain_turns"] += 1
                s["models"][model] += 1

                # tool_use names this turn is about to call
                calls = [b.get("name") for b in content_blocks(msg)
                         if isinstance(b, dict) and b.get("type") == "tool_use"]

                turns.append({
                    "sid": sid, "agent": agent, "ts": ts, "model": model,
                    "input": inp, "output": out, "cache_read": cr,
                    "cache_creation": cc, "sidechain": is_side,
                    "context": cr + cc + inp,       # total context size this turn
                    "fed_chars": pending_result_chars,
                    "fed_top": pending_result_top,
                    "calls": calls,
                })
                pending_result_chars = 0
                pending_result_top = ("", 0)

    return sessions, tool_payload, turns


def cost(d):
    return (d["input"] * PRICE["input"]
            + d["output"] * PRICE["output"]
            + d.get("cache_5m", 0) * PRICE["cache_5m"]
            + d.get("cache_1h", 0) * PRICE["cache_1h"]
            + d["cache_read"] * PRICE["cache_read"]) / 1_000_000


def hit_rate(cr, cc):
    denom = cr + cc
    return (cr / denom) if denom else 0.0


def fmt(n):
    return f"{n:,}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("projects_dir", nargs="?",
                    default=os.path.expanduser("~/.claude/projects/-home-jesus/"))
    ap.add_argument("--json", dest="json_out")
    ap.add_argument("--top", type=int, default=20)
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.projects_dir, "**", "*.jsonl"),
                             recursive=True))
    sessions, tool_payload, turns = analyze(files)

    # ---- global totals ----
    g = collections.Counter()
    for s in sessions.values():
        for k in ("input", "output", "cache_read", "cache_creation",
                  "cache_5m", "cache_1h", "turns"):
            g[k] += s[k]
    total_ctx = g["input"] + g["cache_read"] + g["cache_creation"]
    total_cost = sum(cost(s) for s in sessions.values())

    W = 78
    print("=" * W)
    print("TOKEN AUDIT — Claude Code transcripts")
    print(f"dir: {args.projects_dir}")
    print(f"transcripts: {len(files)}   sessions-with-usage: "
          f"{sum(1 for s in sessions.values() if s['turns'])}   "
          f"assistant turns: {fmt(g['turns'])}")
    print("=" * W)

    print("\n## GLOBAL TOKENS")
    rows = [
        ("input (fresh)",      g["input"]),
        ("output (gen+reason)", g["output"]),
        ("cache_read",         g["cache_read"]),
        ("cache_creation",     g["cache_creation"]),
        ("  ├ ephemeral_5m",   g["cache_5m"]),
        ("  └ ephemeral_1h",   g["cache_1h"]),
    ]
    for name, v in rows:
        pct = 100 * v / total_ctx if total_ctx else 0
        print(f"  {name:<22} {fmt(v):>16}  {pct:5.1f}% of context-in")
    print(f"  {'TOTAL context-in':<22} {fmt(total_ctx):>16}")
    print(f"\n  cache HIT RATE (read/(read+creation)): "
          f"{100*hit_rate(g['cache_read'], g['cache_creation']):.1f}%")
    print(f"  input:output ratio: {g['input']/max(g['output'],1):.1f} : 1")
    print(f"  est. cost (Opus 4.8 rates): ${total_cost:,.2f}")
    if g["turns"]:
        print(f"  per-turn avg: input {fmt(g['input']//g['turns'])}  "
              f"output {fmt(g['output']//g['turns'])}  "
              f"cache_read {fmt(g['cache_read']//g['turns'])}  "
              f"cache_creation {fmt(g['cache_creation']//g['turns'])}")

    # ---- per agent ----
    print("\n## PER AGENT")
    agg = collections.defaultdict(lambda: collections.Counter())
    for s in sessions.values():
        a = agg[s["agent"]]
        for k in ("input", "output", "cache_read", "cache_creation",
                  "cache_5m", "cache_1h", "turns"):
            a[k] += s[k]
        a["cost"] += 0  # placeholder
    print(f"  {'agent':<10}{'turns':>7}{'input':>12}{'output':>11}"
          f"{'cache_rd':>13}{'cache_cr':>13}{'hit%':>7}{'cost$':>10}")
    for a in sorted(agg, key=lambda x: -(agg[x]["input"] + agg[x]["cache_creation"])):
        d = agg[a]
        c = cost(d)
        print(f"  {a:<10}{d['turns']:>7}{fmt(d['input']):>12}"
              f"{fmt(d['output']):>11}{fmt(d['cache_read']):>13}"
              f"{fmt(d['cache_creation']):>13}"
              f"{100*hit_rate(d['cache_read'],d['cache_creation']):>6.0f}%"
              f"{c:>10.2f}")

    # ---- per session (top by cost) ----
    print("\n## TOP SESSIONS BY COST")
    ranked = sorted(sessions.items(), key=lambda kv: -cost(kv[1]))
    print(f"  {'session':<12}{'agent':<9}{'turns':>6}{'input':>11}"
          f"{'out':>9}{'cache_cr':>12}{'hit%':>6}{'cost$':>9}")
    for sid, s in ranked[:15]:
        if not s["turns"]:
            continue
        print(f"  {sid[:10]:<12}{s['agent']:<9}{s['turns']:>6}"
              f"{fmt(s['input']):>11}{fmt(s['output']):>9}"
              f"{fmt(s['cache_creation']):>12}"
              f"{100*hit_rate(s['cache_read'],s['cache_creation']):>5.0f}%"
              f"{cost(s):>9.2f}")

    # ---- tool payloads ----
    print("\n## TOOL-RESULT PAYLOADS (approx tokens = chars/4)")
    print(f"  {'tool':<28}{'calls':>8}{'~tok total':>14}{'~tok avg':>12}{'~tok max':>12}")
    for name, tp in sorted(tool_payload.items(), key=lambda kv: -kv[1]["chars"])[:15]:
        tot = tp["chars"] // CHARS_PER_TOK
        avg = tot // max(tp["calls"], 1)
        mx = tp["max"] // CHARS_PER_TOK
        print(f"  {name[:28]:<28}{tp['calls']:>8}{fmt(tot):>14}"
              f"{fmt(avg):>12}{fmt(mx):>12}")

    # ---- top turns by input ----
    print(f"\n## TOP {args.top} TURNS BY INPUT TOKENS (cause = largest payload fed in)")
    print(f"  {'input':>9}{'out':>7}{'ratio':>8}  {'agent':<9}{'session':<11}"
          f"{'fed(top tool→~tok)':<26}{'calls'}")
    for t in sorted(turns, key=lambda x: -x["input"])[:args.top]:
        ratio = t["input"] / max(t["output"], 1)
        fed = f"{t['fed_top'][0]}→{fmt(t['fed_top'][1]//CHARS_PER_TOK)}" if t["fed_top"][1] else "-"
        calls = ",".join(dict.fromkeys(t["calls"]))[:34] or "-"
        print(f"  {fmt(t['input']):>9}{fmt(t['output']):>7}{ratio:>7.0f}x  "
              f"{t['agent']:<9}{t['sid'][:9]:<11}{fed:<26}{calls}")

    # ---- context-in : output observation (the charter's 33,560 -> 5) ----
    # context-in = input + cache_read + cache_creation, i.e. everything the model
    # must attend to on this turn. This is what "33,560 input tokens" meant.
    lopsided = [t for t in turns if t["context"] >= 30000 and t["output"] <= 50]
    print(f"\n## OUTPUT-COMPRESSION CHECK (context-in vs output)")
    print(f"  turns with context-in>=30k AND output<=50: {len(lopsided)} "
          f"({100*len(lopsided)/max(len(turns),1):.1f}% of turns)")
    if lopsided:
        s_in = sum(t["context"] for t in lopsided)
        s_out = sum(t["output"] for t in lopsided)
        print(f"  those turns: {fmt(s_in)} context-in -> {fmt(s_out)} output "
              f"(mean ratio {s_in/max(s_out,1):,.0f}:1)")
    med_ctx = sorted(t["context"] for t in turns)[len(turns)//2] if turns else 0
    print(f"  median context-in per turn: {fmt(med_ctx)}")
    print(f"  → output tokens are {100*g['output']/max(total_ctx+g['output'],1):.1f}% "
          f"of all tokens billed. Confirms: compression of output is not the lever.")

    # ---- Tier 3 Economics KPIs (KPIS.md) — greppable, one line each ---------
    # Every KPI is computed here from the transcripts, by this command.
    eco1 = 100 * hit_rate(g["cache_read"], g["cache_creation"])
    # ECO-2: the baseline "33,560:5" was a cold turn (cache_read=0), so its
    # 33,560 = input + cache_creation = all input-side tokens paid at write price.
    # The faithful fleet analog is non-cached-input : output.
    noncached_in = g["input"] + g["cache_creation"]
    eco2_paid = noncached_in / max(g["output"], 1)
    eco2_attn = total_ctx / max(g["output"], 1)   # all input-side : output
    print("\n## KPI — Tier 3 Economics (KPIS.md)")
    print(f"  ECO-1 cache_hit_rate      = {eco1:.1f}%   "
          f"(cache_read {fmt(g['cache_read'])} / (read+creation {fmt(g['cache_read']+g['cache_creation'])}))")
    print(f"  ECO-2 input:output        = {eco2_paid:.1f} : 1  (non-cached-input:output; "
          f"attention-in:output = {eco2_attn:.0f}:1)")
    print(f"  ECO-3 tokens_per_point    = BLOCKED — no machine-readable CTO verdict artifact to divide by")
    print(f"  ECO-4 rework_rate         = BLOCKED — no CTO submission/rejection log to count")

    if args.json_out:
        out = {
            "files": len(files),
            "global": dict(g),
            "total_context_in": total_ctx,
            "cache_hit_rate": hit_rate(g["cache_read"], g["cache_creation"]),
            "est_cost_usd": total_cost,
            "per_agent": {a: dict(agg[a]) | {"cost": cost(agg[a])} for a in agg},
            "sessions": {sid: {k: v for k, v in s.items()
                               if k not in ("models",)} | {"cost": cost(s)}
                         for sid, s in sessions.items()},
        }
        with open(args.json_out, "w") as fh:
            json.dump(out, fh, indent=2, default=str)
        print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
