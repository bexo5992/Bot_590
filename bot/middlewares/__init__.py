# bot/middlewares/__init__.py
from .rate_limit import RateLimiter, rate_limit_decorator

__all__ = ['RateLimiter', 'rate_limit_decorator']
