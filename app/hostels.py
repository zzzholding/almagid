import os
import time
import pathlib
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db import get_db
from app.models import Hostel
from app.author import get_current_user

router = APIRouter(prefix="/hostels", tags=["hostels"])

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ---------------- Pydantic модель ----------------
class HostelOut(BaseModel):
    id: int
    name: str
    location: str | None
    price_text: str | None
    rating: int
    description: str | None
    image_url: str | None

    class Config:
        from_attributes = True


# ---------------- Создание хостела ----------------
@router.post("/", response_model=HostelOut)
async def create_hostel(
    name: str = Form(...),
    location: str = Form(...),
    price_text: str | None = Form(None),
    rating: int = Form(...),
    description: str | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    image_url = None

    # загрузка изображения
    if image and image.filename:
        ext = pathlib.Path(image.filename).suffix
        filename = f"{int(time.time())}_{os.urandom(4).hex()}{ext}"
        save_path = UPLOAD_DIR / filename

        with open(save_path, "wb") as f:
            f.write(await image.read())

        image_url = f"/static/uploads/{filename}"

    hostel = Hostel(
        name=name.strip(),
        location=location.strip(),
        price_text=price_text,
        rating=rating,
        description=description,
        image_url=image_url,
        user_id=user.id
    )

    db.add(hostel)
    db.commit()
    db.refresh(hostel)

    return hostel


# ---------------- Все хостелы ----------------
@router.get("/", response_model=list[HostelOut])
def list_hostels(db: Session = Depends(get_db)):
    return db.query(Hostel).order_by(Hostel.created_at.desc()).all()


# ---------------- Только мои ----------------
@router.get("/my", response_model=list[HostelOut])
def my_hostels(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Hostel).filter(Hostel.user_id == user.id).all()


# ---------------- Один хостел ----------------
@router.get("/{hostel_id}", response_model=HostelOut)
def get_hostel(hostel_id: int, db: Session = Depends(get_db)):
    h = db.query(Hostel).filter(Hostel.id == hostel_id).first()
    if not h:
        raise HTTPException(404, "Hostel not found")
    return h


# ---------------- Обновление ----------------
@router.put("/{hostel_id}", response_model=HostelOut)
async def update_hostel(
    hostel_id: int,
    name: str = Form(...),
    location: str = Form(...),
    price_text: str | None = Form(None),
    rating: int = Form(...),
    description: str | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    hostel = db.query(Hostel).filter(Hostel.id == hostel_id).first()

    if not hostel:
        raise HTTPException(404, "Hostel not found")

    if hostel.user_id != user.id:
        raise HTTPException(403, "Forbidden")

    # обновляем поля
    hostel.name = name.strip()
    hostel.location = location.strip()
    hostel.price_text = price_text
    hostel.rating = rating
    hostel.description = description

    # если новое изображение
    if image and image.filename:
        ext = pathlib.Path(image.filename).suffix
        filename = f"{int(time.time())}_{os.urandom(4).hex()}{ext}"
        save_path = UPLOAD_DIR / filename

        with open(save_path, "wb") as f:
            f.write(await image.read())

        hostel.image_url = f"/static/uploads/{filename}"

    db.commit()
    db.refresh(hostel)

    return hostel


# ---------------- Удаление ----------------
@router.delete("/{hostel_id}")
def delete_hostel(
    hostel_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    hostel = db.query(Hostel).filter(Hostel.id == hostel_id).first()

    if not hostel:
        raise HTTPException(404, "Hostel not found")

    if hostel.user_id != user.id:
        raise HTTPException(403, "Forbidden")

    db.delete(hostel)
    db.commit()

    return {"status": "deleted"}

