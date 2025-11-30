"""
Scheduling Routes
Intent parsing, slot proposal, and event creation endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timedelta
import logging

from app.database import get_db
from app.schemas.intent import ParseIntentRequest, ParseIntentResponse
from app.schemas.slot import ProposeSlotsRequest, ProposeSlotsResponse
from app.schemas.meeting import CreateEventRequest, CreateEventResponse
from app.services.intent_extraction import IntentExtractionService
from app.services.google_calendar import GoogleCalendarService
from app.services.slot_proposer import SlotProposerService
from app.services.meeting import MeetingService
from app.utils.jwt import decode_access_token

router = APIRouter()
logger = logging.getLogger(__name__)


def get_current_user_id(request: Request) -> UUID:
    """Dependency to get current user ID from JWT"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = auth_header.split(" ")[1]
    user_id = decode_access_token(token)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user_id


@router.post("/parse-intent", response_model=ParseIntentResponse)
async def parse_intent(
    request_data: ParseIntentRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Parse natural language scheduling request into structured intent
    
    Uses Claude Sonnet 4.5 to extract:
    - Meeting title and description
    - Participants (emails/names)
    - Duration
    - Preferred time windows
    """
    try:
        intent_service = IntentExtractionService()
        
        intent = intent_service.extract_intent(
            prompt=request_data.prompt,
            user_timezone=request_data.user_timezone
        )
        
        # Create a meeting record with status 'proposed'
        meeting_service = MeetingService(db)
        meeting = meeting_service.create_meeting(
            user_id=user_id,
            intent=intent,
            timezone=request_data.user_timezone
        )
        
        logger.info(f"Parsed intent and created meeting {meeting.id} for user {user_id}")
        
        return intent
        
    except Exception as e:
        logger.error(f"Failed to parse intent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to parse intent: {str(e)}")


@router.post("/propose-slots", response_model=ProposeSlotsResponse)
async def propose_slots(
    request_data: ProposeSlotsRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Propose 2-3 available time slots based on calendar availability
    
    Checks user's Google Calendar FreeBusy data and finds optimal slots
    """
    try:
        calendar_service = GoogleCalendarService(db)
        slot_proposer = SlotProposerService(calendar_service)
        
        slots = slot_proposer.find_slots(
            user_id=user_id,
            participants=request_data.participants,
            duration_minutes=request_data.duration_minutes,
            preferred_windows=request_data.preferred_windows
        )
        
        logger.info(f"Proposed {len(slots)} slots for user {user_id}")
        
        return ProposeSlotsResponse(slots=slots)
        
    except Exception as e:
        logger.error(f"Failed to propose slots: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to propose slots: {str(e)}")


@router.get("/day-availability")
async def get_day_availability(
    date: str,
    timezone: str = "UTC",
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get hourly availability for a specific day (9 AM - 6 PM in user's timezone)
    Returns list of hourly slots with busy/free status
    """
    try:
        import pytz
        
        calendar_service = GoogleCalendarService(db)
        
        # Parse the date string (YYYY-MM-DD format)
        date_parts = date.split('T')[0]  # Get just the date part
        year, month, day = map(int, date_parts.split('-'))
        
        # Create timezone-aware datetime for the user's timezone
        user_tz = pytz.timezone(timezone)
        
        # Generate hourly slots from 9 AM to 6 PM in user's timezone
        slots = []
        for hour in range(9, 18):  # 9 AM to 6 PM (18 is exclusive, so last slot is 5-6 PM)
            # Create datetime in user's timezone
            slot_start = user_tz.localize(datetime(year, month, day, hour, 0, 0))
            slot_end = slot_start + timedelta(hours=1)
            
            # Convert to UTC for calendar API
            slot_start_utc = slot_start.astimezone(pytz.UTC)
            slot_end_utc = slot_end.astimezone(pytz.UTC)
            
            # Get event details for this slot
            events = calendar_service.get_events_in_slot(
                user_id=user_id,
                start_time=slot_start_utc,
                end_time=slot_end_utc
            )
            
            # Calculate busy and free time within the hour
            is_busy = len(events) > 0
            busy_minutes = 0
            free_minutes = 60
            free_periods = []
            
            if events:
                # Sort events by start time
                sorted_events = sorted(events, key=lambda e: e["start"])
                
                # Find free periods between events
                current_time = slot_start_utc
                
                for event in sorted_events:
                    event_start = datetime.fromisoformat(event["start"].replace('Z', '+00:00'))
                    event_end = datetime.fromisoformat(event["end"].replace('Z', '+00:00'))
                    
                    # Clip to slot boundaries
                    event_start = max(event_start, slot_start_utc)
                    event_end = min(event_end, slot_end_utc)
                    
                    # Check if there's free time before this event
                    if current_time < event_start:
                        free_start = current_time.astimezone(user_tz)
                        free_end = event_start.astimezone(user_tz)
                        free_duration = (event_start - current_time).total_seconds() / 60
                        free_periods.append({
                            "start": free_start.isoformat(),
                            "end": free_end.isoformat(),
                            "duration_minutes": int(free_duration)
                        })
                    
                    # Update current time and busy minutes
                    duration = (event_end - event_start).total_seconds() / 60
                    busy_minutes += duration
                    current_time = max(current_time, event_end)
                
                # Check if there's free time after the last event
                if current_time < slot_end_utc:
                    free_start = current_time.astimezone(user_tz)
                    free_end = slot_end_utc.astimezone(user_tz)
                    free_duration = (slot_end_utc - current_time).total_seconds() / 60
                    free_periods.append({
                        "start": free_start.isoformat(),
                        "end": free_end.isoformat(),
                        "duration_minutes": int(free_duration)
                    })
                
                free_minutes = 60 - busy_minutes
            else:
                # Entire hour is free
                free_periods.append({
                    "start": slot_start.isoformat(),
                    "end": slot_end.isoformat(),
                    "duration_minutes": 60
                })
            
            # Determine status
            if busy_minutes == 0:
                status = "available"
            elif busy_minutes >= 60:
                status = "busy"
            else:
                status = "partial"
            
            slots.append({
                "start": slot_start.isoformat(),  # Return in user's timezone
                "end": slot_end.isoformat(),
                "is_busy": is_busy,
                "status": status,
                "busy_minutes": int(busy_minutes),
                "free_minutes": int(free_minutes),
                "free_periods": free_periods,
                "hour": hour,
                "events": events
            })
        
        logger.info(f"Retrieved day availability for user {user_id} on {date} in {timezone}")
        return {"slots": slots}
        
    except Exception as e:
        logger.error(f"Failed to get day availability: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get day availability: {str(e)}")


@router.delete("/delete-event/{event_id}")
async def delete_event(
    event_id: str,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete a Google Calendar event and associated meeting record
    """
    try:
        calendar_service = GoogleCalendarService(db)
        meeting_service = MeetingService(db)
        
        # Delete from Google Calendar
        success = calendar_service.delete_event(
            user_id=user_id,
            event_id=event_id
        )
        
        if success:
            # Find and delete the meeting record from database
            from app.models.meeting import Meeting
            meeting = db.query(Meeting).filter(
                Meeting.event_id == event_id,
                Meeting.user_id == str(user_id)
            ).first()
            
            if meeting:
                meeting_service.delete_meeting(UUID(meeting.id))
                logger.info(f"Deleted event {event_id} and meeting {meeting.id} for user {user_id}")
            else:
                logger.info(f"Deleted event {event_id} for user {user_id} (no meeting record found)")
            
            return {"success": True, "message": "Event deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete event")
        
    except Exception as e:
        logger.error(f"Failed to delete event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete event: {str(e)}")


@router.post("/create-event", response_model=CreateEventResponse)
async def create_event(
    request_data: CreateEventRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Create a Google Calendar event with selected slot
    
    Creates event with:
    - All participants as attendees
    - Google Meet conference link
    - Email invitations sent automatically
    """
    try:
        calendar_service = GoogleCalendarService(db)
        meeting_service = MeetingService(db)
        
        # Prepare attendees list
        attendees = [
            {"email": p.email} for p in request_data.participants if p.email
        ]
        
        # Datetime strings come from frontend (naive datetime - no timezone)
        # Use GMT+5:30 (Asia/Kolkata) timezone
        start_str = str(request_data.slot.start)
        end_str = str(request_data.slot.end)
        
        # Create Google Calendar event with GMT+5:30 timezone
        # This ensures 9 AM is interpreted as 9 AM GMT+5:30
        event = calendar_service.create_event(
            user_id=user_id,
            title=request_data.title,
            description=request_data.description,
            start_time=start_str,
            end_time=end_str,
            attendees=attendees,
            timezone="Asia/Kolkata"  # GMT+5:30
        )
        
        event_id = event["id"]
        # Use the htmlLink from Google Calendar API response, or construct a proper link
        calendar_link = event.get("htmlLink")
        if not calendar_link:
            # Fallback: use the event ID in the proper format
            calendar_link = f"https://calendar.google.com/calendar/u/0/r/eventedit/{event_id}"
        
        # Parse datetime strings to datetime objects for database
        if isinstance(request_data.slot.start, str):
            start_dt_db = datetime.fromisoformat(request_data.slot.start.replace('Z', '+00:00'))
            end_dt_db = datetime.fromisoformat(request_data.slot.end.replace('Z', '+00:00'))
        else:
            start_dt_db = request_data.slot.start
            end_dt_db = request_data.slot.end
        
        # Create or update meeting record
        if request_data.meeting_id:
            meeting = meeting_service.confirm_meeting(
                meeting_id=request_data.meeting_id,
                start_time=start_dt_db,
                end_time=end_dt_db,
                event_id=event_id
            )
        else:
            # Create new meeting if no ID provided
            from app.schemas.intent import IntentSchema, TimeWindowSchema
            
            # Parse datetime strings if needed
            if isinstance(request_data.slot.start, str):
                start_dt = datetime.fromisoformat(request_data.slot.start.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(request_data.slot.end.replace('Z', '+00:00'))
            else:
                start_dt = request_data.slot.start
                end_dt = request_data.slot.end
            
            # Create a time window from the selected slot
            time_window = TimeWindowSchema(
                start=start_dt,
                end=end_dt
            )
            intent = IntentSchema(
                title=request_data.title,
                description=request_data.description,
                participants=request_data.participants,
                duration_minutes=int((end_dt - start_dt).total_seconds() / 60),
                preferred_windows=[time_window]
            )
            meeting = meeting_service.create_meeting(
                user_id=user_id,
                intent=intent,
                timezone="UTC"
            )
            meeting = meeting_service.confirm_meeting(
                meeting_id=meeting.id,
                start_time=start_dt_db,
                end_time=end_dt_db,
                event_id=event_id
            )
        
        logger.info(f"Created event {event_id} and confirmed meeting {meeting.id}")
        
        return CreateEventResponse(
            event_id=event_id,
            calendar_link=calendar_link,
            meeting_id=meeting.id
        )
        
    except Exception as e:
        logger.error(f"Failed to create event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")
