"""
Service layer for business logic.
Services coordinate between repositories and external integrations.
"""

import logging
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import User, Meeting, Context, Notification
from app.schemas.base import (
    UserCreate, UserResponse, MeetingResponse, ContextResponse
)
from app.repositories.base import (
    UserRepository, MeetingRepository, ContextRepository,
    NotificationRepository, AttendeeInfoRepository
)
from app.utils.helpers import SecurityUtils, DateTimeUtils
from app.services.ai_service import ai_generator
from app.services.google_calendar import calendar_service
from app.services.notification_delivery import notification_dispatcher

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create new user account."""
        existing = await self.user_repo.get_by_email(user_data.email)
        if existing:
            raise ValueError("User with this email already exists")
        
        user = User(
            email=user_data.email,
            name=user_data.name,
            timezone=user_data.timezone
        )
        
        if user_data.password:
            user.password_hash = SecurityUtils.hash_password(user_data.password)
        
        return await self.user_repo.create(user)
    
    async def authenticate_user(
        self,
        email: str,
        password: str
    ) -> Optional[User]:
        """Authenticate user with email and password."""
        user = await self.user_repo.get_by_email(email)
        
        if not user or not user.password_hash:
            return None
        
        if not SecurityUtils.verify_password(password, user.password_hash):
            return None
        
        return user
    
    async def get_or_create_google_user(
        self,
        email: str,
        name: str,
        google_token: str
    ) -> User:
        """Get existing user or create new from Google OAuth."""
        user = await self.user_repo.get_by_email(email)
        
        if not user:
            user = User(
                email=email,
                name=name,
                google_token=google_token
            )
            user = await self.user_repo.create(user)
        else:
            user.google_token = google_token
            user = await self.user_repo.update(user)
        
        return user


class CalendarService:
    """Service for calendar operations with Google Calendar integration."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.meeting_repo = MeetingRepository(session)
        self.attendee_repo = AttendeeInfoRepository(session)
        self.user_repo = UserRepository(session)
    
    async def sync_user_calendar(
        self,
        user_id: UUID,
        days_ahead: int = 7
    ) -> List[Meeting]:
        """Sync all meetings from user's Google Calendar."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Fetch events from Google Calendar
        events = await calendar_service.fetch_upcoming_events(user, days_ahead)
        
        synced_meetings = []
        for event_data in events:
            meeting = await self.sync_meeting(user_id, event_data)
            synced_meetings.append(meeting)
        
        logger.info(f"Synced {len(synced_meetings)} meetings for user {user_id}")
        return synced_meetings
    
    async def sync_meeting(
        self,
        user_id: UUID,
        event_data: dict
    ) -> Meeting:
        """Sync single meeting from Google Calendar event."""
        event_id = event_data.get("event_id")
        
        # Check if meeting already exists
        existing = await self.meeting_repo.get_by_event_id(user_id, event_id)
        
        meeting_obj = existing or Meeting(user_id=user_id, event_id=event_id)
        
        # Update meeting data
        meeting_obj.title = event_data.get("title", "")
        meeting_obj.description = event_data.get("description")
        meeting_obj.start_time = event_data.get("start_time")
        meeting_obj.end_time = event_data.get("end_time")
        meeting_obj.meeting_link = event_data.get("meeting_link")
        meeting_obj.location = event_data.get("location")
        meeting_obj.attendees = [att['email'] for att in event_data.get("attendees", [])]
        meeting_obj.status = event_data.get("status", "confirmed")
        meeting_obj.synced_at = datetime.utcnow()
        
        if existing:
            meeting_obj = await self.meeting_repo.update(meeting_obj)
        else:
            meeting_obj = await self.meeting_repo.create(meeting_obj)
        
        # Update attendee info
        for attendee in event_data.get("attendees", []):
            await self.attendee_repo.get_or_create(
                user_id,
                attendee.get("email"),
                attendee.get("name")
            )
        
        logger.info(f"Meeting synced: {meeting_obj.id}")
        return meeting_obj
    
    async def get_upcoming_meetings(
        self,
        user_id: UUID,
        days: int = 7
    ) -> List[Meeting]:
        """Get upcoming meetings for user."""
        return await self.meeting_repo.get_upcoming_for_user(user_id, days)


class ContextService:
    """Service for AI-powered context generation and management."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.context_repo = ContextRepository(session)
        self.meeting_repo = MeetingRepository(session)
    
    async def generate_and_create_context(
        self,
        meeting_id: UUID,
        user_id: UUID,
        force_regenerate: bool = False
    ) -> Context:
        """Generate AI context for meeting and save to database."""
        meeting = await self.meeting_repo.get_by_id(meeting_id)
        if not meeting:
            raise ValueError("Meeting not found")
        
        # Check if context already exists
        if not force_regenerate:
            existing = await self.context_repo.get_by_meeting_id(meeting_id)
            if existing:
                logger.info(f"Context already exists for meeting {meeting_id}")
                return existing
        
        # Get previous contexts for learning
        previous_contexts = await self.context_repo.get_recent_for_user(user_id, limit=5)
        previous_data = [
            {"title": meeting.title, "type": ctx.meeting_type}
            for ctx in previous_contexts
        ] if previous_contexts else None
        
        # Generate AI context
        ai_context = await ai_generator.generate_meeting_context(
            title=meeting.title,
            description=meeting.description,
            attendees=meeting.attendees or [],
            start_time=meeting.start_time,
            previous_contexts=previous_data
        )
        
        # Save to database
        context = await self.create_context(meeting_id, user_id, ai_context)
        
        return context
    
    async def create_context(
        self,
        meeting_id: UUID,
        user_id: UUID,
        context_data: dict
    ) -> Context:
        """Create context record from AI-generated data."""
        meeting = await self.meeting_repo.get_by_id(meeting_id)
        if not meeting:
            raise ValueError("Meeting not found")
        
        context = Context(
            user_id=user_id,
            meeting_id=meeting_id,
            ai_brief=context_data.get("brief", ""),
            meeting_type=context_data.get("type", "general"),
            key_topics=context_data.get("topics", []),
            preparation_checklist=context_data.get("checklist", []),
            attendee_context=context_data.get("attendees", {}),
            confidence_score=context_data.get("confidence", 85)
        )
        
        context = await self.context_repo.create(context)
        
        # Mark meeting as context generated
        meeting.context_generated = True
        await self.meeting_repo.update(meeting)
        
        logger.info(f"Context created for meeting: {meeting_id}")
        return context
    
    async def update_context(
        self,
        meeting_id: UUID,
        context_data: dict
    ) -> Context:
        """Update user-edited context."""
        context = await self.context_repo.get_by_meeting_id(meeting_id)
        if not context:
            raise ValueError("Context not found")
        
        for key, value in context_data.items():
            if hasattr(context, key) and value is not None:
                setattr(context, key, value)
        
        context.user_edited = True
        context = await self.context_repo.update(context)
        
        logger.info(f"Context updated: {context.id}")
        return context


class NotificationService:
    """Service for notification scheduling and delivery."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.notification_repo = NotificationRepository(session)
        self.meeting_repo = MeetingRepository(session)
        self.context_repo = ContextRepository(session)
        self.user_repo = UserRepository(session)
    
    async def schedule_notifications(
        self,
        meeting_id: UUID,
        user_id: UUID,
        reminder_times: List[int],
        meeting_start: datetime,
        preferred_channels: List[str]
    ) -> List[Notification]:
        """Schedule multiple notifications for a meeting."""
        notifications = []
        
        for minutes_before in reminder_times:
            scheduled_time = DateTimeUtils.add_minutes(meeting_start, -minutes_before)
            
            for channel in preferred_channels:
                notification = Notification(
                    meeting_id=meeting_id,
                    user_id=user_id,
                    channel=channel,
                    scheduled_time=scheduled_time,
                    status="scheduled"
                )
                
                notification = await self.notification_repo.create(notification)
                notifications.append(notification)
        
        logger.info(f"Scheduled {len(notifications)} notifications for meeting: {meeting_id}")
        return notifications
    
    async def get_pending_notifications(self) -> List[Notification]:
        """Get all notifications ready to send."""
        return await self.notification_repo.get_pending()
    
    async def send_notification(
        self,
        notification_id: UUID
    ) -> bool:
        """Send a scheduled notification."""
        notification = await self.notification_repo.get_by_id(notification_id)
        if not notification:
            logger.error(f"Notification {notification_id} not found")
            return False
        
        # Get related data
        meeting = await self.meeting_repo.get_by_id(notification.meeting_id)
        user = await self.user_repo.get_by_id(notification.user_id)
        context = await self.context_repo.get_by_meeting_id(notification.meeting_id)
        
        if not meeting or not user:
            logger.error(f"Meeting or user not found for notification {notification_id}")
            return False
        
        # Send via dispatcher
        success = await notification_dispatcher.send_notification(
            notification=notification,
            meeting=meeting,
            user_email=user.email,
            telegram_chat_id=user.telegram_chat_id,
            context=context
        )
        
        # Update notification status
        if success:
            notification.sent_time = datetime.utcnow()
            notification.status = "sent"
        else:
            notification.status = "failed"
        
        await self.notification_repo.update(notification)
        return success
    
    async def mark_sent(
        self,
        notification_id: UUID,
        sent_time: datetime = None
    ) -> Notification:
        """Mark notification as sent."""
        from sqlalchemy import select
        
        stmt = select(Notification).where(Notification.id == notification_id)
        result = await self.session.execute(stmt)
        notification = result.scalar_one()
        
        if sent_time is None:
            sent_time = datetime.utcnow()
        
        notification.sent_time = sent_time
        notification.status = "sent"
        
        notification = await self.notification_repo.update(notification)
        logger.info(f"Notification marked as sent: {notification_id}")
        return notification


__all__ = [
    "AuthService",
    "CalendarService",
    "ContextService",
    "NotificationService"
]
