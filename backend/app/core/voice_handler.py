"""
Voice Handler for Speech Recognition and Text-to-Speech
"""
import speech_recognition as sr
from gtts import gTTS
import io
import tempfile
import os
from typing import Optional, Tuple
import config


class VoiceHandler:
    """Handles voice input (speech-to-text) and voice output (text-to-speech)"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self._initialize_microphone()
    
    def _initialize_microphone(self):
        """Initialize microphone for speech recognition"""
        try:
            self.microphone = sr.Microphone()
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
        except Exception as e:
            print(f"Microphone initialization warning: {e}")
            self.microphone = None
    
    def speech_to_text(self, language: str = "en", timeout: int = 10) -> Tuple[bool, str]:
        """
        Convert speech to text
        Returns (success, text/error_message)
        """
        if not self.microphone:
            return False, "Microphone not available"
        
        # Map language codes to speech recognition codes
        speech_lang_map = {
            "en": "en-US",
            "es": "es-ES",
            "fr": "fr-FR",
            "de": "de-DE",
            "it": "it-IT",
            "pt": "pt-PT",
            "hi": "hi-IN",
            "zh": "zh-CN",
            "ja": "ja-JP",
            "ar": "ar-SA"
        }
        
        speech_lang = speech_lang_map.get(language, "en-US")
        
        try:
            with self.microphone as source:
                print("Listening...")
                # Listen with timeout
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                
            print("Processing speech...")
            
            # Try Google Speech Recognition first
            try:
                text = self.recognizer.recognize_google(audio, language=speech_lang)
                return True, text
            except sr.UnknownValueError:
                return False, "Could not understand audio. Please speak clearly."
            except sr.RequestError as e:
                # Fallback to Sphinx (offline) if available
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                    return True, text
                except:
                    return False, f"Speech recognition service error: {e}"
                    
        except sr.WaitTimeoutError:
            return False, "No speech detected. Please try again."
        except Exception as e:
            return False, f"Error recording audio: {str(e)}"
    
    def text_to_speech(self, text: str, language: str = "en", slow: bool = False) -> Optional[str]:
        """
        Convert text to speech and return audio file path
        Returns path to temporary audio file or None on error
        """
        # Map language codes to gTTS codes
        tts_lang_map = {
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
        
        tts_lang = tts_lang_map.get(language, "en")
        
        try:
            # Create TTS object
            tts = gTTS(text=text, lang=tts_lang, slow=slow)
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_file.close()
            
            tts.save(temp_file.name)
            return temp_file.name
            
        except Exception as e:
            print(f"TTS Error: {e}")
            return None
    
    def text_to_speech_bytes(self, text: str, language: str = "en") -> Optional[bytes]:
        """
        Convert text to speech and return audio bytes
        Useful for streaming or in-memory processing
        """
        tts_lang_map = {
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
        
        tts_lang = tts_lang_map.get(language, "en")
        
        try:
            tts = gTTS(text=text, lang=tts_lang)
            
            # Save to BytesIO object
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            
            return fp.read()
            
        except Exception as e:
            print(f"TTS Error: {e}")
            return None
    
    def is_microphone_available(self) -> bool:
        """Check if microphone is available"""
        return self.microphone is not None
    
    @staticmethod
    def get_available_microphones():
        """Get list of available microphone devices"""
        try:
            return sr.Microphone.list_microphone_names()
        except Exception as e:
            print(f"Error listing microphones: {e}")
            return []
    
    def cleanup_temp_file(self, file_path: str):
        """Clean up temporary audio file"""
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error cleaning up temp file: {e}")


# Alternative: ElevenLabs for premium voice (optional)
class ElevenLabsVoice:
    """Premium voice generation using ElevenLabs API (optional)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.enabled = bool(api_key)
    
    def text_to_speech(self, text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> Optional[bytes]:
        """
        Generate speech using ElevenLabs
        voice_id options:
        - 21m00Tcm4TlvDq8ikWAM: Rachel (default)
        - ErXwobaYiN019PkySvjV: Antoni
        - VR6AewLTigWG4xSOukaG: Arnold
        """
        if not self.enabled:
            return None
        
        try:
            from elevenlabs import generate, set_api_key
            
            set_api_key(self.api_key)
            audio = generate(text=text, voice=voice_id)
            
            return audio
            
        except Exception as e:
            print(f"ElevenLabs TTS Error: {e}")
            return None
