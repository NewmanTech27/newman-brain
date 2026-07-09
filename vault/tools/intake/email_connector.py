# -*- coding: utf-8 -*-
"""Email transport for the client-intake layer (IMAP fetch + approval-gated SMTP).

ON-DEMAND, not always-on. You run `fetch` to pull new client mail into
intake/<slug>/; you run `send` (with --confirm) only after approving the draft.

  fetch   IMAP UNSEEN -> intake/<slug>/{messages,attachments,thread.json}
  send    intake/<slug>/outbound_draft.md -> the client, via SMTP

DRAFT-FOR-APPROVAL is enforced in code: `send` is a DRY RUN unless you pass
--confirm. Nothing outward-facing leaves automatically.

Config: tools/intake/config.json (see config.example.json). Credentials live there
(use a Gmail App Password, not your account password) and the file is git-ignored.
Raw mail bytes never enter LLM context: this writes files locally and prints a
compact JSON summary.

Usage:
  python tools/intake/email_connector.py fetch
  python tools/intake/email_connector.py send <slug>            # dry run (prints)
  python tools/intake/email_connector.py send <slug> --confirm  # actually sends
"""
from __future__ import annotations
import argparse, email, imaplib, json, smtplib, sys, re
from email.header import decode_header, make_header
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from intake_schema import slugify

CONFIG = Path(__file__).resolve().parent / "config.json"
INTAKE = ROOT / "intake"


def _load_config() -> dict:
    if not CONFIG.exists():
        sys.exit(f"Missing {CONFIG}. Copy config.example.json -> config.json and fill it.")
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def _dh(s) -> str:
    try:
        return str(make_header(decode_header(s or "")))
    except Exception:                            # noqa: BLE001
        return s or ""


def _sender(msg) -> tuple[str, str]:
    raw = _dh(msg.get("From", ""))
    m = re.search(r"<([^>]+)>", raw)
    addr = (m.group(1) if m else raw).strip().lower()
    name = raw.split("<")[0].strip().strip('"') or addr.split("@")[0]
    return name, addr


def fetch(cfg: dict) -> dict:
    im = cfg["imap"]
    M = imaplib.IMAP4_SSL(im["host"], im.get("port", 993))
    M.login(im["user"], im["password"])
    M.select(cfg.get("mailbox", "INBOX"))
    crit = "(UNSEEN)"
    typ, data = M.search(None, crit)
    ids = data[0].split()
    allow = {a.lower() for a in cfg.get("allowed_senders", [])}
    seen = []
    for num in ids:
        typ, msg_data = M.fetch(num, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])
        name, addr = _sender(msg)
        if allow and addr not in allow:
            continue                              # leave unseen; not an authorized client
        slug = slugify(addr.split("@")[0] + "-" + addr.split("@")[-1].split(".")[0])
        cdir = INTAKE / slug
        (cdir / "messages").mkdir(parents=True, exist_ok=True)
        (cdir / "attachments").mkdir(parents=True, exist_ok=True)
        mid = _dh(msg.get("Message-ID", num.decode())).strip("<>").replace("/", "_")[:80] or num.decode()
        subject = _dh(msg.get("Subject", ""))
        body = _extract_body(msg)
        (cdir / "messages" / f"{mid}.txt").write_text(
            f"From: {name} <{addr}>\nSubject: {subject}\n\n{body}", encoding="utf-8")
        atts = _save_attachments(msg, cdir / "attachments")
        # thread log
        tf = cdir / "thread.json"
        thread = json.loads(tf.read_text(encoding="utf-8")) if tf.exists() else \
            {"slug": slug, "name": name, "email": addr, "channel": "email", "messages": []}
        thread["messages"].append({"id": mid, "dir": "in", "subject": subject,
                                   "attachments": atts})
        tf.write_text(json.dumps(thread, ensure_ascii=False, indent=2), encoding="utf-8")
        seen.append({"slug": slug, "from": addr, "subject": subject, "attachments": atts})
    M.logout()
    return {"fetched": len(seen), "clients": seen}


def _extract_body(msg) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and \
               "attachment" not in str(part.get("Content-Disposition", "")):
                try:
                    return part.get_payload(decode=True).decode(
                        part.get_content_charset() or "utf-8", "replace")
                except Exception:                # noqa: BLE001
                    continue
        return ""
    try:
        return msg.get_payload(decode=True).decode(
            msg.get_content_charset() or "utf-8", "replace")
    except Exception:                            # noqa: BLE001
        return msg.get_payload() or ""


def _save_attachments(msg, dest: Path) -> list[str]:
    saved = []
    for part in msg.walk():
        if "attachment" not in str(part.get("Content-Disposition", "")):
            continue
        fn = _dh(part.get_filename() or "")
        if not fn:
            continue
        fn = re.sub(r"[^\w.\- ]", "_", fn)
        data = part.get_payload(decode=True)
        if data:
            (dest / fn).write_bytes(data)
            saved.append(fn)
    return saved


def send(cfg: dict, slug: str, confirm: bool) -> dict:
    cdir = INTAKE / slug
    draft = cdir / "outbound_draft.md"
    if not draft.exists():
        sys.exit(f"No draft at {draft}. Run profile_builder first.")
    tf = cdir / "thread.json"
    if not tf.exists():
        sys.exit(f"No thread.json for {slug}; unknown recipient.")
    thread = json.loads(tf.read_text(encoding="utf-8"))
    to_addr = thread.get("email")
    text = draft.read_text(encoding="utf-8")
    # strip the internal header lines (everything up to the first 'Estimado' or blank body)
    body = re.sub(r"^#.*?\n(?:_.*?_\n)?", "", text, flags=re.S).strip()
    sm = cfg["smtp"]
    subject = cfg.get("reply_subject", "Información para su análisis de ahorro — CFE Brain")
    if not confirm:
        return {"dry_run": True, "to": to_addr, "subject": subject,
                "preview": body[:600],
                "note": "Add --confirm to actually send. Nothing was sent."}
    em = EmailMessage()
    em["From"] = f'{sm.get("from_name","CFE Brain")} <{sm["user"]}>'
    em["To"] = to_addr
    em["Subject"] = subject
    em.set_content(body)
    with smtplib.SMTP(sm["host"], sm.get("port", 587)) as s:
        s.starttls()
        s.login(sm["user"], sm["password"])
        s.send_message(em)
    thread.setdefault("messages", []).append({"dir": "out", "subject": subject})
    tf.write_text(json.dumps(thread, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"sent": True, "to": to_addr, "subject": subject}


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch")
    sp = sub.add_parser("send"); sp.add_argument("slug"); sp.add_argument("--confirm", action="store_true")
    a = ap.parse_args()
    cfg = _load_config()
    if a.cmd == "fetch":
        print(json.dumps(fetch(cfg), ensure_ascii=False, indent=2))
    elif a.cmd == "send":
        print(json.dumps(send(cfg, a.slug, a.confirm), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
