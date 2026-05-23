import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base


class PayoutStatus(str, enum.Enum):
    NOT_ELIGIBLE = "NOT_ELIGIBLE"
    PAYOUT_PENDING = "PAYOUT_PENDING"
    PAYOUT_PROCESSING = "PAYOUT_PROCESSING"
    PAID = "PAID"
    PAYOUT_FAILED = "PAYOUT_FAILED"
    PAYOUT_HOLD = "PAYOUT_HOLD"
    CANCELLED = "CANCELLED"


class Payout(Base):
    __tablename__ = "payout"

    submission_id = Column(Integer, ForeignKey("videosubmission.id"), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    payout_account_id = Column(Integer, ForeignKey("payoutaccount.id"), nullable=False)

    amount = Column(Integer, nullable=False, default=5000)
    currency = Column(String, nullable=False, default="KRW")
    status = Column(Enum(PayoutStatus), nullable=False, default=PayoutStatus.PAYOUT_PENDING)

    approved_at = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    paid_by_admin_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    payment_reference = Column(String, nullable=True)
    memo = Column(String, nullable=True)

    submission = relationship("VideoSubmission", back_populates="payout")
    payout_account = relationship("PayoutAccount", back_populates="payouts")
    user = relationship("User", foreign_keys=[user_id])
    paid_by_admin = relationship("User", foreign_keys=[paid_by_admin_id])
