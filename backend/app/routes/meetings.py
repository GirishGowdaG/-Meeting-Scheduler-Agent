"""
Meetings Routes
Meeting history and management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import logging

from app.database import get_db
from app.schemas.meeting import MeetingSchema
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


@router.get("/meetings/history", response_model=List[MeetingSchema])
async def get_meetings_history(
    status: Optional[str] = Query(None, description="Filter by status (proposed, confirmed, cancelled)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get meeting history for authenticated user
    
    Returns list of meetings ordered by creation date (most recent first)
    Supports filtering by status and pagination
    """
    try:
        meeting_service = MeetingService(db)
        
        meetings = meeting_service.get_user_meetings(
            user_id=user_id,
            status=status,
            limit=limit,
            offset=offset
        )
        
        logger.info(f"Retrieved {len(meetings)} meetings for user {user_id}")
        
        return meetings
        
    except Exception as e:
        logger.error(f"Failed to get meetings history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get meetings history: {str(e)}")


@router.get("/meetings/{meeting_id}", response_model=MeetingSchema)
async def get_meeting(
    meeting_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get a specific meeting by ID
    
    Only returns meeting if it belongs to the authenticated user
    """
    try:
        meeting_service = MeetingService(db)
        meeting = meeting_service.get_meeting_by_id(meeting_id)
        
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        # Verify meeting belongs to user (convert to string for comparison with SQLite)
        if str(meeting.user_id) != str(user_id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        logger.info(f"Retrieved meeting {meeting_id} for user {user_id}")
        
        return meeting
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get meeting: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get meeting: {str(e)}")


@router.delete("/meetings/{meeting_id}")
async def cancel_meeting(
    meeting_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Cancel a meeting
    
    Updates meeting status to 'cancelled'
    Note: Does not delete the Google Calendar event
    """
    try:
        meeting_service = MeetingService(db)
        meeting = meeting_service.get_meeting_by_id(meeting_id)
        
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        # Verify meeting belongs to user (convert to string for comparison with SQLite)
        if str(meeting.user_id) != str(user_id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        cancelled_meeting = meeting_service.cancel_meeting(meeting_id)
        
        logger.info(f"Cancelled meeting {meeting_id} for user {user_id}")
        
        return {
            "message": "Meeting cancelled successfully",
            "meeting_id": str(meeting_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel meeting: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel meeting: {str(e)}")
