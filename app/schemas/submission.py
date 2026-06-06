from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.video_submission import SubmissionStatus, RiskLevel
from app.models.payout import PayoutStatus


class SubmissionCreate(BaseModel):
    title: Optional[str] = None
    description: str
    incident_type: str
    region_sido: str
    region_sigungu: Optional[str] = None
    approximate_address: Optional[str] = None
    original_lat: Optional[float] = None
    original_lng: Optional[float] = None
    bank_name: str
    account_number: str
    account_holder: str
    is_original_owner: bool
    is_rights_holder: bool
    commercial_use_agreed: bool
    edit_and_blur_agreed: bool
    warranty_agreed: bool
    privacy_policy_agreed: bool
    reward_policy_confirmed: bool


class SubmissionResponse(BaseModel):
    id: int
    submission_no: str
    status: SubmissionStatus
    incident_type: str
    region_sido: str
    title: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SubmissionDetail(SubmissionResponse):
    description: str
    region_sigungu: Optional[str]
    approximate_address: Optional[str]
    noisy_lat: Optional[float]
    noisy_lng: Optional[float]
    rejection_reason: Optional[str]
    thumbnail_storage_key: Optional[str]
    video_id: Optional[int]


class AdminSubmissionDetail(SubmissionDetail):
    user_id: int
    user_email: Optional[str] = None
    original_storage_key: Optional[str]
    original_lat: Optional[float]
    original_lng: Optional[float]
    original_file_hash: Optional[str]
    risk_level: Optional[RiskLevel]
    review_memo: Optional[str]


class AdminReviewRequest(BaseModel):
    decision: str
    rejection_reason: Optional[str] = None
    memo: Optional[str] = None
    checklist_playable: Optional[bool] = None
    checklist_under_one_minute: Optional[bool] = None
    checklist_likely_original: Optional[bool] = None
    checklist_no_news_source: Optional[bool] = None
    checklist_blur_possible: Optional[bool] = None
    checklist_location_safe: Optional[bool] = None
    checklist_not_sensitive: Optional[bool] = None
    checklist_payout_eligible: Optional[bool] = None


class PayoutResponse(BaseModel):
    id: int
    submission_id: int
    amount: int
    currency: str
    status: PayoutStatus
    approved_at: Optional[datetime]
    paid_at: Optional[datetime]
    payment_reference: Optional[str]
    memo: Optional[str]

    class Config:
        from_attributes = True


class MarkPaidRequest(BaseModel):
    payment_reference: Optional[str] = None
    memo: Optional[str] = None
