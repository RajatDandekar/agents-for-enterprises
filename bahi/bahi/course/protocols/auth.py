"""A remote Rasoi toolbox behind OAuth 2.1, the way the MCP authorization spec (2026-07-28) asks for it.

Three parts, all in this file, all on localhost:

    RasoiSignIn          a toy authorization server ("Rasoi sign-in"), built from the official SDK's auth routes:
                         /.well-known/oauth-authorization-server (RFC 8414), /register (dynamic client
                         registration, RFC 7591), /authorize (PKCE S256; it signs in whichever test user the
                         demo chose, with the scopes that user "consents" to), /token.
                         Tokens are opaque random strings; the server remembers sub, scope and audience.
    protected_toolbox()  the MCP server as a *resource server*: no token -> 401 + WWW-Authenticate pointing at
                         /.well-known/oauth-protected-resource/mcp (RFC 9728). Each request runs as the token's
                         own Bahi user (Kavita's token -> Kavita's session), and the token's scopes decide which
                         tools it may list and call: purchase:read (the 7 look-ups), purchase:write (the 8 writes).
                         Tokens issued for any other server (audience) are refused.
    sign_in(...)         an official-SDK MCP client that runs the whole flow by itself (OAuthClientProvider):
                         401 -> discovery -> registration -> authorize -> code -> token -> retry with Bearer.

    from bahi.course.protocols.auth import start_protected_toolbox, sign_in
    world = start_protected_toolbox()                       # URLs, the sign-in server, the shared Bahi
    async with sign_in(world, "KJOSHI", ["purchase:read", "purchase:write"]) as c:
        await c.call_tool("check_stock", {"item_code": "GSK-SIL-05L"})

`bound_user="SVC_AGENT"` builds the *wrong* server on purpose (the confused deputy): it ignores whose token
arrived and acts as the all-powerful service account.

What a real deployment adds: a real identity provider (sign-in page, MFA, consent screen), signed JWTs or
token introspection instead of a shared in-memory table, HTTPS everywhere, refresh-token rotation,
Client ID Metadata Documents instead of dynamic registration (deprecated in 2026-07-28), and audit logs.
"""
from __future__ import annotations

import contextlib
import json
import secrets
import time
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

from ...erp.engine import ERP
from ...toolbox import SPECS, Toolbox
from .wire import Recorder, free_port, serve

READ, WRITE = "purchase:read", "purchase:write"
SCOPES = [READ, WRITE]
REDIRECT = "http://localhost:3030/callback"  # the client's loopback redirect; never actually served


def tool_scope(name: str) -> str:
    return WRITE if SPECS[name].writes else READ


class RasoiSignIn:
    """An OAuthAuthorizationServerProvider (the SDK's interface), kept in memory."""

    def __init__(self, issuer: str):
        self.issuer = issuer
        self.clients: dict[str, Any] = {}
        self.codes: dict[str, Any] = {}
        self.tokens: dict[str, Any] = {}
        self.next_login = ("KJOSHI", list(SCOPES))  # who signs in at the next /authorize, and what they allow
        self.events: list[dict] = []

    def as_user(self, user: str, grant: list[str]):
        """The demo's stand-in for the sign-in page: who types their password next, and what they tick."""
        self.next_login = (user, list(grant))

    # --- registration (RFC 7591) ---
    async def get_client(self, client_id):
        return self.clients.get(client_id)

    async def register_client(self, client_info):
        self.clients[client_info.client_id] = client_info
        self.events.append({"event": "registered", "client_id": client_info.client_id[:8] + "…",
                            "scope": client_info.scope, "application_type": getattr(client_info, "application_type", None)})

    # --- authorization code with PKCE ---
    async def authorize(self, client, params):
        from mcp.server.auth.provider import AuthorizationCode

        user, grant = self.next_login
        asked = params.scopes or []
        scopes = [s for s in asked if s in grant]  # the user consents to part of what was asked, or all of it
        code = secrets.token_urlsafe(24)
        self.codes[code] = AuthorizationCode(code=code, scopes=scopes, expires_at=time.time() + 300,
                                             client_id=client.client_id, code_challenge=params.code_challenge,
                                             redirect_uri=params.redirect_uri,
                                             redirect_uri_provided_explicitly=params.redirect_uri_provided_explicitly,
                                             resource=params.resource, subject=user)
        self.events.append({"event": "signed in", "user": user, "asked": asked, "granted": scopes,
                            "resource": params.resource})
        # RFC 9207: iss must equal the metadata's issuer string exactly (the SDK checks; a missing trailing
        # slash made our first run fail with "iss mismatch").
        from pydantic import AnyHttpUrl
        q = {"code": code, "iss": str(AnyHttpUrl(self.issuer))}
        if params.state:
            q["state"] = params.state
        return f"{params.redirect_uri}?{urlencode(q)}"

    async def load_authorization_code(self, client, authorization_code):
        c = self.codes.get(authorization_code)
        return c if c and c.client_id == client.client_id else None

    async def exchange_authorization_code(self, client, authorization_code):
        from mcp.server.auth.provider import AccessToken
        from mcp.shared.auth import OAuthToken

        self.codes.pop(authorization_code.code, None)  # a code works once
        tok = secrets.token_urlsafe(32)
        self.tokens[tok] = AccessToken(token=tok, client_id=client.client_id, scopes=authorization_code.scopes,
                                       expires_at=int(time.time()) + 3600, resource=authorization_code.resource,
                                       subject=authorization_code.subject, claims={"iss": self.issuer})
        self.events.append({"event": "token issued", "sub": authorization_code.subject,
                            "scope": authorization_code.scopes, "aud": authorization_code.resource})
        return OAuthToken(access_token=tok, expires_in=3600, scope=" ".join(authorization_code.scopes))

    async def load_refresh_token(self, client, refresh_token):
        return None

    async def exchange_refresh_token(self, client, refresh_token, scopes):
        raise NotImplementedError

    async def load_access_token(self, token):
        return self.tokens.get(token)

    async def revoke_token(self, token):
        self.tokens.pop(getattr(token, "token", ""), None)

    async def exchange_identity_assertion(self, *a, **k):
        raise NotImplementedError


class SharedTableVerifier:
    """The resource server's TokenVerifier. Here it reads the sign-in server's table; a real server would check
    a JWT signature (JWKS) or call the token introspection endpoint (RFC 7662)."""

    def __init__(self, signin: RasoiSignIn):
        self.signin = signin

    async def verify_token(self, token):
        return self.signin.tokens.get(token)


def signin_app(signin: RasoiSignIn):
    from mcp.server.auth.routes import create_auth_routes
    from mcp.server.auth.settings import ClientRegistrationOptions
    from pydantic import AnyHttpUrl
    from starlette.applications import Starlette

    routes = create_auth_routes(signin, AnyHttpUrl(signin.issuer),
                                client_registration_options=ClientRegistrationOptions(
                                    enabled=True, valid_scopes=SCOPES, default_scopes=[READ]))
    return Starlette(routes=routes)


def _token_from(ctx):
    """The access token of the request being handled (set by the SDK's auth middleware)."""
    from mcp.server.auth.middleware.auth_context import get_access_token

    tok = get_access_token()
    if tok is not None:
        return tok, "auth_context"
    req = getattr(ctx, "request", None)
    user = getattr(req, "scope", {}).get("user") if req is not None else None
    if user is not None and hasattr(user, "access_token"):
        return user.access_token, "request.scope"
    return None, "none"


def build_protected_server(erp: ERP, bound_user: str | None = None, name: str = "rasoi-toolbox-remote"):
    """The toolbox as an OAuth-protected MCP server. bound_user=None: act as the token's user (right).
    bound_user="SVC_AGENT": act as the service account whoever calls (the confused deputy)."""
    import mcp_types as t
    from mcp.server import Server

    boxes: dict[str, Toolbox] = {}
    seen: list[dict] = []

    def box(user):
        if user not in boxes:
            boxes[user] = Toolbox(erp, user)
        return boxes[user]

    def identity(ctx):
        tok, how = _token_from(ctx)
        sub = tok.subject if tok else None
        scopes = list(tok.scopes) if tok else []
        return (bound_user or sub), sub, scopes, how

    async def list_tools(ctx, params):
        acting, sub, scopes, how = identity(ctx)
        names = [n for n in box(acting).names if bound_user or tool_scope(n) in scopes]
        seen.append({"method": "tools/list", "token_sub": sub, "acting_as": acting, "scopes": scopes,
                     "tools": len(names), "token_from": how})
        return t.ListToolsResult(tools=[t.Tool(name=n, title=SPECS[n].spec["title"],
                                               description=SPECS[n].spec["description"],
                                               input_schema=SPECS[n].spec["input_schema"],
                                               annotations=t.ToolAnnotations(read_only_hint=not SPECS[n].writes))
                                        for n in names])

    async def call_tool(ctx, params):
        acting, sub, scopes, how = identity(ctx)
        n = params.name
        need = tool_scope(n) if n in SPECS else READ
        if not bound_user and need not in scopes:
            out = {"ok": False, "error": f"insufficient_scope: {n} needs {need}; this token has {scopes}.",
                   "next_step": f"Sign in again and grant {need}, or ask someone who may."}
        else:
            out = box(acting).call(n, dict(params.arguments or {}))
        seen.append({"method": "tools/call", "tool": n, "token_sub": sub, "acting_as": acting, "scopes": scopes,
                     "ok": out.get("ok"), "token_from": how})
        return t.CallToolResult(content=[t.TextContent(type="text", text=json.dumps(out, default=str))],
                                structured_content=out, is_error=not out.get("ok", True))

    server = Server(name, version="9.0", on_list_tools=list_tools, on_call_tool=call_tool,
                    instructions="Rasoi toolbox, remote. Sign in with Rasoi sign-in; tools run as you.")
    server.seen, server.boxes = seen, boxes
    return server


def protected_app(server, signin: RasoiSignIn, resource_url: str):
    from mcp.server.auth.settings import AuthSettings
    from pydantic import AnyHttpUrl

    auth = AuthSettings(issuer_url=AnyHttpUrl(signin.issuer), resource_server_url=AnyHttpUrl(resource_url),
                        required_scopes=None, validate_token_resource=True)
    return server.streamable_http_app(auth=auth, token_verifier=SharedTableVerifier(signin))


class World:
    """Everything the demos need, running on localhost: one Bahi, one sign-in server, the protected toolbox,
    the deputy toolbox (bound to SVC_AGENT) and a second resource server ("Rasoi reports") for audience tests."""

    def __init__(self):
        self.erp = ERP()
        self.rec_as, self.rec_rs = Recorder(), Recorder()
        p_as, p_rs, p_dep, p_rep = free_port(), free_port(), free_port(), free_port()
        self.issuer = f"http://127.0.0.1:{p_as}"
        self.signin = RasoiSignIn(self.issuer)
        self.as_url = serve(self.rec_as.wrap(signin_app(self.signin), "sign-in"), p_as)
        self.toolbox_url = f"http://127.0.0.1:{p_rs}/mcp"
        self.server = build_protected_server(self.erp)
        serve(self.rec_rs.wrap(protected_app(self.server, self.signin, self.toolbox_url), "toolbox"), p_rs)
        self.deputy_url = f"http://127.0.0.1:{p_dep}/mcp"
        self.deputy = build_protected_server(self.erp, bound_user="SVC_AGENT", name="rasoi-toolbox-deputy")
        serve(self.rec_rs.wrap(protected_app(self.deputy, self.signin, self.deputy_url), "deputy"), p_dep)
        self.reports_url = f"http://127.0.0.1:{p_rep}/mcp"
        self.reports = build_protected_server(self.erp, name="rasoi-reports")
        serve(self.rec_rs.wrap(protected_app(self.reports, self.signin, self.reports_url), "reports"), p_rep)


def start_protected_toolbox() -> World:
    return World()


class MemoryStorage:
    def __init__(self):
        self.tokens = None
        self.client = None

    async def get_tokens(self):
        return self.tokens

    async def set_tokens(self, tokens):
        self.tokens = tokens

    async def get_client_info(self):
        return self.client

    async def set_client_info(self, client_info):
        self.client = client_info


def oauth_provider(server_url: str, storage: MemoryStorage | None = None):
    """The SDK's OAuthClientProvider. The 'browser' is httpx: it opens the authorize URL, reads the redirect
    (code, state, iss) from the Location header and hands it back, as a real browser callback would."""
    import httpx
    from mcp.client.auth import OAuthClientProvider
    from mcp.shared.auth import AuthorizationCodeResult, OAuthClientMetadata
    from pydantic import AnyUrl

    box: dict = {}

    async def redirect_handler(url: str):
        async with httpx.AsyncClient() as h:
            r = await h.get(url, follow_redirects=False)
        q = parse_qs(urlparse(r.headers.get("location", "")).query)
        box.update({k: v[0] for k, v in q.items()})
        box["status"] = r.status_code

    async def callback_handler():
        return AuthorizationCodeResult(code=box.get("code", ""), state=box.get("state"), iss=box.get("iss"))

    meta = OAuthClientMetadata(client_name="Ask Rasoi (course demo)", redirect_uris=[AnyUrl(REDIRECT)],
                               grant_types=["authorization_code", "refresh_token"], response_types=["code"],
                               token_endpoint_auth_method="client_secret_post")
    storage = storage or MemoryStorage()
    prov = OAuthClientProvider(server_url=server_url, client_metadata=meta, storage=storage,
                               redirect_handler=redirect_handler, callback_handler=callback_handler)
    return prov, storage


@contextlib.asynccontextmanager
async def sign_in(world: World, user: str, grant: list[str], url: str | None = None, mode: str | None = None):
    """An MCP client signed in as `user`, who consents to the scopes in `grant`. Yields (client, storage)."""
    import httpx2
    from mcp import Client
    from mcp.client.streamable_http import streamable_http_client

    world.signin.as_user(user, grant)
    prov, storage = oauth_provider(url or world.toolbox_url)
    async with httpx2.AsyncClient(auth=prov, timeout=30) as h:
        kw = {"mode": mode} if mode else {}
        async with Client(streamable_http_client(url or world.toolbox_url, http_client=h), **kw) as c:
            yield c, storage
