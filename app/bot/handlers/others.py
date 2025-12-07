from aiogram import Router
from aiogram.types import Message
from psycopg import AsyncConnection


others_router = Router()


@others_router.message()
async def send_echo(
    message: Message,
    conn: AsyncConnection,
    i18n: dict[str, str],
):
    try:
        await message.send_copy(chat_id=message.from_user.id)
    except TypeError:
        await message.reply(text=i18n.get('no_echo'))