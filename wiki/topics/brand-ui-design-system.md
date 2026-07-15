# Brand & UI Design Systems

**Summary**: The Newman v3 design system and its sibling brand kits (Kamú, Swiss), the design-committee /loop workflow that grades sites toward 9+/95, and the recurring build/deploy conventions for the client-facing sites.
**Tags**: #newman #ui #proposal #topic
**Created**: 2026-07-15
**Source**: synthesis

---

## Content

### Newman v3
- LIGHT, purple-forward, FLAT: warm-lilac canvas, deep-aubergine text, ONE brand purple **#621558** accent, NO chrome gradients (the navy→magenta gradient lives only inside the 5-bar solar-ray logo isotype). Font: Space Grotesk (swapped from Montserrat). Logo = a cropped fan of dawn light (N / solar rays), scored iconic-grade over an 11-iteration design-committee loop (avg 7.9 → 9.3).
- Live brand site: lopezpalacios.github.io/newman-brand-ui (repo lopezpalacios/newman-brand-ui); `/newman-ui` skill points at it. The Energy Academy tracks brand-ui v3 in lockstep (Space Grotesk 300, no magenta borders/shadows).

### Sibling systems
- **Kamú Living** (`/kamu-ui`): luxury, photography-forward — forest green + one bronze accent, Mulish; used for the Los Cabos investor site.
- **Swiss bank** (`/swiss-bank-ui`): UBS-inspired red/white.

### Committee /loop workflow (repeated across sites)
- Convene role personas (sales-closer / engineer / designer / consultant, or RE mogul / CFO / vacation-rental expert, or YC/energy-VC), iterate R1–R10+ scoring toward a target (9+/10 or 95/100); each iteration committed + pushed. Personas **refuse to fabricate** missing data — loops pause at a "buildable ceiling" when blocked on real numbers the user must supply (Kamú stopped at ~9.0 with 2 personas <9; VC pitch capped ~89 without real bios/LOI/term sheet).
- Anti-vibe-coded feedback sourced by scraping Reddit UI forums (append `.json`).

### Deploy conventions
- Client sites are password-gated HTML/CSS/vanilla-JS with a data room + calculator, deployed to GitHub Pages under NewmanTech27, subdomain via Cloudflare DNS (e.g. afch.newman.re), password emailed to agents@ **from jesus@** (agents@ is a group). All client source/deliverables → Dataroom_Newman/Leads/<Client>.

## Related Notes
- [[2026-06-26-newman-ui-brand-logo-committee]]
- [[2026-06-27-energy-academy-eu-course]]
- [[2026-06-27-kamu-living-investor-site]]
- [[2026-06-20-pepsico-ppa-proposal]]
- [[2026-07-05-afch-ppa-offer-dataroom]]
- [[2026-07-03-kfc-ppa-offer-workflow]]
- [[2026-07-05-newman-academy-pages-deploy-check]]
- [[2026-07-03-deploy-newman-pages-lisa-api-refusal]]
