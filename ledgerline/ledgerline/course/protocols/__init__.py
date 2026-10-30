"""Lecture 9, Protocols and Integration: library code for the notebook and the experiments.

    northbridge_mcp   the Northbridge toolbox as an MCP server written with the official MCP Python SDK (mcp 2.x):
                tools from the tool.json folders, resources (the purchase policy, live stock), prompts
                ("raise a PR"), and a human confirmation on writes through elicitation.
    wire        start an ASGI app on a local port and record every HTTP exchange (the "wire").
    security    a poisoned server, an injected supplier quote, and the host-side defences, measured.
    auth        a toy OAuth 2.1 authorization server in front of the toolbox (whose token, whose session).
    voltway      Voltway Cells' supplier agent over A2A, and the A2A client Ask Northbridge uses to talk to it.

Everything here is fictional (Northbridge Cycles, Ledgerline ERP, Voltway Cells).
"""
PINS = {  # every version this lecture was built and recorded with (2026-10-28)
    "mcp": "2.3.0",
    "fastmcp": "4.1.4",
    "a2a-sdk": "1.2.3",
    "n8n": "2.45.5",
    "@modelcontextprotocol/inspector": "2.12.0",
    "github-mcp-server": "2.0.3",
}
