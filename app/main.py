from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.config import settings
from app.database import init_db
from app.routes.auth import router as auth_router
from app.routes.planners import router as planner_router
from app.routes.pages import router as page_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title=settings.app_name, version="1.0.0", description="Budget-aware GenAI recommendation assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

app.include_router(page_router)
app.include_router(auth_router, prefix="/api")
app.include_router(planner_router, prefix="/api")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok", "ai_enabled": settings.ai_enabled, "app": settings.app_name}
