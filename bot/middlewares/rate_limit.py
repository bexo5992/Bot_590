# bot/middlewares/rate_limit.py
from collections import defaultdict
from time import time
from functools import wraps
from bot.utils.logger import logger
from bot.config import Config

class RateLimiter:
    """محدد السرعة المتقدم"""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.limit = Config.RATE_LIMIT
        self.window = 60  # ثانية
    
    def is_allowed(self, user_id: int) -> bool:
        """التحقق من السماح بالطلب"""
        now = time()
        window_start = now - self.window
        
        # تنظيف الطلبات القديمة
        self.requests[user_id] = [
            t for t in self.requests[user_id] if t > window_start
        ]
        
        # التحقق من الحد
        if len(self.requests[user_id]) >= self.limit:
            logger.warning(f"Rate limit exceeded: user={user_id}")
            return False
        
        self.requests[user_id].append(now)
        return True

rate_limiter = RateLimiter()

def rate_limit_decorator(func):
    """Decorator لمحدد السرعة"""
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        user_id = message.from_user.id
        
        if not rate_limiter.is_allowed(user_id):
            # إرسال رسالة تحذير
            try:
                message.reply_text(
                    "⚠️ **تم تجاوز حد الطلبات!**\n"
                    f"الحد الأقصى: {rate_limiter.limit} رسالة في الدقيقة\n"
                    "يرجى الانتظار قليلاً ثم المحاولة مرة أخرى.",
                    parse_mode="Markdown"
                )
            except:
                pass
            return
        
        return func(message, *args, **kwargs)
    
    return wrapper
