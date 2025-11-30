"""
Generate Secret Keys
Helper script to generate SECRET_KEY and ENCRYPTION_KEY
"""
import secrets
from cryptography.fernet import Fernet

def generate_secret_key(length=64):
    """Generate a random secret key"""
    return secrets.token_urlsafe(length)

def generate_encryption_key():
    """Generate a Fernet encryption key"""
    return Fernet.generate_key().decode()

if __name__ == "__main__":
    print("=" * 60)
    print("SmartMeet - Secret Key Generator")
    print("=" * 60)
    print()
    print("Copy these values to your backend/.env file:")
    print()
    print(f"SECRET_KEY={generate_secret_key()}")
    print(f"ENCRYPTION_KEY={generate_encryption_key()}")
    print()
    print("=" * 60)
