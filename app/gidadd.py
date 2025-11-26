import os
import time
import pathlib
from typing import Generator

from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session

from pydantic import BaseModel
from app.db import get_db
from app.models import Place


router = APIRouter(prefix="/places", tags=["places"])

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class PlaceOut(BaseModel):
    id: int
    name: str
    location: str
    image_url: str | None
    price_text: str | None
    rating: int
    description: str | None

    class Config:
        from_attributes = True


@router.post("/", response_model=PlaceOut, status_code=201)
async def create_place(
    name: str = Form(...),
    location: str = Form(...),
    price_text: str | None = Form(None),
    rating: int = Form(...),
    description: str | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    image_url = None

    if image and image.filename:
        ext = pathlib.Path(image.filename).suffix or ".jpg"
        filename = f"{int(time.time())}_{os.urandom(4).hex()}{ext}"
        save_path = UPLOAD_DIR / filename
        contents = await image.read()

        with open(save_path, "wb") as f:
            f.write(contents)

        image_url = f"/static/uploads/{filename}"

    place = Place(
        name=name.strip(),
        location=location.strip(),
        image_url=image_url,
        price_text=price_text.strip() if price_text else None,
        rating=rating,
        description=description.strip() if description else None,
    )

    db.add(place)
    db.commit()
    db.refresh(place)

    return place


@router.get("/", response_model=list[PlaceOut])
def list_places(db: Session = Depends(get_db)):
    return db.query(Place).order_by(Place.created_at.desc()).all()





