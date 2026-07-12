# bot/handlers/callbacks.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from bot.services.database import DatabaseService
from bot.utils.logger import logger
from bot.keyboards.buttons import get_main_keyboard

class CallbackHandlers:
    """معالجات الكالبات"""
    
    def __init__(self, db_service: DatabaseService):
        self.db = db_service
    
    async def handle_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """العودة للقائمة الرئيسية"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        keyboard = await get_main_keyboard(user_id, self.db)
        
        await query.edit_message_text(
            "🏠 **القائمة الرئيسية**\nاختر أحد الخيارات:",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    
    async def handle_inbox(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض صندوق الوارد"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        # جلب الرسائل
        messages = await self.db.get_user_messages(user_id, limit=10)
        unread_count = await self.db.get_unread_count(user_id)
        
        if not messages:
            await query.edit_message_text(
                "📭 **صندوق الوارد فارغ**",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")
                ]])
            )
            return
        
        text = f"📩 **صندوق الوارد** (غير مقروء: {unread_count})\n\n"
        
        for i, msg in enumerate(messages[:5]):
            status = "🟢" if not msg.is_read else "✅"
            text += f"{status} من: `{msg.from_user_id}`\n📝 {msg.message[:50]}...\n"
            text += f"📅 {msg.date.strftime('%Y-%m-%d %H:%M')}\n\n"
        
        if len(messages) > 5:
            text += f"\n📌 عرض 5 من {len(messages)} رسائل"
        
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📖 عرض الكل", callback_data="inbox_all")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]
            ])
        )
    
    async def handle_my_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الرابط الخاص"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        # جلب أو إنشاء الرابط
        from bot.utils.security import generate_link_code
        
        link_code = await self.db.get_user_link(user_id)
        if not link_code:
            link_code = generate_link_code()
            await self.db.save_link(user_id, link_code)
        
        bot_username = (await query.get_bot().get_me()).username
        user_link = f"https://t.me/{bot_username}?start={link_code}"
        
        text = f"""
🔗 **رابطك الخاص**

`{user_link}`

💡 شارك الرابط مع أصدقائك ليتمكنوا من مراسلتك!
"""
        
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 نسخ الرابط", callback_data="copy_link")],
                [InlineKeyboardButton("🔄 تجديد الرابط", callback_data="refresh_link")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]
            ])
        )
    
    async def handle_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الإعدادات"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "⚙️ **الإعدادات**\nاختر الخيار المناسب:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔕 إشعارات", callback_data="notifications")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]
            ])
        )
    
    async def handle_inbox_all(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض جميع رسائل الوارد"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        messages = await self.db.get_user_messages(user_id, limit=50)
        
        if not messages:
            await query.edit_message_text("📭 لا توجد رسائل")
            return
        
        text = "📩 **جميع الرسائل**\n\n"
        
        for msg in messages:
            status = "🟢" if not msg.is_read else "✅"
            text += f"{status} من: `{msg.from_user_id}`\n"
            text += f"📝 {msg.message[:100]}\n"
            text += f"📅 {msg.date.strftime('%Y-%m-%d %H:%M')}\n"
            text += "─" * 20 + "\n"
        
        await query.edit_message_text(
            text[:4000],  # حد تيليجرام
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 رجوع", callback_data="inbox")
            ]])
        )
