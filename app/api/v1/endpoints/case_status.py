from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.core.security import get_current_user
from app.schemas.case_status import CaseStatusUpdate, CaseStatusResponse
from app.services.case_status_service import get_case_status, update_case_status

router = APIRouter()


@router.get("/{video_id}/case-status", response_model=CaseStatusResponse)
def read_case_status(video_id: int, db: Session = Depends(get_db)):
    return get_case_status(db, video_id)


@router.put("/{video_id}/case-status", response_model=CaseStatusResponse)
def write_case_status(
    video_id: int,
    body: CaseStatusUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    return update_case_status(db, video_id, user_id, body.status, body.actual_ratio, body.resolution_note)
