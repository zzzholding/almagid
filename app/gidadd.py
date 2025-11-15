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