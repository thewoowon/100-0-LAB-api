from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

VALID_STATUSES = {
    "사고_발생",
    "보험사_협의중",
    "보험_처리완료",
    "경찰_신고접수",
    "조사_진행중",
    "검찰_송치",
    "재판_진행중",
    "판결_완료",
    "합의_완료",
    "알_수_없음",
}

VALID_RATIOS = {"100:0", "90:10", "80:20", "70:30", "60:40", "50:50"}


class CaseStatusUpdate(BaseModel):
    status: str
    actual_ratio: Optional[str] = None
    resolution_note: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in VALID_STATUSES:
            raise ValueError(f"status는 다음 중 하나여야 합니다: {', '.join(sorted(VALID_STATUSES))}")
        return v

    @field_validator("actual_ratio")
    @classmethod
    def validate_ratio(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_RATIOS:
            raise ValueError(f"actual_ratio는 다음 중 하나여야 합니다: {', '.join(sorted(VALID_RATIOS))}")
        return v


class CaseStatusResponse(BaseModel):
    video_id: int
    status: str
    actual_ratio: Optional[str] = None
    resolution_note: Optional[str] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
