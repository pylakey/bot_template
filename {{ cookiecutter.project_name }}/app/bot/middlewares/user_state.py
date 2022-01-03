import logging

from pyrogram.middleware import CallNextMiddlewareCallable
from pyrogram.types import (
    CallbackQuery,
    InlineQuery,
    Message,
)

from app.bot.utils.types import UpdateFromUser

logger = logging.getLogger('user_state_middleware')


async def user_state_middleware(_, update: UpdateFromUser, call_next: CallNextMiddlewareCallable):
    if isinstance(update, (Message, CallbackQuery, InlineQuery)):
        # TODO: Get from redis
        user_state = None

        update.bucket.user_state = user_state

        if isinstance(update, CallbackQuery):
            update.message.bucket.user_state = user_state

    return await call_next(_, update)
