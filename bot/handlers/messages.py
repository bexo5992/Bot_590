# bot/handlers/messages.py
from telegram import Update
from telegram.ext import ContextTypes, filters, MessageHandler
from bot.services.database import DatabaseService
from bot.utils.logger import logger

class MessageHandlers:
    """معالجات الرسائل العامة"""
    
    def __init__(self, db_service: DatabaseService):
        self.db = db_service
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة النصوص العادية"""
        user_id = update.effective_user.id
        text = update.message.text
        
        logger.info(f"Message from {user_id}: {text[:50]}")
        
        # رد افتراضي
        await update.message.reply_text(
            "📨 استلمت رسالتك!\n"
            "استخدم الأزرار للتفاعل مع البوت."
        )
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الصور"""
        await update.message.reply_text("📸 استلمت صورتك!")
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الملفات"""
        file = update.message.document
        if file.file_size > 5 * 1024 * 1024:  # 5MB
            await update.message.reply_text("❌ الملف كبير جداً (الحد الأقصى 5MB)")
            return
        
        await update.message.reply_text(f"📄 استلمت ملف: {file.file_name}")
