from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class VideoResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str] = None
    video_url: str
    thumbnail_url: Optional[str] = None
    views: int
    filmed_date: Optional[date] = None
    filmed_location: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class VideoFeedItem(BaseModel):
    id: int
    user_id: int
    title: str
    thumbnail_url: Optional[str] = None
    views: int
    created_at: datetime

    class Config:
        from_attributes = True


class VideoFeedResponse(BaseModel):
    videos: list[VideoFeedItem]
    next_cursor: Optional[int] = None
    has_more: bool


class VideoLocationResponse(BaseModel):
    id: int
    title: str
    filmed_location: Optional[str]
    lat: Optional[float]
    lng: Optional[float]
    thumbnail_url: Optional[str]
    views: int
