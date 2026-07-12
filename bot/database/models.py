# bot/database/models.py
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, 
    DateTime, Boolean, ForeignKey, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from bot.config import Config

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    ban_status = Column(Boolean, default=False)
    join_date = Column(DateTime, default=datetime.now)
    last_active = Column(DateTime, default=datetime.now)
    
    # العلاقات
    messages_sent = relationship("Message", foreign_keys="Message.from_user_id")
    messages_received = relationship("Message", foreign_keys="Message.to_user_id")
    
    def __repr__(self):
        return f"<User(id={self.user_id}, username={self.username})>"

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    from_user_id = Column(Integer, ForeignKey('users.user_id'), index=True)
    to_user_id = Column(Integer, ForeignKey('users.user_id'), index=True)
    message = Column(Text, nullable=False)
    date = Column(DateTime, default=datetime.now, index=True)
    is_read = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    # العلاقات
    from_user = relationship("User", foreign_keys=[from_user_id])
    to_user = relationship("User", foreign_keys=[to_user_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_messages_from_to', from_user_id, to_user_id),
        Index('idx_messages_unread', to_user_id, is_read),
    )

class Link(Base):
    __tablename__ = 'links'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), unique=True)
    link_code = Column(String(16), unique=True, nullable=False, index=True)
    created_date = Column(DateTime, default=datetime.now)
    expires_date = Column(DateTime, nullable=True)
    
    user = relationship("User")

class TempRecipient(Base):
    __tablename__ = 'temp_recipients'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), unique=True)
    recipient_id = Column(Integer, ForeignKey('users.user_id'))
    date = Column(DateTime, default=datetime.now)
    
    user = relationship("User", foreign_keys=[user_id])
    recipient = relationship("User", foreign_keys=[recipient_id])

class Notification(Base):
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), index=True)
    message = Column(Text, nullable=False)
    date = Column(DateTime, default=datetime.now)
    is_read = Column(Boolean, default=False)
    
    user = relationship("User")

# إعداد قاعدة البيانات
def init_database():
    """تهيئة قاعدة البيانات"""
    engine = create_engine(
        Config.DATABASE_URL,
        echo=False,
        pool_size=10,
        max_overflow=20
    )
    
    # إنشاء الجداول
    Base.metadata.create_all(engine)
    
    # جلسة العمل
    Session = sessionmaker(bind=engine)
    session = Session()
    
    return session, engine

# دالة للحصول على جلسة
def get_db():
    """الحصول على جلسة قاعدة البيانات (مع Context Manager)"""
    from contextlib import contextmanager
    
    session, _ = init_database()
    
    @contextmanager
    def session_scope():
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    return session_scope
