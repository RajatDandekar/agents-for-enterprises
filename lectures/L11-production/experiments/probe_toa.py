"""Probe 2: the standalone temporalio-openai-agents package (Temporal docs, 2026: replaces temporalio.contrib.openai_agents)."""
import subprocess, sys
V = subprocess.run([sys.executable, "-m", "pip", "index", "versions", "temporalio-openai-agents"], capture_output=True, text=True).stdout[:400]
print(V)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "temporalio==1.34.0", "temporalio-openai-agents"], check=False)
from importlib.metadata import version, requires
print("temporalio-openai-agents", version("temporalio-openai-agents"), "openai-agents", version("openai-agents"), "openai", version("openai"))
print(requires("temporalio-openai-agents"))
import inspect, temporalio.openai_agents as t
print([n for n in dir(t) if not n.startswith("_")])
import temporalio.openai_agents.testing as tt
print("testing:", [n for n in dir(tt) if not n.startswith("_")])
import agents
from agents import OpenAIChatCompletionsModel
print(inspect.signature(OpenAIChatCompletionsModel))
from agents.models.interface import ModelProvider
print(inspect.getsource(ModelProvider)[:800])

import os; os.makedirs("logs", exist_ok=True); open("logs/probe_toa.txt","w").write(V + "\n" + " ".join(["temporalio-openai-agents", version("temporalio-openai-agents"), "openai-agents", version("openai-agents"), "openai", version("openai")]) + "\n" + str(requires("temporalio-openai-agents")))
