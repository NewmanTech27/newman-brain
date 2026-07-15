# iTerm 6-pane agent org, CEO/CTO loop, and the newman-rebuild v2 reboot

**Summary**: Built the tmux/iTerm multi-agent org (CFE parser, CRM, Supabase/DevOps, cfe-ppa-bess panes) with a CEO orchestrator and CTO reviewer, then rebooted it as the newman-rebuild v2 org with a fresh Supabase project and vaulted secrets.
**Tags**: #newman #agents #devops #crm #tmux #supabase
**Created**: 2026-07-09
**Source**: macbook session fc8bf2fb-2a8b-43bc-902b-8b845848282d.jsonl, user jesus

---

## Content
- iTerm2 split into 6 panes (3 columns × 2): column 1 local Mac, columns 2–3 direct to the droplet; themed dark/high-contrast; sessions wrapped in tmux, run `claude --dangerously-skip-permissions`.
- Named agent sessions: (1) CFE bill parser — WhatsApp + OCR + CFE endpoint extraction; (2) tuesday.newman.re CRM inputs; (3) Supabase/data management + DevOps keeping main current; (4) cfe-ppa-bess (was misc).
- Discipline: each session first assesses its tool's status across conversation/GitHub/Supabase, gets committee-scored /100 striving for 95, and must have a plan before working.
- Company goals set: state-of-the-art tuesday CRM syncing WhatsApp/email/text to pipeline; RPU invoice extraction visualized at extraction.newman.re; client deal offers + salesman calculators with pre-fixed adjustment ranges; all work synced to main, then dev/staging/prod envs in GitHub + Supabase with Actions CI/CD.
- CEO agent created (handover ceo.md, remote-controlled); lesson learned: do NOT run the CEO on the VPS — if the VPS resets you lose remote access; CEO moved to the mini, directing via GitHub issues.
- v2 reboot ("newman-rebuild"): new Supabase project `oioyawhgvazebtarigpc` (us-east-2, ACTIVE_HEALTHY), DB password generated on-box straight into HashiCorp Vault (`NEWMAN_REBUILD_DB_PASSWORD`); repo `newman-rebuild` with charter v2 + 10 seed issues; 5 droplet tmux seats (cto=Opus; data/harvest/engine/crm=Sonnet); old flock retired, newman-architecture main marked FROZEN; DO token rotated to Vault v8 and the leaked plaintext row deleted.
- Gotcha: first Vault password write failed silently (AppRole is read-only) — always verify the token can write before relying on it.

## Related Notes
- [[2026-07-07-droplet-setup-secrets]]
- [[2026-07-07-newman-architecture-cleanroom-deploy]]
