"""
Slot Proposer Service
Finds and ranks available meeting time slots
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from uuid import UUID
import logging

from app.schemas.slot import SlotSchema
from app.schemas.intent import ParticipantSchema, TimeWindowSchema
from app.services.google_calendar import GoogleCalendarService

logger = logging.getLogger(__name__)


class SlotProposerService:
    """Service for proposing available meeting slots"""
    
    def __init__(self, calendar_service: GoogleCalendarService):
        self.calendar_service = calendar_service
    
    def find_slots(
        self,
        user_id: UUID,
        participants: List[ParticipantSchema],
        duration_minutes: int,
        preferred_windows: List[TimeWindowSchema]
    ) -> List[SlotSchema]:
        """
        Find available meeting slots
        
        Args:
            user_id: User UUID
            participants: List of meeting participants
            duration_minutes: Meeting duration in minutes
            preferred_windows: Preferred time windows
            
        Returns:
            List of 2-3 proposed slots, ranked by score
        """
        all_slots = []
        
        for window in preferred_windows:
            # Get busy periods for the user
            try:
                freebusy_data = self.calendar_service.get_freebusy(
                    user_id=user_id,
                    time_min=window.start,
                    time_max=window.end
                )
                
                busy_periods = self._extract_busy_periods(freebusy_data)
                
            except Exception as e:
                logger.warning(f"Failed to get FreeBusy data: {e}")
                busy_periods = []
            
            # Find free slots in this window
            window_slots = self._find_free_slots(
                window.start,
                window.end,
                busy_periods,
                duration_minutes
            )
            
            all_slots.extend(window_slots)
        
        # Score and rank slots
        scored_slots = [self._score_slot(slot, preferred_windows[0].start) for slot in all_slots]
        scored_slots.sort(key=lambda x: x.score, reverse=True)
        
        # Return top 2-3 slots
        return scored_slots[:3] if len(scored_slots) >= 3 else scored_slots[:2] if len(scored_slots) >= 2 else scored_slots
    
    def _extract_busy_periods(self, freebusy_data: Dict[str, Any]) -> List[Tuple[datetime, datetime]]:
        """Extract busy periods from FreeBusy API response"""
        busy_periods = []
        
        calendars = freebusy_data.get("calendars", {})
        for calendar_id, calendar_data in calendars.items():
            for busy in calendar_data.get("busy", []):
                start = datetime.fromisoformat(busy["start"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(busy["end"].replace("Z", "+00:00"))
                busy_periods.append((start, end))
        
        # Sort by start time
        busy_periods.sort(key=lambda x: x[0])
        
        return busy_periods
    
    def _find_free_slots(
        self,
        window_start: datetime,
        window_end: datetime,
        busy_periods: List[Tuple[datetime, datetime]],
        duration_minutes: int
    ) -> List[SlotSchema]:
        """Find free slots within a time window"""
        slots = []
        duration = timedelta(minutes=duration_minutes)
        
        # Start from the beginning of the window
        current = window_start
        
        # Align to 15-minute boundaries
        if current.minute % 15 != 0:
            current = current.replace(
                minute=(current.minute // 15 + 1) * 15,
                second=0,
                microsecond=0
            )
        
        while current + duration <= window_end:
            slot_end = current + duration
            
            # Check if this slot overlaps with any busy period
            is_free = True
            for busy_start, busy_end in busy_periods:
                if self._slots_overlap(current, slot_end, busy_start, busy_end):
                    is_free = False
                    # Jump to end of busy period
                    current = busy_end
                    # Align to next 15-minute boundary
                    if current.minute % 15 != 0:
                        current = current.replace(
                            minute=(current.minute // 15 + 1) * 15,
                            second=0,
                            microsecond=0
                        )
                    break
            
            if is_free:
                slots.append(SlotSchema(
                    start=current,
                    end=slot_end,
                    score=0.0,  # Will be scored later
                    conflicts=[]
                ))
                # Move to next 15-minute slot
                current += timedelta(minutes=15)
            
        return slots
    
    def _slots_overlap(
        self,
        slot_start: datetime,
        slot_end: datetime,
        busy_start: datetime,
        busy_end: datetime
    ) -> bool:
        """Check if two time periods overlap"""
        return slot_start < busy_end and slot_end > busy_start
    
    def _score_slot(self, slot: SlotSchema, reference_time: datetime) -> SlotSchema:
        """
        Score a slot based on various factors
        
        Scoring factors:
        - Earlier slots get higher scores
        - Slots closer to reference time get higher scores
        - Slots during typical business hours get higher scores
        """
        score = 1.0
        
        # Time of day preference (9 AM - 5 PM is ideal)
        hour = slot.start.hour
        if 9 <= hour < 17:
            score *= 1.0
        elif 8 <= hour < 9 or 17 <= hour < 18:
            score *= 0.9
        else:
            score *= 0.7
        
        # Proximity to reference time (sooner is better, but not too soon)
        time_diff = (slot.start - reference_time).total_seconds() / 3600  # hours
        if time_diff < 2:
            score *= 0.8  # Too soon
        elif time_diff < 24:
            score *= 1.0  # Same day is great
        elif time_diff < 48:
            score *= 0.95  # Next day is good
        else:
            score *= 0.9  # Further out is okay
        
        # Avoid Monday mornings and Friday afternoons
        weekday = slot.start.weekday()
        if weekday == 0 and hour < 10:  # Monday morning
            score *= 0.85
        elif weekday == 4 and hour >= 15:  # Friday afternoon
            score *= 0.85
        
        slot.score = min(score, 1.0)
        return slot
