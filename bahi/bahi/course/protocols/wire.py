"""Serve an ASGI app on a local port in a background thread, and record every HTTP exchange.

    from bahi.course.protocols.wire import Recorder, serve
    rec = Recorder()
    url = serve(rec.wrap(app), port=8931)        # http://127.0.0.1:8931
    ...                                          # any client talks to it
    rec.log                                      # [{method, path, status, req, resp, ms, headers}, ...]

Bodies that are JSON are parsed; server-sent-event bodies are split into their `data:` JSON payloads.
Authorization headers are recorded as "Bearer <redacted>" so a log never holds a token.
"""
from __future__ import annotations

import json
import socket
import threading
import time

KEEP_HEADERS = ("content-type", "accept", "mcp-session-id", "mcp-protocol-version", "mcp-method", "mcp-name",
                "www-authenticate", "location", "a2a-version", "x-a2a-extensions")


def _parse(body: bytes, ctype: str):
    if not body:
        return None
    text = body.decode("utf-8", "replace")
    if "text/event-stream" in ctype:
        events = []
        for line in text.splitlines():
            if line.startswith("data:"):
                d = line[5:].strip()
                try:
                    events.append(json.loads(d))
                except json.JSONDecodeError:
                    if d:
                        events.append(d)
        return {"sse": events}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text[:4000]


class Recorder:
    """An ASGI middleware that keeps a list of every request and response that went through it."""

    def __init__(self):
        self.log: list[dict] = []
        self.t0 = time.perf_counter()
        self._lock = threading.Lock()

    def wrap(self, app, tag: str = ""):
        rec = self

        async def mw(scope, receive, send):
            if scope["type"] != "http":
                return await app(scope, receive, send)
            t = time.perf_counter()
            req_body, resp_body, status, resp_headers = bytearray(), bytearray(), [0], {}
            req_headers = {k.decode().lower(): v.decode() for k, v in scope.get("headers", [])}

            async def recv():
                m = await receive()
                if m["type"] == "http.request":
                    req_body.extend(m.get("body", b""))
                return m

            async def snd(m):
                if m["type"] == "http.response.start":
                    status[0] = m["status"]
                    for k, v in m.get("headers", []):
                        resp_headers[k.decode().lower()] = v.decode()
                elif m["type"] == "http.response.body":
                    resp_body.extend(m.get("body", b""))
                await send(m)

            try:
                await app(scope, recv, snd)
            finally:
                hdr = {k: v for k, v in req_headers.items() if k in KEEP_HEADERS}
                if "authorization" in req_headers:
                    hdr["authorization"] = req_headers["authorization"].split(" ")[0] + " <redacted>"
                entry = {"tag": tag, "at_ms": round((t - rec.t0) * 1000, 1), "method": scope["method"],
                         "path": scope["path"] + (("?" + scope["query_string"].decode()) if scope.get("query_string") else ""),
                         "status": status[0], "ms": round((time.perf_counter() - t) * 1000, 1),
                         "req_headers": hdr,
                         "resp_headers": {k: v for k, v in resp_headers.items() if k in KEEP_HEADERS},
                         "req": _parse(bytes(req_body), req_headers.get("content-type", "")),
                         "resp": _parse(bytes(resp_body), resp_headers.get("content-type", "")),
                         "req_bytes": len(req_body), "resp_bytes": len(resp_body)}
                with rec._lock:
                    rec.log.append(entry)
        return mw

    def rpc_calls(self):
        """The JSON-RPC method of every POST, in order (with the tool name for tools/call)."""
        out = []
        for e in self.log:
            r = e["req"]
            if isinstance(r, dict) and "method" in r:
                name = (r.get("params") or {}).get("name")
                out.append(r["method"] + (f" {name}" if name else ""))
        return out


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def serve(app, port: int | None = None, host: str = "127.0.0.1") -> str:
    """Run `app` under uvicorn in a daemon thread; return its base URL once it accepts connections."""
    import uvicorn

    port = port or free_port()
    cfg = uvicorn.Config(app, host=host, port=port, log_level="warning", lifespan="on")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    for _ in range(200):
        try:
            with socket.create_connection((host, port), timeout=0.2):
                break
        except OSError:
            time.sleep(0.05)
    return f"http://{host}:{port}"
