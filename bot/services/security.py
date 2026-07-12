# bot/services/security.py
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from bot.utils.logger import logger

class SecurityService:
    """خدمة الأمان"""
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """توليد توكن آمن"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """تشفير كلمة المرور"""
        salt = secrets.token_hex(16)
        return f"{salt}:{hashlib.sha256((salt + password).encode()).hexdigest()}"
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """التحقق من كلمة المرور"""
        salt, hash_value = hashed.split(':')
        return hash_value == hashlib.sha256((salt + password).encode()).hexdigest()
    
    @staticmethod
    def validate_session(token: str, expiry: datetime) -> bool:
        """التحقق من صحة الجلسة"""
        return datetime.now() < expiry
