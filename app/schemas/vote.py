from pydantic import BaseModel, field_validator
from typing import Optional

VALID_RATIOS = {"100:0", "90:10", "80:20", "70:30", "60:40", "50:50"}


class VoteCreate(BaseModel):
    ratio: str

    @field_validator("ratio")
    @classmethod
    def validate_ratio(cls, v: str) -> str:
        if v not in VALID_RATIOS:
            raise ValueError(f"ratio는 다음 중 하나여야 합니다: {', '.join(sorted(VALID_RATIOS))}")
        return v


class VoteOption(BaseModel):
    ratio: str
    count: int
    percentage: float


class VoteResult(BaseModel):
    total: int
    options: list[VoteOption]


class MyVote(BaseModel):
    ratio: Optional[str] = None
