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


class UserState(pydantic.BaseModel):
    # Classmethod
    _redis: aioredis.Redis = None

    chat_id: int
    user_id: int
    name: str = None
    data: dict = None

    async def clear(self) -> 'UserState':
        return await self.set(name=None, data=None)

    async def set(self, name: str = None, data: dict = None) -> 'UserState':
        redis = await UserState.get_redis()
        self.name = name
        self.data = data
        await redis.set(f"{self.chat_id}_{self.user_id}", self.json())
        return self

    @classmethod
    async def get_redis(cls) -> aioredis.Redis:
        if cls._redis is None:
            cls._redis = await aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")

        return cls._redis

    class Config:
        json_dumps = json.dumps
        json_loads = json.loads
        use_enum_values = True
        validate_assignment = True


async def user_state_middleware(_, update: Union[Message, CallbackQuery], call_next: CallNextMiddlewareCallable):
    if isinstance(update, (Message, CallbackQuery)):
        redis = await UserState.get_redis()
        user_state_data = await redis.get(f"{update.chat.id}_{update.from_user.id}")
        user_state_data = json.loads(user_state_data) if bool(user_state_data) else {}

        user_state = UserState(
            chat_id=update.chat.id,
            user_id=update.from_user.id,
            name=user_state_data.get('name'),
            data=user_state_data.get('data'),
        )
        update.bucket.state = user_state

        if isinstance(update, CallbackQuery):
            update.message.bucket.state = user_state

    return await call_next(_, update)
