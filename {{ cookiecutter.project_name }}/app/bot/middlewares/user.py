import logging

from pyrogram.middleware import CallNextMiddlewareCallable
from pyrogram.types import (
    CallbackQuery,
    InlineQuery,
    Message,
)

from app.bot.utils.types import UpdateFromUser
from app.database import crud

logger = logging.getLogger('user_middleware')


async def user_middleware(_, update: UpdateFromUser, call_next: CallNextMiddlewareCallable):
    if isinstance(update, (Message, CallbackQuery, InlineQuery)):
        try:
            user = await crud.user.create_or_update_from_pyrogram_user(update.from_user)
        except Exception as _e:
            logger.error(
                f'Unable to create TG user. Stop from using BOT {_e.__class__.__qualname__}. {_e}',
                exc_info=True
            )
            return update.stop_propagation()

        update.bucket.user = user

        if isinstance(update, CallbackQuery):
            update.message.bucket.user = user

    return await call_next(_, update)
