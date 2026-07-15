# Qwen3.6 local-model bake-off on the mac mini

**Summary**: Verified the NVIDIA-quantized Qwen3.6 claim, pulled it to the mini via Ollama, and bake-tested it against qwen3.5 on Newman agent tasks — it wins but must be called via /api/chat.
**Tags**: #newman #agents #ollama #llm
**Created**: 2026-06-24
**Source**: macbook session afb0572b-0d7b-4923-8687-5e2201c25aa2.jsonl, user jesus

---

## Content
- Started as onboarding the gws Google Workspace CLI task for jesus@newman.re, then pivoted to confirm/debunk a claim about a quantized Qwen3.6 35B MoE running like a 3B model.
- Pulled qwen3.6 (Q4) to the mini, aliased it, and ran API bake-offs vs qwen3.5 on a representative Newman task (GDMTO/PPA analysis).
- Verdict: qwen3.6 beats qwen3.5 — distinguishes energy-only PPA vs demand/TR-DT charges, computes break-even (2.89 MXN/kWh), self-consumption ratio, GDMTO subcode granularity; 25.5 tok/s, tighter output (2,436 vs 5,333 tokens).
- Gotcha locked in: qwen3.6 requires `/api/chat` (chat template); `/api/generate` skips the template and returns a greeting. Any consumer must use the chat endpoint or `ollama run`.
- Ollama 0.30.10 on the mini was still a manual serve at session end (not yet pinned in launchd).
- Follow-up loop launched: run the flock's task types (savings, research, proposal) through qwen3.6 as the local brain.

## Related Notes
- [[2026-06-21-newman-agents-founding]]
