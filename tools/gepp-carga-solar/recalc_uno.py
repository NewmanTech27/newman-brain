#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
recalc_uno.py — Force a FULL recalculation of the surgered rev4 books with
LibreOffice via the UNO bridge (soffice --convert-to kept the stale rev3 caches
even with fullCalcOnLoad=1: the profile had a leftover `safemode` marker and
--convert-to does not reliably honor OOXMLRecalcMode).

Run with SYSTEM python3 (python3-uno). Expects a soffice UNO listener on
socket port 2002 started with a FRESH profile. For each book: load hidden,
document.calculateAll(), storeToURL -> <name>_values.xlsx (Calc MS Excel 2007 XML).
The surgered books themselves are NOT rewritten (charts stay byte-identical;
they carry fullCalcOnLoad=1 for Excel).
"""
import os, sys, uno
from com.sun.star.beans import PropertyValue

HERE = os.path.dirname(os.path.abspath(__file__))
REV3DIR = os.path.join(os.path.dirname(HERE), 'gepp-deck')
# (src, dst) pairs: the two rev4 books -> *_values.xlsx, plus the two delivered rev3
# books -> _rev3_recalc/ (live-formula reference for verify_cs.py GATE 1 — the
# delivered rev3 caches for C52/C55 are stale vs their own formulas).
JOBS = [(os.path.join(HERE, n), os.path.join(HERE, n[:-5] + '_values.xlsx')) for n in
        ('GEPP - Solucion Energetica Solar-Charge BESS - 4 Sitios.xlsx',
         'GEPP - Solucion Energetica Solar-Charge BESS - Proplasa.xlsx')] + [
    (os.path.join(REV3DIR, 'GEPP - Propuesta PV+BESS 4 Sitios (2026-07) rev3 - Esc 4pct TIR 14.xlsx'),
     os.path.join(HERE, '_rev3_recalc', 'rev3_4S_recalc.xlsx')),
    (os.path.join(REV3DIR, 'GEPP - Propuesta Proplasa (3 sitios) (2026-07) rev3 - Esc 4pct TIR 14.xlsx'),
     os.path.join(HERE, '_rev3_recalc', 'rev3_PP_recalc.xlsx'))]


def pv(name, value):
    p = PropertyValue(); p.Name = name; p.Value = value
    return p


def main():
    localContext = uno.getComponentContext()
    resolver = localContext.ServiceManager.createInstanceWithContext(
        'com.sun.star.bridge.UnoUrlResolver', localContext)
    ctx = resolver.resolve(
        'uno:socket,host=127.0.0.1,port=2002;urp;StarOffice.ComponentContext')
    desktop = ctx.ServiceManager.createInstanceWithContext(
        'com.sun.star.frame.Desktop', ctx)

    for src, dst in JOBS:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        url_in = uno.systemPathToFileUrl(src)
        url_out = uno.systemPathToFileUrl(dst)
        doc = desktop.loadComponentFromURL(url_in, '_blank', 0,
                                           (pv('Hidden', True), pv('ReadOnly', True)))
        assert doc is not None, f'failed to load {src}'
        doc.calculateAll()
        doc.storeToURL(url_out, (pv('FilterName', 'Calc MS Excel 2007 XML'),
                                 pv('Overwrite', True)))
        doc.close(False)
        print('recalced ->', os.path.basename(dst))
    print('OK')


if __name__ == '__main__':
    main()
