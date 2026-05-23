from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "auditlog"

    actor_type = Column(String, nullable=False)  # USER, ADMIN, SYSTEM
    actor_id = Column(Integer, nullable=True)
    action = Column(String, nullable=False)
    target_type = Column(String, nullable=False)
    target_id = Column(String, nullable=False)
    before = Column(JSON, nullable=True)
    after = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
