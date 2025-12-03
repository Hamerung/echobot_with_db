import os
import logging
from dataclasses import dataclass
from environs import Env


logger = logging.getLogger(__name__)

@dataclass
class BotSettings:
    token: str
    admin_ids: list[int]


@dataclass
class DatabaseSettings:
    name: str
    host: str
    port: int
    user: str
    password: str


@dataclass
class RedisSettings:
    host: str
    port: int
    db: int
    user: str
    password: str


@dataclass
class LogSettings:
    level: str
    frmt: str


@dataclass
class Config:
    bot: BotSettings
    log: LogSettings
    db: DatabaseSettings
    redis: RedisSettings


def load_config(path: str | None = None) -> Config:
    env = Env()

    if not os.path.exists(path):
        logger.warning(f'.env file not find at {path}')
    else:
        logger.info('Loading .env')

    env.read_env(path)

    token = env['BOT_TOKEN']

    if not token:
        raise ValueError('BOT_TOKEN must not be empty!')

    test_ids = env.list('ADMIN_IDS', default=[])

    try:
        admin_ids = [int(i) for i in test_ids]
    except ValueError as e:
        raise ValueError('ADMIN_IDS must be integer!') from e

    db = DatabaseSettings(
        name=env('POSTGRES_DB'),
        host=env('POSTGRES_HOST'),
        port=int(env('POSTGRES_PORT')),
        user=env('POSTGRES_USER'),
        password=env('POSTGRES_PASSWORD')
    )

    redis = RedisSettings(
        host=env('REDIS_HOST'),
        port=int(env('REDIS_PORT')),
        db=int(env('REDIS_DATABASE')),
        username=env('REDIS_USERNAME'),
        password=env('REDIS_PASSWORD')
    )

    log = LogSettings(
        level=env('LOG_LEVEL'),
        frmt=env('LOG_FORMAT')
    )

    logger.info('Configuration loaded successfully!!!')

    return Config(
        bot=BotSettings(token=token, admin_ids=admin_ids),
        log=log,
        db=db,
        redis=redis
    )
