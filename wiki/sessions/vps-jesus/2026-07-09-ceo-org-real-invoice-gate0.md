# CEO Session: Six-Agent Org, Real WhatsApp Invoice Test, GATE 0 Canonicity Ruling

**Summary**: The VPS CEO agent took over the six-agent org, drove a real invoice through the WhatsApp intake (surfacing two prod bugs), got Jesus's "edge function maximalist" doctrine, and executed his canonicity ruling — preserve-both merge of dev+main on integration/gate0.
**Tags**: #newman #agent-org #ceo #gate0 #whatsapp-intake #canonicity
**Created**: 2026-07-09
**Source**: newman-vps session 813a8a67-a8b5-4cf2-8e61-5b8a4db3a291.jsonl, user jesus

---

## Content
- Handover: prior MacBook CEO stood down; VPS session is sole CEO of the six-agent org (cto, cfe, tuesday, data, ppa, research). GATE 0 blocks all merges until Jesus picks the canonical branch; integrity_check.py must exit 0.
- Handover warnings internalized: (1) reset-vs-merge — any canonicity ruling must REPLAY both sides' unique commits, never reset/discard; instructions lacking the word "preserve" are ambiguous, data runs with bypass permissions and won't stop to ask. (2) design-engine live-or-orphan is the top open item (sizing.py lost umbral + inverted PV→BESS charging = possible live DEL-5 exposure).
- Jesus interacted live: asked for org graphs/reports, added tmux tabs/panes, then focused on invoice extraction mapped through all input channels.
- Real-invoice test: Jesus forwarded an actual CFE invoice over the live WhatsApp wire (Twilio ack: "PDF recibido, procesando sus recibos. Te confirmaremos los RPUs."); it initially got stuck, exposing the claim_media type bug (see cfe-bill-parser note); resent after fixes.
- Doctrine from Jesus: "let's become edge function maximalist" — Supabase edge functions preferred for logic because the UI/observability is good.
- Jesus approved the canonicity ruling: dev as base, merge main in, preserve both. data executed the merge in isolated worktree/branch `integration/gate0` — 100+ conflicted files, 119 migrations to reconcile; no shared branch or prod touched.
- CEO explained the fork clearly: main = collector (deploys to newman-vps), dev = CRM (deploys to tuesday.newman.re); picking one branch would delete half the live product, hence merge-not-pick.

## Related Notes
- [[2026-07-09-cfe-real-invoice-claim-media]]
- [[2026-07-09-supabase-devops-gate0]]
- [[newman-architecture-branch-fork]]
