import math
import random
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.models.video_submission import VideoSubmission, SubmissionStatus
from app.models.content_agreement import ContentAgreement
from app.models.payout_account import PayoutAccount
from app.models.payout import Payout, PayoutStatus
from app.models.admin_review import AdminReview, ReviewDecision
from app.models.audit_log import AuditLog
from app.schemas.submission import SubmissionCreate, AdminReviewRequest, MarkPaidRequest
from app.services import r2_service
from app.services import email_service
from app.models.user import User


PAYOUT_AMOUNT = 5000
NOISE_RADIUS_METERS = 300


def _add_coordinate_noise(lat: float, lng: float, radius_m: float = NOISE_RADIUS_METERS):
    r = radius_m / 111300
    u, v = random.random(), random.random()
    w = r * math.sqrt(u)
    t = 2 * math.pi * v
    noisy_lat = lat + w * math.cos(t)
    noisy_lng = lng + (w * math.sin(t)) / math.cos(lat * (math.pi / 180))
    return noisy_lat, noisy_lng


def _mask_account_number(account_number: str) -> str:
    if len(account_number) <= 4:
        return "****"
    return account_number[:2] + "*" * (len(account_number) - 4) + account_number[-2:]


def _generate_submission_no(db: Session) -> str:
    year = datetime.now().year
    count = db.query(VideoSubmission).count() + 1
    return f"BB-{year}-{count:06d}"


def _log(db: Session, actor_type: str, actor_id: int, action: str, target_type: str, target_id: str,
         before=None, after=None, ip: str = None, ua: str = None):
    db.add(AuditLog(
        actor_type=actor_type,
        actor_id=actor_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        before=before,
        after=after,
        ip_address=ip,
        user_agent=ua,
    ))


def create_submission(
    db: Session,
    user_id: int,
    data: SubmissionCreate,
    video_file: UploadFile,
    ip: str = None,
    user_agent: str = None,
) -> VideoSubmission:
    file_bytes = video_file.file.read()
    file_hash = r2_service.compute_file_hash(file_bytes)
    storage_key = f"submissions/{user_id}/{uuid.uuid4()}/{video_file.filename}"
    r2_service.upload_file(file_bytes, storage_key, video_file.content_type or "video/mp4")

    noisy_lat, noisy_lng = None, None
    if data.original_lat and data.original_lng:
        noisy_lat, noisy_lng = _add_coordinate_noise(data.original_lat, data.original_lng)

    payout_account = PayoutAccount(
        user_id=user_id,
        bank_name=data.bank_name,
        account_number_encrypted=data.account_number,  # TODO: 실제 암호화 적용
        account_number_masked=_mask_account_number(data.account_number),
        account_holder=data.account_holder,
    )
    db.add(payout_account)
    db.flush()

    submission = VideoSubmission(
        submission_no=_generate_submission_no(db),
        user_id=user_id,
        title=data.title,
        description=data.description,
        incident_type=data.incident_type,
        original_storage_key=storage_key,
        original_file_hash=file_hash,
        file_size_bytes=len(file_bytes),
        mime_type=video_file.content_type,
        region_sido=data.region_sido,
        region_sigungu=data.region_sigungu,
        approximate_address=data.approximate_address,
        original_lat=data.original_lat,
        original_lng=data.original_lng,
        noisy_lat=noisy_lat,
        noisy_lng=noisy_lng,
        status=SubmissionStatus.PENDING_REVIEW,
    )
    db.add(submission)
    db.flush()

    agreement = ContentAgreement(
        submission_id=submission.id,
        user_id=user_id,
        is_original_owner=data.is_original_owner,
        is_rights_holder=data.is_rights_holder,
        commercial_use_agreed=data.commercial_use_agreed,
        edit_and_blur_agreed=data.edit_and_blur_agreed,
        warranty_agreed=data.warranty_agreed,
        privacy_policy_agreed=data.privacy_policy_agreed,
        reward_policy_confirmed=data.reward_policy_confirmed,
        ip_address=ip,
        user_agent=user_agent,
        file_hash_at_agreement=file_hash,
    )
    db.add(agreement)

    _log(db, "USER", user_id, "SUBMIT", "VideoSubmission", str(submission.id),
         after={"status": "PENDING_REVIEW"}, ip=ip, ua=user_agent)

    db.commit()
    db.refresh(submission)

    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.email:
            email_service.send_submission_confirmation(
                to_email=user.email,
                submission_no=submission.submission_no,
                incident_type=submission.incident_type,
                region_sido=submission.region_sido,
                bank_name=payout_account.bank_name,
                account_number_masked=payout_account.account_number_masked,
                account_holder=payout_account.account_holder,
            )
    except Exception:
        pass  # 이메일 실패가 제출 성공을 막으면 안 됨

    return submission


def get_my_submissions(db: Session, user_id: int) -> list[VideoSubmission]:
    return db.query(VideoSubmission).filter(
        VideoSubmission.user_id == user_id
    ).order_by(VideoSubmission.id.desc()).all()


def get_admin_submissions(db: Session, status: str = None) -> list[VideoSubmission]:
    q = db.query(VideoSubmission)
    if status:
        q = q.filter(VideoSubmission.status == status)
    return q.order_by(VideoSubmission.id.desc()).all()


def admin_review(db: Session, submission_id: int, admin_id: int, data: AdminReviewRequest) -> VideoSubmission:
    submission = db.query(VideoSubmission).filter(VideoSubmission.id == submission_id).first()
    if not submission:
        return None

    decision = ReviewDecision(data.decision)
    before_status = submission.status.value

    if decision == ReviewDecision.APPROVE:
        submission.status = SubmissionStatus.APPROVED
        payout_account = db.query(PayoutAccount).filter(PayoutAccount.user_id == submission.user_id).order_by(PayoutAccount.id.desc()).first()
        payout = Payout(
            submission_id=submission.id,
            user_id=submission.user_id,
            payout_account_id=payout_account.id,
            amount=PAYOUT_AMOUNT,
            status=PayoutStatus.PAYOUT_PENDING,
            approved_at=datetime.now(timezone.utc),
        )
        db.add(payout)
    elif decision == ReviewDecision.REJECT:
        submission.status = SubmissionStatus.REJECTED
        submission.rejection_reason = data.rejection_reason
    elif decision == ReviewDecision.DUPLICATE:
        submission.status = SubmissionStatus.DUPLICATE
    elif decision == ReviewDecision.RIGHTS_RISK:
        submission.status = SubmissionStatus.RIGHTS_RISK
    elif decision == ReviewDecision.NEEDS_MORE_INFO:
        submission.status = SubmissionStatus.NEEDS_MORE_INFO

    submission.review_memo = data.memo

    review = AdminReview(
        submission_id=submission.id,
        admin_id=admin_id,
        decision=decision,
        memo=data.memo,
        rejection_reason=data.rejection_reason,
        checklist_playable=data.checklist_playable,
        checklist_under_one_minute=data.checklist_under_one_minute,
        checklist_likely_original=data.checklist_likely_original,
        checklist_no_news_source=data.checklist_no_news_source,
        checklist_blur_possible=data.checklist_blur_possible,
        checklist_location_safe=data.checklist_location_safe,
        checklist_not_sensitive=data.checklist_not_sensitive,
        checklist_payout_eligible=data.checklist_payout_eligible,
    )
    db.add(review)

    _log(db, "ADMIN", admin_id, f"REVIEW_{decision.value}", "VideoSubmission", str(submission.id),
         before={"status": before_status}, after={"status": submission.status.value})

    db.commit()
    db.refresh(submission)
    return submission


def mark_payout_paid(db: Session, payout_id: int, admin_id: int, data: MarkPaidRequest) -> Payout:
    payout = db.query(Payout).filter(Payout.id == payout_id).first()
    if not payout:
        return None
    payout.status = PayoutStatus.PAID
    payout.paid_at = datetime.now(timezone.utc)
    payout.paid_by_admin_id = admin_id
    payout.payment_reference = data.payment_reference
    payout.memo = data.memo

    _log(db, "ADMIN", admin_id, "MARK_PAID", "Payout", str(payout.id),
         before={"status": "PAYOUT_PENDING"}, after={"status": "PAID"})

    db.commit()
    db.refresh(payout)
    return payout
