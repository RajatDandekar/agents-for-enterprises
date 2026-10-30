"""Our own Lecture 5 harness and control graph, on the same footing as the frameworks: tools over MCP (HTTP), the
same model through OpenRouter, the cost OpenRouter billed.

    from ledgerline.course.frameworks.ours import harness_port, graph_port
    a = harness_port(Toolbox(erp, "ECLARKE"), cassette="IND8_ours")              # every harness part on
    b = harness_port(Toolbox(erp, "ECLARKE"), cassette="IND8_bare", parts=())   # only the loop
"""
from __future__ import annotations

from ..l5.harness import PARTS, Harness
from .base import MODEL, toolbox_server
from .mcp_http import MCPToolbox
from .meter import MeteredLLM

_TOOLBOXES: dict = {}


def mcp_toolbox(tb) -> MCPToolbox:
    key = (id(tb.erp), tb.user)
    if key not in _TOOLBOXES:
        from ...toolbox import Toolbox
        _TOOLBOXES[key] = MCPToolbox(toolbox_server(tb.erp, tb.user, None if isinstance(tb, Toolbox) else tb))
    return _TOOLBOXES[key]


def harness_port(tb, cassette: str = "IND8_ours", model: str = MODEL, parts=PARTS, llm=None, mode=None) -> Harness:
    llm = llm or MeteredLLM("openrouter:" + model if ":" not in model.split("/")[0] else model, cassette=cassette,
                            mode=mode)
    h = Harness(mcp_toolbox(tb), llm, parts=parts)
    h.framework = "ours"
    return h


def graph_port(tb, cassette: str = "IND8_graph", model: str = MODEL, mode=None):
    from ..l5.graph import ControlGraph
    g = ControlGraph(mcp_toolbox(tb), MeteredLLM("openrouter:" + model, cassette=cassette, mode=mode))
    g.framework = "langgraph_control"
    return g
