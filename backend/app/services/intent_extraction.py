"""
Intent Extraction Service
Uses Google Gemini to parse natural language into structured meeting data
"""
from datetime import datetime, timedelta
from typing import Dict, Any
import json
import logging
import google.generativeai as genai
import pytz

from app.config import settings
from app.schemas.intent import IntentSchema, ParticipantSchema, TimeWindowSchema

logger = logging.getLogger(__name__)


class IntentExtractionService:
    """Service for extracting structured intent from natural language"""
    
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def extract_intent(self, prompt: str, user_timezone: str = "UTC") -> IntentSchema:
        """
        Extract meeting intent from natural language prompt
        
        Args:
            prompt: Natural language scheduling request
            user_timezone: User's timezone string
            
        Returns:
            IntentSchema with extracted meeting details
        """
        system_prompt = self._build_system_prompt(user_timezone)
        full_prompt = f"{system_prompt}\n\nUser request: {prompt}"
        
        try:
            response = self.model.generate_content(full_prompt)
            
            # Extract JSON from response
            content = response.text
            
            # Try to parse JSON from the response
            json_data = self._extract_json(content)
            
            # Validate and create IntentSchema
            intent = self._validate_and_create_intent(json_data, user_timezone)
            
            logger.info(f"Successfully extracted intent from prompt: {prompt[:50]}...")
            return intent
            
        except Exception as e:
            logger.error(f"Failed to extract intent: {str(e)}")
            # Return default intent on failure
            return self._create_default_intent(prompt, user_timezone)
    
    def _build_system_prompt(self, user_timezone: str) -> str:
        """Build the system prompt for Claude"""
        return f"""You are an assistant that converts natural-language meeting requests into a strict JSON schema.

Return ONLY valid JSON with this exact structure:
{{
  "title": "string",
  "description": "string or null",
  "participants": [
    {{"email": "string or null", "name": "string or null"}}
  ],
  "duration_minutes": 30,
  "preferred_windows": [
    {{"start": "ISO8601 datetime", "end": "ISO8601 datetime"}}
  ]
}}

Rules:
1. If participant email is not provided but a name is present, return name and leave email null
2. If dates are vague, fill preferred_windows with next 5 working days 09:00-18:00 in timezone {user_timezone}
3. duration_minutes default is 30 if not specified
4. title should be a short summary of the meeting purpose
5. All datetimes must be in ISO8601 format with timezone
6. preferred_windows should cover reasonable business hours

Return ONLY the JSON, no other text."""
    
    def _extract_json(self, content: str) -> Dict[str, Any]:
        """Extract JSON from Claude's response"""
        # Try to find JSON in the response
        content = content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1]) if len(lines) > 2 else content
            if content.startswith("json"):
                content = content[4:].strip()
        
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise ValueError(f"Invalid JSON response from Claude: {content[:100]}")
    
    def _validate_and_create_intent(self, json_data: Dict[str, Any], user_timezone: str) -> IntentSchema:
        """Validate and create IntentSchema from JSON data"""
        # Parse participants
        participants = []
        for p in json_data.get("participants", []):
            participants.append(ParticipantSchema(
                email=p.get("email"),
                name=p.get("name")
            ))
        
        # Parse time windows
        windows = []
        for w in json_data.get("preferred_windows", []):
            windows.append(TimeWindowSchema(
                start=datetime.fromisoformat(w["start"]),
                end=datetime.fromisoformat(w["end"])
            ))
        
        # If no windows provided, create default
        if not windows:
            windows = self._create_default_windows(user_timezone)
        
        return IntentSchema(
            title=json_data.get("title", "Meeting"),
            description=json_data.get("description"),
            participants=participants,
            duration_minutes=json_data.get("duration_minutes", 30),
            preferred_windows=windows
        )
    
    def _create_default_windows(self, user_timezone: str) -> list[TimeWindowSchema]:
        """Create default time windows for next 5 working days"""
        windows = []
        # Handle timezone aliases (Calcutta -> Kolkata)
        timezone_aliases = {
            'Asia/Calcutta': 'Asia/Kolkata',
            'US/Eastern': 'America/New_York',
            'US/Pacific': 'America/Los_Angeles',
        }
        user_timezone = timezone_aliases.get(user_timezone, user_timezone)
        
        try:
            tz = pytz.timezone(user_timezone)
        except Exception as e:
            # Fallback to Asia/Kolkata if timezone is invalid
            logger.warning(f"Invalid timezone {user_timezone}, using Asia/Kolkata. Error: {e}")
            tz = pytz.timezone('Asia/Kolkata')
        
        current = datetime.now(tz).replace(hour=9, minute=0, second=0, microsecond=0)
        
        # Skip to next day if it's past business hours
        if datetime.now(tz).hour >= 18:
            current += timedelta(days=1)
        
        days_added = 0
        while days_added < 5:
            # Skip weekends
            if current.weekday() < 5:  # Monday = 0, Friday = 4
                start = current.replace(hour=9, minute=0)
                end = current.replace(hour=18, minute=0)
                windows.append(TimeWindowSchema(start=start, end=end))
                days_added += 1
            current += timedelta(days=1)
        
        return windows
    
    def _create_default_intent(self, prompt: str, user_timezone: str) -> IntentSchema:
        """Create a default intent when extraction fails"""
        return IntentSchema(
            title="Meeting",
            description=prompt[:200],
            participants=[ParticipantSchema(email=None, name="Participant")],
            duration_minutes=30,
            preferred_windows=self._create_default_windows(user_timezone)
        )
