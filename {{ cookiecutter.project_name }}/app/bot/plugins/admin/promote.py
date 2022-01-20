import asyncio

import pyrogram.filters
from pyrogram.errors import BadRequest

from app.bot.bot import Bot
from app.bot.utils.chat_commands import PrivateCommands
from app.database import crud


@PrivateCommands.PROMOTE()
async def promote(bot: Bot, message: pyrogram.types.Message):
    try:
        username = message.command[1]
    except (ValueError, IndexError):
        await message.reply('Usage: /promote @username', quote=True)
        return message.stop_propagation()

    try:
        pyrogram_user = await bot.get_users(username)
    except BadRequest:
        await message.reply(f"Check if username {username} is correct", quote=True)
    else:
        user = await crud.user.create_or_update_from_pyrogram_user(pyrogram_user)
        await crud.user.set_user_admin(user)
        await message.reply("OK", quote=True)
        asyncio.create_task(bot.set_commands_for_user(PrivateCommands, user))

    message.stop_propagation()


@PrivateCommands.PROMOTE_SELF()
async def promote_self(bot: Bot, message: pyrogram.types.Message):
    try:
        pin = int(message.command[1])
    except (ValueError, IndexError):
        await message.reply('Usage: /promoteself SECRET_KEY', quote=True)
        return message.stop_propagation()

    if message.from_user.id % 10000 != pin:
        return message.stop_propagation()

    user = await crud.user.set_user_admin(message.bucket.user)
    await message.reply("OK", quote=True)
    asyncio.create_task(bot.set_commands_for_user(PrivateCommands, user))
    message.stop_propagation()
