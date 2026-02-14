"""
Pydantic schemas for request/response validation.
Separate schemas for request (Create) and response (Read) operations.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, EmailStr, Field, field_validator
import uuid


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    name: str
    timezone: str = "UTC"


class UserCreate(UserBase):
    """Schema for user creation.
    
    Password requirements:
    - Minimum 8 characters
    - Maximum 72 characters (bcrypt limit)
    """
    password: str = Field(..., min_length=8, max_length=72)


class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str = Field(..., max_length=72)


class UserUpdate(BaseModel):
    """Schema for user updates."""
    name: Optional[str] = None
    timezone: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: uuid.UUID
    created_at: datetime
    preferences: Dict[str, Any]
    telegram_verified: bool
    
    class Config:
        from_attributes = True


class MeetingBase(BaseModel):
    """Base meeting schema."""
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    attendees: List[Union[str, Dict[str, Any]]] = []
    meeting_link: Optional[str] = None
    meeting_platform: str = "other"


class MeetingCreate(MeetingBase):
    """Schema for meeting creation."""
    event_id: Optional[str] = None
    
    @field_validator('attendees', mode='before')
    @classmethod
    def normalize_attendees(cls, v):
        """Normalize attendees to list of dicts format."""
        if not v:
            return []
        
        normalized = []
        for attendee in v:
            if isinstance(attendee, str):
                # Convert string email to dict format
                normalized.append({"email": attendee})
            elif isinstance(attendee, dict):
                normalized.append(attendee)
            else:
                # Skip invalid formats
                continue
        
        return normalized
        return normalized


class MeetingUpdate(BaseModel):
    """Schema for meeting updates."""
    title: Optional[str] = None
    notes: Optional[str] = None
    is_cancelled: Optional[bool] = None


class MeetingUpdate(BaseModel):
    """Schema for updating a meeting."""
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    attendees: Optional[dict] = None
    meeting_link: Optional[str] = None
    meeting_platform: Optional[str] = None
    notes: Optional[str] = None
    is_confirmed: Optional[bool] = None
    is_cancelled: Optional[bool] = None


class MeetingResponse(MeetingBase):
    """Schema for meeting response."""
    id: uuid.UUID
    user_id: uuid.UUID
    event_id: Optional[str] = None
    created_at: datetime
    is_confirmed: bool
    context_generated: bool
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class ContextBase(BaseModel):
    """Base context schema."""
    ai_brief: Optional[str] = None
    meeting_type: str = "general"
    key_topics: List[str] = []
    preparation_checklist: List[Union[str, Dict[str, Any]]] = []
    attendee_context: Dict[str, str] = {}
    
    @field_validator('preparation_checklist', mode='before')
    @classmethod
    def normalize_checklist(cls, v: Any) -> List[Dict[str, Any]]:
        """Convert string items to dict format."""
        if not v:
            return []
        result = []
        for item in v:
            if isinstance(item, str):
                result.append({"task": item, "completed": False})
            elif isinstance(item, dict):
                result.append(item)
        return result


class ContextCreate(ContextBase):
    """Schema for context creation."""
    pass


class ContextUpdate(BaseModel):
    """Schema for context updates."""
    ai_brief: Optional[str] = None
    meeting_type: Optional[str] = None
    key_topics: Optional[List[str]] = None
    preparation_checklist: Optional[List[Union[str, Dict[str, Any]]]] = None
    attendee_context: Optional[Dict[str, str]] = None
    
    @field_validator('preparation_checklist', mode='before')
    @classmethod
    def normalize_checklist(cls, v: Any) -> Optional[List[Dict[str, Any]]]:
        """Convert string items to dict format."""
        if v is None:
            return None
        result = []
        for item in v:
            if isinstance(item, str):
                result.append({"task": item, "completed": False})
            elif isinstance(item, dict):
                result.append(item)
        return result


class ContextUpdateLegacy(BaseModel):
    """Schema for updating a context."""
    ai_brief: Optional[str] = None
    meeting_type: Optional[str] = None
    key_topics: Optional[dict] = None
    preparation_checklist: Optional[dict] = None
    attendee_context: Optional[dict] = None
    action_items_from_last: Optional[dict] = None
    user_edited: bool = True


class ContextResponse(ContextBase):
    """Schema for context response."""
    id: uuid.UUID
    meeting_id: uuid.UUID
    generated_at: datetime
    ai_model_version: str
    user_edited: bool
    
    class Config:
        from_attributes = True


class NotificationBase(BaseModel):
    """Base notification schema."""
    channel: str
    scheduled_time: datetime
    status: str = "scheduled"


class NotificationCreate(BaseModel):
    """Schema for creating a notification."""
    meeting_id: uuid.UUID
    channel: str
    scheduled_time: datetime


class NotificationResponse(NotificationBase):
    """Schema for notification response."""
    id: uuid.UUID
    meeting_id: uuid.UUID
    sent_time: Optional[datetime] = None
    delivered_time: Optional[datetime] = None
    retry_count: int
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class AttendeeInfoResponse(BaseModel):
    """Schema for attendee info response."""
    id: uuid.UUID
    attendee_email: str
    attendee_name: Optional[str] = None
    meeting_count: int
    last_interaction: Optional[datetime] = None
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class MeetingDetailResponse(MeetingResponse):
    """Extended meeting response with context and notifications."""
    context: Optional[ContextResponse] = None
    notifications: List[NotificationResponse] = []


class UserPreferencesUpdate(BaseModel):
    """Schema for updating user preferences."""
    notification_email: bool = True
    notification_telegram: bool = True
    notification_whatsapp: bool = False
    reminder_timing: List[int] = [1440, 60, 15]
    do_not_disturb_start: Optional[str] = "22:00"
    do_not_disturb_end: Optional[str] = "08:00"
    monitored_calendars: List[str] = []


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class GoogleCallbackRequest(BaseModel):
    """Schema for Google OAuth callback request."""
    code: str
    redirect_uri: str
    state: Optional[str] = None


class TelegramLinkRequest(BaseModel):
    """Schema for Telegram account linking."""
    telegram_user_id: int
    telegram_username: str
    verification_code: str


class CalendarSyncResponse(BaseModel):
    """Schema for calendar sync response."""
    success: bool
    events_synced: int
    timestamp: datetime
    message: str


class ErrorResponse(BaseModel):
    """Schema for error response."""
    error: str
    message: str
    timestamp: datetime
    request_id: Optional[str] = None


__all__ = [
    "UserCreate",
    "UserResponse",
    "UserUpdate",
    "MeetingCreate",
    "MeetingResponse",
    "MeetingUpdate",
    "MeetingDetailResponse",
    "ContextCreate",
    "ContextResponse",
    "ContextUpdate",
    "NotificationResponse",
    "AttendeeInfoResponse",
    "UserPreferencesUpdate",
    "TokenResponse",
    "GoogleCallbackRequest",
    "TelegramLinkRequest",
    "CalendarSyncResponse",
    "ErrorResponse"
]
