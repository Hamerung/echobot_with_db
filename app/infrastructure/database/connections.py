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
