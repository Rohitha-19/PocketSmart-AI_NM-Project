import os
import json
from pathlib import Path
from types import SimpleNamespace

os.environ["USE_AI"] = "false"
os.environ["SECRET_KEY"] = "test-secret"

from fastapi.testclient import TestClient
from app.main import app
from app.services.catalog import product_url, service_url
from app.services import gemini as gemini_service

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_page_routes_render():
    for path in ("/", "/login", "/register", "/dashboard", "/planner/home", "/planner/party", "/planner/jewelry"):
        r = client.get(path)
        assert r.status_code == 200, f"{path} returned {r.status_code}"

def test_planner_history_navigation_highlights_current_section():
    pages = {
        "/planner/home": "Home Budget Planner",
        "/planner/party": "Party Budget Planner",
        "/planner/jewelry": "Jewelry Budget Planner",
        "/history": "History",
    }
    for path, label in pages.items():
        response = client.get(path)
        assert response.status_code == 200
        navigation = response.text.split('<nav>', 1)[1].split('</nav>', 1)[0]
        assert f'class="planner-nav-link" href="{path}" aria-current="page">{label}</a>' in navigation

def test_register_login_and_home():
    email = "test@example.com"
    r = client.post("/api/register", json={"name":"Test User","email":email,"password":"secret123"})
    assert r.status_code in (200, 409)
    if r.status_code == 409:
        r = client.post("/api/login", json={"email":email,"password":"secret123"})
    token = r.json()["token"]
    headers = {"Authorization":f"Bearer {token}"}
    r = client.post("/api/generate-home", headers=headers, json={
        "budget": 25000, "city":"Chennai", "style":"Modern",
        "rooms":["Living Room"], "items":[{"category":"Lighting","quantity":2,"notes":""}]
    })
    assert r.status_code == 200
    assert r.json()["planner"] == "home"
    assert len(r.json()["recommendations"]) > 0


def test_catalog_shopping_links_and_jewelry_tips_text():
    assert "myntra.com" in product_url("Myntra", "lamp")
    assert "ajio.com" in product_url("Ajio", "lamp")
    assert "bookmyshow.com" in service_url("BookMyShow", "birthday party")
    assert "meesho.com" in product_url("Meesho", "necklace")

    app_js = Path("app/static/js/app.js").read_text(encoding="utf-8")
    assert "Styling Tips" in app_js


def test_planner_currency_uses_indian_rupees():
    app_js = Path("app/static/js/app.js").read_text(encoding="utf-8")
    assert 'currency:"INR"' in app_js

    for template in ("home_planner.html", "party_planner.html", "jewelry_planner.html"):
        page = (Path("app/templates") / template).read_text(encoding="utf-8")
        assert "Total Budget (₹)" in page
        assert "$" not in page


def test_jewelry_upload_shows_selected_image_preview():
    page = client.get("/planner/jewelry").text
    assert 'id="outfitPreview"' in page
    assert 'id="removeImage"' in page

    planner_js = Path("app/static/js/planners.js").read_text(encoding="utf-8")
    assert "URL.createObjectURL(file)" in planner_js
    assert "remove.addEventListener(\"click\"" in planner_js


def test_gemini_retries_with_flash_lite_on_capacity_error(monkeypatch):
    calls = []

    class CapacityError(Exception):
        code = 503

    class FakeModels:
        def generate_content(self, *, model, **kwargs):
            calls.append(model)
            if len(calls) == 1:
                raise CapacityError("Model capacity temporarily unavailable")
            return SimpleNamespace(text=json.dumps({"summary": "Plan ready", "recommendations": [], "tips": []}))

    class FakeClient:
        models = FakeModels()

    monkeypatch.setattr(gemini_service, "_client", lambda: FakeClient())
    result = gemini_service.generate_plan("Make a budget plan")

    assert result is not None
    assert calls == [gemini_service.settings.gemini_model, "gemini-flash-lite-latest"]
    assert result["_model_used"] == "gemini-flash-lite-latest"


def test_testimonials_registration_and_jewelry_styling_tips():
    response = client.get("/testimonials", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/#testimonials"

    home = client.get("/").text
    assert 'id="features"' in home
    assert 'id="testimonials"' in home
    assert "Example user stories" in home
    assert "site-footer" in home

    for path in ("/login", "/register", "/dashboard", "/planner/home"):
        page = client.get(path).text
        assert "site-footer" not in page
        assert 'id="testimonials"' not in page

    register_page = client.get("/register")
    assert 'name="username"' in register_page.text
    assert 'name="email"' in register_page.text
    assert 'name="password"' in register_page.text
    assert 'name="confirm_password"' in register_page.text

    email = "confirm-mismatch@example.com"
    response = client.post("/api/register", json={
        "username": "ConfirmMismatch",
        "email": email,
        "password": "secret123",
        "confirm_password": "different123",
    })
    assert response.status_code == 422

    from app.services.recommendations import build_jewelry
    result = build_jewelry({"budget": 5000, "occasion": "Wedding", "style": "Minimal", "metal": "Gold"})
    assert result["tips"]
    assert any("Wedding" in tip or "Gold" in tip for tip in result["tips"])
