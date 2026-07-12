# bot/handlers/admin.py
import json
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from bot.services.database import DatabaseService
from bot.utils.logger import logger
from bot.config import Config

class AdminHandlers:
    """معالجات الأدمن"""
    
    def __init__(self, db_service: DatabaseService):
        self.db = db_service
        self.admin_id = Config.ADMIN_ID
    
    async def _check_admin(self, update: Update) -> bool:
        """التحقق من صلاحيات الأدمن"""
        user_id = update.effective_user.id
        if user_id != self.admin_id:
            await update.message.reply_text("❌ غير مصرح لك!")
            return False
        return True
    
    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الإحصائيات"""
        if not await self._check_admin(update):
            return
        
        stats = await self.db.get_stats()
        
        text = f"""
📊 **إحصائيات البوت**

👥 المستخدمين: {stats['users']}
💬 الرسائل: {stats['messages']}
📩 غير مقروءة: {stats['unread']}
🔗 الروابط: {stats['links']}

📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
        
        await update.message.reply_text(text, parse_mode="Markdown")
    
    async def export_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تصدير البيانات"""
        if not await self._check_admin(update):
            return
        
        await update.message.reply_text("⏳ جاري تصدير البيانات...")
        
        try:
            # جلب جميع البيانات
            users = await self.db.session.query(User).all()
            messages = await self.db.session.query(Message).filter(
                Message.is_deleted == False
            ).all()
            
            data = {
                'export_date': datetime.now().isoformat(),
                'users': [{
                    'id': u.user_id,
                    'username': u.username,
                    'first_name': u.first_name,
                    'join_date': u.join_date.isoformat() if u.join_date else None
                } for u in users],
                'messages': [{
                    'id': m.id,
                    'from': m.from_user_id,
                    'to': m.to_user_id,
                    'message': m.message[:100],
                    'date': m.date.isoformat()
                } for m in messages[:1000]]  # حد أقصى 1000 رسالة
            }
            
            # إرسال الملف
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                temp_path = f.name
            
            await update.message.reply_document(
                document=open(temp_path, 'rb'),
                filename=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                caption="📊 تصدير البيانات"
            )
            
            os.unlink(temp_path)
            
        except Exception as e:
            logger.error(f"Export error: {e}")
            await update.message.reply_text(f"❌ خطأ: {str(e)}")
    
    async def broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إرسال إشعار عام"""
        if not await self._check_admin(update):
            return
        
        # التحقق من وجود نص
        if not context.args:
            await update.message.reply_text(
                "📢 **إرسال إشعار عام**\n\n"
                "الاستخدام:\n"
                "/broadcast نص الإشعار"
            )
            return
        
        message = ' '.join(context.args)
        
        # جلب جميع المستخدمين
        users = await self.db.session.query(User).filter(
            User.ban_status == False
        ).all()
        
        success = 0
        failed = 0
        
        await update.message.reply_text(f"⏳ جاري الإرسال لـ {len(users)} مستخدم...")
        
        for user in users:
            try:
                await context.bot.send_message(
                    user.user_id,
                    f"📢 **إشعار عام**\n\n{message}",
                    parse_mode="Markdown"
                )
                success += 1
            except:
                failed += 1
            
            # تأخير لتجنب الحظر
            if success % 30 == 0:
                import asyncio
                await asyncio.sleep(1)
        
        await update.message.reply_text(
            f"✅ تم الإرسال:\n"
            f"✅ نجح: {success}\n"
            f"❌ فشل: {failed}"
        )
    
    async def ban_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """حظر أو إلغاء حظر مستخدم"""
        if not await self._check_admin(update):
            return
        
        if not context.args:
            await update.message.reply_text(
                "🚫 **إدارة الحظر**\n\n"
                "الاستخدام:\n"
                "/ban <user_id> - لحظر مستخدم\n"
                "/ban <user_id> 0 - لإلغاء الحظر"
            )
            return
        
        try:
            user_id = int(context.args[0])
            ban_status = 1 if len(context.args) == 1 else int(context.args[1])
            
            # التحقق من وجود المستخدم
            user = await self.db.get_user(user_id)
            if not user:
                await update.message.reply_text("❌ المستخدم غير موجود!")
                return
            
            # تحديث حالة الحظر
            user.ban_status = bool(ban_status)
            await self.db.session.commit()
            
            status = "✅ تم حظر" if ban_status == 1 else "✅ تم إلغاء حظر"
            await update.message.reply_text(f"{status} المستخدم `{user_id}`", parse_mode="Markdown")
            
            # إشعار المستخدم
            try:
                await context.bot.send_message(
                    user_id,
                    f"🚫 **تم {'حظرك' if ban_status == 1 else 'إلغاء حظرك'}**\n"
                    f"من قبل الإدارة.",
                    parse_mode="Markdown"
                )
            except:
                pass
            
        except ValueError:
            await update.message.reply_text("❌ المعرف غير صحيح!")
