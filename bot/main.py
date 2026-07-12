# bot/main.py
import asyncio
from datetime import datetime
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters
)
from telegram.ext import ContextTypes

from bot.config import Config
from bot.utils.logger import logger
from bot.database.models import init_database
from bot.services.database import DatabaseService
from bot.handlers.user import UserHandlers, WAITING_RECIPIENT, WAITING_MESSAGE
from bot.handlers.admin import AdminHandlers
from bot.handlers.callbacks import CallbackHandlers
from bot.middlewares.rate_limit import rate_limit_decorator
from bot.keyboards.buttons import get_main_keyboard

class BotApp:
    """تطبيق البوت الرئيسي"""

    def __init__(self):
        self.token = Config.MAIN_BOT_TOKEN
        self.admin_id = Config.ADMIN_ID

        # تهيئة قاعدة البيانات
        session, engine = init_database()
        self.db = DatabaseService(session)

        # تهيئة المعالجات
        self.user_handlers = UserHandlers(self.db)
        self.admin_handlers = AdminHandlers(self.db)
        self.callback_handlers = CallbackHandlers(self.db)

        # تهيئة التطبيق
        self.app = None

    async def post_init(self, application):
        """تهيئة ما بعد البدء"""
        logger.info("🤖 Bot started successfully!")
        logger.info(f"👑 Admin ID: {self.admin_id}")

        # إزالة أي Webhook قديم
        try:
            await application.bot.delete_webhook(drop_pending_updates=True)
            logger.info("✅ Webhook removed")
        except Exception as e:
            logger.warning(f"Could not remove webhook: {e}")

        # إرسال إشعار للأدمن
        try:
            await application.bot.send_message(
                self.admin_id,
                "✅ **البوت يعمل الآن!**\n"
                f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                f"🔗 روابط الدعوة مفعلة!",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.warning(f"Could not notify admin: {e}")

    def setup_handlers(self):
        """إعداد المعالجات"""

        # محادثة إرسال الرسالة
        send_conversation = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(
                    self.user_handlers.handle_send,
                    pattern="^send$"
                ),
                CallbackQueryHandler(
                    self.callback_handlers.handle_send_to,
                    pattern="^send_to_"
                )
            ],
            states={
                WAITING_RECIPIENT: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        self.user_handlers.process_recipient
                    )
                ],
                WAITING_MESSAGE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        self.user_handlers.process_message
                    )
                ]
            },
            fallbacks=[
                CommandHandler('cancel', self.user_handlers.cancel)
            ]
        )

        # إضافة المعالجات
        handlers = [
            # الأوامر
            CommandHandler('start', self.user_handlers.start),
            CommandHandler('help', self.user_handlers.help_command),

            # المحادثات
            send_conversation,

            # الكالبات
            CallbackQueryHandler(
                self.callback_handlers.handle_main_menu,
                pattern="^main_menu$"
            ),
            CallbackQueryHandler(
                self.callback_handlers.handle_inbox,
                pattern="^inbox$"
            ),
            CallbackQueryHandler(
                self.callback_handlers.handle_my_link,
                pattern="^my_link$"
            ),
            CallbackQueryHandler(
                self.callback_handlers.handle_settings,
                pattern="^settings$"
            ),
            CallbackQueryHandler(
                self.callback_handlers.handle_inbox_all,
                pattern="^inbox_all$"
            ),
            CallbackQueryHandler(
                self.callback_handlers.handle_share_link,
                pattern="^share_link$"
            ),
            CallbackQueryHandler(
                self.callback_handlers.handle_copy_link,
                pattern="^copy_link$"
            ),
            CallbackQueryHandler(
                self.callback_handlers.handle_refresh_link,
                pattern="^refresh_link$"
            ),

            # دوال الأدمن
            CommandHandler('stats', self.admin_handlers.stats),
            CommandHandler('export', self.admin_handlers.export_data),
            CommandHandler('broadcast', self.admin_handlers.broadcast),
            CommandHandler('ban', self.admin_handlers.ban_user),
        ]

        for handler in handlers:
            self.app.add_handler(handler)

    def run(self):
        """تشغيل البوت"""
        logger.info("🚀 Starting bot...")

        # تهيئة التطبيق
        self.app = (
            ApplicationBuilder()
            .token(self.token)
            .post_init(self.post_init)
            .concurrent_updates(True)
            .build()
        )

        # إعداد المعالجات
        self.setup_handlers()

        # تشغيل البوت
        self.app.run_polling(
            allowed_updates=['message', 'callback_query'],
            drop_pending_updates=True
        )

if __name__ == "__main__":
    bot_app = BotApp()
    bot_app.run()
