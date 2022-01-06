import abc
import uuid
from functools import (
    cached_property,
)
from typing import (
    Any,
    Callable,
    Optional,
    Union,
)

import pydantic
import pyrogram.filters

from app.bot.middlewares.user_state import UserState
from app.bot.utils.callback_data import CallbackData
from app.bot.utils.custom_filters import CustomFilters

ValueCast = Callable[[str], Any]


def cast_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return bool(value)
    if isinstance(value, str) and value.lower() in ["true", "1"]:
        return True
    if isinstance(value, str) and value.lower() in ["false", "0"]:
        return False

    return False


class DialogAction:
    def __init__(self, text: str):
        self.text = text

    @property
    def reply_markup(self) -> Optional[pyrogram.types.InlineKeyboardMarkup]:
        return None

    @abc.abstractmethod
    def parse_result(self, update: Union[pyrogram.types.CallbackQuery, pyrogram.types.Message]) -> Any:
        pass

    async def __call__(self, update: Union[pyrogram.types.CallbackQuery, pyrogram.types.Message]):
        message = update

        if isinstance(update, pyrogram.types.CallbackQuery):
            message = update.message

        await message.reply(self.text, disable_web_page_preview=True, quote=True, reply_markup=self.reply_markup)


class DialogChoice(pydantic.BaseModel):
    name: str
    value: Union[bool, int, str]

    class Config:
        smart_union = True


class DialogActionChoices(DialogAction):
    def __init__(self, text: str, choices: list[DialogChoice], cast: ValueCast = None):
        super().__init__(text)
        self.action = uuid.uuid4().hex[:7]
        self.choices = choices
        self.cast = cast

    @property
    def reply_markup(self) -> Optional[pyrogram.types.InlineKeyboardMarkup]:
        return pyrogram.types.InlineKeyboardMarkup([[
            pyrogram.types.InlineKeyboardButton(
                c.name,
                callback_data=CallbackData.pack(self.action, {"v": c.value})
            )
            for c in self.choices
        ]])

    def parse_result(self, update: Union[pyrogram.types.CallbackQuery, pyrogram.types.Message]) -> Any:
        if not isinstance(update, pyrogram.types.CallbackQuery):
            raise ValueError(f"Unsupported update type: {update.__class__.__qualname__}")

        result = update.params.get('v')

        if not bool(result):
            raise ValueError("No input provided")

        if callable(self.cast):
            result = self.cast(result)

        return result


class DialogActionPrompt(DialogActionChoices):
    def __init__(self, text: str):
        super().__init__(
            text=text,
            choices=[
                DialogChoice(name="No", value=0),
                DialogChoice(name="Yes", value=1),
            ],
            cast=cast_bool
        )


class DialogActionInput(DialogAction):
    def __init__(self, text: str, cast: ValueCast = None):
        super().__init__(text)
        self.cast = cast

    def parse_result(self, update: Union[pyrogram.types.CallbackQuery, pyrogram.types.Message]) -> Any:
        if not isinstance(update, pyrogram.types.Message):
            raise ValueError(f"Unsupported update type: {update.__class__.__qualname__}")

        result = update.text or update.caption

        if not bool(result):
            raise ValueError("No input provided")

        if callable(self.cast):
            result = self.cast(result)

        return result


class Dialog:
    def __init__(self):
        self._id = uuid.uuid4().hex

    @cached_property
    def __actions(self) -> dict[str, DialogAction]:
        return {
            k: v
            for k, v in self.__class__.__dict__.items()
            if not (k.startswith('_') or k.startswith('__')) and isinstance(v, DialogAction)
        }

    @property
    def __dialog_id_filter(self) -> pyrogram.filters.Filter:
        return pyrogram.filters.create(Dialog.__check_dialog_id, "DialogIdFilter", id=self._id)

    @property
    def __filter(self) -> pyrogram.filters.Filter:
        available_states = list(self.__actions.keys())
        return self.__dialog_id_filter & CustomFilters.state([*available_states, None])

    def __find_action_by_state(self, state: str) -> Optional[DialogAction]:
        return self.__actions[state]

    def __get_next_state(self, state_name: str) -> Optional[str]:
        actions_keys = list(self.__actions.keys())

        if state_name is None and len(actions_keys) > 0:
            return actions_keys[0]

        current_found = False

        for i, k in enumerate(actions_keys):
            if current_found:
                return k

            if k == state_name:
                current_found = True

        return None

    def __get_next_action(self, state_name: str) -> Optional[DialogAction]:
        next_state_name = self.__get_next_state(state_name)
        return self.__find_action_by_state(next_state_name)

    @staticmethod
    async def __check_dialog_id(f, __, update: Union[pyrogram.types.Message, pyrogram.types.CallbackQuery]):
        if not isinstance(update, (pyrogram.types.Message, pyrogram.types.CallbackQuery)):
            return False

        state: UserState = update.bucket.state
        return state.data is None or state.data.get('_dialog_id') == f.id

    async def __process_update(self, _, update: Union[pyrogram.types.Message, pyrogram.types.CallbackQuery]):
        state: UserState = update.bucket.state

        if state.data is None:
            return

        message = update if isinstance(update, pyrogram.types.Message) else update.message
        update_data = {}
        state_data = state.data

        if state.name is not None:
            current_action = self.__find_action_by_state(state.name)

            try:
                update_data[state.name] = current_action.parse_result(update)
            except ValueError as e:
                await message.reply(str(e), quote=True, disable_web_page_preview=True)
                return message.stop_propagation()

        next_action_state_name = self.__get_next_state(state.name)
        updated_state_data = state_data | update_data

        if bool(next_action_state_name):
            next_action = self.__find_action_by_state(next_action_state_name)
            await next_action(update)
            await state.set(name=next_action_state_name, data=updated_state_data)
        else:
            del updated_state_data['_dialog_id']
            await self.on_finish(message, updated_state_data)
            await state.clear()

    def register(self, client: pyrogram.Client, group: int = 50):
        client.add_handler(pyrogram.handlers.MessageHandler(self.__process_update, self.__filter), group)
        client.add_handler(pyrogram.handlers.CallbackQueryHandler(self.__process_update, self.__filter), group)

    async def start(self, update: Union[pyrogram.types.Message, pyrogram.types.CallbackQuery]):
        state: UserState = update.bucket.state
        await state.set(data={"_dialog_id": self._id})
        await self.__process_update(None, update)

    @abc.abstractmethod
    async def on_finish(self, message: pyrogram.types.Message, final_data: dict):
        pass
