# cfe-brain

Compiled knowledge base for Newman Energy, maintained by LLM agents, viewed in Obsidian.

Karpathy's wiki method, adapted for engineering knowledge: claims about code carry provenance
(`file:line`, commit SHA) and a freshness stamp, because code rots under a wiki in a way that
papers do not.

- `CLAUDE.md` — the schema. Read it first. It defines ingest / query / lint.
- `raw/` — sources awaiting compilation
- `wiki/` — the compiled, linked knowledge
- `index.md`, `log.md` — catalog and history

Fed by four agent sessions on `newman-vps`: `cfe-bill-parser`, `cfe-ppa-bess`,
`supabase-devops`, `tuesday-inputs`.

No secrets, no client PII, no real RPUs.
