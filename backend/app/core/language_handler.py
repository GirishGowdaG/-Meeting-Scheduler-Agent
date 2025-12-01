"""
Language Handler for Multilingual Support
Handles language detection and translation
"""
from langdetect import detect, LangDetectException
from deep_translator import GoogleTranslator
from typing import Optional, Tuple
import config


class LanguageHandler:
    """Manages language detection, translation, and multilingual support"""
    
    def __init__(self):
        self.supported_languages = config.SUPPORTED_LANGUAGES
        self.default_language = config.DEFAULT_LANGUAGE
    
    def detect_language(self, text: str) -> str:
        """
        Detect language of input text
        Returns ISO 639-1 language code (e.g., 'en', 'es', 'fr')
        """
        try:
            detected = detect(text)
            
            # Map to our supported languages
            if detected in self.supported_languages:
                return detected
            
            # Handle language variants (e.g., en-us -> en)
            base_lang = detected.split('-')[0]
            if base_lang in self.supported_languages:
                return base_lang
            
            # Default to English if not supported
            return self.default_language
            
        except LangDetectException:
            return self.default_language
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        Translate text from source language to target language
        Returns translated text or None on error
        """
        # No translation needed if same language
        if source_lang == target_lang:
            return text
        
        # Map our codes to Google Translate codes
        lang_map = {
            "en": "en",
            "es": "es",
            "fr": "fr",
            "de": "de",
            "it": "it",
            "pt": "pt",
            "hi": "hi",
            "zh": "zh-CN",
            "ja": "ja",
            "ar": "ar"
        }
        
        src = lang_map.get(source_lang, "en")
        tgt = lang_map.get(target_lang, "en")
        
        try:
            translator = GoogleTranslator(source=src, target=tgt)
            translated = translator.translate(text)
            return translated
            
        except Exception as e:
            print(f"Translation error: {e}")
            return None
    
    def get_greeting(self, language: str) -> str:
        """Get greeting message in specified language"""
        greetings = {
            "en": "Hello! How can I assist you today?",
            "es": "¡Hola! ¿Cómo puedo ayudarte hoy?",
            "fr": "Bonjour! Comment puis-je vous aider aujourd'hui?",
            "de": "Hallo! Wie kann ich Ihnen heute helfen?",
            "it": "Ciao! Come posso aiutarti oggi?",
            "pt": "Olá! Como posso ajudá-lo hoje?",
            "hi": "नमस्ते! मैं आज आपकी कैसे मदद कर सकता हूं?",
            "zh": "你好！我今天能帮你什么忙？",
            "ja": "こんにちは！今日はどのようにお手伝いできますか？",
            "ar": "مرحبا! كيف يمكنني مساعدتك اليوم؟"
        }
        return greetings.get(language, greetings["en"])
    
    def get_language_name(self, code: str) -> str:
        """Get full language name from code"""
        return self.supported_languages.get(code, "English")
    
    def is_supported(self, language_code: str) -> bool:
        """Check if language is supported"""
        return language_code in self.supported_languages
    
    def get_voice_confirmation(self, language: str) -> str:
        """Get voice mode confirmation message"""
        messages = {
            "en": "Voice mode activated. Click 'Start Recording' to speak.",
            "es": "Modo de voz activado. Haga clic en 'Iniciar grabación' para hablar.",
            "fr": "Mode vocal activé. Cliquez sur 'Commencer l'enregistrement' pour parler.",
            "de": "Sprachmodus aktiviert. Klicken Sie auf 'Aufnahme starten', um zu sprechen.",
            "it": "Modalità vocale attivata. Fare clic su 'Avvia registrazione' per parlare.",
            "pt": "Modo de voz ativado. Clique em 'Iniciar gravação' para falar.",
            "hi": "वॉयस मोड सक्रिय। बोलने के लिए 'रिकॉर्डिंग शुरू करें' पर क्लिक करें।",
            "zh": "语音模式已激活。点击'开始录音'进行语音输入。",
            "ja": "音声モードが有効になりました。「録音開始」をクリックして話してください。",
            "ar": "تم تنشيط وضع الصوت. انقر فوق 'بدء التسجيل' للتحدث."
        }
        return messages.get(language, messages["en"])
    
    def get_all_supported_languages(self) -> dict:
        """Get dictionary of all supported languages"""
        return self.supported_languages.copy()
    
    def format_language_response(self, text: str, detected_lang: str, user_lang: str) -> Tuple[str, bool]:
        """
        Format response considering detected and user preferred language
        Returns (formatted_text, was_translated)
        """
        # If detected language matches user preference, no translation needed
        if detected_lang == user_lang:
            return text, False
        
        # Translate if needed
        translated = self.translate_text(text, detected_lang, user_lang)
        if translated:
            return translated, True
        
        # Return original if translation failed
        return text, False
