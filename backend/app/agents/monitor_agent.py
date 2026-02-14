"""
Monitor Agent - Google Calendar sync

This agent monitors Google Calendar for changes and automatically
imports new meetings and updates to existing meetings.
"""

from datetime import datetime, timedelta
import logging
from sqlalchemy import select
from app.agents.base_agent import BaseAgent
from app.models.db import Meeting, User
from app.services.google_calendar import GoogleCalendarService
from app.core.config import db_manager

logger = logging.getLogger(__name__)


class MonitorAgent(BaseAgent):
    """
    Agent that monitors Google Calendar and syncs meetings.
    
    This agent:
    - Polls Google Calendar for all users with connected calendars
    - Imports new meetings automatically
    - Updates existing meetings if changed
    - Marks cancelled meetings
    """
    
    def __init__(self):
        """Initialize the monitor agent (checks every 10 minutes)."""
        super().__init__(name="MonitorAgent", check_interval_seconds=600)  # 10 minutes
        self.meetings_imported = 0
        self.meetings_updated = 0
        
    async def run(self):
        """Check Google Calendar and sync meetings."""
        async with db_manager.AsyncSessionLocal() as db:
            try:
                # Get all users with Google Calendar connected (have refresh_token)
                stmt = select(User).where(User.google_refresh_token.isnot(None))
                result = await db.execute(stmt)
                users_with_calendar = result.scalars().all()
                
                if not users_with_calendar:
                    logger.debug(f"[{self.name}] No users with Google Calendar connected")
                    return
                
                logger.info(f"[{self.name}] Checking calendars for {len(users_with_calendar)} users")
                
                total_imported = 0
                total_updated = 0
                
                for user in users_with_calendar:
                    try:
                        # Get upcoming events from Google Calendar
                        calendar_service = GoogleCalendarService(
                            access_token=user.google_token,  # Fixed: was google_access_token
                            refresh_token=user.google_refresh_token
                        )
                        
                        # Get events for next 30 days
                        time_min = datetime.utcnow()
                        time_max = time_min + timedelta(days=30)
                        
                        events = await calendar_service.get_upcoming_events(
                            time_min=time_min.isoformat() + 'Z',
                            time_max=time_max.isoformat() + 'Z'
                        )
                        
                        logger.info(f"[{self.name}] Found {len(events)} events for user {user.email}")
                        
                        for event in events:
                            try:
                                event_id = event.get('id')
                                
                                # Check if meeting already exists
                                existing = await db.execute(
                                    select(Meeting).where(
                                        Meeting.user_id == user.id,
                                        Meeting.event_id == event_id
                                    )
                                )
                                existing_meeting = existing.scalar_one_or_none()
                                
                                if existing_meeting:
                                    # Update if changed
                                    updated = await self._update_meeting_from_event(
                                        existing_meeting, event, db
                                    )
                                    if updated:
                                        total_updated += 1
                                else:
                                    # Import new meeting
                                    imported = await self._import_meeting_from_event(
                                        user.id, event, db
                                    )
                                    if imported:
                                        total_imported += 1
                                        
                            except Exception as e:
                                logger.error(f"[{self.name}] Error processing event {event.get('id')}: {e}")
                        
                    except Exception as e:
                        logger.error(f"[{self.name}] Error syncing calendar for user {user.email}: {e}")
                
                if total_imported > 0 or total_updated > 0:
                    logger.info(f"[{self.name}] Synced: {total_imported} imported, {total_updated} updated")
                    self.meetings_imported += total_imported
                    self.meetings_updated += total_updated
                    
            except Exception as e:
                logger.error(f"[{self.name}] Error in calendar monitoring: {e}", exc_info=True)
    
    async def _import_meeting_from_event(self, user_id, event, db):
        """Import a new meeting from Google Calendar event."""
        try:
            # Extract event details
            start = event.get('start', {})
            end = event.get('end', {})
            
            start_time = datetime.fromisoformat(
                start.get('dateTime', start.get('date', '')).replace('Z', '+00:00')
            ).replace(tzinfo=None)
            
            end_time = datetime.fromisoformat(
                end.get('dateTime', end.get('date', '')).replace('Z', '+00:00')
            ).replace(tzinfo=None)
            
            # Get attendees
            attendees = []
            for attendee in event.get('attendees', []):
                attendees.append({"email": attendee.get('email')})
            
            # Create meeting
            meeting = Meeting(
                user_id=user_id,
                event_id=event.get('id'),
                title=event.get('summary', 'Untitled Meeting'),
                description=event.get('description', ''),
                start_time=start_time,
                end_time=end_time,
                attendees=attendees,
                meeting_link=event.get('hangoutLink') or event.get('location', ''),
                meeting_platform='google_meet' if event.get('hangoutLink') else 'other',
                is_confirmed=True,
                is_cancelled=False,
                context_generated=False
            )
            
            db.add(meeting)
            await db.commit()
            
            logger.info(f"[{self.name}] ✅ Imported meeting: {meeting.title}")
            return True
            
        except Exception as e:
            logger.error(f"[{self.name}] Error importing event: {e}")
            await db.rollback()
            return False
    
    async def _update_meeting_from_event(self, meeting, event, db):
        """Update existing meeting from Google Calendar event."""
        try:
            changed = False
            
            # Check if title changed
            new_title = event.get('summary', 'Untitled Meeting')
            if meeting.title != new_title:
                meeting.title = new_title
                changed = True
            
            # Check if times changed
            start = event.get('start', {})
            end = event.get('end', {})
            
            new_start = datetime.fromisoformat(
                start.get('dateTime', start.get('date', '')).replace('Z', '+00:00')
            ).replace(tzinfo=None)
            
            new_end = datetime.fromisoformat(
                end.get('dateTime', end.get('date', '')).replace('Z', '+00:00')
            ).replace(tzinfo=None)
            
            if meeting.start_time != new_start or meeting.end_time != new_end:
                meeting.start_time = new_start
                meeting.end_time = new_end
                changed = True
            
            # Check if cancelled
            if event.get('status') == 'cancelled' and not meeting.is_cancelled:
                meeting.is_cancelled = True
                changed = True
            
            if changed:
                await db.commit()
                logger.info(f"[{self.name}] Updated meeting: {meeting.title}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"[{self.name}] Error updating meeting: {e}")
            await db.rollback()
            return False
    
    def get_status(self):
        """Get agent status with monitor-specific stats."""
        status = super().get_status()
        status["stats"]["meetings_imported"] = self.meetings_imported
        status["stats"]["meetings_updated"] = self.meetings_updated
        return status
