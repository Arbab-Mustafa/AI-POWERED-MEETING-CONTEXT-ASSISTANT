"""
Google Calendar Integration Service.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from uuid import UUID

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import settings
from app.models.db import Meeting, User

logger = logging.getLogger(__name__)


class GoogleCalendarService:
    """Service for Google Calendar API integration."""
    
    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/calendar.readonly']
    
    def _get_calendar_service(self, user: User):
        """Build Google Calendar API service with user credentials."""
        
        if not user.google_token:
            raise ValueError("User has not connected Google Calendar")
        
        try:
            # Build credentials from stored token
            creds = Credentials.from_authorized_user_info(
                info={
                    "token": user.google_token,
                    "refresh_token": user.google_refresh_token,
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "scopes": self.scopes
                }
            )
            
            # Build the service
            service = build('calendar', 'v3', credentials=creds)
            return service
            
        except Exception as e:
            logger.error(f"Failed to build calendar service: {e}")
            raise
    
    async def fetch_upcoming_events(
        self,
        user: User,
        days_ahead: int = 7,
        max_results: int = 50
    ) -> List[Dict]:
        """
        Fetch upcoming calendar events from Google Calendar.
        
        Args:
            user: User object with Google credentials
            days_ahead: Number of days to fetch events for
            max_results: Maximum number of events to return
        
        Returns:
            List of event dictionaries
        """
        
        try:
            service = self._get_calendar_service(user)
            
            # Calculate time range
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'  # RFC3339 format
            time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            # Fetch events
            events_result = service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            logger.info(f"Fetched {len(events)} events for user {user.id}")
            return [self._parse_event(event) for event in events]
            
        except HttpError as e:
            logger.error(f"Google Calendar API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch calendar events: {e}")
            raise
    
    def _parse_event(self, event: Dict) -> Dict:
        """Parse Google Calendar event into our format."""
        
        # Extract start and end times
        start = event.get('start', {})
        end = event.get('end', {})
        
        start_time = self._parse_datetime(start.get('dateTime') or start.get('date'))
        end_time = self._parse_datetime(end.get('dateTime') or end.get('date'))
        
        # Extract attendees
        attendees = []
        for attendee in event.get('attendees', []):
            attendees.append({
                'email': attendee.get('email'),
                'name': attendee.get('displayName', attendee.get('email')),
                'response_status': attendee.get('responseStatus', 'needsAction')
            })
        
        # Extract meeting link
        meeting_link = None
        conference_data = event.get('conferenceData', {})
        for entry_point in conference_data.get('entryPoints', []):
            if entry_point.get('entryPointType') == 'video':
                meeting_link = entry_point.get('uri')
                break
        
        # If no conference data, check for Zoom/Meet links in description
        if not meeting_link:
            description = event.get('description', '')
            meeting_link = self._extract_meeting_link(description)
        
        return {
            'event_id': event.get('id'),
            'title': event.get('summary', 'Untitled Event'),
            'description': event.get('description'),
            'start_time': start_time,
            'end_time': end_time,
            'location': event.get('location'),
            'meeting_link': meeting_link,
            'attendees': attendees,
            'organizer': event.get('organizer', {}).get('email'),
            'status': event.get('status', 'confirmed'),
            'recurrence': event.get('recurrence'),
            'html_link': event.get('htmlLink')
        }
    
    def _parse_datetime(self, dt_string: Optional[str]) -> Optional[datetime]:
        """Parse datetime string from Google Calendar."""
        
        if not dt_string:
            return None
        
        try:
            # Handle both datetime and date-only formats
            if 'T' in dt_string:
                # Full datetime - remove timezone suffix if present
                dt_clean = dt_string.split('+')[0].split('Z')[0]
                return datetime.fromisoformat(dt_clean)
            else:
                # Date only
                return datetime.fromisoformat(dt_string)
        except Exception as e:
            logger.error(f"Failed to parse datetime: {dt_string}, error: {e}")
            return None
    
    def _extract_meeting_link(self, description: str) -> Optional[str]:
        """Extract meeting link from description text."""
        
        if not description:
            return None
        
        import re
        
        # Common video conferencing URL patterns
        patterns = [
            r'https://[a-zA-Z0-9-]+\.zoom\.us/j/[0-9]+[^\s]*',
            r'https://meet\.google\.com/[a-zA-Z0-9-]+',
            r'https://teams\.microsoft\.com/l/meetup-join/[^\s]+',
            r'https://[a-zA-Z0-9-]+\.webex\.com/[^\s]+'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description)
            if match:
                return match.group(0)
        
        return None
    
    async def sync_event_to_meeting(
        self,
        event_data: Dict,
        user_id: UUID
    ) -> Dict:
        """
        Convert Google Calendar event to Meeting format.
        
        Args:
            event_data: Parsed event dictionary
            user_id: User ID
        
        Returns:
            Meeting data dictionary ready for database
        """
        
        return {
            'user_id': user_id,
            'event_id': event_data.get('event_id'),
            'title': event_data.get('title'),
            'description': event_data.get('description'),
            'start_time': event_data.get('start_time'),
            'end_time': event_data.get('end_time'),
            'location': event_data.get('location'),
            'meeting_link': event_data.get('meeting_link'),
            'attendees': [att['email'] for att in event_data.get('attendees', [])],
            'status': event_data.get('status'),
            'synced_at': datetime.utcnow()
        }
    
    async def create_event(
        self,
        user: User,
        event_data: Dict
    ) -> Dict:
        """
        Create a new event in Google Calendar.
        
        Args:
            user: User object with Google credentials
            event_data: Event details (title, description, start_time, end_time, attendees)
        
        Returns:
            Created event data
        """
        
        try:
            service = self._get_calendar_service(user)
            
            # Build event object
            event = {
                'summary': event_data.get('title'),
                'description': event_data.get('description'),
                'start': {
                    'dateTime': event_data.get('start_time').isoformat(),
                    'timeZone': user.timezone or 'UTC'
                },
                'end': {
                    'dateTime': event_data.get('end_time').isoformat(),
                    'timeZone': user.timezone or 'UTC'
                }
            }
            
            # Add attendees if provided
            if event_data.get('attendees'):
                event['attendees'] = [
                    {'email': email} for email in event_data.get('attendees', [])
                ]
            
            # Add meeting link if provided
            if event_data.get('meeting_link'):
                event['conferenceData'] = {
                    'createRequest': {'requestId': 'contextmeet-' + str(UUID)}
                }
            
            # Create the event
            created_event = service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1 if event_data.get('meeting_link') else 0
            ).execute()
            
            logger.info(f"Created calendar event: {created_event.get('id')}")
            return self._parse_event(created_event)
            
        except HttpError as e:
            logger.error(f"Failed to create calendar event: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            raise
    
    async def update_event(
        self,
        user: User,
        event_id: str,
        updates: Dict
    ) -> Dict:
        """Update an existing calendar event."""
        
        try:
            service = self._get_calendar_service(user)
            
            # Get existing event
            event = service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            # Apply updates
            if updates.get('title'):
                event['summary'] = updates['title']
            if updates.get('description') is not None:
                event['description'] = updates['description']
            if updates.get('start_time'):
                event['start']['dateTime'] = updates['start_time'].isoformat()
            if updates.get('end_time'):
                event['end']['dateTime'] = updates['end_time'].isoformat()
            
            # Update the event
            updated_event = service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            logger.info(f"Updated calendar event: {event_id}")
            return self._parse_event(updated_event)
            
        except HttpError as e:
            logger.error(f"Failed to update calendar event: {e}")
            raise
        except Exception as e:
            logger.error(f"Error updating event: {e}")
            raise
    
    async def delete_event(
        self,
        user: User,
        event_id: str
    ) -> bool:
        """Delete a calendar event."""
        
        try:
            service = self._get_calendar_service(user)
            
            service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            logger.info(f"Deleted calendar event: {event_id}")
            return True
            
        except HttpError as e:
            logger.error(f"Failed to delete calendar event: {e}")
            return False
        except Exception as e:
            logger.error(f"Error deleting event: {e}")
            return False


# Singleton instance
calendar_service = GoogleCalendarService()
