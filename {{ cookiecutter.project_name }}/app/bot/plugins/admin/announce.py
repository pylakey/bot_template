import pyrogram.filters

from app.bot.bot import Bot
from app.bot.utils.chat_commands import (
    CommandArgs,
    PrivateCommands,
)
from app.database import crud


class AnnounceArgs(CommandArgs):
    users: list[int] = []


@PrivateCommands.ANNOUNCE(reply=True, args_model=AnnounceArgs)
async def announce(bot: Bot, message: pyrogram.types.Message):
    users = message.bucket.args.users

    if len(users) == 0:
        users = [u.id for u in (await crud.user.get_multi())]

    await bot.broadcast_message(message.reply_to_message, chats=users)
    message.stop_propagation()
