"""
Configuration settings for the AI Support Assistant
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# Language Settings
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")
SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "hi": "Hindi",
    "zh": "Chinese",
    "ja": "Japanese",
    "ar": "Arabic"
}

# AI Model Settings
AI_MODEL = "gpt-4-turbo-preview"
TEMPERATURE = 0.7
MAX_TOKENS = 500

# Voice Settings
VOICE_SPEED = 1.0
VOICE_ENABLED = True

# FAQ Categories
FAQ_CATEGORIES = [
    "General Information",
    "Technical Support",
    "Billing & Payments",
    "Account Management",
    "Product Features",
    "Troubleshooting"
]

# Escalation Keywords
ESCALATION_KEYWORDS = [
    "speak to human",
    "talk to agent",
    "customer service",
    "manager",
    "escalate",
    "complaint",
    "urgent",
    "legal",
    "refund request"
]
