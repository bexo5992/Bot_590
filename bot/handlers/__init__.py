# bot/handlers/__init__.py
from .user import UserHandlers
from .admin import AdminHandlers
from .callbacks import CallbackHandlers

__all__ = ['UserHandlers', 'AdminHandlers', 'CallbackHandlers']
