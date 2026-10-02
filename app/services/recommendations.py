from app.config import settings
from app.services.catalog import home_catalog, party_catalog, jewelry_catalog
from app.services.gemini import generate_plan

def _prompt(planner: str, data: dict, catalog: list[dict]) -> str:
    return f"""
You are PocketSmart AI, a budget planning assistant.
Planner: {planner}
User input:
{data}

Candidate catalog:
{catalog}

Return practical recommendations using ONLY the candidate catalog URLs/platforms.
Do not invent live stock, exact availability, reviews, or current prices.
Keep the total estimated cost at or below the user's budget where possible.
Explain that prices are estimates and users should verify the destination site.
For jewelry image input, use the image only for general color/style coordination.
""".strip()

def build_home(data: dict):
    catalog = home_catalog(data["budget"], data.get("items", []))
    ai = generate_plan(_prompt("home interior", data, catalog))
    return _merge("home", data["budget"], catalog, ai)

def build_party(data: dict):
    catalog = party_catalog(
        data["budget"], data["guests"], data["event_type"],
        data.get("needs"), data.get("venue_type", "Flexible"),
    )
    ai = generate_plan(_prompt("party planning", data, catalog))
    return _merge("party", data["budget"], catalog, ai)

def build_jewelry(data: dict):
    catalog = jewelry_catalog(data["budget"])
    ai = generate_plan(_prompt("jewelry selection", data, catalog), data.get("image_data_url"))
    result = _merge("jewelry", data["budget"], catalog, ai)
    result["tips"] = _jewelry_styling_tips(data)
    return result

def _jewelry_styling_tips(data: dict) -> list[str]:
    occasion = data.get("occasion", "your occasion")
    style = data.get("style") or data.get("style_preferences") or "balanced"
    metal = data.get("metal", "Any")
    tips = [
        f"For {occasion}, choose {style.lower()} pieces that suit the formality of the event.",
        f"{f'Keep to {metal.lower()} tones for a coordinated finish.' if metal != 'Any' else 'Choose one metal tone across your main pieces for a coordinated finish.'}",
        "Pair one statement piece with simpler accessories so the overall look feels balanced.",
    ]
    if data.get("image_data_url") or data.get("outfit_color"):
        tips.append("Coordinate jewelry with your outfit color and neckline; use a contrasting accent when the outfit is monochrome.")
    else:
        tips.append("Match necklace length to the neckline, and consider earrings as the focal point when your outfit has a high neckline.")
    tips.append("Prioritize the piece you will wear most, then use the remaining budget for complementary accessories.")
    return tips

def _merge(planner: str, budget: float, fallback: list[dict], ai: dict | None):
    if ai and isinstance(ai.get("recommendations"), list):
        recs = ai["recommendations"][:8]
        for rec in recs:
            if not isinstance(rec.get("estimated_price"), (int, float)):
                rec["estimated_price"] = 0
        summary = ai.get("summary", "AI-generated budget plan.")
        tips = ai.get("tips", [])
        ai_used = True
    else:
        recs = fallback
        summary = {
            "home": "A starter home-interior plan based on your budget and selected needs.",
            "party": "A starter party plan with food, venue, and decoration references.",
            "jewelry": "A starter jewelry shortlist based on occasion, style, and budget.",
        }[planner]
        tips = [
            "Prices are estimates for planning only.",
            "Open the source links to verify current price, stock, delivery, and availability.",
            "Adjust quantities or remove lower-priority items if the plan exceeds your budget.",
        ]
        ai_used = False

    total = sum(float(r.get("estimated_price", 0)) for r in recs)
    return {
        "planner": planner,
        "budget": budget,
        "allocated_total": round(total, 2),
        "summary": summary,
        "recommendations": recs,
        "tips": tips,
        "ai_used": ai_used,
        "ai_status": "gemini" if ai_used else "unavailable" if settings.ai_enabled else "disabled",
        "model": ai.get("_model_used", settings.gemini_model) if ai_used else "fallback-catalog",
    }
