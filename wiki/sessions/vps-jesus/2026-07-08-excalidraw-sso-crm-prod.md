# Excalidraw Diagrams, login.newman.re SSO Gate, Contact Enrichment, and "Push to Prod"

**Summary**: Mapped the CFE invoice pipeline in self-hosted Excalidraw, built the Supabase-Auth SSO gate at login.newman.re for all *.newman.re apps, enriched all 2,583 CRM contacts, added WhatsApp salesman onboarding — and established that dev (CRM) and main (CFE collector) deploy two different halves of the product.
**Tags**: #newman #excalidraw #sso #tuesday-crm #whatsapp #branch-fork
**Created**: 2026-07-08
**Source**: newman-vps sessions bd80fd0f-63bd-4f8f-a689-642a1226fee8.jsonl (main, 5.5 MB) and c0b723f5-2f4d-40ce-a456-37735b076298.jsonl (excalidraw CI/CD), user jesus; consolidated

---

## Content
- Excalidraw self-hosted at excalidraw.newman.re; CI/CD built in NewmanTech27/newman-excalidraw (push to main or workflow_dispatch deploys; `EXCALIDRAW_REF` pins version v0.18.1; rollback = re-point `/opt/excalidraw/current` symlink).
- Fine-grained PAT needed Secrets RW + Workflows RW + Actions RW for gh secret set / workflow dispatch (403s otherwise).
- Diagrams: CFE invoice-extraction → Supabase pipeline mapped as .excalidraw; best-practice storage folder `04_Diagrams` on the Newman Shared Drive incl. the stamp library so other LLMs can generate flows.
- Auth evolution: "add auth to excalidraw" → full Supabase-Auth SSO gate at login.newman.re (Google-only after magic-link was removed), `.newman.re` cookie gating all subdomains; DNS for login.newman.re reclaimed from the tuesday app.
- Magic-link detour: branded email template built; SMTP via Gmail app password + Workspace group login@newman.re (send-as for jesus+mario); hit 429/500s on Supabase OTP; magic link removed "for now" (later re-enabled for salesmen).
- Contacts: all 2,583 CRM contacts enriched via website research — category/country tags, company description, address, filters.
- RBAC: admins = mario, jonathan, jesus (admin dashboard onboards users, sees everything); others RLS-scoped by email/phone; ~2,583 contacts visible to admins only, salesmen see own/assigned.
- WhatsApp intake: reads sender number, asks for missing email/name, OpenRouter enriches; onboarded Twilio numbers become salesmen who log in via email magic link; leads auto-assign to the agent whose line received them (whatsapp-intake edge fn v55).
- KEY FACT (the fork): "push all to prod" revealed `main` is 98 behind / diverged from `dev` — `origin/main` deploys the CFE collector on newman-vps, `origin/dev` deploys the CRM on the newman-crm droplet; 53 collector-hardening commits live only on main, 98 CRM commits only on dev. CRM was already fully live; dev→main promotion deliberately NOT done.
- login page deployed at `/opt/newman-sso` on the VPS (no git repo — later a capture target).

## Related Notes
- [[newman-architecture-branch-fork]]
- [[2026-07-10-newman-rebuild-seat-org]]
- [[2026-07-08-tuesday-crm-committee-loop]]
