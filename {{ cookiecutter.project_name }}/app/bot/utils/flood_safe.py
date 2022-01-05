import asyncio
import logging
from functools import (
    wraps,
)

from pyrogram.errors import FloodWait

logger = logging.getLogger('flood_safe')


def flood_safe(func: callable):
    @wraps(func)
    async def decorator(*args, **kwargs):
        while True:
            try:
                return await func(*args, **kwargs)
            except FloodWait as e:
                logger.info(f"FloodWait for {e.x} seconds when calling {func.__name__}")
                await asyncio.sleep(e.x)

    return decorator
