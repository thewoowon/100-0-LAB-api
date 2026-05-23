from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class PayoutAccount(Base):
    __tablename__ = "payoutaccount"

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    bank_name = Column(String, nullable=False)
    account_number_encrypted = Column(String, nullable=False)
    account_number_masked = Column(String, nullable=False)
    account_holder = Column(String, nullable=False)

    user = relationship("User", back_populates="payout_accounts")
    payouts = relationship("Payout", back_populates="payout_account")
