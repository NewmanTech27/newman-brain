# CFE Invoice Collection — Architecture & Hard-Won Gotchas

How a dropped bill becomes a client's full CFE invoice history in the warehouse.
Supabase orchestrates; the Mac mini (residential MX IP) does the browser work.

## Flow

```
WhatsApp media ─▶ edge fn `whatsapp-intake`
                    ├─ image  ─▶ OCR (OpenRouter/Gemini) ─▶ request_collection
                    └─ PDF    ─▶ store + enqueue_bulk_pdf   (no edge OCR: 168pg/16MB kills it)
                                     │
pg_cron `enqueue-undercollected` (*/5, ≤12-mo RPUs) ─┐
                                                      ▼
                                       client.collection_request  ◀─ mini splits bulk_pdf
                                                      │  (pdftotext: one PDF → N bills)
                        mini launchd 5-min one-shot ──┤  (main.py --once: claim → drain → exit)
                                                      ▼
                              harvest.js (Consulta → MiEspacio → fallback)
                                                      ▼
                              enrich.py  (parse → reconcile → upsert_bill)
                                                      ▼
                                          client.bill (warehouse)
```

- **Supabase can't SSH / run Chrome / hold a residential IP.** It enqueues; the
  mini drains. The queue is the bus. pg_cron = brain, mini = hands.
- **Mini worker is a 5-min launchd one-shot** (not a loop): claim → drain → exit.
  Self-heals via `claim_collection_requests` reclaiming stale `processing` (>30 min).

## The three MiEspacio inputs — all in the CFDI

`AgregarServicio` needs exactly: **No. de Servicio (RPU)**, **Nombre del servicio**,
**Total a pagar del último período**. All extractable from the latest CFDI:

| Input | CFDI source | Note |
|---|---|---|
| RPU | `<RPU>` / `RPU="…"` | 12 digits |
| Nombre | `<NOMBRE>` **raw, as-is** | e.g. `GRUPO YAZAKI S.A. DE C.V.` |
| Total a pagar | main `Comprobante Total` | NOT the fiscal sub-total; `totalFromXmlString` picks the right one (the file has two `Total="…"`) |

## Gotchas (each cost real debugging)

1. **Name = raw `<NOMBRE>`, NOT normalized.** AgregarServicio matches the CFDI
   `<NOMBRE>` character-exact (periods intact). Stripping/spacing the dots
   *breaks* the match. `registerService` tries candidates best-first: raw
   `<NOMBRE>`, then `canonName` variants, then the Receptor razón social.
   Consulta is the fiscal-name gotcha's other half — it matches the recibo's
   printed "Nombre del servicio", which differs from `receptor_nombre`
   (`FIDEICOMISO F 1596` vs `F/1596`).

2. **`ASSIGNED_ELSEWHERE` is the real depth blocker.** *"El número de servicio
   está asignado a otra cuenta, no es posible volver a agregarlo."* — the service
   is on the **client's own MiEspacio account**; CFE won't let us add it to the
   collection account. No name/total/captcha/hidden-API fixes this. `626`-type
   RPUs work only because they're *not* on another account.
   → **Fallback: full Consulta drain.** When MiEspacio is blocked, drain ALL of
   Consulta's ~6-8 recibos (`consultaLatestTotal(false)`) instead of just the
   latest. Recovers ~8 months automatically. Full history for client-owned
   services needs the client's MiEspacio credentials.

3. **`classifyAgregarText` must not default to a false OK.** It distinguishes
   `NAME_MISMATCH` / `TOTAL_MISMATCH` / `ASSIGNED_ELSEWHERE` / `ALREADY` /
   `RPU_BAD`; an unknown page is NOT success. `agregar` logs the url + message.

4. **A leftover registered service wedges everything.** Once any service exists,
   Default.aspx hides the add-form (`txtRpu`) behind a dropdown → registration
   crashes. `cleanAllServices` deletes all services before each registration.

5. **Consulta grid is an async AutoPostBack** — `waitForSelector` the grid
   button, never a fixed sleep (raced → silent empty drains).

6. **`fetchDrain` is the pseudo-API** — replay each recibo download as an
   in-page `fetch()` POST (chunked/parallel), carrying the Imperva + session
   cookies. Both Consulta uns page and MiEspacio OtrasFacturas.

7. **Multi-bill PDFs** — `pdf_intake.parse_pdf_bills`: `pdftotext -layout` →
   every `NO. DE SERVICIO:<12d>` + the account name off the `TOTAL A PAGAR:`
   line, deduped by RPU. No OCR (text layer). Scanned (no text layer) → `[]` →
   OCR fallback. One statement → N `collection_request`s.

8. **ETL is per-file isolated + retried.** One malformed XML / RPC blip never
   aborts the batch. CFDIs de **Pago** (`TipoDeComprobante="P"`) are not bills —
   counted separately, not failures.

## Ops

- **Mini**: host `mini`, launchd `com.newman.collector` → `scripts/run-collector-mini.sh`
  (nix-darwin node at `/run/current-system/sw/bin`). `~/newman-architecture` is a
  plain dir synced by CI, not a git checkout.
- **Deploy**: `deploy-mini.yml` (self-hosted runner) syncs + reloads launchd;
  `deploy.yml` SSHes the droplet. Both gate on green CI.
- **Debug flags**: `CFE_DEBUG_GRID=1` (OtrasFacturas grid diag), `CFE_DEBUG_AGREGAR=1`
  (full agregar page), `CFE_HEADFUL=1` (visible browser).
- **Edge secrets**: Deno.env (OPENROUTER_API_KEY / TWILIO_* / WEBHOOK_URL).
