# bot/middlewares/auth.py
from functools import wraps
from telegram import Update
from bot.config import Config
from bot.utils.logger import logger

def admin_required(func):
    """Decorator للتحقق من صلاحيات الأدمن"""
    @wraps(func)
    async def wrapper(update: Update, *args, **kwargs):
        user_id = update.effective_user.id
        
        if user_id != Config.ADMIN_ID:
            await update.message.reply_text("❌ غير مصرح لك!")
            logger.warning(f"Unauthorized access attempt: {user_id}")
            return
        
        return await func(update, *args, **kwargs)
    
    return wrapper

def user_required(func):
    """Decorator للتحقق من وجود المستخدم في قاعدة البيانات"""
    @wraps(func)
    async def wrapper(update: Update, *args, **kwargs):
        user_id = update.effective_user.id
        
        # هنا يمكن التحقق من وجود المستخدم في قاعدة البيانات
        # وإضافة منطق إضافي
        
        return await func(update, *args, **kwargs)
    
    return wrapper
