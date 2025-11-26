from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.db import engine
from app.models import Base

from app.author import router as auth_router
from app.gidadd import router as places_router

app = FastAPI(title="Almagid API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(places_router)

