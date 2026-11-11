"""The smallest agent loop (Lecture 5, Section 2): no harness at all, only the loop.

    from ledgerline.daedalus.smallest import agent
    reply = agent("How many BAT-500 packs do we have?", toolbox, llm)
"""
import json


def agent(question, toolbox, llm, system="You are Ask Northbridge."):
    messages = [{"role": "system", "content": system},
                {"role": "user", "content": question}]
    while True:                                    # no step limit, no budget
        r = llm.chat(messages, tools=toolbox.schemas())         # 1. think
        messages.append(r.message())
        if not r.tool_calls:                               # 2. words: done
            return r.content
        for call in r.tool_calls:                                 # 3. act
            result = toolbox.call(call.name, call.arguments)
            messages.append({"role": "tool", "tool_call_id": call.id,
                             "content": json.dumps(result, default=str)})  # 4. observe
