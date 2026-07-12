# bot/utils/logger.py
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from bot.config import Config

def setup_logger(name: str = "bot") -> logging.Logger:
    """إعداد نظام التسجيل"""
    
    # إنشاء مجلد السجلات
    log_dir = Config.LOG_FILE.parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # تهيئة الـ Logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    # منع تكرار الـ Handlers
    if logger.handlers:
        return logger
    
    # تنسيق السجلات
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handlers
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # ملف السجلات مع Rotation
    file_handler = RotatingFileHandler(
        Config.LOG_FILE,
        maxBytes=10_485_760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logger()
