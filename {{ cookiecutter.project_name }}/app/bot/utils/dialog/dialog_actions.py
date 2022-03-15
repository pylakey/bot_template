import abc
import uuid
from typing import (
    Any,
    Type,
    TypeVar,
)

import pydantic
import pydash
import pyrogram.filters
from pydantic import ValidationError

from app.bot.utils.callback_data import CallbackData
from .types import (
    Choices,
    DialogChoice,
    DialogKeyboard,
    DialogSupportedUpdate,
    DialogText,
    StrChoices,
)

ResultType = TypeVar('ResultType')


class DialogAction(abc.ABC):
    supported_updates = [pyrogram.types.CallbackQuery, pyrogram.types.Message]

    def __init__(
            self,
            text: DialogText,
            result_type: Type[ResultType] = str,
            gt: float = None,
            ge: float = None,
            lt: float = None,
            le: float = None,
            multiple_of: float = None,
            max_digits: int = None,
            decimal_places: int = None,
            min_length: int = None,
            max_length: int = None,
            regex: str = None,
    ):
        self.text = text
        self.result_model = pydantic.create_model(
            'DialogActionResultModel',
            value=(
                result_type,
                pydantic.Field(
                    ...,
                    gt=gt,
                    ge=ge,
                    lt=lt,
                    le=le,
                    multiple_of=multiple_of,
                    max_digits=max_digits,
                    decimal_places=decimal_places,
                    min_length=min_length,
                    max_length=max_length,
                    regex=regex,
                )
            ),
        )

    async def parse_result(self, update: DialogSupportedUpdate) -> ResultType:
        if type(update) not in self.supported_updates:
            raise TypeError(f"Unsupported update type: {update.__class__.__qualname__}")

        result = await self.get_result_from_update(update)

        try:
            return self.result_model(value=result).value
        except ValidationError as e:
            errors = e.errors()

            if len(errors) > 0:
                raise ValueError(e.errors()[0].get('msg').capitalize())

            raise ValueError('Incorrect value')

    async def get_reply_markup(self) -> DialogKeyboard:
        return pyrogram.types.ReplyKeyboardRemove(selective=True)

    @abc.abstractmethod
    async def get_result_from_update(self, update: DialogSupportedUpdate) -> Any:
        raise NotImplementedError

    async def __call__(self, update: DialogSupportedUpdate):
        message = update

        if isinstance(update, pyrogram.types.CallbackQuery):
            message = update.message

        if callable(self.text):
            text = await self.text(update.bucket.state)
        else:
            text = self.text

        reply_markup = await self.get_reply_markup()
        await message.reply(text, disable_web_page_preview=True, reply_markup=reply_markup)


class DialogMessageAction(DialogAction, abc.ABC):
    supported_updates = [pyrogram.types.Message]

    @abc.abstractmethod
    async def get_result_from_update(self, update: pyrogram.types.Message) -> Any:
        raise NotImplementedError


class DialogCallbackQueryAction(DialogAction, abc.ABC):
    supported_updates = [pyrogram.types.CallbackQuery]

    @abc.abstractmethod
    async def get_reply_markup(self) -> pyrogram.types.InlineKeyboardMarkup:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_result_from_update(self, update: pyrogram.types.CallbackQuery) -> Any:
        raise NotImplementedError


class DialogActionText(DialogMessageAction):
    async def get_result_from_update(self, update: pyrogram.types.Message) -> Any:
        if not isinstance(update, pyrogram.types.Message):
            raise ValueError(f"Unsupported update type: {update.__class__.__qualname__}")

        return update.text or update.caption


class DialogActionReplySelect(DialogActionText):
    def __init__(self, text: DialogText, choices: StrChoices, columns: int = 3):
        super().__init__(text)
        self.choices = choices
        self.columns = columns

    async def get_reply_markup(self) -> pyrogram.types.ReplyKeyboardMarkup:
        if callable(self.choices):
            choices = await self.choices()
        else:
            choices = self.choices

        rows = pydash.chunk(choices, self.columns)

        return pyrogram.types.ReplyKeyboardMarkup(rows, resize_keyboard=True, one_time_keyboard=True)


class DialogActionInlineSelect(DialogCallbackQueryAction):
    def __init__(self, text: DialogText, choices: Choices, result_type: Type[ResultType] = str, columns: int = 1):
        super().__init__(text, result_type=result_type)
        self.action = uuid.uuid4().hex[:7]
        self.choices = choices
        self.columns = columns

    async def get_result_from_update(self, update: pyrogram.types.CallbackQuery) -> Any:
        return update.params.get('v')

    async def get_reply_markup(self) -> DialogKeyboard:
        if callable(self.choices):
            choices = await self.choices()
        else:
            choices = self.choices

        buttons = pydash.chunk([
            pyrogram.types.InlineKeyboardButton(
                c.title,
                callback_data=CallbackData.pack(self.action, {"v": c.value})
            )
            for c in choices
        ], self.columns)

        return pyrogram.types.InlineKeyboardMarkup(buttons)


class DialogActionBoolPrompt(DialogActionInlineSelect):
    def __init__(self, text: DialogText):
        super().__init__(
            text=text,
            choices=[
                DialogChoice(title="No", value=0),
                DialogChoice(title="Yes", value=1),
            ],
            result_type=bool,
            columns=2
        )
