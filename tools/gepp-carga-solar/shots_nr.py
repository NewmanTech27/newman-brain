#!/usr/bin/env python3
import os, glob
from playwright.sync_api import sync_playwright

os.environ.setdefault('PLAYWRIGHT_BROWSERS_PATH', os.path.expanduser('~/.cache/ms-playwright'))
exe = glob.glob(os.path.expanduser('~/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell'))[0]
HTML = 'file://' + os.path.abspath('GEPP - Solucion Energetica Solar-Charge BESS + Autoconsumo Max.html')
OUT = 'shots'; os.makedirs(OUT, exist_ok=True)

def shoot(pg, sel, path):
    el = pg.query_selector(sel)
    el.scroll_into_view_if_needed(); pg.wait_for_timeout(400)
    el.screenshot(path=f'{OUT}/{path}')

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe, headless=True)
    pg = b.new_page(viewport={'width':1280,'height':1600}, device_scale_factor=2)
    pg.goto(HTML, wait_until='networkidle'); pg.wait_for_timeout(800)

    # ---- Op1 regression baseline (default state) ----
    shoot(pg, '#resumen', 'nr-resumen-op1.png')
    shoot(pg, '#optimo',  'nr-optimo-ixt-op1.png')   # new section under Op1 (banner shown)

    # ---- select Opción 3 ----
    pg.click('#opswitch button[data-op="2"]'); pg.wait_for_timeout(600)

    shoot(pg, '#resumen',    'nr-resumen-op3.png')
    shoot(pg, '#cobertura',  'nr-cobertura-op3.png')
    shoot(pg, '#supmas',     'nr-supmas-op3.png')
    shoot(pg, '#superficie', 'nr-superficie-op3.png')

    # ---- new section "¿Por qué este tamaño?" Op3: Ixtlahuacán (interior peak), Acapulco, Proplasa (cap) ----
    shoot(pg, '#optimo', 'nr-optimo-ixt-op3.png')
    for site in ['aca','pro']:
        pg.click(f'#tabs-optimo button[data-k="{site}"]'); pg.wait_for_timeout(450)
        shoot(pg, '#optimo', f'nr-optimo-{site}-op3.png')

    # ---- Despacho Op3: Ixtlahuacán + Proplasa, invierno + verano ----
    for site in ['ixt','pro']:
        pg.click(f'#tabs-desp button[data-k="{site}"]'); pg.wait_for_timeout(350)
        for season in ['inv','ver']:
            pg.click(f'#season-desp button[data-s="{season}"]'); pg.wait_for_timeout(450)
            shoot(pg, '#despacho', f'nr-desp-{site}-{season}-op3.png')

    b.close()
print('screenshots -> shots/nr-*.png')
