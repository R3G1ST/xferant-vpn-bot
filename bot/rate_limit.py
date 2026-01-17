from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable
import time

class RateLimitMiddleware(BaseMiddleware):
    def __init__(self):
        self.users = {}
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        current_time = time.time()
        
        if user_id in self.users:
            if current_time - self.users[user_id] < 1:  # 1 second cooldown
                await event.answer("⏳ Пожалуйста, подождите перед следующим сообщением")
                return
        
        self.users[user_id] = current_time
        return await handler(event, data)
