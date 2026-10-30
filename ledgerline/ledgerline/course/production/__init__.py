"""Lecture 11, Running Agents in Production: the industry tools, each mapped onto what the students built by hand.

    from ledgerline.course.production import guards     # labelled messages, keyword filter, Llama Guard, gpt-oss-safeguard, NeMo config
    from ledgerline.course.production import injection  # a poisoned supplier record and three defences (L7's trust layer is one)
    from ledgerline.course.production import durable    # Ask Northbridge's order as a Temporal workflow with the OpenAI Agents SDK
    from ledgerline.course.production import cost       # cost per order from measured token logs
    from ledgerline.course.production import fixtures   # recorded runs NB11 replays with no key

Every module here imports its heavy dependency (temporalio, nemoguardrails, psycopg, redis, litellm) lazily, so the
notebook replays on free Colab without installing them.
"""
