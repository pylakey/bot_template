import asyncio
import logging
import os

import peewee
from tenacity import (
    after_log,
    before_log,
    retry,
    stop_after_attempt,
    wait_fixed,
)

from app.database.database import (
    database,
)
from app.settings import settings
from app.utils.logger import configure_logger

logger = logging.getLogger('Pre Start')

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def wait_db_connection():
    try:
        logger.info("Checking if DB is awake...")
        with database:
            database.execute(peewee.SQL("SELECT 1"))
    except Exception as e:
        logger.error(e)
        raise e


def create_missing_dirs():
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    os.makedirs(settings.SESSIONS_DIR, exist_ok=True)


async def main():
    create_missing_dirs()
    # await wait_db_connection()


if __name__ == '__main__':
    configure_logger()
    asyncio.run(main())
