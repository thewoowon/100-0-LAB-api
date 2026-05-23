from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.video import Video
from app.models.video_embedding import VideoEmbedding
import app.services.embedding_service as embedding_service


PAGE_SIZE = 20


def get_feed(db: Session, cursor: int | None = None) -> dict:
    query = db.query(Video).order_by(Video.id.desc())
    if cursor:
        query = query.filter(Video.id < cursor)
    videos = query.limit(PAGE_SIZE + 1).all()

    has_more = len(videos) > PAGE_SIZE
    if has_more:
        videos = videos[:PAGE_SIZE]

    next_cursor = videos[-1].id if has_more and videos else None
    return {"videos": videos, "next_cursor": next_cursor, "has_more": has_more}


def get_video(video_id: int, db: Session) -> Video:
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="영상을 찾을 수 없습니다")
    video.views += 1
    db.commit()
    db.refresh(video)
    return video


def get_user_videos(user_id: int, db: Session) -> list[Video]:
    return db.query(Video).filter(Video.user_id == user_id).order_by(Video.id.desc()).all()


def create_video(
    db: Session,
    user_id: int,
    title: str,
    description: str | None,
    video_url: str,
    thumbnail_url: str | None,
    filmed_date=None,
    filmed_location: str | None = None,
) -> Video:
    video = Video(
        user_id=user_id,
        title=title,
        description=description,
        video_url=video_url,
        thumbnail_url=thumbnail_url,
        filmed_date=filmed_date,
        filmed_location=filmed_location,
    )
    db.add(video)
    db.commit()
    db.refresh(video)

    try:
        embedding_service.index_video(video.id, db)
    except Exception as e:
        print(f"[video_service] embedding index_video failed for video_id={video.id}: {e}")

    return video


def get_top_videos(db: Session, limit: int = 10) -> list[Video]:
    return db.query(Video).order_by(Video.views.desc()).limit(limit).all()


def get_controversial_videos(db: Session, limit: int = 10) -> list[Video]:
    from app.models.vote import Vote
    from sqlalchemy import func, case, Float
    from sqlalchemy.sql.expression import cast
    # 100:0 또는 0:100 투표가 많을수록 명확, 50:50에 가까울수록 논란
    # ratio별 투표 수 집계 후 비율 계산
    subq = (
        db.query(
            Vote.video_id,
            func.count(Vote.id).label("total"),
            func.sum(case((Vote.ratio == "50:50", 1), else_=0)).label("fifty"),
        )
        .group_by(Vote.video_id)
        .subquery()
    )
    rows = (
        db.query(Video, subq.c.total, subq.c.fifty)
        .join(subq, Video.id == subq.c.video_id)
        .filter(subq.c.total >= 3)
        .all()
    )
    # 50:50 비율이 높을수록 앞에
    rows.sort(key=lambda r: r[2] / r[1] if r[1] else 0, reverse=True)
    return [r[0] for r in rows[:limit]]


def get_related_videos(video_id: int, db: Session, limit: int = 4) -> list[Video]:
    from app.services.embedding_service import _cache, embed_text
    from app.models.video_embedding import VideoEmbedding
    import numpy as np

    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video_id not in _cache:
        # fallback: 같은 날짜 또는 최신순
        return db.query(Video).filter(Video.id != video_id).order_by(Video.views.desc()).limit(limit).all()

    target_vec = _cache[video_id]
    scores = []
    for vid, vec in _cache.items():
        if vid == video_id:
            continue
        score = float(np.dot(target_vec, vec) / (np.linalg.norm(target_vec) * np.linalg.norm(vec) + 1e-8))
        scores.append((vid, score))
    scores.sort(key=lambda x: x[1], reverse=True)
    top_ids = [s[0] for s in scores[:limit]]
    videos = db.query(Video).filter(Video.id.in_(top_ids)).all()
    # 점수 순 정렬
    id_order = {vid: i for i, vid in enumerate(top_ids)}
    return sorted(videos, key=lambda v: id_order.get(v.id, 999))


def delete_video(video_id: int, user_id: int, db: Session):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="영상을 찾을 수 없습니다")
    if video.user_id != user_id:
        raise HTTPException(status_code=403, detail="권한이 없습니다")

    existing_emb = db.query(VideoEmbedding).filter(VideoEmbedding.video_id == video_id).first()
    if existing_emb:
        db.delete(existing_emb)

    embedding_service.remove_from_cache(video_id)

    db.delete(video)
    db.commit()
