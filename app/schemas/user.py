from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: str
    nickname: Optional[str] = None
    profile_image: Optional[str] = None
    user_type: int = 0


class UserResponse(BaseModel):
    id: int
    email: str
    nickname: Optional[str] = None
    profile_image: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
