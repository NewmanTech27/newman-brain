# Launch newman-ceo session: bug-fixing + single-main-branch consolidation

**Summary**: Started the newman-ceo agent session to fix bugs across projects and consolidate every repo onto a single main branch, ahead of a flawless morning extraction run; also pulled a droplet backup off-box.
**Tags**: #newman #agents
**Created**: 2026-07-10
**Source**: macbook session 00b31b13-4c92-4211-9113-4aff7c88fe0a.jsonl, user jesus

---

## Content
- Goal: launch the CEO agent, let it work on improving all bugs and creating one single main branch across all projects; user wanted the extraction to run flawlessly by morning.
- Ran via `/loop`.
- Backup hygiene: pulled a backup off the droplet ("a backup that only lives on the box it protects isn't a backup"); fixed a zsh glob expansion issue by quoting the remote path; `git bundle verify` had to run inside a repo (used a scratch one).

## Related Notes
- [[2026-07-14-newman-rebuild-miespacio-phases]]
