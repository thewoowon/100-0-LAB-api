from sqlalchemy.orm import Session
from app.models.vote import Vote
from app.schemas.vote import VoteResult, VoteOption, MyVote

VALID_RATIOS = ["100:0", "90:10", "80:20", "70:30", "60:40", "50:50"]


def cast_vote(db: Session, video_id: int, user_id: int, ratio: str) -> Vote:
    vote = db.query(Vote).filter(Vote.video_id == video_id, Vote.user_id == user_id).first()
    if vote:
        vote.ratio = ratio
    else:
        vote = Vote(video_id=video_id, user_id=user_id, ratio=ratio)
        db.add(vote)
    db.commit()
    db.refresh(vote)
    return vote


def get_vote_result(db: Session, video_id: int) -> VoteResult:
    votes = db.query(Vote).filter(Vote.video_id == video_id).all()
    total = len(votes)

    count_map: dict[str, int] = {r: 0 for r in VALID_RATIOS}
    for vote in votes:
        if vote.ratio in count_map:
            count_map[vote.ratio] += 1

    options = [
        VoteOption(
            ratio=ratio,
            count=count,
            percentage=round(count / total * 100, 1) if total > 0 else 0.0,
        )
        for ratio, count in count_map.items()
    ]

    return VoteResult(total=total, options=options)


def get_my_vote(db: Session, video_id: int, user_id: int) -> MyVote:
    vote = db.query(Vote).filter(Vote.video_id == video_id, Vote.user_id == user_id).first()
    return MyVote(ratio=vote.ratio if vote else None)
