import logging
from urllib.parse import quote

from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool


logger = logging.getLogger(__name__)

def build_pg_conninfo(
        db_name: str,
        host: str,
        port: int,
        user: str,
        password: str
) -> str:
    conninfo = (
        f"postgresql://{quote(user, safe='')}:{quote(password, safe='')}"
        f"@{host}:{port}/{db_name}"
    )

    logger.info(f"Building PostgreSQL connection string (password omitted): "
                f"postgresql://{quote(user, safe='')}@{host}:{port}/{db_name}"
    )

    return conninfo

async def log_db_version(connection: AsyncConnection) -> None:
    try:
        async with connection.cursor() as cursor:
            await cursor.execute('SELECT version();')
            db_version = await cursor.fetchone()
            logger.info(f'Connection to PostgreSQL version: {db_version[0]}')
    except Exception as e:
        logger.warning(f'Failed to fetch DB version: {e}')


async def get_pg_connection(
        db_name: str,
        host: str,
        port: int,
        user: str,
        password: str,
) -> AsyncConnection:
    conninfo = build_pg_conninfo(db_name, host, port, user, password)
    connection: AsyncConnection | None = None

    try:
        connection = await AsyncConnection.connect(conninfo=conninfo)
        await log_db_version(connection)
        return connection
    except Exception as e:
        logger.exception(f'Failed to connect to PosrgreSQL: {e}')
        if connection:
            await connection.close()
        raise


async def get_pg_pool(
        db_name: str,
        host: str,
        port: int,
        user: str,
        password: str,
        min_size: int = 1,
        max_size: int = 3,
        timeout: float | None = 10.0,
) -> AsyncConnectionPool:
    conninfo = build_pg_conninfo(db_name, host, port, user, password)
    db_pool: AsyncConnectionPool | None = None

    try:
        db_pool = AsyncConnectionPool(
            conninfo=conninfo,
            min_size=min_size,
            max_size=max_size,
            timeout=timeout,
            open=False,
        )

        await db_pool.open()

        async with db_pool.connection() as connection:
            await log_db_version(connection)

        return db_pool
    except Exception as e:
        logger.exception(f'Failed initialize PosrgreSQL pool: {e}')
        if db_pool and not db_pool.closed:
            db_pool.close()

        raise