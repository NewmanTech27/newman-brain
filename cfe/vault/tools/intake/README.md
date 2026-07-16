# Client-intake layer

Turns raw client contact (email today; WhatsApp later) into a **structured profile**
ready for the engine — by auto-deriving everything the bills can answer and asking the
client only the few simple things they can't.

Two parts, by design (see CLAUDE.md "create a subagent mechanism…" thread):

1. **Transport** (`email_connector.py`) — a *service* you run on demand. A Claude
   subagent cannot watch an inbox; this does the IMAP/SMTP.
2. **Profiling brain** (`profile_builder.py` + the `client-intake` subagent) —
   channel-agnostic. Analyzes the message + attachments, fills the profile against
   the canonical Intake question bank (`intake_schema.py` mirrors CLAUDE.md), and
   drafts simple Spanish questions for the gaps.

## Flow

```
client email ──▶ fetch ──▶ intake/<slug>/{messages,attachments,thread.json}
                              │
                  profile_builder / client-intake subagent
                              │
              ┌───────────────┴───────────────┐
        profile.json                     outbound_draft.md
   (handoff to cfe-savings-analyst)   (simple Qs → YOU approve → send)
```

## Commands

```powershell
$PY = "C:/Users/vidan/AppData/Local/Programs/Python/Python314/python.exe"

# 1. pull new client mail (on demand)
& $PY tools/intake/email_connector.py fetch

# 2. analyze a client folder -> profile.json + outbound_draft.md
& $PY tools/intake/profile_builder.py <slug>

# 3. review intake/<slug>/outbound_draft.md, edit if needed, then send
& $PY tools/intake/email_connector.py send <slug>            # DRY RUN (prints)
& $PY tools/intake/email_connector.py send <slug> --confirm  # actually sends

# 4. when the client replies, fetch again (or drop files into attachments/),
#    optionally record answers in intake/<slug>/answers.json, re-run step 2.
#    When profile.ready_for = ["cfe-savings-analyst"], hand off.
```

`answers.json` (optional, you fill as replies arrive):
```json
{ "roof_area_m2": 4000, "transformer_kva": 1000, "interval_15min": true, "growth_plans": "no" }
```

## Guarantees

- **Draft-for-approval:** `send` is a dry run unless `--confirm`. Nothing outward-facing
  leaves automatically.
- **On-demand:** no always-on watcher; you trigger `fetch`.
- **Token discipline:** raw bill/mail bytes never enter LLM context — attachments are
  summarized by `cfe_savings.extract`; only the summary lands in `profile.json`.
- **No guessing:** internal financial assumptions are defaulted and labeled, never asked
  to the client; only the simple physical questions go out.

## Setup (email)

1. `cp config.example.json config.json`, fill IMAP/SMTP with a **Gmail App Password**.
2. (Optional) put authorized client addresses in `allowed_senders` to ignore the rest.

## Manual / no-transport mode

Don't need live email yet? Drop the client's files into
`intake/<slug>/attachments/`, run `profile_builder.py <slug>`, and the brain works the
same — the transport is the only email-specific piece.

## WhatsApp (later)

Add a `whatsapp_connector.py` that writes the same `intake/<slug>/{messages,attachments,
thread.json}` shape and reads `outbound_draft.md`. The brain needs zero changes.
