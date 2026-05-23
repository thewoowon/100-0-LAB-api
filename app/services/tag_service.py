from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.tag import Tag
from app.models.video import Video
from app.schemas.tag import TagListResponse


def add_tag(db: Session, video_id: int, user_id: int, name: str) -> Tag:
    existing = db.query(Tag).filter(Tag.video_id == video_id, Tag.name == name).first()
    if existing:
        return existing
    tag = Tag(video_id=video_id, name=name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def remove_tag(db: Session, video_id: int, tag_id: int, user_id: int) -> None:
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="영상을 찾을 수 없습니다")
    if video.user_id != user_id:
        raise HTTPException(status_code=403, detail="업로더만 태그를 삭제할 수 있습니다")

    tag = db.query(Tag).filter(Tag.id == tag_id, Tag.video_id == video_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="태그를 찾을 수 없습니다")

    db.delete(tag)
    db.commit()


def get_tags(db: Session, video_id: int) -> TagListResponse:
    tags = db.query(Tag).filter(Tag.video_id == video_id).all()
    return TagListResponse(tags=tags)
