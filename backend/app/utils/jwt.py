"""
JWT Utilities
Token generation and validation for session management
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from uuid import UUID

from app.config import settings


def create_access_token(user_id: UUID, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        user_id: User UUID
        expires_delta: Optional expiration time delta
        
    Returns:
        JWT token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)
    
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[UUID]:
    """
    Decode and validate a JWT access token
    
    Args:
        token: JWT token string
        
    Returns:
        User UUID if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return UUID(user_id)
    except JWTError:
        return None
