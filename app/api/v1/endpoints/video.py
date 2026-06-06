import os
import uuid
import subprocess
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.core.security import get_current_user
from app.services.video_service import get_feed, get_video, get_user_videos, create_video, delete_video, get_top_videos, get_controversial_videos, get_related_videos
from app.schemas.video import VideoResponse, VideoFeedResponse, VideoLocationResponse
from app.schemas.search import SearchResponse, SearchResultItem
from settings import UPLOAD_DIR, THUMBNAIL_DIR

router = APIRouter()

ALLOWED_EXTENSIONS = {"mp4", "mov"}


def _ext(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def _save_upload(file: UploadFile, directory: str) -> str:
    os.makedirs(directory, exist_ok=True)
    ext = _ext(file.filename or "")
    filename = f"{uuid.uuid4()}.{ext}"
    path = os.path.join(directory, filename)
    with open(path, "wb") as f:
        f.write(file.file.read())
    return path


def _extract_thumbnail(video_path: str) -> str | None:
    os.makedirs(THUMBNAIL_DIR, exist_ok=True)
    thumbnail_filename = f"{uuid.uuid4()}.jpg"
    thumbnail_path = os.path.join(THUMBNAIL_DIR, thumbnail_filename)
    try:
        result = subprocess.run(
            [
                "ffmpeg", "-i", video_path,
                "-ss", "00:00:01",
                "-vframes", "1",
                "-q:v", "2",
                thumbnail_path,
            ],
            capture_output=True,
            timeout=30,
        )
        if result.returncode == 0 and os.path.exists(thumbnail_path):
            return thumbnail_path
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


@router.get("/feed", response_model=VideoFeedResponse)
def feed(cursor: Optional[int] = None, db: Session = Depends(get_db)):
    return get_feed(db, cursor)


@router.get("/search", response_model=SearchResponse)
def search_videos_endpoint(q: str, top_k: int = 10, db: Session = Depends(get_db)):
    from app.services.embedding_service import search_videos
    raw_results = search_videos(q, db, top_k)
    items = [SearchResultItem(**r) for r in raw_results]
    return SearchResponse(query=q, results=items)


@router.get("/locations", response_model=list[VideoLocationResponse])
def video_locations(db: Session = Depends(get_db)):
    from app.models.video import Video
    videos = db.query(Video).all()
    return [
        VideoLocationResponse(
            id=v.id,
            title=v.title,
            filmed_location=v.filmed_location,
            lat=v.lat,
            lng=v.lng,
            thumbnail_url=v.thumbnail_url,
            views=v.views,
        )
        for v in videos
    ]


@router.get("/top", response_model=list[VideoResponse])
def top_videos(limit: int = 10, db: Session = Depends(get_db)):
    return get_top_videos(db, limit)


@router.get("/controversial", response_model=list[VideoResponse])
def controversial_videos(limit: int = 10, db: Session = Depends(get_db)):
    return get_controversial_videos(db, limit)


@router.get("/{video_id}/related", response_model=list[VideoResponse])
def related_videos(video_id: int, db: Session = Depends(get_db)):
    return get_related_videos(video_id, db)


@router.get("/{video_id}", response_model=VideoResponse)
def video_detail(video_id: int, db: Session = Depends(get_db)):
    return get_video(video_id, db)


@router.post("/upload", response_model=VideoResponse)
def upload(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    filmed_date: Optional[date] = Form(None),
    filmed_location: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    ext = _ext(file.filename or "")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="mp4 또는 mov 파일만 업로드 가능합니다")

    video_path = _save_upload(file, UPLOAD_DIR)
    thumbnail_path = _extract_thumbnail(video_path)

    video = create_video(
        db=db,
        user_id=user_id,
        title=title,
        description=description,
        video_url=video_path,
        thumbnail_url=thumbnail_path,
        filmed_date=filmed_date,
        filmed_location=filmed_location,
    )
    return video


@router.delete("/{video_id}")
def remove_video(video_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    delete_video(video_id, user_id, db)
    return {"message": "삭제 완료"}
