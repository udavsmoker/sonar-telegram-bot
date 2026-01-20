from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message
import time
from cachetools import TTLCache

class ThrottlingMiddleware(BaseMiddleware):
    """
    Simple anti-spam middleware using TTLCache.
    Limits users to 1 request per REQ_INTERVAL seconds.
    """
    def __init__(self, limit: float = 2.0):
        self.limit = limit
        self.cache = TTLCache(maxsize=10000, ttl=limit)

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)
            
        user_id = event.from_user.id
        
        if user_id in self.cache:
            # User is throttled, silently drop or could reply with warning
            return
            
        self.cache[user_id] = True
        return await handler(event, data)
