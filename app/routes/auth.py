from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import RegisterRequest, LoginRequest
from app.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(tags=["authentication"])

@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if data.confirm_password is not None and data.password != data.confirm_password:
        raise HTTPException(422, "Passwords do not match")
    username = (data.username or data.name or "").strip()
    if not username:
        raise HTTPException(422, "Username is required")
    email = (data.email or username).strip().lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(409, "That username is already in use")
    user = User(name=username, email=email, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "Registration successful", "token": create_access_token(user.id), "user": {"id": user.id, "name": user.name, "email": user.email}}

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    identifier = (data.username or data.email or "").strip()
    user = db.query(User).filter(User.email == identifier.lower()).first()
    if not user and identifier:
        user = db.query(User).filter(User.name.ilike(identifier)).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid username or password")
    return {"message": "Login successful", "token": create_access_token(user.id), "user": {"id": user.id, "name": user.name, "email": user.email}}

@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "name": user.name, "email": user.email}

@router.post("/logout")
def logout():
    return {"message": "Logout is handled client-side by removing the access token"}
