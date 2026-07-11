# HelioScope design library — training examples

30 past HelioScope projects, exported 2026-07-09. Each `2026-<slug>/` folder holds `report.pdf` (HelioScope Production Report), `layout.png` (field-segment render), `single-line.dxf` + `layout-cad.zip` (CAD), `hourly-results.zip` (8760), `_raw_export.zip`, and `notes.md` (auto-drafted facts + a rationale section to distill). Spans 10 kW rooftop to 10 MW ground-mount across hotel, retail, university, casino, industrial, agricola, food, logistics, venue and a foreign cold-climate site.

| Size (DC) | Project | Type | DC:AC | Modules | Segs | Tilt | Racking | Keepouts |
|---|---|---|---|---|---|---|---|---|
| 10 kW | [Alfa Montes](2026-alfa-montes/) | micro-rooftop | 1.25 | 14 | 2 | 0/10° | flush/rack | 0 |
| 11 kW | [Casa Santiago](2026-casa-santiago/) | residential | 1.07 | 15 | 4 | 6/8/15° | flush | 3 |
| 17 kW | [Tiendas 3B-7664](2026-tiendas-3b-7664/) | retail-chain | 1.14 | 24 | 2 | 3° | flush | 0 |
| 39 kW | [O'Reilly Autopartes](2026-oreilly-autopartes/) | auto-retail | 1.29 | 54 | 3 | 4/10° | flush/rack | 0 |
| 49 kW | [Calimax Californias](2026-calimax-californias/) | grocery-retail | 1.22 | 68 | 1 | 3° | flush | 8 |
| 104 kW | [Up Fitness](2026-up-fitness/) | gym | 1.3 | 324 | 1 | 2° | flush | 0 |
| 123 kW | [Centro Joyero Guadalajara](2026-centro-joyero-guadalajara/) | commercial | 1.23 | 172 | 6 | 4° | flush | 0 |
| 182 kW | [Casino Solaz Delicias](2026-casino-solaz-delicias/) | casino | 1.3 | 254 | 11 | 3.4/10/3.9/3/4° | flush | 34 |
| 200 kW | [Universidad Anahuac Veracruz](2026-universidad-anahuac-veracruz/) | university | 1.25 | 280 | 11 | 4° | flush/rack | 0 |
| 204 kW | [Pinnacle Aerospace](2026-pinnacle-aerospace/) | aerospace | 1.27 | 285 | 3 | 3° | carport | 0 |
| 230 kW | [Smart Plastics de Mexico](2026-smart-plastics/) | plastics-industrial | 1.28 | 321 | 4 | 4/10° | flush/rack | 0 |
| 231 kW | [Hotel Yori Inn](2026-hotel-yori-inn/) | hotel | 1.28 | 323 | 8 | 5° | flush | 0 |
| 327 kW | [Tiendas 3B - Cedis](2026-tiendas-3b-cedis/) | distribution-center | 1.26 | 458 | 2 | 3° | flush | 0 |
| 328 kW | [Africam Safari](2026-africam-safari/) | tourism | 1.26 | 459 | 3 | 4° | carport | 0 |
| 430 kW | [Universidad Anahuac Queretaro](2026-universidad-anahuac-queretaro/) | university | 1.27 | 602 | 9 | 10° | rack | 0 |
| 481 kW | [EQUIALUM](2026-equialum/) | aluminum-industrial | 1.2 | 673 | 4 | 4° | flush | 0 |
| 488 kW | [Hotel Tesoro Manzanillo](2026-hotel-tesoro-manzanillo/) | hotel | 1.28 | 682 | 33 | 10/0° | flush | 0 |
| 549 kW | [Foro Sol](2026-foro-sol/) | venue | 1.25 | 768 | 8 | 10/0° | rack/flush | 0 |
| 583 kW | [Kotobukiya Treves de Mexico](2026-kotobukiya-treves/) | auto-parts | 1.22 | 816 | 6 | 3° | flush | 0 |
| 588 kW | [Conservas del Norte](2026-conservas-del-norte/) | food-processing | 1.23 | 823 | 7 | 3° | flush | 0 |
| 701 kW | [YAQUI](2026-yaqui/) | ground-mount | 1.21 | 980 | 3 | 4° | flush | 0 |
| 725 kW | [Productores Pecuarios Petatlan](2026-productores-pecuarios-petatlan/) | livestock-agri | 1.29 | 1014 | 12 | 4/10/0° | flush | 0 |
| 778 kW | [Frutos de Huerta Real](2026-frutos-de-huerta-real/) | agri | 1.14 | 1088 | 10 | 5/15/2° | flush/rack | 0 |
| 1.00 MW | [Alberta Calgary](2026-alberta-calgary/) | foreign-cold-climate | 1.25 | 1404 | 1 | 10° | rack | 0 |
| 1.14 MW | [Molex de Mexico](2026-molex-de-mexico/) | electronics-industrial | 1.29 | 1592 | 10 | 4/10° | flush/rack | 0 |
| 2.11 MW | [Kuehne & Nagel](2026-kuehne-nagel/) | logistics | 1.24 | 2948 | 1 | 4° | flush | 0 |
| 2.50 MW | [Leche 19 Hermanos](2026-leche-19-hermanos/) | dairy | 1.25 | 3494 | 10 | 3° | flush | 0 |
| 5.00 MW | [OCESA - Hipodromo](2026-ocesa-hipodromo/) | venue-mega | 1.22 | 7000 | 2 | 3° | flush | 0 |
| 7.00 MW | [Grupo Frisa](2026-grupo-frisa/) | ground-mount-mw | 1.23 | 9792 | 4 | 3° | flush | 0 |
| 10.00 MW | [TMEX Industrial Park](2026-tmex-industrial-park/) | industrial-park | 1.21 | 13992 | 11 | 10° | rack | 0 |

## Quick house-style signals (auto)
- **Module:** predominantly 715 W (from design names).
- **DC:AC ratio:** 1.07–1.30, mean 1.24.
- **Racking mix (segment-count):** flush×25, rack×10, carport×2.
- **Inverters:** Huawei SUN2000 family dominates (40/60/100 KTL); Growatt on small residential/retail.
- **Row spacing:** ~0.025 m (flush rooftop) vs 1.2–2.2 m (tilt racks / ground mount).
