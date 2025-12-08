import asyncio
import logging

from app.bot import main
from config.config import Config, load_config

config: Config = load_config('.env')

logging.basicConfig(
    level=config.log.level,
    format=config.log.frmt,
    style='{'
)

asyncio.run(main(config))