from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.core.security import get_current_user
from app.schemas.comment import CommentCreate, CommentResponse, CommentListResponse
from app.services.comment_service import list_comments, create_comment, delete_comment, verify_party

router = APIRouter()


@router.get("/{video_id}/comments", response_model=CommentListResponse)
def read_comments(video_id: int, db: Session = Depends(get_db)):
    return list_comments(db, video_id)


@router.post("/{video_id}/comments", response_model=CommentResponse)
def write_comment(
    video_id: int,
    body: CommentCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    return create_comment(db, video_id, user_id, body.content, body.is_party, body.party_role)


@router.delete("/comments/{comment_id}", status_code=204)
def remove_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    delete_comment(db, comment_id, user_id)


@router.post("/{video_id}/comments/{comment_id}/verify-party", response_model=CommentResponse)
def verify_party_comment(
    video_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    return verify_party(db, comment_id, video_id, user_id)
