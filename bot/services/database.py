# bot/services/database.py
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime
from typing import List, Optional, Dict
from bot.database.models import User, Message, Link, Notification
from bot.utils.logger import logger

class DatabaseService:
    """خدمة قاعدة البيانات"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def save_user(self, user_id: int, username: str = None, 
                         first_name: str = None, last_name: str = None) -> User:
        """حفظ أو تحديث مستخدم"""
        user = self.session.query(User).filter_by(user_id=user_id).first()
        
        if not user:
            user = User(
                user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            self.session.add(user)
        else:
            user.username = username or user.username
            user.first_name = first_name or user.first_name
            user.last_name = last_name or user.last_name
            user.last_active = datetime.now()
        
        self.session.commit()
        return user
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """جلب مستخدم"""
        return self.session.query(User).filter_by(user_id=user_id).first()
    
    async def save_message(self, from_user: int, to_user: int, message: str) -> Message:
        """حفظ رسالة"""
        msg = Message(
            from_user_id=from_user,
            to_user_id=to_user,
            message=message
        )
        self.session.add(msg)
        self.session.commit()
        return msg
    
    async def get_user_messages(self, user_id: int, limit: int = 50, 
                                 offset: int = 0, unread_only: bool = False) -> List[Message]:
        """جلب رسائل المستخدم"""
        query = self.session.query(Message).filter(
            Message.to_user_id == user_id,
            Message.is_deleted == False
        )
        
        if unread_only:
            query = query.filter(Message.is_read == False)
        
        return query.order_by(desc(Message.date)).limit(limit).offset(offset).all()
    
    async def get_unread_count(self, user_id: int) -> int:
        """جلب عدد الرسائل غير المقروءة"""
        return self.session.query(Message).filter(
            Message.to_user_id == user_id,
            Message.is_read == False,
            Message.is_deleted == False
        ).count()
    
    async def mark_as_read(self, message_id: int) -> bool:
        """تحديد رسالة كمقروءة"""
        msg = self.session.query(Message).filter_by(id=message_id).first()
        if msg:
            msg.is_read = True
            self.session.commit()
            return True
        return False
    
    async def save_link(self, user_id: int, code: str) -> Link:
        """حفظ رابط"""
        link = self.session.query(Link).filter_by(user_id=user_id).first()
        
        if not link:
            link = Link(user_id=user_id, link_code=code)
            self.session.add(link)
        else:
            link.link_code = code
            link.created_date = datetime.now()
        
        self.session.commit()
        return link
    
    async def get_user_link(self, user_id: int) -> Optional[str]:
        """جلب رابط المستخدم"""
        link = self.session.query(Link).filter_by(user_id=user_id).first()
        return link.link_code if link else None
    
    async def get_user_by_link(self, code: str) -> Optional[User]:
        """جلب مستخدم عبر الرابط"""
        link = self.session.query(Link).filter_by(link_code=code).first()
        if link:
            return await self.get_user(link.user_id)
        return None
    
    async def get_stats(self) -> Dict:
        """جلب إحصائيات"""
        users = self.session.query(User).count()
        messages = self.session.query(Message).filter(Message.is_deleted == False).count()
        unread = await self.get_unread_count_all()
        links = self.session.query(Link).count()
        
        return {
            'users': users,
            'messages': messages,
            'unread': unread,
            'links': links
        }
    
    async def get_unread_count_all(self) -> int:
        """جلب جميع الرسائل غير المقروءة"""
        return self.session.query(Message).filter(
            Message.is_read == False,
            Message.is_deleted == False
        ).count()
