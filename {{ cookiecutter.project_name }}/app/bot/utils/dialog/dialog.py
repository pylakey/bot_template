import abc
import uuid
from functools import (
    cached_property,
)
from typing import (
    Optional,
    Union,
)

import pyrogram.filters

from app.bot.middlewares.user_state import UserState
from app.bot.utils.custom_filters import CustomFilters
from .dialog_actions import DialogAction


class Dialog:
    def __init__(self):
        self.__id = f"{self.__class__.__name__}_{uuid.uuid4().hex[:8]}"

    def register(self, client: pyrogram.Client, group: int = 50):
        client.add_handler(pyrogram.handlers.MessageHandler(self.__process_update, self.__filter), group)
        client.add_handler(pyrogram.handlers.CallbackQueryHandler(self.__process_update, self.__filter), group)

    async def start(self, update: Union[pyrogram.types.Message, pyrogram.types.CallbackQuery]):
        state: UserState = update.bucket.state
        await state.set(data={"_dialog_id": self.__id})
        await self.__process_update(None, update)

    @abc.abstractmethod
    async def on_finish(self, message: pyrogram.types.Message, final_data: dict):
        pass

    @cached_property
    def __actions(self) -> dict[str, DialogAction]:
        return {
            k: v
            for k, v in self.__class__.__dict__.items()
            if not (k.startswith('_') or k.startswith('__')) and isinstance(v, DialogAction)
        }

    @property
    def __dialog_id_filter(self) -> pyrogram.filters.Filter:
        return pyrogram.filters.create(Dialog.__check_dialog_id, "DialogIdFilter", id=self.__id)

    @property
    def __filter(self) -> pyrogram.filters.Filter:
        available_states = list(self.__actions.keys())
        return self.__dialog_id_filter & CustomFilters.state([*available_states, None])

    def __find_action_by_state(self, state: str) -> DialogAction:
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
        state_data = state.data

        if state_data is None:
            return

        message = update if isinstance(update, pyrogram.types.Message) else update.message
        update_data = {}

        if state.name is not None:
            current_action = self.__find_action_by_state(state.name)

            try:
                update_data[state.name] = await current_action.parse_result(update)
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
