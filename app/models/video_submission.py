import enum
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Enum, Text
from sqlalchemy.orm import relationship
from app.db.base import Base


class SubmissionStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    NEEDS_MORE_INFO = "NEEDS_MORE_INFO"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DUPLICATE = "DUPLICATE"
    RIGHTS_RISK = "RIGHTS_RISK"
    PROCESSING_PRIVACY = "PROCESSING_PRIVACY"
    READY_TO_PUBLISH = "READY_TO_PUBLISH"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class VideoSubmission(Base):
    __tablename__ = "videosubmission"

    submission_no = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    title = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    incident_type = Column(String, nullable=False)

    original_storage_key = Column(String, nullable=True)
    processed_storage_key = Column(String, nullable=True)
    thumbnail_storage_key = Column(String, nullable=True)
    original_file_hash = Column(String, nullable=True)
    duration_sec = Column(Integer, nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    mime_type = Column(String, nullable=True)

    region_sido = Column(String, nullable=False)
    region_sigungu = Column(String, nullable=True)
    approximate_address = Column(String, nullable=True)
    original_lat = Column(Float, nullable=True)
    original_lng = Column(Float, nullable=True)
    noisy_lat = Column(Float, nullable=True)
    noisy_lng = Column(Float, nullable=True)

    status = Column(Enum(SubmissionStatus), nullable=False, default=SubmissionStatus.PENDING_REVIEW)
    risk_level = Column(Enum(RiskLevel), nullable=True)
    rejection_reason = Column(String, nullable=True)
    review_memo = Column(Text, nullable=True)

    video_id = Column(Integer, ForeignKey("video.id"), nullable=True)

    user = relationship("User", back_populates="submissions")
    video = relationship("Video", foreign_keys=[video_id])
    agreement = relationship("ContentAgreement", back_populates="submission", uselist=False)
    payout = relationship("Payout", back_populates="submission", uselist=False)
    admin_reviews = relationship("AdminReview", back_populates="submission")
