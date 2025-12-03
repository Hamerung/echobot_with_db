import asyncio
import logging
from psycopg import AsyncConnection, Error

from config.config import Config, load_config
from app.infrastructure.database.connections import get_pg_connection


config: Config = load_config()

logging.basicConfig(
    level=config.log.level,
    format=config.log.frmt,
    style='{'
)

logger = logging.getLogger(__name__)

async def main():
    connection: AsyncConnection | None = None

    try:
        connection = await get_pg_connection(
            db_name=config.db.name,
            host=config.db.host,
            port=config.db.port,
            user=config.db.user,
            password=config.db.password
        )

        async with connection.transaction():
            async with connection.cursor() as cursor:
                await cursor.execute(
                    query='''
                        CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            user_id BIGINT NOT NULL UNIQUE,
                            username VARCHAR(50),
                            created_at TIMESTAMPZ NOT NULL DEFAULT NOW(),
                            language VARCHAR(10) NOT NULL,
                            role VARCHAR(30) NOT NULL,
                            is_alive BOOLEAN NOT NULL,
                            banned BOOLEAN NOT NULL
                        );'''
                    )
                await cursor.execute(
                    query='''
                        CREATE TABLE IF NOT EXISTS activity (
                            id SERIAL PRIMARY KEY,
                            user BIGINT REFERNSEC user(user_id),
                            created_at TIMESTAMPZ NOT NULL DEFAULT NOW(),
                            activity_date DATE NOT NULL DEFAULT CURRENT_DATE,
                            actions INT NOT NULL DEFAULT 1
                        );
                        CREATE UNIQUE INDEX IF NOT EXISTS idx_activity_user_day
                        ON activity (user_id, activity_date);
                        '''
                    )
            logger.info('tables "users" and "activity" successfully created')
    except Error as db_error:
        logger.exception(f'database specific error {db_error}')
    except Exception as e:
        logger.exception(f'Unhandled error {e}')
    finally:
        if connection:
            await connection.close()
            logger.info('Connection to Postgres closed')

asyncio.run(main())