"""Travel entitlement: the starter tool of this kit (read-only). Copy its shape for the rest of your toolbox.

Input and output are described in tool.json next to this file."""
from bahi.agent.tools import ToolError, _bahi  # noqa: F401

def run(s, city=None, city_code=None):
    if not city_code:
        if not city:
            raise ToolError("Give a city or a city code.", "Ask the user where they are going.")
        rows = _bahi(s, "tv_ent_get", q=city)["rows"]
        exact = [r for r in rows if r["name"].lower() == city.lower()]
        if len(exact) != 1:
            return {"ok": True, "matches": rows, "next_step": "Several cities match. Ask the user which one."}
        city_code = exact[0]["city_cd"]
    e = _bahi(s, "tv_ent_get", to_cd=city_code)
    return {"ok": True, "city_code": city_code, "grade": e["grade"], "modes": e["modes"], "km": e["km"],
            "hotel_cap": e["hotel_cap"], "daily_allowance": e["da"], "cost_centre": e["cc_cd"]}
