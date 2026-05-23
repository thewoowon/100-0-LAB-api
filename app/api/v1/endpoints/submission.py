from fastapi import APIRouter, Depends, UploadFile, File, Form, Request, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.dependencies import get_db, get_current_user_obj, require_admin
from app.models.user import User
from app.schemas.submission import (
    SubmissionResponse, SubmissionDetail, AdminSubmissionDetail,
    AdminReviewRequest, PayoutResponse, MarkPaidRequest,
)
from app.services import submission_service
from app.models.payout import Payout

router = APIRouter()


@router.post("", response_model=SubmissionResponse)
async def create_submission(
    request: Request,
    title: Optional[str] = Form(None),
    description: str = Form(...),
    incident_type: str = Form(...),
    region_sido: str = Form(...),
    region_sigungu: Optional[str] = Form(None),
    approximate_address: Optional[str] = Form(None),
    original_lat: Optional[float] = Form(None),
    original_lng: Optional[float] = Form(None),
    bank_name: str = Form(...),
    account_number: str = Form(...),
    account_holder: str = Form(...),
    is_original_owner: bool = Form(...),
    is_rights_holder: bool = Form(...),
    commercial_use_agreed: bool = Form(...),
    edit_and_blur_agreed: bool = Form(...),
    warranty_agreed: bool = Form(...),
    privacy_policy_agreed: bool = Form(...),
    reward_policy_confirmed: bool = Form(...),
    video_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db),
):
    from app.schemas.submission import SubmissionCreate
    data = SubmissionCreate(
        title=title,
        description=description,
        incident_type=incident_type,
        region_sido=region_sido,
        region_sigungu=region_sigungu,
        approximate_address=approximate_address,
        original_lat=original_lat,
        original_lng=original_lng,
        bank_name=bank_name,
        account_number=account_number,
        account_holder=account_holder,
        is_original_owner=is_original_owner,
        is_rights_holder=is_rights_holder,
        commercial_use_agreed=commercial_use_agreed,
        edit_and_blur_agreed=edit_and_blur_agreed,
        warranty_agreed=warranty_agreed,
        privacy_policy_agreed=privacy_policy_agreed,
        reward_policy_confirmed=reward_policy_confirmed,
    )
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")
    return submission_service.create_submission(db, current_user.id, data, video_file, ip, ua)


@router.get("/my", response_model=list[SubmissionResponse])
def my_submissions(
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db),
):
    return submission_service.get_my_submissions(db, current_user.id)


@router.get("/admin", response_model=list[AdminSubmissionDetail])
def admin_list(
    status: Optional[str] = None,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return submission_service.get_admin_submissions(db, status)


@router.get("/admin/{submission_id}", response_model=AdminSubmissionDetail)
def admin_detail(
    submission_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    from app.models.video_submission import VideoSubmission
    sub = db.query(VideoSubmission).filter(VideoSubmission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Not found")
    return sub


@router.post("/admin/{submission_id}/review", response_model=SubmissionResponse)
def admin_review(
    submission_id: int,
    data: AdminReviewRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    result = submission_service.admin_review(db, submission_id, admin.id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@router.get("/admin/payouts", response_model=list[PayoutResponse])
def admin_payouts(
    status: Optional[str] = None,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    q = db.query(Payout)
    if status:
        q = q.filter(Payout.status == status)
    return q.order_by(Payout.id.desc()).all()


@router.post("/admin/payouts/{payout_id}/mark-paid", response_model=PayoutResponse)
def mark_payout_paid(
    payout_id: int,
    data: MarkPaidRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    result = submission_service.mark_payout_paid(db, payout_id, admin.id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result
