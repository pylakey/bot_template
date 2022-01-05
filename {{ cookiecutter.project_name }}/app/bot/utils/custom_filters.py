import logging
import re
from typing import (
    List,
    Optional,
    Union,
)

import pyrogram
from pyrogram import filters

from app.bot.middlewares.user_state import UserState

logger = logging.getLogger('CustomFilters')


def _check_admin(_, __, update: Union[pyrogram.types.Message, pyrogram.types.CallbackQuery]):
    user = getattr(update.bucket, 'user', None)

    if not bool(user):
        return False

    return getattr(user, 'is_admin', False)


def _check_cq_regex(f, _, cq: pyrogram.types.CallbackQuery):
    return bool(re.match(fr"^({f.data}|{f.data}\?.*)$", cq.data, re.IGNORECASE))


def _check_state(f, _, update: Union[pyrogram.types.Message, pyrogram.types.CallbackQuery]):
    if not isinstance(update, (pyrogram.types.Message, pyrogram.types.CallbackQuery)):
        return True

    check_states = f.state if isinstance(f.state, list) else [f.state]

    if '*' in check_states:
        return True

    state: UserState = update.bucket.state

    if state is None:
        logger.warning("User state is None! You probably disabled user_state middleware!")
        return False

    return state.name in check_states


class CustomFilters:
    admin = filters.create(_check_admin, "AdminRightsFilter")

    @staticmethod
    def callback_data(regex: str) -> filters.Filter:
        return filters.create(_check_cq_regex, "CallbackDataRegexFilter", data=regex)

    @staticmethod
    def state(state: Union[Optional[str], List[Optional[str]]] = '*') -> filters.Filter:
        return filters.create(_check_state, "CheckUserState", state=state)
