from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.core.security import get_current_user
from app.schemas.tag import TagCreate, TagResponse, TagListResponse
from app.services.tag_service import add_tag, remove_tag, get_tags

router = APIRouter()


@router.get("/{video_id}/tags", response_model=TagListResponse)
def list_tags(video_id: int, db: Session = Depends(get_db)):
    return get_tags(db, video_id)


@router.post("/{video_id}/tags", response_model=TagResponse)
def create_tag(
    video_id: int,
    body: TagCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    return add_tag(db, video_id, user_id, body.name)


@router.delete("/{video_id}/tags/{tag_id}")
def delete_tag(
    video_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    remove_tag(db, video_id, tag_id, user_id)
    return {"message": "태그 삭제 완료"}
