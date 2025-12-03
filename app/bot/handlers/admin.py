import logging

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from app.bot.enums.roles import UserRole
from app.bot.filters.filters import UserRoleFilter
from app.infrastructure.database.db import (
    change_user_banned_status_by_id,
    change_user_banned_status_by_username,
    get_statistics,
    get_user_banned_status_by_id,
    get_user_banned_status_by_username
)
from psycopg import AsyncConnection


logger = logging.getLogger(__name__)

admin_router = Router()

admin_router.message.filter(UserRoleFilter(UserRole.ADMIN))


@admin_router.message(Command(commands='help'))
async def process_admin_help_command(message: Message, i18n: dict[str, str]):
    await message.answer(text=i18n.get('/help_admin'))


@admin_router.message(Command(commands='statistics'))
async def process_statistics_command(
    message: Message,
    conn: AsyncConnection,
    i18n: dict[str, str],
):
    stat = await get_statistics(conn)
    await message.answer(
        text=i18n.get('statistics').format(
            '\n'.join(
                f'{i}. <b>{s[0]}</b>: {s[1]}'
                for i, s in enumerate(stat, 1)
            )
        )
    )


@admin_router.message(Command(commands='ban'))
async def process_ban_command(
    message: Message,
    command: CommandObject,
    conn: AsyncConnection,
    i18n: dict[str, str],
):
    args = command.args

    if not args:
        await message.answer(text=i18n.get('empty_ban_answer'))
        return

    arg_user = args.split()[0].strip()

    if arg_user.isdigit():
        banned_status = await get_user_banned_status_by_id(conn, user_id=int(arg_user))
    elif arg_user.startswith('@'):
        banned_status = await get_user_banned_status_by_username(conn, username=arg_user[1:])
    else:
        await message.answer(text=i18n.get('incorrect_bat_arg'))

    if banned_status is None:
        await message.answer(text=i18n.get('no_user'))
    elif banned_status:
        await message.answer(text=i18n.get('already_banned'))
    else:
        if arg_user.isdigit():
            await change_user_banned_status_by_id(conn, user_id=int(arg_user), banned=True)
        else:
            await change_user_banned_status_by_username(conn, username=arg_user[1:], banned=True)
        await message.answer(text=i18n.get('successfully_banned'))


@admin_router.message(Command(commands='unban'))
async def process_unban_command(
    message: Message,
    command: CommandObject,
    conn: AsyncConnection,
    i18n: dict[str, str],
):
    args = command.args

    if not args:
        await message.answer(text=i18n.get('empty_unban_answer'))
        return

    arg_user = args.split()[0].strip()

    if arg_user.isdigit():
        banned_status = await get_user_banned_status_by_id(conn, user_id=int(arg_user))
    elif arg_user.startswith('@'):
        banned_status = await get_user_banned_status_by_username(conn, username=arg_user[1:])
    else:
        await message.answer(text=i18n.get('incorrect_unban_arg'))

    if banned_status is None:
        await message.answer(text=i18n.get('no_user'))
    elif banned_status:
        if arg_user.isdigit():
            await change_user_banned_status_by_id(conn, user_id=int(arg_user), banned=False)
        else:
            await change_user_banned_status_by_username(conn, username=arg_user[1:], banned=False)
        await message.answer(text=i18n.get('successfully_unbanned'))
    else:
        await message.answer(text=i18n.get('not_banned'))
