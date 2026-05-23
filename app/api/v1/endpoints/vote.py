from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.core.security import get_current_user
from app.schemas.vote import VoteCreate, VoteResult, MyVote
from app.services.vote_service import cast_vote, get_vote_result, get_my_vote

router = APIRouter()


@router.post("/{video_id}/votes", response_model=VoteResult)
def vote(
    video_id: int,
    body: VoteCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    cast_vote(db, video_id, user_id, body.ratio)
    return get_vote_result(db, video_id)


@router.get("/{video_id}/votes", response_model=VoteResult)
def vote_result(video_id: int, db: Session = Depends(get_db)):
    return get_vote_result(db, video_id)


@router.get("/{video_id}/votes/me", response_model=MyVote)
def my_vote(
    video_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    return get_my_vote(db, video_id, user_id)
