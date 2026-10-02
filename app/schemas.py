from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

class RegisterRequest(BaseModel):
    username: str | None = Field(default=None, min_length=2, max_length=100)
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: str | None = Field(default=None, min_length=5, max_length=255)
    password: str = Field(min_length=6, max_length=128)
    confirm_password: str | None = None

class LoginRequest(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str

class HomeItem(BaseModel):
    category: str
    quantity: int = Field(default=1, ge=1, le=50)
    notes: str = ""

class HomeRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    city: str = "Chennai"
    style: str = "Modern"
    rooms: list[str] = []
    items: list[HomeItem] = []
    special_requirements: str = ""

class PartyRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    guests: int = Field(gt=0, le=10000)
    event_type: str = "Birthday"
    city: str = "Chennai"
    venue_preference: str = "Flexible"
    venue_type: str = "Home"
    food_preference: str = "Mixed"
    needs: list[str] = ["Catering", "Decoration", "Entertainment"]
    special_requests: str = ""

class JewelryRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    occasion: str = "Wedding"
    style: str = "Elegant"
    metal: str = "Any"
    outfit_color: str = ""
    image_data_url: Optional[str] = None

class Recommendation(BaseModel):
    title: str
    category: str
    platform: str
    estimated_price: float
    reason: str
    url: str
    tags: list[str] = []

class PlanResult(BaseModel):
    planner: Literal["home", "party", "jewelry"]
    budget: float
    allocated_total: float
    summary: str
    recommendations: list[Recommendation]
    tips: list[str]
    ai_used: bool
    model: str
