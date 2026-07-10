"""Per-division CONSUMO -> period mapping regression (issue #18).

`parse_bill_xml` must map the CFDI addenda registers CONSUMO1F/2F/3F to
base/intermedia/punta by the CFE-addenda convention, NOT the pre-2026-07 fixed
`1F=base` order (which was inverted base<->punta for division DW and never
independently verified elsewhere).

Byte-verified convention (harvest PR #17 + issue #18): **1F=punta, 2F=inter,
3F=base**, reconciling to CONSUMO_R on real XML for two independent divisions.

This suite is self-contained: it synthesizes minimal CFDI XMLs from the
PDF-validated canonical splits for RPU 780881200029 (División DW / SIN
Peninsular) — the same table the harvest `test_recibo_parser.py` asserts — so no
real bill bytes (PII) are needed. It ports the canonical XML-ordering assertion
into the engine's own suite, as #18 requires.

Run: "$PY" tools/cfe_savings/test_consumo_period_mapping.py
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cfe_savings.extract import parse_bill_xml, consumo_order_verified  # noqa
from cfe_savings.extract import _consumo_order, _STD_CONSUMO_ORDER  # noqa

# Canonical PDF-validated splits (kwh_base, kwh_inter, kwh_punta) for RPU
# 780881200029, División DW. Source: wiki 2026-06-08-cfe-bills-780881200029, the
# same table harvest test_recibo_parser.py::_XML_CANON asserts.
_DW_CANON = {
    "WH-000552276133": ("2025-11-30", 268822.0, 440446.0, 104467.0),  # NOV 25
    "WH-000552737190": ("2026-01-31", 268796.0, 477099.0, 114681.0),  # ENE 26
    "WH-000552970339": ("2026-02-28", 222447.0, 382846.0,  91302.0),  # FEB 26
    "WH-000553203984": ("2026-03-31", 281755.0, 452258.0, 108970.0),  # MAR 26
}

_END_TO_FECHASTA = {  # 'YYYY-MM-DD' end -> CFE 'DD MMM YY' string
    "2025-11-30": "30 NOV 25", "2026-01-31": "31 ENE 26",
    "2026-02-28": "28 FEB 26", "2026-03-31": "31 MAR 26",
}


def _xml(division, f1, f2, f3, fechasta, consumo_r=None, extra=""):
    """A minimal CFE/iTComplements CFDI carrying just the fields parse_bill_xml
    reads. Namespaced like the real complemento so _xml_text_map flattens it."""
    cr = "" if consumo_r is None else f"<CONSUMO_R>{consumo_r}</CONSUMO_R>"
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/4"
  xmlns:it="http://itcomplement.com/cfe">
  <cfdi:Complemento>
    <it:clsRegArchFact>
      <it:RPU>780881200029</it:RPU>
      <it:TARIFA>GDMTH</it:TARIFA>
      <it:DIVISION>{division}</it:DIVISION>
      <it:FECDESDE>31 OCT 25</it:FECDESDE>
      <it:FECHASTA>{fechasta}</it:FECHASTA>
      <it:CONSUMO1F>{f1}</it:CONSUMO1F>
      <it:CONSUMO2F>{f2}</it:CONSUMO2F>
      <it:CONSUMO3F>{f3}</it:CONSUMO3F>
      {cr}
      <it:SubTotal>1000.00</it:SubTotal>
      {extra}
    </it:clsRegArchFact>
  </cfdi:Complemento>
</cfdi:Comprobante>"""


def _write(tmp, name, text):
    p = os.path.join(tmp, name + ".xml")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)
    return p


def main():
    checks = []

    with tempfile.TemporaryDirectory() as tmp:
        # 1) DW canonical: registers laid out in CFE order 1F=punta/2F=inter/3F=base
        #    must parse back to the PDF-validated base/inter/punta split.
        for stem, (end, base, inter, punta) in _DW_CANON.items():
            fechasta = _END_TO_FECHASTA[end]
            # XML raw order is (1F=punta, 2F=inter, 3F=base)
            path = _write(tmp, stem, _xml("DW", punta, inter, base, fechasta,
                                          consumo_r=base + inter + punta))
            d = parse_bill_xml(path)
            ok = (d["kwh_base"] == base and d["kwh_inter"] == inter
                  and d["kwh_punta"] == punta and d["end"] == end)
            checks.append((f"DW {stem} split {'base='+str(d['kwh_base'])}", ok,
                           None if ok else (d["kwh_base"], d["kwh_inter"], d["kwh_punta"])))

        # 2) Anti-inversion guard: assert we did NOT fall back to the OLD 1F=base
        #    order. Under the old code, NOV25 1F=104467 would land in kwh_base.
        nov = _write(tmp, "WH-000552276133",
                     _xml("DW", 104467, 440446, 268822, "30 NOV 25",
                          consumo_r=813735))
        d = parse_bill_xml(nov)
        checks.append(("NOV25 base != CONSUMO1F (not the inverted order)",
                       d["kwh_base"] == 268822.0 and d["kwh_base"] != 104467.0,
                       d["kwh_base"]))
        checks.append(("NOV25 punta == CONSUMO1F (104467)",
                       d["kwh_punta"] == 104467.0, d["kwh_punta"]))

        # 3) kwh_total preserved regardless of order.
        checks.append(("kwh_total == sum registers",
                       abs(d["kwh_total"] - 813735.0) < 0.5, d["kwh_total"]))

        # 4) Unknown division falls back to the CFE-standard order (1F=punta) and
        #    is flagged unverified. A reconciling split still parses fine.
        dx = _write(tmp, "DX-sample",
                    _xml("DX", 50000, 300000, 150000, "30 NOV 25",
                         consumo_r=500000))
        d = parse_bill_xml(dx)
        checks.append(("DX (unlisted) uses std order 1F=punta",
                       d["kwh_punta"] == 50000.0 and d["kwh_base"] == 150000.0,
                       (d["kwh_punta"], d["kwh_base"])))
        checks.append(("DX flagged NOT verified", not consumo_order_verified("DX"),
                       consumo_order_verified("DX")))
        checks.append(("DW flagged verified", consumo_order_verified("DW"),
                       consumo_order_verified("DW")))

        # 5) Reconciliation guard: a CONSUMO_R that the three registers do not sum
        #    to must RAISE (unknown addenda layout) rather than emit garbage.
        bad = _write(tmp, "bad-recon",
                     _xml("DZ", 10, 20, 30, "30 NOV 25", consumo_r=999999))
        try:
            parse_bill_xml(bad)
            checks.append(("recon mismatch raises", False, "no raise"))
        except ValueError as e:
            checks.append(("recon mismatch raises", "CONSUMO_R" in str(e), None))

    # 6) Table sanity: the standard order is punta/inter/base and DW resolves to it.
    checks.append(("std order == (punta,inter,base)",
                   _STD_CONSUMO_ORDER == ("kwh_punta", "kwh_inter", "kwh_base"),
                   _STD_CONSUMO_ORDER))
    checks.append(("_consumo_order('DW') == std", _consumo_order("DW") == _STD_CONSUMO_ORDER, None))
    checks.append(("_consumo_order(None) defaults std", _consumo_order(None) == _STD_CONSUMO_ORDER, None))

    npass = sum(1 for _, ok, _ in checks if ok)
    for name, ok, got in checks:
        tag = "PASS" if ok else "FAIL"
        extra = "" if ok else f"  got={got}"
        print(f"  [{tag}] {name}{extra}")
    print(f"\n{npass}/{len(checks)} checks passed")
    return 0 if npass == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
