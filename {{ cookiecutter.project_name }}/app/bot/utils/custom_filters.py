import re
from typing import (
    List,
    Optional,
    Union,
)

import pydash
import pyrogram
from pyrogram import filters


def _check_admin(_, __, update: Union[pyrogram.types.Message, pyrogram.types.CallbackQuery]):
    user = getattr(update.bucket, 'user', None)

    if not bool(user):
        return False

    return getattr(user, 'is_admin', False)


def _check_cq_regex(f, client: pyrogram.Client, cq: pyrogram.types.CallbackQuery):
    return bool(re.match(fr"^({f.data}|{f.data}\?.*)$", cq.data, re.IGNORECASE))


def _check_not_command(f, client: pyrogram.Client, message: pyrogram.types.Message):
    prefixes = list(f.prefixes)
    message_text = message.text or message.caption

    if not message_text:
        return True

    for p in prefixes:
        if message_text.startswith(p):
            return False

    return True


def _check_state(
        f,
        client: pyrogram.Client,
        update: Union[pyrogram.types.Message, pyrogram.types.CallbackQuery, pyrogram.types.InlineQuery]
):
    check_states = f.state if isinstance(f.state, list) else [f.state]

    if '*' in check_states:
        return True

    state = pydash.get(update, 'bucket.user_state.state', None)

    return state in check_states


class CustomFilters:
    admin = filters.create(_check_admin, "AdminRightsFilter")

    @staticmethod
    def callback_data(callback_data: str) -> filters.Filter:
        return filters.create(_check_cq_regex, "CallbackDataRegexFilter", data=callback_data)

    @staticmethod
    def not_command(prefixes: Union[List[str], str] = '/') -> filters.Filter:
        return filters.create(_check_not_command, "CheckNotCommand", prefixes=prefixes)

    @staticmethod
    def state(state: Union[Optional[str], List[Optional[str]]] = '*') -> filters.Filter:
        return filters.create(_check_state, "CheckUserState", state=state)

    @staticmethod
    def reply_command(
            commands: str or list,
            prefixes: str or list = "/",
            case_sensitive: bool = False
    ) -> filters.Filter:
        return filters.incoming & filters.reply & filters.command(commands, prefixes, case_sensitive)

    @staticmethod
    def private_reply_command(
            commands: str or list,
            prefixes: str or list = "/",
            case_sensitive: bool = False
    ) -> filters.Filter:
        return filters.private & CustomFilters.reply_command(commands, prefixes, case_sensitive)

    @staticmethod
    def group_reply_command(
            commands: str or list,
            prefixes: str or list = "/",
            case_sensitive: bool = False
    ) -> filters.Filter:
        return filters.group & CustomFilters.reply_command(commands, prefixes, case_sensitive)
