import logging
import psycopg
from datetime import datetime, timezone
from typing import Any
from app.bot.enums.roles import UserRole


logger = logging.getLogger(__name__)


async def add_user(
        conn: psycopg.AsyncConnection,
        *,
        user_id: int,
        username: str | None = None,
        language: str = 'ru',
        role: UserRole = UserRole.USER,
        is_alive: bool = True,
        banned: bool = False,
) -> None:
    async with conn.cursor() as cursor:
        await cursor.execute(
            query='''
                INSERT INTO users(user_id, username, language, role, is_alive, banned)
                    VALUES (
                        %(user_id)s,
                        %(username)s,
                        %(language)s,
                        %(role)s,
                        %(is_alive)s,
                        %(banned)s
                    ) ON CONFLICT DO NOTHING;''',
            params={
                'user_id': user_id,
                'username': username,
                'language': language,
                'role': role,
                'is_alive': is_alive,
                'banned': banned,
            },
        )
    logger.info(f'User {user_id} added to table "users" at {datetime.now(timezone.utc)}, role: {role}')


async def get_user(
        conn: psycopg.AsyncConnection,
        *,
        user_id: int,
) -> tuple[Any, ...] | None:
    async with conn.cursor() as cursor:
        await cursor.execute(
            query='SELECT * FROM users WHERE user_id = %s',
            params=(user_id,),
        )
        try:
            row = await cursor.fetchone()
        except psycopg.InterfaceError:
            row = None

    logger.info(f'Row is {row}')
    return row if row else None


async def change_user_alive_status(
        conn: psycopg.AsyncConnection,
        *,
        user_id: int,
        is_alive: bool,
) -> None:
    async with conn.cursor() as cursor:
        await cursor.execute(
            query='UPDATE users SET is_alive = %s WHERE user_id = %s',
            params=(is_alive, user_id),
        )

    logger.info(f'Change user {user_id} is_alive status to {is_alive}')


async def change_user_banned_status_by_id(
        conn: psycopg.AsyncConnection,
        *,
        user_id: int,
        banned: bool,
) -> None:
    async with conn.cursor() as cursor:
        await cursor.execute(
            query='UPDATE users SET banned = %s WHERE user_id = %s',
            params=(banned, user_id),
        )

    logger.info(f'Update banned status to {banned} for user {user_id}')


async def change_user_banned_status_by_username(
        conn: psycopg.AsyncConnection,
        *,
        username: str,
        banned: bool,
) -> None:
    async with conn.cursor() as cursor:
        await cursor.execute(
            query='UPDATE users SET banned = %s WHERE username = %s',
            params=(banned, username),
        )

    logger.info(f'Update banned status to {banned} for user {username}')


async def update_user_lang(
        conn: psycopg.AsyncConnection,
        *,
        user_id: int,
        lang: str,
) -> None:
    async with conn.cursor() as cursor:
        await cursor.execute(
            query='UPDATE users SET language = %s WHERE user_id = %s',
            params=(lang, user_id),
        )

    logger.info(f'Set language {lang} for user {user_id}')


async def get_user_lang(
        conn: psycopg.AsyncConnection,
        *,
        user_id: int,
) -> str | None:
    async with conn.cursor() as cursor:
        await cursor.execute(
            query='SELECT language FROM users WHERE user_id = %s',
            params=(user_id,),
        )

        try:
            row = await cursor.fetchone()
        except psycopg.InterfaceError:
            row = None
        if not row:
            logger.warning(f'No user with {user_id} found in the database')

    return row[0] if row else None


async def get_user_alive_status(
        conn: psycopg.AsyncConnection,
        *,
        user_id: int,
) -> bool | None:
    async with conn.cursor() as cursor:
        await cursor.execute(
            query='SELECT is_alive FROM users WHERE user_id = %s',
            params=(user_id,),
        )

        try:
            row = await cursor.fetchone()
        except psycopg.InterfaceError:
            row = None
        if not row:
            logger.warning(f'No user with id:{user_id} found in the database')

    return row[0] if row else None


async def get_user_banned_status_by_id(
        conn: psycopg.AsyncConnection,
        *,
        user_id: int,
) -> bool | None:
    async with conn.cursor() as cursor:
        await cursor.execute(
            query='SELECT banned FROM users WHERE user_id = %s',
            params=(user_id,),
        )

        try:
            row = await cursor.fetchone()
        except psycopg.InterfaceError:
            row = None
        if not row:
            logger.warning(f'No user with id:{user_id} found in the database')

    return row[0] if row else None


async def get_user_banned_status_by_username(
        conn: psycopg.AsyncConnection,
        *,
        username: str,
) -> bool | None:
    async with conn.cursor() as cursor:
        await cursor.execute(
            query='SELECT banned FROM users WHERE username = %s',
            params=(username,),
        )

        try:
            row = await cursor.fetchone()
        except psycopg.InterfaceError:
            row = None
        if not row:
            logger.warning(f'No user with username:{username} found in the database')

    return row[0] if row else None


async def get_user_role(
        conn: psycopg.AsyncConnection,
        *,
        user_id: int,
) -> UserRole | None:
    async with conn.cursor() as cursor:
        await cursor.execute(
            query='SELECT role FROM users WHERE user_id = %s',
            params=(user_id,),
        )

        try:
            row = await cursor.fetchone()
        except psycopg.InterfaceError:
            row = None
        if not row:
            logger.warning(f'No user with id:{user_id} found in the database')

    return UserRole(row[0]) if row else None


async def add_user_activity(
        conn: psycopg.AsyncConnection,
        *,
        user_id: int,
) -> None:
    async with conn.cursor() as cursor:
        await cursor.execute(
            query='''
                INSERT INTO activity (user_id)
                VALUES (%s)
                ON CONFLICT (user_id, activity_date)
                DO UPDATE
                SET actions = activity.actions + 1;
                ''',
            params=(user_id,),
        )

    logger.info(f'User {user_id} activity updated')


async def get_statistics(conn: psycopg.AsyncConnection) -> list[Any, ...] | None:
    async with conn.cursor() as cursor:
        await cursor.execute(
            query='''
                SELECT user_id, SUM(actions) AS total_activity
                FROM activity
                GROUP BY user_id
                ORDER BY 2 DESC
                LIMIT 5;
                '''
        )

        try:
            rows = await cursor.fetchall()
        except psycopg.InterfaceError:
            rows = None

    return [*rows] if rows else None
