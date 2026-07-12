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
    async def wrapper(update, context, *args, **kwargs):
        # استخراج user_id من update
        user_id = None
        
        # من message
        if hasattr(update, 'message') and update.message:
            user_id = update.message.from_user.id
        # من callback_query
        elif hasattr(update, 'callback_query') and update.callback_query:
            user_id = update.callback_query.from_user.id
        # من inline_query
        elif hasattr(update, 'inline_query') and update.inline_query:
            user_id = update.inline_query.from_user.id
        
        if not user_id:
            # إذا لم نجد user_id، نسمح بالطلب
            return await func(update, context, *args, **kwargs)

        if not rate_limiter.is_allowed(user_id):
            # إرسال رسالة تحذير
            try:
                if update.callback_query:
                    await update.callback_query.answer(
                        "⚠️ تم تجاوز حد الطلبات! انتظر قليلاً.",
                        show_alert=True
                    )
                elif update.message:
                    await update.message.reply_text(
                        "⚠️ **تم تجاوز حد الطلبات!**\n"
                        f"الحد الأقصى: {rate_limiter.limit} طلب في الدقيقة\n"
                        "يرجى الانتظار قليلاً ثم المحاولة مرة أخرى.",
                        parse_mode="Markdown"
                    )
            except:
                pass
            return

        return await func(update, context, *args, **kwargs)

    return wrapper
