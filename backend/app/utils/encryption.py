"""
Encryption Utilities
AES-256 encryption for sensitive data like OAuth tokens
"""
from cryptography.fernet import Fernet
from app.config import settings
import base64


class EncryptionService:
    """Service for encrypting and decrypting sensitive data"""
    
    def __init__(self):
        # Ensure encryption key is properly formatted
        key = settings.encryption_key.encode() if isinstance(settings.encryption_key, str) else settings.encryption_key
        
        # If key is not base64 encoded, encode it
        try:
            base64.urlsafe_b64decode(key)
            self.cipher = Fernet(key)
        except Exception:
            # Generate a key from the provided string
            key = base64.urlsafe_b64encode(key.ljust(32)[:32])
            self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt a string
        
        Args:
            data: Plain text string to encrypt
            
        Returns:
            Encrypted string (base64 encoded)
        """
        if not data:
            return ""
        
        encrypted_bytes = self.cipher.encrypt(data.encode())
        return encrypted_bytes.decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt a string
        
        Args:
            encrypted_data: Encrypted string (base64 encoded)
            
        Returns:
            Decrypted plain text string
        """
        if not encrypted_data:
            return ""
        
        decrypted_bytes = self.cipher.decrypt(encrypted_data.encode())
        return decrypted_bytes.decode()


# Global encryption service instance
encryption_service = EncryptionService()
