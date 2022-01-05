import pyrogram.filters

from app.bot.bot import Bot
from app.bot.utils.chat_commands import PrivateCommands


@PrivateCommands.CANCEL()
async def cancel(bot: Bot, message: pyrogram.types.Message):
    await message.bucket.state.clear()
    await message.reply("Current operation cancelled", quote=True)
    message.stop_propagation()
