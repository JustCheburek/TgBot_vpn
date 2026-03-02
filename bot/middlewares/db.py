from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from bot.models.database import DatabaseManager


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        session = self.db_manager.get_session()
        try:
            data["session"] = session
            return await handler(event, data)
        finally:
            session.close()
