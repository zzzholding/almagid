# app/author.py

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from app.db import get_db

from app.models import User  # покажу ниже

router = APIRouter(prefix="/auth", tags=["auth"])

JWT_SECRET = "change_me_secret_key"
JWT_ALG = "HS256"
JWT_TTL_MIN = 60 * 24

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(p: str):
    return pwd_context.hash(p)

def verify_password(p: str, h: str):
    return pwd_context.verify(p, h)

def create_access_token(sub: str):
    now = datetime.now(timezone.utc)
    return jwt.encode({
        "sub": sub,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=JWT_TTL_MIN)).timestamp())
    }, JWT_SECRET, algorithm=JWT_ALG)


class RegisterRequest(BaseModel):
    full_name: str
    phone: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):

    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(400, "Email exists")

    user = User(
        full_name=payload.full_name.strip(),
        phone=payload.phone.strip(),
        email=payload.email.lower(),
        password_hash=hash_password(payload.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"id": user.id, "email": user.email}


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == payload.email.lower()).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")

    token = create_access_token(str(user.id))
    return {"access_token": token}

