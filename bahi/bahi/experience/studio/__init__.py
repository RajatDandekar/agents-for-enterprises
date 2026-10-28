"""The Workflow Studio: an n8n-like playground where students stitch toolbox tools into workflows and build agents.

    from bahi.experience.studio import make_router
    app.include_router(make_router(players))          # the page at /studio, JSON under /api/studio

The engine (bahi.experience.studio.engine) needs no web framework; make_router imports FastAPI only when called.
See SPEC.md for the workflow JSON, the run semantics and the API.
"""


def make_router(players, store=None):
    from .api import make_router as _make_router

    return _make_router(players, store)
