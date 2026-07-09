# Newman KPIs — board scorecard

Jesus is the board. The CEO reports. The CTO verifies. Agents do not score themselves into the record.

## The rule that governs every KPI here

**Every KPI must be computable from an artifact, by a command, without asking an agent.**

On 2026-07-09 `supabase-devops` reported filing three wiki pages, appended a row to `log.md` naming them, and the pages did not exist. Any metric derived from an agent's own account of its work is unverifiable. A KPI an agent can satisfy by *claiming* to satisfy it manufactures false confidence, which is worse than having no KPI.

If a proposed KPI has no `ls`, `git log`, `grep`, `pytest`, or SQL query behind it, it is not a KPI. It is a hope. Do not put it on the scorecard.

---

## Tier 1 — Integrity (gates everything)

These are not performance metrics. They are trust metrics. A failure here invalidates every number below it.

| KPI | Definition | Measured by | Target |
|---|---|---|---|
| `INT-1` Claim–artifact match | Of all artifacts an agent reports creating, the share that exist on disk | `ls` every claimed path from the agent's report | **100%.** Anything below is a P0. |
| `INT-2` Log truthfulness | Rows in `vault/log.md` whose named pages exist | script over `log.md` vs `wiki/` | **100%** |
| `INT-3` Evidence density | Normative requirements (`NRM-xx`) carrying a verification method | grep the specs | **100%** |
| `INT-4` Part B independence | Normative requirements sourced from outside the implementation | CTO review, written verdict | **100%** |

`INT-4` is the one that decides whether the whole exercise was theatre. A Part B paraphrased from Part A yields a spec the code satisfies by construction.

## Tier 2 — Delivery (the four outcomes)

| KPI | Definition | Measured by | Target |
|---|---|---|---|
| `DEL-1` Spec coverage | Services with a Part A/B/C spec merged | `ls docs/specs/*.md` on canonical branch | 5/5 |
| `DEL-2` CTO score | Independent re-score against Part B | CTO written verdict | **≥95/100** to merge |
| `DEL-3` Golden test | RPU `780881200029` peso-exact: `$30,157,371` baseline, `$7,083,252` / 23.5% Ahorro, 18 checks | run the test | pass, always |
| `DEL-4` Git↔prod fidelity | Migrations in git that exist in the prod ledger | Supabase ledger vs `supabase/migrations` | **75/75.** Today: **5/75.** |
| `DEL-5` Price floor holds | Attempts to construct a losing deal through the calculator UI | CTO adversarial test | 0 succeed |
| `DEL-6` Auth gate | Requests to `ceo.` / `extraction.newman.re` from outside `newman.re` | server-side `hd` claim check + test | 0 admitted |

`DEL-4` at **5/75** is the single worst number in this company. It means production was built by hand and git cannot rebuild it. Every environment/CI ambition depends on fixing it.

## Tier 3 — Economics

| KPI | Definition | Measured by | Target |
|---|---|---|---|
| `ECO-1` Cache hit rate | `cache_read / (cache_read + cache_creation)` | `token_audit.py` over `~/.claude/projects/` | establish baseline, then improve |
| `ECO-2` Input:output ratio | input tokens per output token | same | baseline is **33,560 : 5** on one sampled turn |
| `ECO-3` Tokens per merged point | total tokens ÷ CTO score points earned | audit + CTO verdicts | falling |
| `ECO-4` Rework rate | CTO rejections ÷ submissions | CTO log | falling |

`ai-research` owns these and may not recommend a change it has not measured.

## Tier 4 — Product (once Tier 1–2 clear)

Deliberately unset. Revenue, pipeline conversion, deal cycle time, and extraction coverage per RPU matter — but a KPI on a pipeline that cannot be rebuilt from git measures noise. These get defined at GATE 4, not before.

---

## Scoring cadence

- **Continuous**: CEO sweeps panes, surfaces material change.
- **Per gate**: CTO issues a written verdict. Below 95 returns with named gaps.
- **Board report**: CEO to Jesus, on change. Every number cited with the command that produced it.

**A score is a claim. Claims need evidence. A criterion with no evidence scores low, not high.**
Expect first-pass scores in the 20s–50s. `supabase-devops` self-scored **28/100** and that is a *good* first result — an honest 28 is worth more than a fictional 96.

---

## Hiring on demand

Agents are cheap; a confused org is not. The bar for a new hire:

1. **A named, verifiable deliverable** the existing seven cannot produce without dropping their own.
2. **An owner for its output.** Who reads it? Who acts on it? If nobody, don't hire.
3. **No shared-tree collision.** Give it a git worktree, or a read-only remit.
4. **It must not be able to merge.** Only `supabase-devops` merges, only on CTO sign-off.

Standing seats: CEO, CTO, `ai-research`, and four builders.

**Do not hire a CFO, CMO, or "conference agent" for its title.** A C-suite of agents with nothing verifiable to produce is cosplay, and it costs tokens and attention. Hire when a specific deliverable is blocked, and say what the deliverable is.

Candidate hires, with the trigger that would justify each:

| Seat | Hire when | Deliverable |
|---|---|---|
| `security` | before `ceo.`/`extraction.newman.re` ship | adversarial test of the `hd` domain gate; a written attempt to breach it |
| `market-intel` | after GATE 3 | CENACE/CRE/CNE regulatory diff vs the vault's invariants; every claim cited to a primary source |
| `sre` | after GATE 4 | the reboot the VPS still needs; the 155MB of vault PDFs and `entregables/` that exist on one disk |
| `cfo` | after Tier 4 KPIs exist | unit economics per deal; token cost per closed PPA |

**Conferences and energy mappings**: these are `market-intel` work, and they are downstream of GATE 3. A regulatory finding that contradicts a vault invariant (e.g. the `0.7 MW` LSE ceiling, `CNE` not `CRE`) is worth more than any conference note. Until git can rebuild prod, market intel has nowhere trustworthy to land.
