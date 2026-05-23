from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse
from app.services.video_service import get_user_videos
from app.schemas.video import VideoFeedItem

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_me(current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    from fastapi import HTTPException
    user = db.query(User).filter(User.id == int(current_user_id), User.is_deleted == 0).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    return user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id, User.is_deleted == 0).first()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    return user


@router.get("/{user_id}/videos", response_model=list[VideoFeedItem])
def user_videos(user_id: int, db: Session = Depends(get_db)):
    return get_user_videos(user_id, db)
