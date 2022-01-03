import asyncio

import pyrogram.filters

from app.bot.bot import Bot
from app.bot.utils.chat_commands import PrivateCommands


@PrivateCommands.START()
async def start(bot: Bot, message: pyrogram.types.Message):
    await message.reply(f'Hello, {message.from_user.mention}!')
    asyncio.create_task(bot.set_bot_commands(
        commands=PrivateCommands.to_bot_commands(),
        lang_code=message.from_user.language_code or "en"
    ))
    message.stop_propagation()
