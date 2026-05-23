from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SearchResultItem(BaseModel):
    id: int
    user_id: int
    title: str
    thumbnail_url: Optional[str]
    views: int
    created_at: datetime
    score: float

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultItem]
