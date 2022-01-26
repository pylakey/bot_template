import asyncio

import pyrogram.filters

from app.bot.bot import Bot
from app.bot.utils.callback_actions import CallbackActions
from app.bot.utils.chat_commands import PrivateCommands


@PrivateCommands.START()
async def start(bot: Bot, message: pyrogram.types.Message):
    await message.reply(
        f'Hello, {message.from_user.mention}!\n\n'
        f'<b>Available commands:</b>\n\n'
        f'{PrivateCommands.stringify(include_admin=message.bucket.user.is_admin)}',
        reply_markup=pyrogram.types.ReplyKeyboardRemove(selective=True)
    )

    asyncio.create_task(
        bot.set_commands_for_user(
            PrivateCommands,
            message.bucket.user,
            lang_code=message.from_user.language_code
        )
    )
    message.stop_propagation()


@CallbackActions.HELLO()
async def hello(bot: Bot, cq: pyrogram.types.CallbackQuery):
    await cq.answer("Hello!", show_alert=True)
    cq.stop_propagation()
