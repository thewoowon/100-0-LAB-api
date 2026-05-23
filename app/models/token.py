from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base


class Token(Base):
    __tablename__ = "token"

    refresh_token = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="tokens")
