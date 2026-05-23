from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CommentCreate(BaseModel):
    content: str
    is_party: bool = False
    party_role: Optional[str] = None  # "가해자" / "피해자" / "목격자"


class CommentResponse(BaseModel):
    id: int
    video_id: int
    user_id: int
    content: str
    is_party: bool
    party_role: Optional[str]
    party_verified: bool
    created_at: datetime
    nickname: Optional[str] = None
    profile_image: Optional[str] = None

    class Config:
        from_attributes = True


class CommentListResponse(BaseModel):
    comments: list[CommentResponse]
    total: int
