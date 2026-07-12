# bot/config.py
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# تحديد المسار الأساسي
BASE_DIR = Path(__file__).resolve().parent.parent

# تحميل .env
load_dotenv(BASE_DIR / '.env')

class Config:
    """إعدادات البوت"""
    
    # التوكنات
    MAIN_BOT_TOKEN: str = os.getenv("MAIN_BOT_TOKEN", "")
    DB_BOT_TOKEN: str = os.getenv("DB_BOT_TOKEN", "")
    
    # الأدمن
    ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))
    GROUP_CHAT_ID: int = int(os.getenv("GROUP_CHAT_ID", "0"))
    
    # قاعدة البيانات
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///data/bot.db")
    
    # إعدادات الأداء
    MAX_THREADS: int = int(os.getenv("MAX_THREADS", "10"))
    RATE_LIMIT: int = int(os.getenv("RATE_LIMIT", "5"))  # رسائل في الدقيقة
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "100"))
    
    # إعدادات الأمان
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    
    # إعدادات السجلات
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Path = BASE_DIR / "logs" / "bot.log"
    
    @classmethod
    def validate(cls) -> bool:
        """التحقق من صحة الإعدادات"""
        errors = []
        
        if not cls.MAIN_BOT_TOKEN:
            errors.append("MAIN_BOT_TOKEN is required")
        if not cls.DB_BOT_TOKEN:
            errors.append("DB_BOT_TOKEN is required")
        if not cls.ADMIN_ID:
            errors.append("ADMIN_ID is required")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True
    
    @classmethod
    def is_admin(cls, user_id: int) -> bool:
        """التحقق من صلاحيات الأدمن"""
        return user_id == cls.ADMIN_ID

# التحقق من الإعدادات عند التحميل
Config.validate()
