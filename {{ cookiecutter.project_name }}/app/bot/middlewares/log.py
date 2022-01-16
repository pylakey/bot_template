import logging

from pyrogram.middleware import CallNextMiddlewareCallable
from pyrogram.types import (
    CallbackQuery,
    InlineQuery,
    Message,
)

from app.bot.utils.types import UpdateFromUser

logger = logging.getLogger('log_middleware')


async def log_middleware(_, update: UpdateFromUser, call_next: CallNextMiddlewareCallable):
    logs = []

    if isinstance(update, CallbackQuery):
        logs.append(f"Data: {update.data}")
    elif isinstance(update, InlineQuery):
        logs.append(f"Query: {update.query or '-'}?offset={update.offset}")
    elif isinstance(update, Message):
        text = update.text or update.caption

        if bool(update.media):
            logs.append(f"Media message")
        elif bool(text):
            if text.startswith('/'):
                logs.append(f"Command: {text}")
            else:
                logs.append("Text message")
    else:
        logger.info(f"[{update.__class__.__name__}] Unsupported update type")
        return await call_next(_, update)

    pyrogram_user_log = f"ID: {update.from_user.id}"

    if bool(update.from_user.username):
        pyrogram_user_log += f" (https://t.me/{update.from_user.username})"

    if bool(update.from_user.language_code):
        pyrogram_user_log += f" Language: {update.from_user.language_code}"

    logs.append(pyrogram_user_log)
    logger.info(f"[{update.__class__.__name__}] {'. '.join(logs)}")

    return await call_next(_, update)
