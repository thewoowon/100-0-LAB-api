from pydantic import BaseModel
from datetime import datetime


class TagCreate(BaseModel):
    name: str


class TagResponse(BaseModel):
    id: int
    video_id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class TagListResponse(BaseModel):
    tags: list[TagResponse]
