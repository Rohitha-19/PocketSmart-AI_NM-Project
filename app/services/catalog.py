"""Small deterministic demo catalog.

The source document asks for Amazon/Flipkart/IKEA/Swiggy/Zomato/OYO-style sourcing
but does not provide credentials or live API contracts. This catalog therefore uses
search URLs rather than pretending to have live inventory or prices.
"""

from urllib.parse import quote_plus

def product_url(platform: str, query: str) -> str:
    q = quote_plus(query)
    key = platform.casefold()
    urls = {
        "amazon": f"https://www.amazon.in/s?k={q}",
        "flipkart": f"https://www.flipkart.com/search?q={q}",
        "ikea": f"https://www.ikea.com/in/en/search/?q={q}",
        "myntra": f"https://www.myntra.com/search?searchTerm={q}",
        "ajio": f"https://www.ajio.com/search/?text={q}",
        "meesho": f"https://www.meesho.com/search?q={q}",
    }
    return urls.get(key, f"https://www.google.com/search?q={q}")

def service_url(platform: str, query: str) -> str:
    q = quote_plus(query)
    key = platform.casefold()
    urls = {
        "swiggy": f"https://www.swiggy.com/search?query={q}",
        "zomato": f"https://www.zomato.com/chennai/restaurants/search?query={q}",
        "oyo": f"https://www.oyorooms.com/search?q={q}",
        "bookmyshow": f"https://in.bookmyshow.com/explore?query={q}",
    }
    return urls.get(key, f"https://www.google.com/search?q={q}")

HOME_TEMPLATES = [
    ("Ceiling LED Light", "Lighting", "IKEA", 899, "Energy-efficient lighting for a clean modern look."),
    ("Modern Ceiling Fan", "Fans", "Amazon", 2499, "A practical airflow upgrade that stays within a moderate budget."),
    ("Compact Study/Side Table", "Furniture", "Flipkart", 3499, "Useful compact furniture for small rooms."),
    ("Wall Art Set", "Decor", "Amazon", 1299, "Adds visual character without taking a large share of the budget."),
    ("Storage Cabinet", "Storage", "IKEA", 5999, "Improves organization while keeping the room visually tidy."),
    ("Cushion Cover Set", "Soft Furnishing", "Flipkart", 699, "Low-cost way to refresh the color palette."),
    ("Decorative Table Lamp", "Lighting", "Myntra", 1199, "Soft ambient lighting that adds warmth and style."),
    ("Modern Sofa Throw", "Soft Furnishing", "Ajio", 1599, "Adds texture and comfort with a modest spend."),
    ("Minimalist Accent Chair", "Furniture", "Amazon", 4299, "A practical accent piece for reading corners or guest spaces."),
]

def home_catalog(budget: float, items: list[dict]):
    requested = [x.get("category", "").lower() for x in items]
    matches = [x for x in HOME_TEMPLATES if any(k in x[1].lower() or k in x[0].lower() for k in requested)]
    pool = matches or HOME_TEMPLATES
    return [
        {
            "title": title, "category": category, "platform": platform,
            "estimated_price": price, "reason": reason,
            "url": product_url(platform, title), "tags": ["budget-friendly", category.lower()]
        }
        for title, category, platform, price, reason in pool[:6]
    ]

PARTY_TEMPLATES = [
    ("Birthday catering package", "Catering", "Swiggy", 450, "Estimated per-person planning reference."),
    ("Party food package", "Catering", "Zomato", 500, "Useful starting point for comparing local food options."),
    ("Budget event venue", "Venue", "OYO", 6500, "Search-based venue/accommodation reference; verify availability directly."),
    ("Balloon & backdrop decor", "Decoration", "Amazon", 1800, "Simple decoration package for a small event."),
    ("Games and music setup", "Entertainment", "Amazon", 900, "A flexible low-cost option for keeping guests engaged."),
    ("Party return gifts", "Gifts", "Flipkart", 1200, "Can be adjusted based on guest count."),
    ("Party snacks combo", "Catering", "Swiggy", 700, "Useful for quick serving and guest-friendly options."),
    ("Event booking package", "Venue", "BookMyShow", 8200, "Good for entertainment-heavy or ticketed gatherings."),
    ("Decor essentials bundle", "Decoration", "Flipkart", 1500, "A cost-effective way to create a festive mood."),
]

def party_catalog(budget: float, guests: int, event_type: str, needs: list[str] | None = None, venue_type: str = "Flexible"):
    out = []
    requested = {need.casefold() for need in (needs if needs is not None else ["Catering", "Decoration", "Entertainment"])}
    for title, category, platform, price, reason in PARTY_TEMPLATES:
        if category not in {"Venue", "Catering"} and category.casefold() not in requested:
            continue
        if category == "Catering" and "catering" not in requested:
            continue
        estimated = price * guests if category == "Catering" else price
        if category == "Venue":
            title = f"Budget {venue_type.lower()} option"
        if estimated <= budget:
            query = f"{venue_type} {event_type} venue" if category == "Venue" else f"{event_type} {title}"
            url = service_url(platform, query) if platform in {"Swiggy", "Zomato", "OYO"} else product_url(platform, title)
            out.append({
                "title": title, "category": category, "platform": platform,
                "estimated_price": estimated, "reason": reason,
                "url": url, "tags": [event_type.lower(), category.lower()]
            })
    return out

JEWELRY_TEMPLATES = [
    ("Minimal necklace set", "Necklace", "Amazon", 1499, "Versatile option for elegant occasions."),
    ("Statement earrings", "Earrings", "Flipkart", 999, "Adds a focal point without a large budget allocation."),
    ("Classic bracelet", "Bracelet", "Amazon", 799, "Easy to pair with many outfit styles."),
    ("Pearl-inspired set", "Set", "Flipkart", 1899, "Works well with formal and festive styling."),
    ("Traditional jhumka", "Earrings", "Amazon", 699, "Suitable for traditional and festive looks."),
    ("Elegant stackable rings", "Rings", "Meesho", 799, "Easy to style with everyday and festive ensembles."),
    ("Minimal gold-tone necklace", "Necklace", "Myntra", 1299, "A polished accessory that works across multiple occasions."),
    ("Ethnic gemstone earrings", "Earrings", "Ajio", 1499, "Adds color and character without exceeding the budget."),
]

def jewelry_catalog(budget: float):
    return [
        {
            "title": title, "category": category, "platform": platform,
            "estimated_price": price, "reason": reason,
            "url": product_url(platform, title), "tags": ["style-match", "budget-aware"]
        }
        for title, category, platform, price, reason in JEWELRY_TEMPLATES
        if price <= budget
    ][:6] or [{
        "title": "Budget jewelry search",
        "category": "Jewelry",
        "platform": "Amazon",
        "estimated_price": min(499, budget),
        "reason": "Search directly for options at or below your budget.",
        "url": product_url("Amazon", "jewelry"),
        "tags": ["budget-aware"]
    }]
