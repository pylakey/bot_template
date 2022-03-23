from typing import (
    Any,
    Callable,
    Coroutine,
    Optional,
    Union,
)

import pydantic
import pyrogram.filters


class DialogChoice(pydantic.BaseModel):
    title: str
    value: str


DialogSupportedUpdate = Union[pyrogram.types.CallbackQuery, pyrogram.types.Message]
DialogText = Union[str, Callable[[DialogSupportedUpdate], Coroutine[Any, Any, str]]]

DialogKeyboard = Optional[Union[
    pyrogram.types.InlineKeyboardMarkup,
    pyrogram.types.ReplyKeyboardMarkup,
    pyrogram.types.ReplyKeyboardRemove,
]]

# Union[T, Callable[[...], Coroutine[Any, Any, T]]]
StrChoices = Union[list[str], Callable[[DialogSupportedUpdate], Coroutine[Any, Any, list[str]]]]
Choices = Union[list[DialogChoice], Callable[[DialogSupportedUpdate], Coroutine[Any, Any, list[DialogChoice]]]]
