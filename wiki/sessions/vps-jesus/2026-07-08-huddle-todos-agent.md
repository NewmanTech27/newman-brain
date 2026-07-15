# Daily-Huddle Agent: Drive Transcripts → Tuesday Kanban + ToDos Tab

**Summary**: Built an OpenRouter-powered Supabase edge-function agent that reads Newman daily-huddle minutes from Google Drive and updates Tuesday CRM deal cards, plus a new ToDos board (Pipeline/In progress/Done/Blocker) with an editable detail drawer.
**Tags**: #newman #tuesday-crm #openrouter #edge-functions #google-drive
**Created**: 2026-07-08
**Source**: newman-vps session 9f789a9e-7a2a-4fe9-ada9-36dd8907d86c.jsonl, user jesus

---

## Content
- Agent: OpenRouter via Supabase edge functions + gws auth reads huddle minutes/transcripts on Drive, comments on or creates kanban cards on tuesday.newman.re, and creates ToDos assigned to Google Workspace users, blocked/unblocked from the minutes.
- Google auth pain: GOOGLE_CLIENT_ID/SECRET/REFRESH_TOKEN hunt; `redirect_uri_mismatch` (Error 400) on the OAuth consent; org policy `iam.disableServiceAccountKeyCreation` blocks service-account keys — refresh-token flow used instead.
- ToDos tab: renamed navbar to "ToDos"; detail drawer added (title, detail, status, owner from Workspace users, due-date chip, blocker reason, delete), matching the existing DealDrawer; links to matched deal card and source huddle doc.
- Server actions `crm_web_update_todo` / `crm_web_delete_todo`, @newman.re-guarded; kept in separate `app/todo-actions.ts` to avoid touching in-progress finance work in `actions.ts`.
- Shipped on `dev` commit `f649230`, migration `20260708190000_crm_web_todo_edit.sql`; deploy verified live.

## Related Notes
- [[2026-07-08-tuesday-crm-committee-loop]]
- [[gws-cli-project]]
