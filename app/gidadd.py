import os
import time
import pathlib
import json

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db import get_db
from app.models import Place
from app.author import get_current_user
from app.redis_client import redis_client   # <─ добавили Redis

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


CACHE_KEY_ALL = "places:list"   # ключ кэша для /places


@router.post("/", response_model=PlaceOut, status_code=201)
async def create_place(
    name: str = Form(...),
    location: str = Form(...),
    price_text: str | None = Form(None),
    rating: int = Form(...),
    description: str | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    image_url = None

    if image and image.filename:
        ext = pathlib.Path(image.filename).suffix
        filename = f"{int(time.time())}_{os.urandom(4).hex()}{ext}"
        save_path = UPLOAD_DIR / filename

        with open(save_path, "wb") as f:
            f.write(await image.read())

        image_url = f"/static/uploads/{filename}"

    place = Place(
        name=name.strip(),
        location=location.strip(),
        price_text=price_text,
        rating=rating,
        description=description,
        image_url=image_url,
        user_id=user.id,
    )

    db.add(place)
    db.commit()
    db.refresh(place)

    # инвалидируем кэш списка
    redis_client.delete(CACHE_KEY_ALL)

    return place


@router.get("/", response_model=list[PlaceOut])
def list_places(db: Session = Depends(get_db)):
    """
    GET /places — теперь с кэшем Redis:
    1) сначала пробуем прочитать из Redis
    2) если нет — читаем из БД, кладём в кэш на 60 секунд
    """
    cached = redis_client.get(CACHE_KEY_ALL)
    if cached:
        # в кэше уже готовый list[dict]
        return json.loads(cached)

    places = db.query(Place).order_by(Place.created_at.desc()).all()
    data = [PlaceOut.model_validate(p).model_dump() for p in places]

    # кладём в Redis на 60 секунд
    redis_client.setex(CACHE_KEY_ALL, 60, json.dumps(data))

    return data


@router.get("/my", response_model=list[PlaceOut])
def get_my_places(
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    return db.query(Place).filter(Place.user_id == user.id).all()


@router.delete("/{place_id}")
def delete_place(
    place_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    place = db.query(Place).filter(Place.id == place_id).first()

    if not place:
        raise HTTPException(404, "Place not found")

    if place.user_id != user.id:
        raise HTTPException(403, "Forbidden")

    db.delete(place)
    db.commit()

    # инвалидируем кэш списка
    redis_client.delete(CACHE_KEY_ALL)

    return {"status": "deleted"}

@router.put("/{place_id}", response_model=PlaceOut)
async def update_place(
    place_id: int,
    name: str = Form(...),
    location: str = Form(...),
    price_text: str | None = Form(None),
    rating: int = Form(...),
    description: str | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    place = db.query(Place).filter(Place.id == place_id).first()

    if not place:
        raise HTTPException(404, "Place not found")

    if place.user_id != user.id:
        raise HTTPException(403, "Forbidden")

    # обновить обычные поля
    place.name = name.strip()
    place.location = location.strip()
    place.price_text = price_text
    place.rating = rating
    place.description = description

    # если загружено новое изображение
    if image and image.filename:
        ext = pathlib.Path(image.filename).suffix
        filename = f"{int(time.time())}_{os.urandom(4).hex()}{ext}"
        save_path = UPLOAD_DIR / filename

        with open(save_path, "wb") as f:
            f.write(await image.read())

        place.image_url = f"/static/uploads/{filename}"

    db.commit()
    db.refresh(place)

    # чистим кэш
    redis_client.delete(CACHE_KEY_ALL)

    return place
