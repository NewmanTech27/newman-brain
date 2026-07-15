#!/usr/bin/env python3
import os, glob
from playwright.sync_api import sync_playwright

os.environ.setdefault('PLAYWRIGHT_BROWSERS_PATH', os.path.expanduser('~/.cache/ms-playwright'))
exe = glob.glob(os.path.expanduser('~/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell'))[0]
HTML = 'file://' + os.path.abspath('GEPP - Solucion Energetica Solar-Charge BESS.html')
OUT = 'shots'; os.makedirs(OUT, exist_ok=True)

def shoot(pg, sel, path):
    el = pg.query_selector(sel)
    el.scroll_into_view_if_needed(); pg.wait_for_timeout(350)
    el.screenshot(path=f'{OUT}/{path}')

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe, headless=True)
    pg = b.new_page(viewport={'width':1280,'height':1600}, device_scale_factor=2)
    pg.goto(HTML, wait_until='networkidle'); pg.wait_for_timeout(800)

    # ---- Despacho: ixt & can, invierno & verano (Op1 default) ----
    for site in ['ixt','can']:
        pg.click(f'#tabs-desp button[data-k="{site}"]'); pg.wait_for_timeout(300)
        for season in ['inv','ver']:
            pg.click(f'#season-desp button[data-s="{season}"]'); pg.wait_for_timeout(450)
            shoot(pg, '#despacho', f'cs-desp-{site}-{season}.png')

    # ---- Cobertura (Op1) ----
    shoot(pg, '#cobertura', 'cs-cobertura-op1.png')

    # ---- ¿Y con más superficie?: ixt & can ----
    for site in ['ixt','can']:
        pg.click(f'#tabs-supmas button[data-k="{site}"]'); pg.wait_for_timeout(450)
        shoot(pg, '#supmas', f'cs-supmas-{site}.png')

    # ---- Op2 cobertura (sanity) ----
    pg.query_selector_all('#opswitch button[data-op]')[1].click(); pg.wait_for_timeout(500)
    shoot(pg, '#cobertura', 'cs-cobertura-op2.png')

    b.close()
print('screenshots -> shots/cs-*.png')
