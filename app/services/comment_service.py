from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.comment import Comment
from app.models.video import Video
from app.schemas.comment import CommentResponse, CommentListResponse

VALID_PARTY_ROLES = {"가해자", "피해자", "목격자"}


def _to_response(c: Comment) -> CommentResponse:
    return CommentResponse(
        id=c.id,
        video_id=c.video_id,
        user_id=c.user_id,
        content=c.content,
        is_party=c.is_party,
        party_role=c.party_role,
        party_verified=c.party_verified,
        created_at=c.created_at,
        nickname=c.user.nickname if c.user else None,
        profile_image=c.user.profile_image if c.user else None,
    )


def list_comments(db: Session, video_id: int) -> CommentListResponse:
    comments = (
        db.query(Comment)
        .filter(Comment.video_id == video_id)
        .order_by(Comment.created_at.asc())
        .all()
    )
    return CommentListResponse(
        comments=[_to_response(c) for c in comments],
        total=len(comments),
    )


def create_comment(
    db: Session,
    video_id: int,
    user_id: int,
    content: str,
    is_party: bool = False,
    party_role: str | None = None,
) -> CommentResponse:
    if not db.query(Video).filter(Video.id == video_id).first():
        raise HTTPException(status_code=404, detail="영상을 찾을 수 없습니다")
    if not content.strip():
        raise HTTPException(status_code=400, detail="댓글 내용을 입력해주세요")
    if is_party and party_role not in VALID_PARTY_ROLES:
        raise HTTPException(status_code=400, detail=f"party_role은 {', '.join(VALID_PARTY_ROLES)} 중 하나여야 합니다")

    comment = Comment(
        video_id=video_id,
        user_id=user_id,
        content=content.strip(),
        is_party=is_party,
        party_role=party_role if is_party else None,
        party_verified=False,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return _to_response(comment)


def delete_comment(db: Session, comment_id: int, user_id: int) -> None:
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다")
    # 본인 댓글 또는 영상 업로더만 삭제 가능
    video = db.query(Video).filter(Video.id == comment.video_id).first()
    if comment.user_id != user_id and (not video or video.user_id != user_id):
        raise HTTPException(status_code=403, detail="삭제 권한이 없습니다")
    db.delete(comment)
    db.commit()


def verify_party(db: Session, comment_id: int, video_id: int, uploader_id: int) -> CommentResponse:
    """업로더가 당사자 댓글을 인증"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video.user_id != uploader_id:
        raise HTTPException(status_code=403, detail="업로더만 당사자를 인증할 수 있습니다")
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.video_id == video_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다")
    if not comment.is_party:
        raise HTTPException(status_code=400, detail="당사자 댓글이 아닙니다")
    comment.party_verified = True
    db.commit()
    db.refresh(comment)
    return _to_response(comment)
