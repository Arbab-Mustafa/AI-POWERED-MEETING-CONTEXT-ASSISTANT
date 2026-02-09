"""
Repository layer for data access.
Implements Data Access Object (DAO) pattern for clean separation of concerns.
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db import User, Meeting, Context, Notification, AttendeeInfo


class UserRepository:
    """Repository for User model operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        stmt = select(User).where(User.id == user_id).where(User.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        stmt = select(User).where(User.email == email).where(User.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create(self, user: User) -> User:
        """Create new user."""
        self.session.add(user)
        await self.session.flush()
        return user
    
    async def update(self, user: User) -> User:
        """Update existing user."""
        await self.session.merge(user)
        await self.session.flush()
        return user
    
    async def delete(self, user_id: UUID) -> bool:
        """Soft delete user."""
        user = await self.get_by_id(user_id)
        if user:
            user.deleted_at = datetime.utcnow()
            await self.update(user)
            return True
        return False


class MeetingRepository:
    """Repository for Meeting model operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, meeting_id: UUID) -> Optional[Meeting]:
        """Get meeting by ID."""
        stmt = select(Meeting).where(Meeting.id == meeting_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_event_id(self, user_id: UUID, event_id: str) -> Optional[Meeting]:
        """Get meeting by Google Calendar event ID."""
        stmt = select(Meeting).where(
            and_(Meeting.user_id == user_id, Meeting.event_id == event_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_upcoming_for_user(
        self, 
        user_id: UUID, 
        days: int = 7
    ) -> List[Meeting]:
        """Get upcoming meetings for user (next N days)."""
        now = datetime.utcnow()
        future = datetime.utcnow() + __import__('datetime').timedelta(days=days)
        
        stmt = select(Meeting).where(
            and_(
                Meeting.user_id == user_id,
                Meeting.start_time >= now,
                Meeting.start_time <= future,
                Meeting.is_cancelled == False
            )
        ).order_by(Meeting.start_time)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def create(self, meeting: Meeting) -> Meeting:
        """Create new meeting."""
        self.session.add(meeting)
        await self.session.flush()
        return meeting
    
    async def update(self, meeting: Meeting) -> Meeting:
        """Update existing meeting."""
        await self.session.merge(meeting)
        await self.session.flush()
        return meeting
    
    async def delete(self, meeting_id: UUID) -> bool:
        """Delete meeting."""
        meeting = await self.get_by_id(meeting_id)
        if meeting:
            await self.session.delete(meeting)
            await self.session.flush()
            return True
        return False


class ContextRepository:
    """Repository for Context model operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_meeting_id(self, meeting_id: UUID) -> Optional[Context]:
        """Get context by meeting ID."""
        stmt = select(Context).where(Context.meeting_id == meeting_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create(self, context: Context) -> Context:
        """Create new context."""
        self.session.add(context)
        await self.session.flush()
        return context
    
    async def update(self, context: Context) -> Context:
        """Update existing context."""
        await self.session.merge(context)
        await self.session.flush()
        return context


class NotificationRepository:
    """Repository for Notification model operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_pending(self) -> List[Notification]:
        """Get all pending notifications to send."""
        stmt = select(Notification).where(
            and_(
                Notification.status == "scheduled",
                Notification.scheduled_time <= datetime.utcnow()
            )
        ).order_by(Notification.scheduled_time)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def create(self, notification: Notification) -> Notification:
        """Create new notification."""
        self.session.add(notification)
        await self.session.flush()
        return notification
    
    async def update(self, notification: Notification) -> Notification:
        """Update notification status."""
        await self.session.merge(notification)
        await self.session.flush()
        return notification


class AttendeeInfoRepository:
    """Repository for AttendeeInfo model operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_or_create(
        self, 
        user_id: UUID,
        email: str,
        name: Optional[str] = None
    ) -> AttendeeInfo:
        """Get existing attendee info or create new."""
        stmt = select(AttendeeInfo).where(
            and_(
                AttendeeInfo.user_id == user_id,
                AttendeeInfo.attendee_email == email
            )
        )
        result = await self.session.execute(stmt)
        attendee = result.scalar_one_or_none()
        
        if not attendee:
            attendee = AttendeeInfo(
                user_id=user_id,
                attendee_email=email,
                attendee_name=name
            )
            self.session.add(attendee)
            await self.session.flush()
        
        return attendee
    
    async def update_interaction(self, attendee_id: UUID) -> AttendeeInfo:
        """Update attendee meeting count and last interaction."""
        stmt = select(AttendeeInfo).where(AttendeeInfo.id == attendee_id)
        result = await self.session.execute(stmt)
        attendee = result.scalar_one()
        
        attendee.meeting_count += 1
        attendee.last_interaction = datetime.utcnow()
        
        await self.session.merge(attendee)
        await self.session.flush()
        return attendee


__all__ = [
    "UserRepository",
    "MeetingRepository",
    "ContextRepository",
    "NotificationRepository",
    "AttendeeInfoRepository"
]
