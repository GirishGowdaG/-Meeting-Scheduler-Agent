"""
Meeting Service
Business logic for meeting management
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
import logging

from app.models.meeting import Meeting
from app.schemas.meeting import MeetingCreate, MeetingUpdate, MeetingSchema
from app.schemas.intent import IntentSchema

logger = logging.getLogger(__name__)


class MeetingService:
    """Service for meeting management operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_meeting(
        self,
        user_id: UUID,
        intent: IntentSchema,
        timezone: str
    ) -> Meeting:
        """
        Create a new meeting record with status 'proposed'
        
        Args:
            user_id: User UUID
            intent: Extracted meeting intent
            timezone: User's timezone
            
        Returns:
            Created Meeting object
        """
        # Convert participants to JSON-serializable format
        participants_data = [
            {"email": p.email, "name": p.name}
            for p in intent.participants
        ]
        
        meeting = Meeting(
            user_id=str(user_id),  # Convert UUID to string for SQLite
            title=intent.title,
            description=intent.description,
            participants=participants_data,
            duration_minutes=intent.duration_minutes,
            timezone=timezone,
            status="proposed"
        )
        
        self.db.add(meeting)
        self.db.commit()
        self.db.refresh(meeting)
        
        logger.info(f"Created meeting {meeting.id} for user {user_id}")
        return meeting
    
    def confirm_meeting(
        self,
        meeting_id: UUID,
        start_time: datetime,
        end_time: datetime,
        event_id: str
    ) -> Meeting:
        """
        Confirm a meeting with selected slot and event ID
        
        Args:
            meeting_id: Meeting UUID
            start_time: Meeting start time
            end_time: Meeting end time
            event_id: Google Calendar event ID
            
        Returns:
            Updated Meeting object
        """
        # Convert UUID to string for SQLite comparison
        meeting = self.db.query(Meeting).filter(Meeting.id == str(meeting_id)).first()
        
        if not meeting:
            raise ValueError(f"Meeting {meeting_id} not found")
        
        meeting.start_time = start_time
        meeting.end_time = end_time
        meeting.event_id = event_id
        meeting.status = "confirmed"
        meeting.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(meeting)
        
        logger.info(f"Confirmed meeting {meeting_id}")
        return meeting
    
    def cancel_meeting(self, meeting_id: UUID) -> Meeting:
        """
        Cancel a meeting
        
        Args:
            meeting_id: Meeting UUID
            
        Returns:
            Updated Meeting object
        """
        # Convert UUID to string for SQLite comparison
        meeting = self.db.query(Meeting).filter(Meeting.id == str(meeting_id)).first()
        
        if not meeting:
            raise ValueError(f"Meeting {meeting_id} not found")
        
        meeting.status = "cancelled"
        meeting.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(meeting)
        
        logger.info(f"Cancelled meeting {meeting_id}")
        return meeting
    
    def delete_meeting(self, meeting_id: UUID) -> bool:
        """
        Permanently delete a meeting from database
        
        Args:
            meeting_id: Meeting UUID
            
        Returns:
            True if deleted successfully
        """
        # Convert UUID to string for SQLite comparison
        meeting = self.db.query(Meeting).filter(Meeting.id == str(meeting_id)).first()
        
        if not meeting:
            raise ValueError(f"Meeting {meeting_id} not found")
        
        self.db.delete(meeting)
        self.db.commit()
        
        logger.info(f"Deleted meeting {meeting_id} from database")
        return True
    
    def get_user_meetings(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Meeting]:
        """
        Get meetings for a user
        
        Args:
            user_id: User UUID
            status: Optional status filter
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of Meeting objects
        """
        # Convert UUID to string for SQLite comparison
        query = self.db.query(Meeting).filter(Meeting.user_id == str(user_id))
        
        if status:
            query = query.filter(Meeting.status == status)
        
        meetings = query.order_by(Meeting.created_at.desc()).limit(limit).offset(offset).all()
        
        logger.info(f"Retrieved {len(meetings)} meetings for user {user_id}")
        return meetings
    
    def get_meeting_by_id(self, meeting_id: UUID) -> Optional[Meeting]:
        """
        Get a meeting by ID
        
        Args:
            meeting_id: Meeting UUID
            
        Returns:
            Meeting object or None
        """
        # Convert UUID to string for SQLite comparison
        return self.db.query(Meeting).filter(Meeting.id == str(meeting_id)).first()
