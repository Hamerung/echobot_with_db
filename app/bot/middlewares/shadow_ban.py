import logging
from typing import Any, Callable, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update, User
from app.infrastructure.database.db import get_user_banned_status_by_id
from psycopg import AsyncConnection


logger = logging.getLogger(__name__)


class SwadowBanMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: dict[str, Any]
    ) -> Any:
        user: User = data.get('event_from_user')

        if user is None:
            return await handler(event, data)

        conn: AsyncConnection = data.get('conn')
        if conn is None:
            logger.warning('Database connection not found in middleware data')
            raise RuntimeError('Missing database connection for shadowban check')

        user_banned_status = await get_user_banned_status_by_id(conn, user_id=user.id)

        if user_banned_status:
            logger.warning(f'Shadow-banned user tried to interact: {user.id}')
            if event.callback_query:
                await event.callback_query.answer()
            return

        return await handler(event, data)