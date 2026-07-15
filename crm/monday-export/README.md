# monday.com Export — newman-re.monday.com

**Export date:** 2026-07-15

monday.com has been **decommissioned**. This directory is the permanent archive of the full account. **newman-brain is now the CRM source of truth.**

Scope: every board with state `active` or `archived` and at least one item (plus their sub-item boards). Boards with state `deleted` were skipped. Each board file contains board metadata, columns (with settings), groups, and all items with full column values.

Also in this export:
- `automations/<board_id>.json` — automations for the main CRM boards (Deals, Leads, Contacts, Deals NPA, CRM Redesign)
- `updates.json` — recent updates/conversations from the main CRM boards (best effort)
- `SUMMARY.md` — human-readable summary of the business content

## Boards

| Board ID | Name | Workspace | State | Items | File |
|---|---|---|---|---|---|
| 9913323254 | Deals | Newman CRM | active | 169 | boards/9913323254_deals.json |
| 9913323670 | Subitems of Deals | Newman CRM | active | 683 | boards/9913323670_subitems-of-deals.json |
| 9913323235 | Contacts | Newman CRM | active | 15 | boards/9913323235_contacts.json |
| 18421500142 | CRM Redesign — Migration | Espacio de trabajo principal | active | 33 | boards/18421500142_crm-redesign-migration.json |
| 18403425692 | Gastos de proyectos | Newman CRM | active | 69 | boards/18403425692_gastos-de-proyectos.json |
| 18403588450 | Fijar presupuesto | Newman CRM | active | 5 | boards/18403588450_fijar-presupuesto.json |
| 18403229975 | Reporte Ops | Newman CRM | active | 26 | boards/18403229975_reporte-ops.json |
| 18402262283 | Deals NPA | Newman CRM | active | 6 | boards/18402262283_deals-npa.json |
| 18402262284 | Subitems of Deals NPA | Newman CRM | active | 62 | boards/18402262284_subitems-of-deals-npa.json |
| 18396093752 | NBM | Newman CRM | active | 20 | boards/18396093752_nbm.json |
| 18410879923 | MCP getting started | Newman CRM | active | 1 | boards/18410879923_mcp-getting-started.json |
| 18406603793 | MCP getting started | Newman CRM | active | 1 | boards/18406603793_mcp-getting-started.json |
| 18402261990 | Deals (archived) | Newman CRM | archived | 124 | boards/18402261990_deals-archived.json |
| 9913323267 | Accounts | Newman CRM | archived | 52 | boards/9913323267_accounts.json |
| 9913323238 | Activities | Newman CRM | archived | 4 | boards/9913323238_activities.json |
| 18402258888 | Deals | other | active | 5 | boards/18402258888_deals-other.json |
| 18402258887 | Accounts | other | active | 3 | boards/18402258887_accounts.json |
| 18402258886 | Contacts | other | active | 3 | boards/18402258886_contacts-other.json |
| 18402258885 | Activities | other | active | 3 | boards/18402258885_activities.json |
| 18402258884 | Leads | other | active | 2 | boards/18402258884_leads-other.json |
| 18402258883 | Client Projects | other | active | 2 | boards/18402258883_client-projects.json |
| 18402258882 | Quotes & Invoices | other | active | 1 | boards/18402258882_quotes-invoices.json |
| 18402258900 | Subitems of Deals | other | active | 3 | boards/18402258900_subitems-of-deals-other.json |
| 18402258903 | Subitems of Client Projects | other | active | 2 | boards/18402258903_subitems-of-client-projects.json |
| 18402258908 | Subitems of Quotes & Invoices | other | active | 1 | boards/18402258908_subitems-of-quotes-invoices.json |
| 8062624689 | Deals | Not workspace | active | 4 | boards/8062624689_deals-notws.json |
| 8062624686 | Accounts | Not workspace | active | 3 | boards/8062624686_accounts-notws.json |
| 8062624681 | Contacts | Not workspace | active | 3 | boards/8062624681_contacts-notws.json |
| 8062624692 | Activities | Not workspace | active | 2 | boards/8062624692_activities-notws.json |
| 8062624667 | Leads | Not workspace | active | 1 | boards/8062624667_leads-notws.json |
| 8062624693 | Client Projects | Not workspace | active | 3 | boards/8062624693_client-projects-notws.json |
| 8062624814 | Subitems of Deals | Not workspace | active | 3 | boards/8062624814_subitems-of-deals-notws.json |
| 8062624876 | Subitems of Client Projects | Not workspace | active | 2 | boards/8062624876_subitems-of-client-projects-notws.json |
| 9906644347 | Quotes & Invoices | Not workspace | active | 2 | boards/9906644347_quotes-invoices-notws.json |
| 951414636 | GASTOS JONATHAN_AHM | Tarjetas | archived | 1241 | boards/951414636_gastos-jonathan-ahm.json |
| 4752072879 | Duplicate of MIRAKL | Espacio de trabajo principal | archived | 44 | boards/4752072879_duplicate-of-mirakl.json |
| 4752072944 | Subitems of Duplicate of MIRAKL | Espacio de trabajo principal | archived | 23 | boards/4752072944_subitems-of-duplicate-of-mirakl.json |
| 4752072813 | Duplicate of SALES FORCE | Espacio de trabajo principal | archived | 13 | boards/4752072813_duplicate-of-sales-force.json |
| 3642340371 | Duplicate of Ventaneando con Chandel Chan | Bucket Energy | archived | 32 | boards/3642340371_duplicate-of-ventaneando-con-chandel-chan.json |
| 2734666183 | Proyectos Chedraui | Espacio de trabajo principal | archived | 120 | boards/2734666183_proyectos-chedraui.json |
| 2734680085 | Subelementos de Proyectos Chedraui | Espacio de trabajo principal | archived | 2 | boards/2734680085_subelementos-de-proyectos-chedraui.json |
| 2607504471 | Plantilla KickOff | Operaciones | archived | 1 | boards/2607504471_plantilla-kickoff.json |
| 1567818984 | Sales Pipeline | Espacio de trabajo principal | archived | 6 | boards/1567818984_sales-pipeline.json |
| 1567819370 | Subitems of Sales Pipeline | Espacio de trabajo principal | archived | 1 | boards/1567819370_subitems-of-sales-pipeline.json |
| 1567819214 | Lead Capturing | Espacio de trabajo principal | archived | 2 | boards/1567819214_lead-capturing.json |
| 1567819095 | Contacts | Espacio de trabajo principal | archived | 3 | boards/1567819095_contacts-archived.json |
| 1492686861 | Mind Map | Direccion | archived | 43 | boards/1492686861_mind-map.json |
| 1492688712 | Subelementos de Mind Map | Direccion | archived | 131 | boards/1492688712_subelementos-de-mind-map.json |
| 1452260149 | Tablero del proyecto | Mejora Continua | archived | 25 | boards/1452260149_tablero-del-proyecto.json |
| 1452260131 | Programa general | Mejora Continua | archived | 7 | boards/1452260131_programa-general.json |
| 1452260123 | Proceso de aprobación de proyectos | Mejora Continua | archived | 7 | boards/1452260123_proceso-de-aprobacion-de-proyectos.json |
| 1256760051 | Campaign Planning & Status | Comercial | archived | 7 | boards/1256760051_campaign-planning-status.json |
| 1256760096 | Subitems of Campaign Planning & Status | Comercial | archived | 12 | boards/1256760096_subitems-of-campaign-planning-status.json |
| 1256760047 | Digital asset management (DAM) | Comercial | archived | 6 | boards/1256760047_digital-asset-management-dam.json |
| 1256760043 | Content calendar | Comercial | archived | 6 | boards/1256760043_content-calendar.json |
| 1256760035 | Creative Planning with Adobe Creative Cloud | Comercial | archived | 5 | boards/1256760035_creative-planning-with-adobe-creative-cloud.json |
| 1256760068 | Subitems of Creative Planning with Adobe Creative Cloud | Comercial | archived | 2 | boards/1256760068_subitems-of-creative-planning-with-adobe-creative-cloud.json |
| 1256760031 | High Level Marketing Plan & Budget | Comercial | archived | 5 | boards/1256760031_high-level-marketing-plan-budget.json |
| 1256760064 | Subitems of High Level Marketing Plan & Budget | Comercial | archived | 7 | boards/1256760064_subitems-of-high-level-marketing-plan-budget.json |
| 1256760058 | Event RSVP Process | Comercial | archived | 4 | boards/1256760058_event-rsvp-process.json |
| 1256477451 | Proyectos | Comercial | archived | 6 | boards/1256477451_proyectos.json |
| 1256477491 | Subitems of Proyectos | Comercial | archived | 1 | boards/1256477491_subitems-of-proyectos.json |
| 1228554880 | Planificación de campaña de eventos | Proyección tipo de cambio | archived | 5 | boards/1228554880_planificacion-de-campana-de-eventos.json |
| 1228554893 | Subelementos de Planificación de campaña de eventos | Proyección tipo de cambio | archived | 2 | boards/1228554893_subelementos-de-planificacion-de-campana-de-eventos.json |
| 1228554872 | Proceso de RSVP | Proyección tipo de cambio | archived | 6 | boards/1228554872_proceso-de-rsvp.json |
| 1063440995 | Ventas corporativas | Comercial | archived | 5 | boards/1063440995_ventas-corporativas.json |
| 997824518 | Creative team planning | Marketing | archived | 5 | boards/997824518_creative-team-planning.json |
| 965138617 | Creative Planning - Plugin for Creative Cloud | Marketing | archived | 5 | boards/965138617_creative-planning-plugin-for-creative-cloud.json |
| 965138650 | Subitems of Creative Planning - Plugin for Creative Cloud | Marketing | archived | 2 | boards/965138650_subitems-of-creative-planning-plugin-for-creative-cloud.json |
| 953405671 | Subelementos de Minutas Reuniones | Espacio de trabajo principal | archived | 28 | boards/953405671_subelementos-de-minutas-reuniones.json |

**70 boards, 3138 items.**
