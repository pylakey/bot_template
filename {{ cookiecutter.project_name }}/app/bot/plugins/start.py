import asyncio

import pyrogram.filters

from app.bot.bot import Bot
from app.bot.utils.chat_commands import PrivateCommands


@PrivateCommands.START()
async def start(bot: Bot, message: pyrogram.types.Message):
    await message.reply(f'Hello, {message.from_user.mention}!')
    asyncio.create_task(bot.set_private_commands_for_user(
        message.bucket.user,
        lang_code=message.from_user.language_code
    ))
    message.stop_propagation()
