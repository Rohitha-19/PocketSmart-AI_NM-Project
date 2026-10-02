import json
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, RecommendationHistory
from app.schemas import HomeRequest, PartyRequest, JewelryRequest
from app.security import get_current_user
from app.services.recommendations import build_home, build_party, build_jewelry

router = APIRouter(tags=["planners"])

def save_history(db, user_id, planner, request_data, result):
    row = RecommendationHistory(
        user_id=user_id,
        planner=planner,
        request_json=json.dumps(request_data),
        result_json=json.dumps(result),
    )
    db.add(row)
    db.commit()

@router.post("/generate-home")
def generate_home(data: HomeRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = build_home(data.model_dump())
    save_history(db, user.id, "home", data.model_dump(), result)
    return result

@router.post("/generate-party")
def generate_party(data: PartyRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = build_party(data.model_dump())
    save_history(db, user.id, "party", data.model_dump(), result)
    return result

@router.post("/generate-jewelry")
async def generate_jewelry(
    budget: float = Form(..., gt=0),
    occasion: str = Form("Wedding"),
    style: str = Form("Elegant"),
    style_preferences: str = Form(""),
    metal: str = Form("Any"),
    outfit_color: str = Form(""),
    image: UploadFile | None = File(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if budget > 10_000_000:
        raise HTTPException(422, "Budget is too large")
    image_data_url = None
    if image and image.filename:
        if image.content_type not in {"image/jpeg", "image/png", "image/webp"}:
            raise HTTPException(415, "Only JPG, PNG, or WEBP images are supported")
        content = await image.read()
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(413, "Image must be 5 MB or smaller")
        import base64
        image_data_url = f"data:{image.content_type};base64,{base64.b64encode(content).decode()}"

    style_context = style_preferences.strip() or style
    data = {
        "budget": budget, "occasion": occasion, "style": style_context,
        "style_preferences": style_preferences.strip(),
        "metal": metal, "outfit_color": outfit_color,
        "image_data_url": image_data_url,
    }
    result = build_jewelry(data)
    safe_history = {k: v for k, v in data.items() if k != "image_data_url"}
    safe_history["image_uploaded"] = bool(image and image.filename)
    save_history(db, user.id, "jewelry", safe_history, result)
    return result

@router.get("/history")
def history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (
        db.query(RecommendationHistory)
        .filter(RecommendationHistory.user_id == user.id)
        .order_by(RecommendationHistory.created_at.desc())
        .limit(30)
        .all()
    )
    return [
        {
            "id": r.id, "planner": r.planner,
            "request": json.loads(r.request_json),
            "result": json.loads(r.result_json),
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]

@router.get("/session-info")
def session_info(user: User = Depends(get_current_user)):
    return {"logged_in": True, "user_id": user.id, "name": user.name}

@router.get("/session-data")
def session_data(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    count = db.query(RecommendationHistory).filter(RecommendationHistory.user_id == user.id).count()
    return {"user_id": user.id, "recommendation_count": count}
