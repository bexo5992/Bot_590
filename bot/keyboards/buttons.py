# bot/keyboards/buttons.py
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from bot.services.database import DatabaseService

async def get_main_keyboard(user_id: int, db: DatabaseService) -> InlineKeyboardMarkup:
    """لوحة المفاتيح الرئيسية"""
    
    # حساب عدد الرسائل غير المقروءة
    unread_count = await db.get_unread_count(user_id)
    inbox_text = f"📩 صندوق الوارد ({unread_count})" if unread_count > 0 else "📩 صندوق الوارد"
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📨 إرسال رسالة", callback_data="send"),
            InlineKeyboardButton(inbox_text, callback_data="inbox")
        ],
        [
            InlineKeyboardButton("🔗 رابط رسائلي", callback_data="my_link"),
            InlineKeyboardButton("⚙️ الإعدادات", callback_data="settings")
        ]
    ])
    
    return keyboard
