# app/profile.py
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db import get_db
from app.author import get_current_user
from app.models import User
from app.schemas_user import UserOut
import pathlib, time, os

router = APIRouter(tags=["profile"])

BASE = pathlib.Path(__file__).resolve().parent.parent
AVATAR_DIR = BASE / "static" / "avatars"
os.makedirs(AVATAR_DIR, exist_ok=True)


@router.get("/me", response_model=UserOut)
def get_me(user: User = Depends(get_current_user)):
    """Возвращает текущего пользователя"""
    return user


@router.put("/me", response_model=UserOut)
def update_me(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Обновление имени/почты/телефона"""

    user.full_name = full_name.strip()
    user.email = email.strip().lower()
    user.phone = phone.strip() if phone else None

    db.commit()
    db.refresh(user)
    return user


@router.post("/me/avatar", response_model=UserOut)
async def upload_avatar(
    avatar: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    ext = pathlib.Path(avatar.filename).suffix.lower()
    filename = f"{int(time.time())}_{user.id}{ext}"

    save_dir = BASE / "static" / "uploads"
    os.makedirs(save_dir, exist_ok=True)

    save_path = save_dir / filename

    with open(save_path, "wb") as f:
        f.write(await avatar.read())

    # Вот так должно быть
    user.avatar_url = f"/static/uploads/{filename}"

    db.commit()
    db.refresh(user)

    return user

