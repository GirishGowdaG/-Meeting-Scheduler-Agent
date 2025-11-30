"""
Authentication Routes
Google OAuth 2.0 login and callback handlers
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import logging

from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.auth_token import AuthToken
from app.utils.encryption import encryption_service
from app.utils.jwt import create_access_token
from app.schemas.user import UserSchema

router = APIRouter()
logger = logging.getLogger(__name__)

# OAuth scopes
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events"
]


@router.get("/google/login")
async def google_login():
    """
    Initiate Google OAuth flow
    Returns authorization URL for user to visit
    """
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.google_redirect_uri]
            }
        },
        scopes=SCOPES,
        redirect_uri=settings.google_redirect_uri
    )
    
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    
    logger.info("Generated OAuth authorization URL")
    
    return {
        "auth_url": authorization_url,
        "state": state
    }


@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth callback
    Exchange authorization code for tokens and create/update user
    """
    try:
        # Exchange authorization code for tokens
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.google_redirect_uri]
                }
            },
            scopes=SCOPES,
            redirect_uri=settings.google_redirect_uri,
            state=state
        )
        
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Get user info from Google
        service = build("oauth2", "v2", credentials=credentials)
        user_info = service.userinfo().get().execute()
        
        email = user_info.get("email")
        name = user_info.get("name")
        
        # Create or update user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(email=email, name=name)
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created new user: {email}")
        else:
            user.name = name
            user.updated_at = datetime.utcnow()
            db.commit()
            logger.info(f"Updated existing user: {email}")
        
        # Store or update auth tokens (user.id is already a string in SQLite)
        auth_token = db.query(AuthToken).filter(
            AuthToken.user_id == user.id,
            AuthToken.provider == "google"
        ).first()
        
        # Encrypt tokens before storing
        encrypted_access = encryption_service.encrypt(credentials.token)
        encrypted_refresh = encryption_service.encrypt(credentials.refresh_token)
        
        if not auth_token:
            auth_token = AuthToken(
                user_id=user.id,
                provider="google",
                access_token=encrypted_access,
                refresh_token=encrypted_refresh,
                token_expiry=credentials.expiry
            )
            db.add(auth_token)
        else:
            auth_token.access_token = encrypted_access
            auth_token.refresh_token = encrypted_refresh
            auth_token.token_expiry = credentials.expiry
            auth_token.updated_at = datetime.utcnow()
        
        db.commit()
        logger.info(f"Stored auth tokens for user {user.id}")
        
        # Create JWT for session
        jwt_token = create_access_token(user.id)
        
        # Redirect to frontend with token
        redirect_url = f"{settings.frontend_url}/auth/callback?token={jwt_token}"
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}")
        error_url = f"{settings.frontend_url}/auth/error?message={str(e)}"
        return RedirectResponse(url=error_url)


@router.get("/me", response_model=UserSchema)
async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user
    Requires JWT token in Authorization header
    """
    from app.utils.jwt import decode_access_token
    
    # Get token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = auth_header.split(" ")[1]
    user_id = decode_access_token(token)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Convert UUID to string for SQLite comparison
    user = db.query(User).filter(User.id == str(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user
