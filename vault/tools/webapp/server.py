# -*- coding: utf-8 -*-
"""Local webapp for the PV/BESS/Hibrido calculator — zero dependencies beyond the
engine's own (pdfplumber, openpyxl). Stdlib HTTP server; bills never leave the machine.

Run:   python tools/webapp/server.py        (opens http://127.0.0.1:8765)

Endpoints (JSON):
  GET  /                -> os.html (OS dashboard: stats, capacidades, actividad)
  GET  /cotizador       -> index.html (cotizador PV/BESS/PPA)
  GET  /portafolio      -> portfolio.html (vista portafolio: todos los RPU)
  GET  /chat            -> chat.html (chat con Claude sobre el vault via Claude Code CLI)
  POST /api/chat        {prompt, session_id?} -> claude -p (lee wiki, corre motor; NO modifica)
  GET  /api/portfolio   -> batch raw/bills/* via tools/portfolio.py (cache por mtime)
  GET  /api/os          -> vault stats (wiki/analyses/RPUs/log)
  POST /api/golden      -> runs tools/cfe_savings/test_golden.py, returns pass/fail
  POST /api/parse       {files:[{name, b64}]} -> bills + derived (RPU, CP->yield, division, sizing proposal)
  POST /api/run         {inputs, bills}       -> calc_core.compute (3 scenarios, regimen, finance)
  POST /api/ppa         {inputs, bills, target_irr, solve, term, esc_ppa} -> ppa_pricer.price
  POST /api/proposal    {inputs, bills, target_irr?} -> {markdown, filename} (propuesta es-MX)
  POST /api/run_flat    {inputs, bills, tarifa}      -> tarifa_flat.compute_flat (GDMTO/PDBT manual)

The math lives in tools/calc_core.py — the same module the Excel auto-fill uses.
"""
from __future__ import annotations
import base64, json, re, shutil, subprocess, sys, tempfile, webbrowser
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))
from cfe_savings import extract, sizing
import calc_core, solar_lookup, load_curves, ppa_pricer, tarifa_flat, make_proposal
import portfolio as portfolio_mod

HERE = Path(__file__).resolve().parent
ROOT = TOOLS.parent
PORT = 8765


def os_stats() -> dict:
    """Live vault stats for the OS dashboard (GET /api/os)."""
    wiki = ROOT / "wiki"
    by_dir = {}
    for d in ("billing", "optimization", "eligibility", "equipment", "entities",
              "concepts", "sources", "analyses"):
        pth = wiki / d
        by_dir[d] = (sum(1 for f in pth.glob("*.md") if not f.name.startswith("_"))
                     if pth.exists() else 0)
    rpus = []
    bills_root = ROOT / "raw" / "bills"
    if bills_root.exists():
        for d in sorted(bills_root.iterdir()):
            if d.is_dir():
                n = len(list(d.glob("*.pdf"))) + len(list(d.glob("*.xml")))
                if n:
                    rpus.append(dict(rpu=d.name, bills=n))
    log = []
    logf = wiki / "log.md"
    if logf.exists():
        for m in re.finditer(r"^## \[(\d{4}-\d{2}-\d{2})\] ([\w-]+) \| (.+)$",
                             logf.read_text(encoding="utf-8"), re.M):
            log.append(dict(date=m.group(1), type=m.group(2), title=m.group(3)))
    return dict(wiki_total=sum(by_dir.values()) + 2, wiki_by_dir=by_dir,
                analyses=by_dir.get("analyses", 0), sources=by_dir.get("sources", 0),
                rpus=rpus, log=list(reversed(log[-8:])))


_PF_CACHE = {"sig": None, "data": None}


def portfolio_cached() -> dict:
    """GET /api/portfolio — corre el batch sobre raw/bills/*; cachea por mtime
    (parsear ~24 PDFs/XMLs tarda segundos; los recibos casi nunca cambian)."""
    sig = []
    root = ROOT / "raw" / "bills"
    if root.exists():
        for f in sorted(root.rglob("*")):
            if f.suffix.lower() in (".pdf", ".xml", ".json"):
                sig.append((str(f), f.stat().st_mtime))
    ov = TOOLS / "portfolio_overrides.json"
    if ov.exists():
        sig.append((str(ov), ov.stat().st_mtime))
    sig = hash(tuple(sig))
    if _PF_CACHE["sig"] != sig:
        _PF_CACHE["data"] = portfolio_mod.run(root)
        _PF_CACHE["sig"] = sig
    return _PF_CACHE["data"]


def run_golden() -> dict:
    """Run the sacred golden test (POST /api/golden) and report pass/fail."""
    t = subprocess.run([sys.executable, str(TOOLS / "cfe_savings" / "test_golden.py")],
                       capture_output=True, text=True, timeout=300, cwd=str(ROOT))
    out = (t.stdout or "") + (t.stderr or "")
    m = re.search(r"(\d+)/(\d+) checks passed", out)
    passed = bool(m and m.group(1) == m.group(2))
    return dict(passed=passed,
                result=(("✓ " if passed else "✗ ") + m.group(0)) if m else "sin resultado",
                returncode=t.returncode)


# --------------------------------------------------------------------- chat
CHAT_SYS = (
    "Estas respondiendo dentro del webchat del CFE Brain OS (pagina /chat de la "
    "webapp local). Tu interlocutor pregunta sobre proyectos, normas, tarifas y "
    "reglas del sistema. Responde en espanol mexicano, compacto (esto es un chat, "
    "no un reporte). Fundamenta en el wiki del vault: lee wiki/index.md primero y "
    "cita paginas como [[demanda-facturable]]. Declara niveles de hecho "
    "(fuente-confirmado / motor / supuesto). Puedes correr herramientas python "
    "del vault (motor, portfolio, golden test) si la pregunta lo amerita, pero "
    "NO modifiques ni crees archivos desde este chat; si algo requiere escribir "
    "al vault, dilo y sugiere pedirlo en la sesion principal de Claude."
)
CHAT_TOOLS = "Read,Grep,Glob,Bash(python *),Bash(python3 *)"


def find_claude() -> list[str] | None:
    """Localiza el CLI de Claude Code; envuelve .cmd/.bat con cmd /c (Windows)."""
    exe = shutil.which("claude")
    if not exe:
        return None
    if exe.lower().endswith((".cmd", ".bat")):
        return ["cmd", "/c", exe]
    return [exe]


def run_chat(prompt: str, session_id: str | None) -> dict:
    base = find_claude()
    if not base:
        return dict(error="No encontre el CLI de Claude Code (comando `claude`). "
                          "Instalalo (https://claude.com/claude-code) y reinicia el OS.")
    cmd = base + ["-p", prompt, "--output-format", "json",
                  "--allowedTools", CHAT_TOOLS,
                  "--append-system-prompt", CHAT_SYS]
    if session_id:
        cmd += ["--resume", session_id]
    try:
        t = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=420, cwd=str(ROOT))
    except subprocess.TimeoutExpired:
        return dict(error="La consulta excedio 7 minutos y se cancelo. "
                          "Intenta una pregunta mas acotada.")
    out = (t.stdout or "").strip()
    try:
        d = json.loads(out[out.index("{"):]) if "{" in out else {}
    except ValueError:
        d = {}
    if d.get("type") == "result" and not d.get("is_error"):
        return dict(text=d.get("result", ""), session_id=d.get("session_id"),
                    turns=d.get("num_turns"), cost=d.get("total_cost_usd"))
    err = d.get("result") or (t.stderr or "").strip()[-600:] or "sin salida del CLI"
    return dict(error=f"El CLI devolvio un error: {err}")


def sniff_cp_pdf_text(text: str) -> str | None:
    m = re.search(r"C\.?P\.?\s*:?\s*(\d{5})", text or "")
    return m.group(1) if m else None


def parse_files(files: list[dict]) -> dict:
    bills, errors, cp = [], [], None
    for f in files:
        name = f.get("name", "archivo")
        try:
            raw = base64.b64decode(f["b64"])
            suffix = ".xml" if name.lower().endswith(".xml") else ".pdf"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tf:
                tf.write(raw)
                tmp = tf.name
            if suffix == ".xml":
                b = extract.parse_bill_xml(tmp)
            else:
                b = extract.parse_bill(tmp)
                if cp is None:
                    import pdfplumber
                    with pdfplumber.open(tmp) as pdf:
                        cp = sniff_cp_pdf_text(pdf.pages[0].extract_text())
            b["file"] = name
            bills.append(b)
        except Exception as e:
            errors.append(f"{name}: {e}")
    bills.sort(key=lambda b: (b["year"], b["month"]))
    if len(bills) > 12:
        bills = bills[-12:]
    cp = next((b.get("cp") for b in bills if b.get("cp")), None) or cp
    yld = solar_lookup.cp_to_yield(cp) if cp else None
    derived = dict(
        rpu=next((b.get("servicio") for b in bills if b.get("servicio")), ""),
        demanda_contratada=max((b.get("demanda_contratada") or 0 for b in bills), default=0),
        cp=cp,
        municipio=(f"{yld['municipio']}, {yld['estado']}" if yld else ""),
        division=(yld["division"] if yld else "SIN"),
        yield_monthly=(yld["monthly"] if yld else None),
        yield_anual=(yld["anual"] if yld else None),
        yield_match=(yld["match"] if yld else None),
        validacion=[dict(file=b["file"], year=b["year"], month=b["month"],
                         **calc_core.validate_bill(b)) for b in bills],
    )
    if bills:
        pv = sizing.propose_pv_kwp(bills, area_m2=None, packing=0.17)
        be = sizing.propose_bess(bills, derived["division"], autonomy_hours=None)
        derived["propuesta"] = dict(kwp=min(pv["proposed_kwp"], 699.0),
                                    bess_kw=be["proposed_power_kw"],
                                    bess_kwh=be["proposed_nominal_kwh"],
                                    nota=be["basis"])
    return dict(bills=bills, derived=derived, errors=errors)


class H(BaseHTTPRequestHandler):
    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _html(self, path):
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/os.html"):
            self._html(HERE / "os.html")
        elif self.path in ("/cotizador", "/index.html"):
            self._html(HERE / "index.html")
        elif self.path in ("/portafolio", "/portfolio.html"):
            self._html(HERE / "portfolio.html")
        elif self.path in ("/chat", "/chat.html"):
            self._html(HERE / "chat.html")
        elif self.path == "/api/portfolio":
            self._json(portfolio_cached())
        elif self.path == "/api/os":
            self._json(os_stats())
        elif self.path == "/api/defaults":
            self._json(dict(inputs=calc_core.DEFAULT_INPUTS, giros=calc_core.GIRO_PCT_AC))
        else:
            self.send_error(404)

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n).decode("utf-8")) if n else {}
            if self.path == "/api/parse":
                self._json(parse_files(data.get("files", [])))
            elif self.path == "/api/run":
                self._json(calc_core.compute(data.get("inputs", {}), data.get("bills", [])))
            elif self.path == "/api/curves":
                div = data.get("division") or "SIN"
                fit = load_curves.fit_bills(data.get("bills", []), div)
                self._json(dict(fit=fit, **load_curves.curve_payload(div)))
            elif self.path == "/api/ppa":
                self._json(ppa_pricer.price(
                    data.get("inputs", {}), data.get("bills", []),
                    target_irr=float(data.get("target_irr", 0.18)),
                    solve=data.get("solve", "ppa"),
                    escenario=data.get("escenario"),
                    ppa_yrs=data.get("term"), esc_ppa=data.get("esc_ppa"),
                    ppa=data.get("ppa"), comision=data.get("comision")))
            elif self.path == "/api/proposal":
                inputs, bills = data.get("inputs", {}), data.get("bills", [])
                res = calc_core.compute(inputs, bills)
                bad = [f"{b['year']}-{b['month']:02d}" for b in bills
                       if not calc_core.validate_bill(b)["ok"]]
                tirr = data.get("target_irr")
                ppa = (ppa_pricer.price(inputs, bills, target_irr=float(tirr),
                                        sensitivity=False) if tirr else None)
                md = make_proposal._render(res, ppa, "webapp", bad)
                rpu = inputs.get("rpu") or "sin-rpu"
                self._json(dict(markdown=md, filename=f"Propuesta - {rpu}.md"))
            elif self.path == "/api/golden":
                self._json(run_golden())
            elif self.path == "/api/chat":
                self._json(run_chat((data.get("prompt") or "").strip(),
                                    data.get("session_id") or None))
            elif self.path == "/api/run_flat":
                inputs = data.get("inputs", {})
                cp = data.get("cp")
                if cp and not inputs.get("yield_monthly"):
                    yld = solar_lookup.cp_to_yield(cp)
                    if yld:
                        inputs["yield_monthly"] = yld["monthly"]
                        inputs["municipio"] = f"{yld['municipio']}, {yld['estado']}"
                self._json(tarifa_flat.compute_flat(
                    inputs, data.get("bills", []),
                    tarifa=data.get("tarifa", "GDMTO")))
            else:
                self.send_error(404)
        except Exception as e:
            self._json(dict(error=str(e)), code=500)

    def log_message(self, fmt, *args):  # quiet
        pass


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    url = f"http://127.0.0.1:{PORT}"
    print(f"Calculadora corriendo en {url}  (Ctrl+C para salir)")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    srv.serve_forever()
