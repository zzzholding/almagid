# app/places.py

import os
import time
import pathlib
from datetime import datetime, timezone
from collections.abc import Generator

from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Text,
    func,
)
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# ---------- Конфиг ----------
SQLALCHEMY_DATABASE_URL = (
    "postgresql+psycopg2://my_user:root@localhost:5438/my_db"
)

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------- БД ----------
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)        # Название места
    location = Column(String(255), nullable=False)    # Область / город
    image_url = Column(String(500))                   # /static/uploads/...
    price_text = Column(String(255))                  # Цена текстом
    rating = Column(Integer, nullable=False)          # 1..5
    description = Column(Text)                        # Описание
    created_at = Column(DateTime(timezone=True), server_default=func.now())


Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- Pydantic-схемы ----------
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


# ---------- Приложение ----------
app = FastAPI(title="AlmaGid Places API")

# статика: /static/...
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # чтобы HTML с 127.0.0.1:5500 мог ходить к API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "message": "AlmaGid Places API"}


# ---------- Добавление места ----------
@app.post("/places", response_model=PlaceOut, status_code=201)
async def create_place(
    name: str = Form(...),
    location: str = Form(...),
    price_text: str | None = Form(None),
    rating: int = Form(...),
    description: str | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    image_url: str | None = None

    if image and image.filename:
        ext = pathlib.Path(image.filename).suffix or ".jpg"
        filename = f"{int(time.time())}_{os.urandom(4).hex()}{ext}"
        save_path = os.path.join(UPLOAD_DIR, filename)

        with open(save_path, "wb") as f:
            f.write(await image.read())

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


# ---------- Список мест ----------
@app.get("/places", response_model=list[PlaceOut])
def list_places(db: Session = Depends(get_db)):
    places = db.query(Place).order_by(Place.created_at.desc()).all()
    return places


