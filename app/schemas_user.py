from pydantic import BaseModel

class UserOut(BaseModel):
    id: int
    full_name: str | None
    email: str
    phone: str | None
    avatar_url: str | None

    class Config:
        from_attributes = True
