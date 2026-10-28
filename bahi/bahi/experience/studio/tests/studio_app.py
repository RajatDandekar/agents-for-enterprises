"""A minimal FastAPI app that mounts the Studio router, for tests (the experience app mounts it the same way).

    uvicorn bahi.experience.studio.tests.studio_app:app --port 8770
"""
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from bahi.experience.players import Players
from bahi.experience.studio.api import make_router

players = Players()
app = FastAPI(title="Rasoi Workflow Studio (test app)")
app.include_router(make_router(players))


@app.get("/")
def root():
    return RedirectResponse("/studio")
