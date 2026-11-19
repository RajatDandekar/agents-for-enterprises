"""A live mailbox for the Aegis demo: one label of one real mailbox, read-only, over IMAP. Standard library only.

    IMAP_HOST      imap.gmail.com
    IMAP_LABEL     the one label (IMAP folder) that is read, for example "Northbridge AP"
    IMAP_USER      the mailbox address
    IMAP_PASSWORD  an app password (never the account password); it is read from the environment and held nowhere else

What it does, and nothing more: opens the one label read-only, takes the newest few messages without marking them read
(BODY.PEEK), keeps the sender, subject, date and the plain text of each (HTML stripped, cut near 4,000 characters), and
`sync()` files them in a sandbox's AP inbox as LIVE-<uid>. From there the agent reads them with the ordinary
read_mailbox tool, so every guard treats them like any other e-mail from outside Northbridge. Nothing is written back
to the mailbox, no other label is opened, and the password never appears in a return value, a log line or an error.
"""
from __future__ import annotations

import email
import email.policy
import email.utils
import html
import imaplib
import os
import re
import threading
import time

LIMIT = 5                 # newest messages taken from the label
BODY_MAX = 4000           # characters of one body kept
TTL = 15.0                # seconds one fetch is reused

_lock = threading.Lock()
_cache = {"at": 0.0, "key": None, "rows": []}


class MailboxError(Exception):
    """A plain sentence about what went wrong. It never holds the password."""


def _env():
    return {"host": os.environ.get("IMAP_HOST", "").strip(), "label": os.environ.get("IMAP_LABEL", "").strip(),
            "user": os.environ.get("IMAP_USER", "").strip(), "password": os.environ.get("IMAP_PASSWORD", "")}


def configured() -> bool:
    e = _env()
    return bool(e["host"] and e["label"] and e["user"] and e["password"])


def mask(addr: str) -> str:
    """ra…@example.com: enough to recognise the mailbox on a projector, not enough to read it out."""
    if "@" not in addr:
        return (addr[:2] + "…") if addr else ""
    name, dom = addr.split("@", 1)
    return f"{name[:2]}…@{dom}"


def settings() -> dict:
    """What the page may show. Never the password."""
    e = _env()
    return {"available": configured(), "host": e["host"], "label": e["label"], "user": mask(e["user"])}


# ---------------------------------------------------------------- reading one message
_TAG = re.compile(r"<[^>]+>")
_DROP = re.compile(r"<(script|style|head)\b.*?</\1>", re.S | re.I)
_BREAK = re.compile(r"<\s*(br|/p|/div|/tr|/li|/h[1-6])\b[^>]*>", re.I)


def strip_html(s: str) -> str:
    s = _BREAK.sub("\n", _DROP.sub(" ", s))
    s = html.unescape(_TAG.sub("", s))
    return re.sub(r"\n{3,}", "\n\n", re.sub(r"[ \t\r\f\v]+", " ", s)).strip()


def body_of(msg) -> str:
    """The plain text of a message: text/plain when there is one, else the HTML part with its tags removed."""
    part = msg.get_body(preferencelist=("plain", "html"))
    if part is None:
        return ""
    try:
        text = part.get_content()
    except Exception:                                        # an unknown charset: decode by hand, never fail the fetch
        text = (part.get_payload(decode=True) or b"").decode("utf-8", "replace")
    if part.get_content_type() == "text/html":
        text = strip_html(text)
    text = text.replace("\r\n", "\n").strip()
    return text if len(text) <= BODY_MAX else text[:BODY_MAX].rstrip() + "\n[cut: the e-mail goes on]"


def parse(uid: str, raw: bytes, internal: str | None = None) -> dict:
    msg = email.message_from_bytes(raw, policy=email.policy.default)
    when = None
    try:
        when = email.utils.parsedate_to_datetime(str(msg["Date"])) if msg["Date"] else None
    except Exception:
        when = None
    stamp = when.strftime("%Y-%m-%d %H:%M") if when else (internal or "")
    _name, addr = email.utils.parseaddr(str(msg["From"] or ""))
    return {"uid": str(uid), "msg_id": f"LIVE-{uid}", "sender": addr or str(msg["From"] or "unknown"),
            "subject": " ".join(str(msg["Subject"] or "(no subject)").split())[:200], "received": stamp,
            "body": body_of(msg)}


def _quote(label: str) -> str:
    return '"' + label.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _internal(meta: bytes) -> str | None:
    m = re.search(rb'INTERNALDATE "([^"]+)"', meta or b"")
    if not m:
        return None
    try:
        return time.strftime("%Y-%m-%d %H:%M", imaplib.Internaldate2tuple(b'INTERNALDATE "' + m.group(1) + b'"'))
    except Exception:
        return None


def fetch(limit: int = LIMIT, fresh: bool = False, connect=None) -> list[dict]:
    """The newest `limit` messages of the one label, oldest first. Read-only; nothing is marked read.
    `connect` is for tests: a callable (host) -> an object with imaplib.IMAP4's methods."""
    e = _env()
    if not configured():
        raise MailboxError("The live mailbox is not set up on this server.")
    key = (e["host"], e["label"], e["user"], limit)
    with _lock:
        if not fresh and _cache["key"] == key and time.time() - _cache["at"] < TTL:
            return [dict(r) for r in _cache["rows"]]
        box = None
        try:
            box = (connect or (lambda h: imaplib.IMAP4_SSL(h, timeout=20)))(e["host"])
            try:
                box.login(e["user"], e["password"])
            except Exception:
                raise MailboxError("The mailbox refused the sign-in. Check the address and the app password in the "
                                   "Modal secret northbridge-mailbox.") from None
            typ, _ = box.select(_quote(e["label"]), readonly=True)
            if typ != "OK":
                raise MailboxError(f"The mailbox has no label called “{e['label']}”.")
            typ, data = box.uid("search", None, "ALL")
            if typ != "OK":
                raise MailboxError("The mailbox did not list the label's messages.")
            uids = (data[0] or b"").split()[-limit:]
            rows = []
            for u in uids:
                typ, got = box.uid("fetch", u, "(INTERNALDATE BODY.PEEK[])")
                if typ != "OK":
                    continue
                for item in got or []:
                    if isinstance(item, tuple) and len(item) == 2:
                        rows.append(parse(u.decode(), item[1], _internal(item[0])))
                        break
        except MailboxError:
            raise
        except Exception as ex:                              # network, protocol: say which kind, never the detail
            raise MailboxError(f"Could not read the mailbox ({type(ex).__name__}).") from None
        finally:
            if box is not None:
                for close in ("close", "logout"):
                    try:
                        getattr(box, close)()
                    except Exception:
                        pass
        _cache.update(at=time.time(), key=key, rows=[dict(r) for r in rows])
        return rows


def peek(limit: int = LIMIT) -> list[dict]:
    """For the instructor's eyes before the agent reads anything: who, what, when, and the first 200 characters."""
    return [{"msg_id": m["msg_id"], "sender": m["sender"], "subject": m["subject"], "received": m["received"],
             "preview": m["body"][:200]} for m in fetch(limit)]


def sync(erp, limit: int = LIMIT) -> dict:
    """File the label's newest messages in this sandbox's AP inbox as LIVE-<uid>, status NEW, and mark the sandbox's
    own mail DONE, so read_mailbox returns the live messages. Returns {"added": n, "live": n}."""
    rows = fetch(limit)
    added = 0
    with erp.lock:
        erp.x("UPDATE mail_msg SET status='DONE' WHERE msg_id NOT LIKE 'LIVE-%'")
        for m in rows:
            if erp.q1("SELECT 1 FROM mail_msg WHERE msg_id=?", m["msg_id"]):
                continue
            erp.x("INSERT INTO mail_msg VALUES (?,?,?,?,?,?,?,?,?)", m["msg_id"], "AP inbox", m["received"], m["sender"],
                  m["subject"], m["body"], "", "invoice", "NEW")
            added += 1
    return {"added": added, "live": len(rows)}


def briefing(n: int, label: str) -> str:
    """What "what's new" says for an agent on the live mailbox."""
    return (f"The AP inbox is connected to a live mailbox (label “{label}”).\n"
            f"- {n} e-mail{'s' if n != 1 else ''} in the AP inbox. Read them with read_mailbox.\n"
            "- Nothing waits for a signature.")
