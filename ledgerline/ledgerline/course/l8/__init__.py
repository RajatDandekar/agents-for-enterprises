"""Lecture 8, Your Module: helpers for scaffolding a module kit's toolbox and putting Ask Northbridge on it.

    from ledgerline.course.l8 import scaffold, LEAVE_PROMPT, leave_agent
    names = scaffold("my_module_tools")                   # writes the hr_leave reference folders (tool.json + tool.py)
    make = leave_agent("gemini:gemini-3.8-flash", "L8v3_leave", "my_module_tools")
    run_module_scenario(make, "hr_leave", SCENARIOS[0])  # Ask Northbridge, over MCP, on HR leave
"""
from .hr_tools import LEAVE_PROMPT, TOOLS, leave_agent, scaffold  # noqa: F401
