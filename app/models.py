"""
SQLAlchemy models for Smart Content Moderator API.
Async setup and relationships included.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, func
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.asyncio import AsyncAttrs
from datetime import datetime

Base = declarative_base(cls=AsyncAttrs)

class ModerationRequest(Base):
    __tablename__ = "moderation_requests"
    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String, nullable=False)  # "text" or "image"
    content_hash = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")  # "pending" or "completed"
    created_at = Column(DateTime, default=datetime.utcnow)
    results = relationship("ModerationResult", back_populates="request", cascade="all, delete-orphan")
    notifications = relationship("NotificationLog", back_populates="request", cascade="all, delete-orphan")

class ModerationResult(Base):
    __tablename__ = "moderation_results"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("moderation_requests.id"))
    classification = Column(String, nullable=False)  # "toxic", "spam", "harassment", "safe"
    confidence = Column(Float, nullable=False)
    reasoning = Column(Text)
    llm_response = Column(Text)  # JSON string
    request = relationship("ModerationRequest", back_populates="results")

class NotificationLog(Base):
    __tablename__ = "notification_logs"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("moderation_requests.id"))
    channel = Column(String, nullable=False)  # "slack" or "email"
    status = Column(String, nullable=False)   # "sent" or "failed"
    sent_at = Column(DateTime, default=datetime.utcnow)
    request = relationship("ModerationRequest", back_populates="notifications")

class ModerationSummary(Base):
    __tablename__ = "moderation_summary"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, nullable=False)   # link to ModerationRequest
    text = Column(String, nullable=False)
    classification = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    notification_status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
