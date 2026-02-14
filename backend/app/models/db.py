"""
Database models using SQLAlchemy ORM.
All models inherit from Base for centralized management.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, UUID, DateTime, Boolean, Integer, Text, JSON, BigInteger, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """User account and authentication model."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    timezone = Column(String(50), default="UTC")
    password_hash = Column(String(255), nullable=True)
    
    google_token = Column(Text, nullable=True)
    google_refresh_token = Column(Text, nullable=True)
    google_token_expiry = Column(DateTime, nullable=True)
    telegram_chat_id = Column(BigInteger, nullable=True, unique=True)
    telegram_verified = Column(Boolean, default=False)
    
    preferences = Column(JSON, default={})
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    meetings = relationship("Meeting", back_populates="user", cascade="all, delete-orphan")
    contexts = relationship("Context", back_populates="user")
    attendee_info = relationship("AttendeeInfo", back_populates="user")
    learning_profile = relationship("UserLearningProfile", back_populates="user", uselist=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class Meeting(Base):
    """Calendar meeting model."""
    __tablename__ = "meetings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    event_id = Column(String(255), index=True)
    
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    attendees = Column(JSON, default=[])
    
    meeting_link = Column(String(500), nullable=True)
    meeting_platform = Column(String(50), default="other")
    calendar_id = Column(String(255))
    
    is_confirmed = Column(Boolean, default=True)
    is_cancelled = Column(Boolean, default=False)
    context_generated = Column(Boolean, default=False)
    
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    synced_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="meetings")
    context = relationship("Context", back_populates="meeting", uselist=False, cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="meeting", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Meeting(id={self.id}, title={self.title})>"


class Context(Base):
    """AI-generated meeting context model."""
    __tablename__ = "contexts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    meeting_id = Column(UUID(as_uuid=True), ForeignKey("meetings.id"), nullable=False, index=True)
    
    ai_brief = Column(Text)
    meeting_type = Column(String(50), default="general")
    key_topics = Column(JSON, default=[])
    preparation_checklist = Column(JSON, default=[])
    attendee_context = Column(JSON, default={})
    action_items_from_last = Column(JSON, default=[])
    
    generated_at = Column(DateTime, default=datetime.utcnow)
    ai_model_version = Column(String(50), default="mistral-7b")
    confidence_score = Column(Integer, default=0)
    user_edited = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="contexts")
    meeting = relationship("Meeting", back_populates="context")
    
    def __repr__(self):
        return f"<Context(id={self.id}, meeting_id={self.meeting_id})>"


class Notification(Base):
    """Notification delivery tracking model."""
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meeting_id = Column(UUID(as_uuid=True), ForeignKey("meetings.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    channel = Column(String(50), nullable=False)
    scheduled_time = Column(DateTime, nullable=False, index=True)
    sent_time = Column(DateTime, nullable=True)
    delivered_time = Column(DateTime, nullable=True)
    opened_time = Column(DateTime, nullable=True)
    
    status = Column(String(50), default="scheduled")
    retry_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    meeting = relationship("Meeting", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, channel={self.channel}, status={self.status})>"


class AttendeeInfo(Base):
    """Attendee information model."""
    __tablename__ = "attendee_info"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    attendee_email = Column(String(255), nullable=False)
    attendee_name = Column(String(255), nullable=True)
    
    meeting_count = Column(Integer, default=0)
    last_interaction = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="attendee_info")
    
    def __repr__(self):
        return f"<AttendeeInfo(id={self.id}, email={self.attendee_email})>"


class UserLearningProfile(Base):
    """User behavior learning profile model."""
    __tablename__ = "user_learning_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    
    reschedule_patterns = Column(JSON, default={})
    prep_time_estimates = Column(JSON, default={})
    optimal_notification_times = Column(JSON, default={})
    back_to_back_tolerance = Column(Integer, default=15)
    average_meeting_duration = Column(Integer, default=60)
    meeting_type_distribution = Column(JSON, default={})
    
    last_analysis = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="learning_profile")
    
    def __repr__(self):
        return f"<UserLearningProfile(user_id={self.user_id})>"


__all__ = [
    "Base",
    "User",
    "Meeting",
    "Context",
    "Notification",
    "AttendeeInfo",
    "UserLearningProfile"
]
