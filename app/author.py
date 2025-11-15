import os
from datetime import datetime, timedelta, timezone
from collections.abc import Generator

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from jose import jwt
from passlib.context import CryptContext

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    func,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# ---------- Конфиг ----------
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://my_user:root@localhost:5438/my_db"

JWT_SECRET = "change_me_secret_key"
JWT_ALG = "HS256"
JWT_TTL_MIN = 60 * 24  # 24 часа

# ---------- БД ----------
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email"), UniqueConstraint("phone"),)

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(32), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- Схемы ----------
class RegisterRequest(BaseModel):
    full_name: str
    phone: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Безопасность ----------
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
) 


def hash_password(p: str) -> str:
    return pwd_context.hash(p)


def verify_password(p: str, h: str) -> bool:
    return pwd_context.verify(p, h)


def create_access_token(sub: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=JWT_TTL_MIN)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

# ---------- Приложение ----------
app = FastAPI(title="AlmaGid API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Технический пинг ----------
@app.get("/ping-db")
def ping_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"ok": True}

# ---------- Регистрация ----------
@app.post("/auth/register", status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    # проверяем уникальность
    if db.query(User).filter(User.email == payload.email.lower()).first():
        raise HTTPException(400, detail="Email уже зарегистрирован")
    if db.query(User).filter(User.phone == payload.phone).first():
        raise HTTPException(400, detail="Телефон уже зарегистрирован")

    user = User(
        full_name=payload.full_name.strip(),
        phone=payload.phone.strip(),
        email=str(payload.email).lower(),
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
    }

# ---------- Логин ----------
@app.post("/auth/login", response_model=TokenOut)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
        )
    token = create_access_token(str(user.id))
    return {"access_token": token, "token_type": "bearer"}


# python -m uvicorn app.author:app --reload
