"""
AuthToken Model
Stores encrypted OAuth tokens for users
"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class AuthToken(Base):
    """AuthToken model for storing encrypted OAuth credentials"""
    
    __tablename__ = "auth_tokens"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(50), nullable=False, default="google")
    access_token = Column(String, nullable=False)  # Encrypted
    refresh_token = Column(String, nullable=False)  # Encrypted
    token_expiry = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="auth_tokens")
    
    def __repr__(self):
        return f"<AuthToken(id={self.id}, user_id={self.user_id}, provider={self.provider})>"
