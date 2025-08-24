from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base
import datetime

Base = declarative_base()

class ModerationRequest(Base):
    __tablename__ = "moderation_requests"
    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String, nullable=False)
    content_hash = Column(String, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    results = relationship("ModerationResult", back_populates="request")
    notifications = relationship("NotificationLog", back_populates="request")

class ModerationResult(Base):
    __tablename__ = "moderation_results"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("moderation_requests.id"))
    classification = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    reasoning = Column(Text)
    llm_response = Column(Text)
    request = relationship("ModerationRequest", back_populates="results")

class NotificationLog(Base):
    __tablename__ = "notification_logs"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("moderation_requests.id"))
    channel = Column(String, nullable=False)
    status = Column(String, nullable=False)
    sent_at = Column(DateTime, default=datetime.datetime.utcnow)
    request = relationship("ModerationRequest", back_populates="notifications")
