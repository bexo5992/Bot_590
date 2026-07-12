# bot/utils/security.py
import secrets
import hashlib
from typing import Optional
from functools import wraps
from datetime import datetime, timedelta
from bot.utils.logger import logger

def generate_secure_code(length: int = 16) -> str:
    """توليد كود آمن"""
    return secrets.token_urlsafe(length)[:length]

def generate_link_code(length: int = 8) -> str:
    """توليد كود رابط (قابل للقراءة)"""
    import string
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def hash_data(data: str) -> str:
    """تشفير البيانات"""
    return hashlib.sha256(data.encode()).hexdigest()

def validate_file_size(file_size: int, max_size: int) -> bool:
    """التحقق من حجم الملف"""
    return file_size <= max_size

def validate_mime_type(mime_type: str, allowed_types: list) -> bool:
    """التحقق من نوع الملف"""
    return mime_type in allowed_types

def rate_limit(limit: int = 5, per_seconds: int = 60):
    """محدد سرعة الطلبات"""
    from collections import defaultdict
    from time import time
    
    requests = defaultdict(list)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # الحصول على user_id من args
            user_id = None
            for arg in args:
                if hasattr(arg, 'from_user'):
                    user_id = arg.from_user.id
                    break
            
            if not user_id:
                return func(*args, **kwargs)
            
            now = time()
            window_start = now - per_seconds
            
            # تنظيف الطلبات القديمة
            requests[user_id] = [t for t in requests[user_id] if t > window_start]
            
            # التحقق من الحد
            if len(requests[user_id]) >= limit:
                logger.warning(f"Rate limit exceeded for user {user_id}")
                return  # تجاهل الطلب
            
            requests[user_id].append(now)
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator
