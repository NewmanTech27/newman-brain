# Newman Charter — the goal, the gates, the order

Jesus is the board. The CEO session (on Jesus's MacBook) sets direction and re-tasks.
The CTO session holds a **merge veto**. Agents build. Nothing reaches `main` without CTO sign-off.

---

## The four outcomes

1. **The CRM at `tuesday.newman.re` is state of the art**, and the pipeline syncs with **WhatsApp and email**.
   ("Text" means WhatsApp text. There is no SMS channel. Two channels, not three.)

2. **RPU invoice extraction works end to end**, and is visible on a dashboard at **`extraction.newman.re`**.
   Owned by `cfe-bill-parser` — backend, dashboard, DNS, deploy.

3. **The pipeline presents a client their deal offer**, and salesmen get a **dynamic calculator**.
   The calculator is a UI over engines that **already exist and are golden-tested**
   (`vault/tools/ppa_pricer.py`, `optimize_sizing.py`, `calc_core.py`, `make_project_book.py`).
   **Do not rebuild the math.** Wrap it.

   **Hard floor, engine-enforced.** `ppa_pricer` solves price for a target financier IRR.
   A rep may move price only inside a band that holds minimum IRR and DSCR.
   Below the floor the UI **refuses**. A rep must not be able to sign a losing deal.
   The golden test (RPU `780881200029`, peso-exact) stays sacred throughout.

4. **One clean `main`.** Only then: `dev` / `staging` / `prod` in GitHub and Supabase, with CI/CD via Actions.
   Supabase environments use **native branching** (Pro plan; branches bill while alive).

---

## The order is not negotiable

Outcome 4 **gates** the CI/CD half of everything else, and `main` is not currently mergeable.

```
GATE 0  Branch audit          -> supabase-devops. NO MERGES until this lands.
GATE 1  Specs + scores        -> every agent: Part A/B/C spec, honest score vs Part B
GATE 2  CTO review            -> independent re-score. Below 95/100 = no merge.
GATE 3  Clean main            -> reconciliation executed, main canonical
GATE 4  Envs + CI/CD          -> dev/staging/prod, GitHub Actions, Supabase branching
GATE 5  The four outcomes     -> build, each behind CTO review
```

### GATE 0 — the branch audit blocks everything
`origin/dev` is **102 commits ahead** of `origin/main`. `origin/main` is **55 commits ahead** of `origin/dev`.
Diverged in **both** directions. This is a fork, not drift. **Neither branch is declared truth.**

`supabase-devops` produces a written reconciliation report BEFORE any merge:
- what is on each side, and what is actually deployed
- what is dead code vs live
- `docs/cfe-collection.md` exists on `origin/main` **only** — what else is stranded like that?
- a recommendation, with evidence, on which branch becomes canonical

Jesus decides from that report. Nobody merges to `main` before he does.
The droplet's local refs are **stale**. `git fetch` before trusting any comparison.

---

## The improve loop

Continuous. The CEO watches the panes and surfaces anything material as it happens:
a finding, a blocked merge, a score below bar, a contradiction between agents.

1. Agent works its phase (assess -> spec -> score -> plan -> work).
2. Agent files everything worth preserving into `~/cfe-brain/vault/wiki/`.
3. CTO independently re-scores against **Part B only**. Never against Part A.
4. Below 95/100: CTO returns it with named gaps. The agent re-plans. Loop.
5. At 95+: CTO signs off. `supabase-devops` merges.
6. CEO reports to Jesus on change, and re-tasks.

**A score is a claim, and claims need evidence.** A criterion with no evidence scores low, not high.
An agent that scores itself 96 on its first pass has failed the exercise, not passed it.

---

## Standing constraints

- The vault (`~/cfe-brain/vault/CLAUDE.md`) is **authoritative** on CFE domain facts. Its invariants are normative. Cite them; do not re-derive them.
- Never force-push. Never rewrite a shared branch. Branch off `dev`, open a PR.
- The golden test is sacred: RPU `780881200029`, baseline `$30,157,371`, Ahorro `$7,083,252` / 23.5%, 18 checks.
- Uncommitted: `deploy/curvas/current/index.html`. Do not discard it.
- A GitHub PAT lives in `~/.config/gh/hosts.yml`. Never print, echo, or commit it.
- The VPS needs a restart and has 4 pending ESM security updates. **Do not reboot** — it kills every session. Escalate to Jesus.
- `/home/mario/CFE Brain` holds 155MB of PDFs and `entregables/` (client deliverables) that are **version-controlled nowhere**. One disk failure from gone. Flag; do not commit without asking.
- Secrets, client PII, and real RPUs never enter the wiki or any repo.

---

## Outcome 5 — `ceo.newman.re`

A reporting page where the CEO surfaces the state of all work: each agent's phase, current score, open findings, blocked merges, and what needs Jesus's decision.

**Access control is the requirement, not the page.** Google auth, restricted to the `newman.re` domain. The `hd` claim is verified **server-side**. A client-side check is not a control.

The same gate protects `extraction.newman.re`. `tuesday-inputs` builds it once, as a reusable shell (`~/newman-sso` exists on the box — investigate before building). The others mount behind it.

These pages expose client RPUs, invoices, deal pricing, and margins. An unauthenticated deploy is a P0, not a follow-up ticket.

Owner: `tuesday-inputs` builds the auth shell and the CEO page. Content is fed by the CEO session.
