"""
Meeting Model
Stores meeting scheduling requests and confirmed events
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, CheckConstraint, Text
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base
from app.config import settings


class Meeting(Base):
    """Meeting model for storing scheduling requests and events"""
    
    __tablename__ = "meetings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    # Use JSON for SQLite
    participants = Column(JSON, nullable=False)
    
    duration_minutes = Column(Integer, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    timezone = Column(String(100), nullable=False)
    event_id = Column(String(255), nullable=True)  # Google Calendar event ID
    status = Column(String(50), nullable=False, default="proposed", index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('proposed', 'confirmed', 'cancelled')", name="check_status"),
        CheckConstraint("duration_minutes > 0", name="check_duration_positive"),
    )
    
    # Relationships
    user = relationship("User", back_populates="meetings")
    
    def __repr__(self):
        return f"<Meeting(id={self.id}, title={self.title}, status={self.status})>"
