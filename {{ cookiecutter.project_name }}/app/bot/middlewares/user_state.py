import logging
from typing import Union

import aioredis
import pydantic
from pyrogram.middleware import CallNextMiddlewareCallable
from pyrogram.types import (
    CallbackQuery,
    Message,
)

from app.settings import settings
from app.utils import json

logger = logging.getLogger('user_state_middleware')
redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.BOT_ID}_user_states")


class UserState(pydantic.BaseModel):
    chat_id: int
    user_id: int
    name: str = None
    data: dict = None

    async def clear(self) -> 'UserState':
        return await self.set(name=None, data=None)

    async def set(self, name: str = None, data: dict = None) -> 'UserState':
        self.name = name
        self.data = data
        await redis.set(f"{self.chat_id}_{self.user_id}", self.json())
        return self

    class Config:
        json_dumps = json.dumps
        json_loads = json.loads
        use_enum_values = True
        validate_assignment = True


async def user_state_middleware(_, update: Union[Message, CallbackQuery], call_next: CallNextMiddlewareCallable):
    if isinstance(update, (Message, CallbackQuery)):
        message = update if isinstance(update, Message) else update.message
        user_state_data = await redis.get(f"{message.chat.id}_{update.from_user.id}")
        user_state_data = json.loads(user_state_data.decode('utf-8')) if bool(user_state_data) else {}

        user_state = UserState(
            chat_id=message.chat.id,
            user_id=update.from_user.id,
            name=user_state_data.get('name'),
            data=user_state_data.get('data'),
        )
        update.bucket.state = user_state

        if isinstance(update, CallbackQuery):
            update.message.bucket.state = user_state

    return await call_next(_, update)
