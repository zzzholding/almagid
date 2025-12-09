from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db import get_db
from app.author import get_current_user, hash_password, verify_password
from app.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


@router.post("/change_password")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    # ------- ГЛАВНОЕ ИСПРАВЛЕНИЕ --------
    old_ok = False
    try:
        old_ok = verify_password(data.old_password, user.password_hash)
    except:
        # старый hash неизвестного формата
        old_ok = False

    if not old_ok:
        raise HTTPException(400, "Старый пароль неверный")

    # ------- Обновляем пароль --------
    user.password_hash = hash_password(data.new_password)
    db.commit()
    db.refresh(user)

    return {"message": "Пароль успешно изменён"}
