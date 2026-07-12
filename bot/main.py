# bot/handlers/user.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from bot.services.database import DatabaseService
from bot.utils.logger import logger
from bot.utils.security import generate_link_code
from bot.middlewares.rate_limit import rate_limit_decorator
from bot.keyboards.buttons import get_main_keyboard

# حالات المحادثة
WAITING_RECIPIENT, WAITING_MESSAGE = range(2)

class UserHandlers:
    """معالجات المستخدمين"""

    def __init__(self, db_service: DatabaseService):
        self.db = db_service

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة أمر /start"""
        user = update.effective_user

        # حفظ المستخدم
        await self.db.save_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )

        logger.info(f"User started bot: {user.id} ({user.username})")

        # رسالة الترحيب
        welcome_text = f"""
👋 مرحباً {user.first_name}!

اختر أحد الخيارات من القائمة أدناه:

📨 **إرسال رسالة** - أرسل رسالة لأي مستخدم
📩 **صندوق الوارد** - عرض الرسائل الواردة
🔗 **رابط رسائلي** - احصل على رابط دعوة خاص بك
⚙️ **الإعدادات** - إعدادات الحساب
"""

        keyboard = await get_main_keyboard(user.id, self.db)

        await update.message.reply_text(
            welcome_text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )

    @rate_limit_decorator
    async def handle_send(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بدء عملية إرسال رسالة"""
        query = update.callback_query
        await query.answer()

        await query.edit_message_text(
            "✏️ أرسل معرف المستخدم (ID):"
        )

        return WAITING_RECIPIENT

    async def process_recipient(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة معرف المستلم"""
        user_id = update.message.text.strip()

        try:
            recipient_id = int(user_id)

            # التحقق من وجود المستخدم
            user = await self.db.get_user(recipient_id)
            if not user:
                await update.message.reply_text("❌ المستخدم غير موجود!")
                return ConversationHandler.END

            context.user_data['recipient'] = recipient_id

            await update.message.reply_text(
                "📝 أرسل نص الرسالة:"
            )

            return WAITING_MESSAGE

        except ValueError:
            await update.message.reply_text("❌ المعرف غير صحيح! يجب أن يكون أرقاماً فقط.")
            return WAITING_RECIPIENT

    async def process_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة نص الرسالة"""
        text = update.message.text
        recipient_id = context.user_data.get('recipient')
        from_user_id = update.message.from_user.id

        if len(text) > 4096:
            await update.message.reply_text("❌ الرسالة طويلة جداً (الحد الأقصى 4096 حرف)")
            return WAITING_MESSAGE

        # حفظ الرسالة
        await self.db.save_message(
            from_user=from_user_id,
            to_user=recipient_id,
            message=text
        )

        # إرسال إشعار للمستلم
        try:
            await update.get_bot().send_message(
                recipient_id,
                f"📩 لديك رسالة جديدة من {update.message.from_user.first_name}:\n\n{text}"
            )
        except Exception as e:
            logger.warning(f"Could not notify user {recipient_id}: {e}")

        await update.message.reply_text("✅ تم إرسال الرسالة بنجاح!")

        return ConversationHandler.END

    async def handle_inbox(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض صندوق الوارد"""
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id

        # جلب الرسائل غير المقروءة
        unread_count = await self.db.get_unread_count(user_id)

        # جلب آخر 5 رسائل
        messages = await self.db.get_user_messages(user_id, limit=5)

        if not messages:
            await query.edit_message_text(
                "📭 لا توجد رسائل في صندوق الوارد",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")
                ]])
            )
            return

        text = f"📩 **صندوق الوارد** (غير مقروء: {unread_count})\n\n"

        for msg in messages:
            status = "🟢" if not msg.is_read else "✅"
            text += f"{status} من: `{msg.from_user_id}`\n📝 {msg.message[:50]}...\n📅 {msg.date.strftime('%Y-%m-%d %H:%M')}\n\n"

        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📖 عرض الكل", callback_data="inbox_all"),
                InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")
            ]])
        )

    async def handle_my_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الرابط الخاص"""
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id

        # جلب الرابط أو إنشائه
        link = await self.db.get_user_link(user_id)
        if not link:
            code = generate_link_code()
            await self.db.save_link(user_id, code)
            link = code

        bot_username = (await query.get_bot().get_me()).username
        user_link = f"https://t.me/{bot_username}?start={link}"

        text = f"""
🔗 **رابطك الخاص**

`{user_link}`

💡 شارك الرابط مع أصدقائك ليتمكنوا من مراسلتك!
"""

        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📋 نسخ الرابط", callback_data="copy_link"),
                InlineKeyboardButton("🔄 تجديد الرابط", callback_data="refresh_link"),
                InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")
            ]])
        )

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إلغاء المحادثة الحالية"""
        user_id = update.effective_user.id
        
        # إنهاء المحادثة
        context.user_data.clear()
        
        # رسالة إلغاء مع القائمة الرئيسية
        await update.message.reply_text(
            "❌ تم إلغاء العملية.",
            reply_markup=await get_main_keyboard(user_id, self.db)
        )
        
        return ConversationHandler.END

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض المساعدة"""
        help_text = """
📖 **مساعدة البوت**

الأوامر المتاحة:
/start - عرض القائمة الرئيسية
/help - عرض هذه المساعدة

الخصائص:
📨 **إرسال رسالة** - أرسل رسالة لأي مستخدم باستخدام معرفه
📩 **صندوق الوارد** - عرض واستعراض الرسائل الواردة
🔗 **رابط رسائلي** - احصل على رابط دعوة خاص بك
⚙️ **الإعدادات** - إعدادات الحساب

🔐 **الخصوصية**: رسائلك آمنة ولا يراها أحد غيرك.
"""
        await update.message.reply_text(help_text, parse_mode="Markdown")
