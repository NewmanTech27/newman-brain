# intake/ — client profiling workspace

One folder per client (slug derived from their email / contact). Created and
maintained by the client-intake layer (`tools/intake/`). Regenerable working area,
not a wiki source.

```
intake/<slug>/
├── messages/         inbound message bodies (.txt)
├── attachments/      client files (CFE bills PDF/XML, perfil .xlsx, …)
├── thread.json       contact + message log (channel, in/out)
├── answers.json      (optional) client answers you record as replies arrive
├── profile.json      THE handoff artifact — what's known/missing, ready_for
└── outbound_draft.md simple Spanish questions, for YOUR approval before sending
```

When `profile.json` shows `ready_for: ["cfe-savings-analyst"]`, the profile is
complete enough to run the savings engine. Hand the slug to that subagent.

See `tools/intake/README.md` for commands. Nothing here is sent to a client without
your explicit approval (`send --confirm`).
