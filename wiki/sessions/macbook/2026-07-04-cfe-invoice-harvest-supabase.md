# CFE portal invoice harvesting (Consulta/MiEspacio) and client schema on Supabase

**Summary**: Worked out the end-to-end CFE portal harvest — Consulta for the latest recibo, MiEspacio login with total-a-pagar, 2captcha solving, up to 12+ historical invoices — and structured every XML field into a Supabase client schema.
**Tags**: #newman #cfe #scraper #supabase #invoices
**Created**: 2026-07-04
**Source**: macbook session 4f17b479-98fe-45e4-8e9f-6fda07c6e7c9.jsonl, user jesus

---

## Content
- Created a client-data schema on Supabase starting from the RPU; read CFE invoices on Drive to enumerate extractable client fields; studied RPU vs RMU semantics.
- Harvest flow discovered: https://app.cfe.mx/Aplicaciones/CCFE/ReciboDeLuzGMX/Consulta gives the latest recibo (importe, no. de servicio, RPU); that "total a pagar" is the credential to register the service in MiEspacio (Login.aspx), where "Administrar recibos → Consulta tu recibo → Otras facturas" yields the last 12 invoices (XML+PDF).
- Ran via Playwright on the mac mini (Mexican residential IP clears the WAF); captchas solved with the 2captcha solver API.
- Hard limit learned: CFE permanently blocks accounts with more than 10 recibos registered — hence the pattern of removing each service from the NewmanEnergi account after extraction ("eliminar servicio").
- Email routing: notifications through tech@newman.re group → arrives at jesus@newman.re inbox.
- Test client: the KFC PDF; after harvest, every XML field parsed into the Supabase clients schema tables.
- Session tail shows the later FibraHotel batch loaded 57/59 invoices; queued improvements: UUID ledger, per-file CFDI validation, crash-safe eliminar.

## Related Notes
- [[2026-07-03-kfc-ppa-offer-workflow]]
- [[2026-07-08-supabase-pipeline-pgcron]]
- [[2026-07-07-whatsapp-intake-cutover]]
