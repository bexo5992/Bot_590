# bot/utils/helpers.py
import re
from datetime import datetime
from typing import Optional, List, Dict
import html

def sanitize_text(text: str) -> str:
    """تنظيف النص من الـ HTML"""
    return html.escape(text)

def validate_phone(phone: str) -> bool:
    """التحقق من صحة رقم الهاتف"""
    pattern = r'^\+?[1-9]\d{1,14}$'
    return bool(re.match(pattern, phone))

def format_date(date: datetime) -> str:
    """تنسيق التاريخ"""
    return date.strftime('%Y-%m-%d %H:%M:%S')

def chunk_text(text: str, chunk_size: int = 4000) -> List[str]:
    """تقسيم النص إلى أجزاء صغيرة"""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def extract_user_id(text: str) -> Optional[int]:
    """استخراج معرف المستخدم من النص"""
    matches = re.findall(r'\d+', text)
    return int(matches[0]) if matches else None
