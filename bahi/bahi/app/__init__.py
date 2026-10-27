"""Lecture 5: the reference web app. Chat <-> agent API <-> control graph <-> MCP intent tools <-> Bahi,
with an approval inbox (web and a Slack-style channel) and an audit viewer.

    python -m bahi.app                      # http://127.0.0.1:8090/app/chat  (Kavita) · /app/inbox (Rohit)
    from bahi.app.main import create_app    # in tests: fastapi.testclient.TestClient(create_app())
"""
