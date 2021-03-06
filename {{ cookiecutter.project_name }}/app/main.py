import asyncio

import pyrogram
import uvloop

from app.bot.dialogs.test_dialog import test_dialog
from app.bot.middlewares.log import log_middleware
from app.bot.middlewares.user import user_middleware
from app.bot.middlewares.user_state import user_state_middleware
from app.utils.logger import configure_logger


async def main():
    # uvloop workaround
    from app import cron
    from app.bot.bot import Bot

    # Start all cron tasks
    cron.initialize()

    bot = Bot()
    bot.add_middleware(log_middleware)
    bot.add_middleware(user_middleware)
    bot.add_middleware(user_state_middleware)

    test_dialog.register(bot)

    async with bot:
        await pyrogram.idle()


if __name__ == '__main__':
    configure_logger()
    uvloop.install()
    asyncio.run(main())
