from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(32), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    avatar_url = Column(String, nullable=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 🔥 чтобы фронт мог читать user.name
    @property
    def name(self):
        return self.full_name

    @name.setter
    def name(self, value):
        self.full_name = value


class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    image_url = Column(String(500))     # просто 1 картинка
    price_text = Column(String(255))
    rating = Column(Integer, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

class Hostel(Base):
    __tablename__ = "hostels"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    image_url = Column(String(500))
    price_text = Column(String(255))
    rating = Column(Integer, nullable=False)
    description = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)




    
    


