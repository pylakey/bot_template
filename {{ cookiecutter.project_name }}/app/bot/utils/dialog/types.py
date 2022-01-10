from typing import (
    Any,
    Callable,
    Coroutine,
    Optional,
    Union,
)

import pydantic
import pyrogram.filters

from app.bot.middlewares.user_state import UserState

DialogText = Union[str, Callable[[UserState], Coroutine[Any, Any, str]]]
DialogSupportedUpdate = Union[pyrogram.types.CallbackQuery, pyrogram.types.Message]
DialogKeyboard = Optional[Union[
    pyrogram.types.InlineKeyboardMarkup,
    pyrogram.types.ReplyKeyboardMarkup,
]]
StrChoices = Union[list[str], Callable[[...], list[str]]]
Choices = Union[list['DialogChoice'], Callable[[...], list['DialogChoice']]]


class DialogChoice(pydantic.BaseModel):
    title: str
    value: Union[bool, int, str]

    class Config:
        smart_union = True
