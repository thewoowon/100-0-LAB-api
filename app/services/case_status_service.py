from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.case_status import CaseStatus
from app.models.video import Video
from app.schemas.case_status import CaseStatusResponse
from datetime import datetime


def get_case_status(db: Session, video_id: int) -> CaseStatusResponse:
    case = db.query(CaseStatus).filter(CaseStatus.video_id == video_id).first()
    if not case:
        return CaseStatusResponse(
            video_id=video_id,
            status="알_수_없음",
            updated_at=datetime.utcnow(),
        )
    return case


def update_case_status(
    db: Session,
    video_id: int,
    user_id: int,
    status: str,
    actual_ratio: str | None = None,
    resolution_note: str | None = None,
) -> CaseStatusResponse:
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="영상을 찾을 수 없습니다")
    if video.user_id != user_id:
        raise HTTPException(status_code=403, detail="업로더만 사건 상태를 변경할 수 있습니다")

    case = db.query(CaseStatus).filter(CaseStatus.video_id == video_id).first()
    if case:
        case.status = status
        case.updated_by = user_id
        if actual_ratio is not None:
            case.actual_ratio = actual_ratio
        if resolution_note is not None:
            case.resolution_note = resolution_note
    else:
        case = CaseStatus(
            video_id=video_id,
            status=status,
            updated_by=user_id,
            actual_ratio=actual_ratio,
            resolution_note=resolution_note,
        )
        db.add(case)

    db.commit()
    db.refresh(case)
    return case
