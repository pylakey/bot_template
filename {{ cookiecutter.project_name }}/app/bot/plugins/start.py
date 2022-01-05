import asyncio

import pyrogram.filters

from app.bot.bot import Bot
from app.bot.utils.callback_actions import CallbackActions
from app.bot.utils.chat_commands import PrivateCommands


@PrivateCommands.START()
async def start(bot: Bot, message: pyrogram.types.Message):
    reply_markup = pyrogram.types.InlineKeyboardMarkup([[CallbackActions.HELLO.button("Hello!")]])
    await message.reply(f'Hello, {message.from_user.mention}!', reply_markup=reply_markup)

    asyncio.create_task(
        bot.set_private_commands_for_user(
            message.bucket.user,
            lang_code=message.from_user.language_code
        )
    )
    message.stop_propagation()


@CallbackActions.HELLO()
async def hello(bot: Bot, cq: pyrogram.types.CallbackQuery):
    await cq.answer("Hello!", show_alert=True)
    cq.stop_propagation()
