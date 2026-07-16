
## [2026-07-09] finding | Token audit baseline — cost is cache_read volume, not low hit rate
- Source: cfe-brain/vault/tools/token_audit.py over ~/.claude/projects/-home-jesus/ (431 transcripts, live snapshot)
- Pages created: [[2026-07-09-token-audit-baseline]]
- Tool written: vault/tools/token_audit.py (dedupes by message.id; emits Tier-3 ECO KPIs)
- Key insight: 98.3% cache hit rate is already excellent; the $2,475 spend is cache_read VOLUME (66%) from a median 146,800-token context dragged across 4,168 turns. tuesday session 81cef301 alone = $1,587 (64% of all spend). Output compression confirmed a non-lever (0.4% of tokens). ECO-1=98.3%, ECO-2=5.2:1; ECO-3/ECO-4 BLOCKED on a machine-readable CTO verdict log.
