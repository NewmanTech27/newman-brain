# Print per-bill FP / bonificacion summary for 780881200029 via the engine extractor.
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\vidan\Desktop\CFE Brain\tools")
from pathlib import Path
from cfe_savings import extract

MEM_KEYS = ("cargo_fijo", "distribucion", "transmision", "cenace",
            "gen_b", "gen_i", "gen_p", "capacidad", "scnmem")
tot_mem = tot_bonif = tot_fact = 0.0
for pdf in sorted(Path(r"C:\Users\vidan\Desktop\CFE Brain\raw\bills\780881200029").glob("*.pdf")):
    b = extract.parse_bill(str(pdf))
    mem = sum(v for k, v in b.items() if k in MEM_KEYS and isinstance(v, (int, float)))
    bonif = b.get("bonif_fp", 0.0) or 0.0
    fact = b.get("facturacion", 0.0) or 0.0
    chk = (mem + bonif) * 1.16
    print(f"{pdf.stem[-5:]:>6}: FP={b.get('fp')}  MEM={mem:,.2f}  bonif_fp={bonif:,.2f}  "
          f"(MEM+bonif)*1.16={chk:,.2f}  printed={fact:,.2f}  diff={chk-fact:,.2f}")
    tot_mem += mem; tot_bonif += bonif; tot_fact += fact
print(f"\nTOTAL: MEM={tot_mem:,.2f}  bonif_fp={tot_bonif:,.2f}  printed(c/IVA)={tot_fact:,.2f}")
print(f"MEM anual (Excel/engine 'Bill ANTES'): {tot_mem:,.2f}")
print(f"Real anual sin IVA (MEM+bonif):        {tot_mem+tot_bonif:,.2f}")
print(f"Bonif as % of MEM: {tot_bonif/tot_mem:+.3%}")
