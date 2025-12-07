import os
import time
import pathlib

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Hostel
from app.author import get_current_user

router = APIRouter(prefix="/hostels", tags=["hostels"])

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/", status_code=201)
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


@router.get("/", summary="Все хостелы")
def list_hostels(db: Session = Depends(get_db)):
    return db.query(Hostel).order_by(Hostel.created_at.desc()).all()


@router.get("/my", summary="Мои хостелы")
def my_hostels(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Hostel).filter(Hostel.user_id == user.id).all()


@router.delete("/{hostel_id}")
def delete_hostel(hostel_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    hostel = db.query(Hostel).filter(Hostel.id == hostel_id).first()

    if not hostel:
        raise HTTPException(404, "Hostel not found")

    if hostel.user_id != user.id:
        raise HTTPException(403, "Forbidden")

    db.delete(hostel)
    db.commit()

    return {"status": "deleted"}


