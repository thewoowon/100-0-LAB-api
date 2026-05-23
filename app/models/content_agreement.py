from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base


class ContentAgreement(Base):
    __tablename__ = "contentagreement"

    submission_id = Column(Integer, ForeignKey("videosubmission.id"), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    agreement_version = Column(String, nullable=False, default="v1")
    is_original_owner = Column(Boolean, nullable=False)
    is_rights_holder = Column(Boolean, nullable=False)
    commercial_use_agreed = Column(Boolean, nullable=False)
    edit_and_blur_agreed = Column(Boolean, nullable=False)
    warranty_agreed = Column(Boolean, nullable=False)
    privacy_policy_agreed = Column(Boolean, nullable=False)
    reward_policy_confirmed = Column(Boolean, nullable=False)

    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    file_hash_at_agreement = Column(String, nullable=True)

    submission = relationship("VideoSubmission", back_populates="agreement")
