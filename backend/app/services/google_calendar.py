"""
Google Calendar Service
Handles all interactions with Google Calendar API
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.auth_token import AuthToken
from app.utils.encryption import encryption_service
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class GoogleCalendarService:
    """Service for Google Calendar API operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _get_credentials(self, user_id: UUID) -> Optional[Credentials]:
        """
        Get Google OAuth credentials for a user
        
        Args:
            user_id: User UUID
            
        Returns:
            Google OAuth2 Credentials object or None
        """
        # Convert UUID to string for SQLite comparison
        auth_token = self.db.query(AuthToken).filter(
            AuthToken.user_id == str(user_id),
            AuthToken.provider == "google"
        ).first()
        
        if not auth_token:
            return None
        
        # Decrypt tokens
        access_token = encryption_service.decrypt(auth_token.access_token)
        refresh_token = encryption_service.decrypt(auth_token.refresh_token)
        
        credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
            scopes=[
                "openid",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/calendar.readonly",
                "https://www.googleapis.com/auth/calendar.events"
            ]
        )
        
        # Check if token needs refresh
        if auth_token.token_expiry <= datetime.utcnow():
            credentials = self.refresh_token(user_id)
        
        return credentials
    
    def refresh_token(self, user_id: UUID) -> Optional[Credentials]:
        """
        Refresh expired access token
        
        Args:
            user_id: User UUID
            
        Returns:
            Updated Credentials object or None
        """
        # Convert UUID to string for SQLite comparison
        auth_token = self.db.query(AuthToken).filter(
            AuthToken.user_id == str(user_id),
            AuthToken.provider == "google"
        ).first()
        
        if not auth_token:
            return None
        
        try:
            from google.auth.transport.requests import Request
            
            refresh_token = encryption_service.decrypt(auth_token.refresh_token)
            
            credentials = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.google_client_id,
                client_secret=settings.google_client_secret
            )
            
            # Refresh the token with a proper Request object
            credentials.refresh(Request())
            
            # Update stored tokens
            auth_token.access_token = encryption_service.encrypt(credentials.token)
            auth_token.token_expiry = credentials.expiry
            self.db.commit()
            
            logger.info(f"Refreshed token for user {user_id}")
            return credentials
            
        except Exception as e:
            logger.error(f"Failed to refresh token for user {user_id}: {str(e)}")
            return None
    
    def get_freebusy(
        self,
        user_id: UUID,
        time_min: datetime,
        time_max: datetime,
        calendars: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Query FreeBusy information from Google Calendar
        
        Args:
            user_id: User UUID
            time_min: Start of time range
            time_max: End of time range
            calendars: List of calendar IDs (default: primary)
            
        Returns:
            FreeBusy data dictionary
        """
        credentials = self._get_credentials(user_id)
        if not credentials:
            raise ValueError("No valid credentials found for user")
        
        try:
            service = build("calendar", "v3", credentials=credentials)
            
            if calendars is None:
                calendars = ["primary"]
            
            body = {
                "timeMin": time_min.isoformat(),
                "timeMax": time_max.isoformat(),
                "items": [{"id": cal} for cal in calendars]
            }
            
            freebusy_result = service.freebusy().query(body=body).execute()
            
            logger.info(f"Retrieved FreeBusy data for user {user_id}")
            return freebusy_result
            
        except HttpError as e:
            logger.error(f"Google Calendar API error: {str(e)}")
            raise
    
    def check_slot_busy(
        self,
        user_id: UUID,
        start_time: datetime,
        end_time: datetime
    ) -> bool:
        """
        Check if a specific time slot is busy
        
        Args:
            user_id: User UUID
            start_time: Slot start time
            end_time: Slot end time
            
        Returns:
            True if slot has any busy periods, False if free
        """
        try:
            freebusy_data = self.get_freebusy(user_id, start_time, end_time)
            
            # Check if there are any busy periods in the primary calendar
            busy_periods = freebusy_data.get("calendars", {}).get("primary", {}).get("busy", [])
            
            return len(busy_periods) > 0
            
        except Exception as e:
            logger.error(f"Failed to check slot busy status: {str(e)}")
            # Default to not busy if check fails
            return False
    
    def get_events_in_slot(
        self,
        user_id: UUID,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get all events in a specific time slot
        
        Args:
            user_id: User UUID
            start_time: Slot start time
            end_time: Slot end time
            
        Returns:
            List of event dictionaries with title, description, attendees
        """
        credentials = self._get_credentials(user_id)
        if not credentials:
            return []
        
        try:
            service = build("calendar", "v3", credentials=credentials)
            
            events_result = service.events().list(
                calendarId="primary",
                timeMin=start_time.isoformat(),
                timeMax=end_time.isoformat(),
                singleEvents=True,
                orderBy="startTime"
            ).execute()
            
            events = events_result.get("items", [])
            
            event_details = []
            for event in events:
                event_details.append({
                    "id": event.get("id", ""),
                    "title": event.get("summary", "No Title"),
                    "description": event.get("description", ""),
                    "start": event.get("start", {}).get("dateTime", ""),
                    "end": event.get("end", {}).get("dateTime", ""),
                    "attendees": [att.get("email", "") for att in event.get("attendees", [])],
                    "location": event.get("location", ""),
                    "htmlLink": event.get("htmlLink", "")
                })
            
            return event_details
            
        except Exception as e:
            logger.error(f"Failed to get events in slot: {str(e)}")
            return []
    
    def create_event(
        self,
        user_id: UUID,
        title: str,
        description: Optional[str],
        start_time,  # Can be datetime or string
        end_time,  # Can be datetime or string
        attendees: List[Dict[str, str]],
        timezone: str = "UTC"
    ) -> Dict[str, Any]:
        """
        Create a Google Calendar event
        
        Args:
            user_id: User UUID
            title: Event title
            description: Event description
            start_time: Event start time
            end_time: Event end time
            attendees: List of attendee dicts with 'email' key
            timezone: Timezone string
            
        Returns:
            Created event data
        """
        credentials = self._get_credentials(user_id)
        if not credentials:
            raise ValueError("No valid credentials found for user")
        
        try:
            service = build("calendar", "v3", credentials=credentials)
            
            # Handle both datetime objects and strings
            start_dt_str = start_time.isoformat() if hasattr(start_time, 'isoformat') else str(start_time)
            end_dt_str = end_time.isoformat() if hasattr(end_time, 'isoformat') else str(end_time)
            
            # Remove any timezone info from the string to treat it as "floating time"
            # This ensures 9 AM in the UI = 9 AM in Google Calendar
            start_dt_str = start_dt_str.split('+')[0].split('Z')[0]
            end_dt_str = end_dt_str.split('+')[0].split('Z')[0]
            
            logger.info(f"Creating event with start: {start_dt_str}, end: {end_dt_str}, timezone: {timezone}")
            
            # Build start/end objects with explicit timezone
            # Google Calendar will interpret this as "9 AM in the specified timezone"
            start_obj = {"dateTime": start_dt_str, "timeZone": timezone if timezone else "UTC"}
            end_obj = {"dateTime": end_dt_str, "timeZone": timezone if timezone else "UTC"}
            
            event = {
                "summary": title,
                "description": description or "",
                "start": start_obj,
                "end": end_obj,
                "attendees": attendees,
                "conferenceData": {
                    "createRequest": {
                        "requestId": f"meet-{user_id}-{int(datetime.utcnow().timestamp())}",
                        "conferenceSolutionKey": {"type": "hangoutsMeet"}
                    }
                },
                "reminders": {
                    "useDefault": True
                }
            }
            
            created_event = service.events().insert(
                calendarId="primary",
                body=event,
                conferenceDataVersion=1,
                sendUpdates="all"
            ).execute()
            
            logger.info(f"Created event {created_event['id']} for user {user_id}")
            return created_event
            
        except HttpError as e:
            logger.error(f"Failed to create event: {str(e)}")
            raise
    
    def delete_event(
        self,
        user_id: UUID,
        event_id: str
    ) -> bool:
        """
        Delete a Google Calendar event
        
        Args:
            user_id: User UUID
            event_id: Google Calendar event ID
            
        Returns:
            True if deleted successfully, False otherwise
        """
        credentials = self._get_credentials(user_id)
        if not credentials:
            raise ValueError("No valid credentials found for user")
        
        try:
            service = build("calendar", "v3", credentials=credentials)
            
            service.events().delete(
                calendarId="primary",
                eventId=event_id,
                sendUpdates="all"  # Send cancellation emails to attendees
            ).execute()
            
            logger.info(f"Deleted event {event_id} for user {user_id}")
            return True
            
        except HttpError as e:
            # If event is already deleted (410), consider it a success
            if e.resp.status == 410:
                logger.info(f"Event {event_id} was already deleted")
                return True
            # If event not found (404), also consider it a success
            elif e.resp.status == 404:
                logger.info(f"Event {event_id} not found (already deleted)")
                return True
            else:
                logger.error(f"Failed to delete event: {str(e)}")
                return False
