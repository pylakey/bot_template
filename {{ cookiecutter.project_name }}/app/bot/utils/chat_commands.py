import inspect
from typing import (
    List,
    Union,
)

import pyrogram
from pyrogram.types import BotCommand

from app.bot.utils.custom_filters import CustomFilters


class _BaseCommand:
    # Под админом подразумевается проверка прав админа в системе, а не в чате
    command: str = None
    admin: bool = False
    hidden: bool = False
    custom_filter: pyrogram.filters.Filter = None

    def __init__(
            self,
            command: str,
            *,
            description: str = "Undocumented",
            admin: bool = False,
            hidden: bool = False,
            custom_filter: pyrogram.filters.Filter = None
    ):
        self.command = command
        self.admin = admin
        self.hidden = hidden
        self.custom_filter = custom_filter
        self.description = description

    @property
    def filter(self) -> pyrogram.filters.Filter:
        _filter = pyrogram.filters.all

        if self.admin:
            _filter = CustomFilters.admin & _filter

        if self.custom_filter is not None:
            _filter = self.custom_filter & _filter

        return _filter

    def __invert__(self):
        return self.filter.__invert__()

    def __and__(self, other):
        return self.filter.__and__(other)

    def __or__(self, other):
        return self.filter.__or__(other)

    def __call__(self, group: int = 0):
        return pyrogram.Client.on_message(self.filter, group=group)


class ChatCommand(_BaseCommand):
    prefix: Union[str, List[str]] = "/"
    private: bool = True
    description: str = "-"

    def __init__(
            self,
            command: str,
            *,
            description: str = "undocumented",
            prefix: Union[str, List[str]] = "/",
            private: bool = True,
            admin: bool = False,
            hidden: bool = False,
            custom_filter: pyrogram.filters.Filter = None,
    ):
        super(ChatCommand, self).__init__(
            command,
            description=description,
            admin=admin,
            hidden=hidden,
            custom_filter=custom_filter
        )
        self.prefix = prefix
        self.private = private

    @property
    def filter(self) -> pyrogram.filters.Filter:
        _filter = super(ChatCommand, self).filter

        if self.private:
            _filter = pyrogram.filters.private & _filter

        return _filter & pyrogram.filters.command(self.command, prefixes=self.prefix)


class BaseCommandsSet:
    @classmethod
    def to_bot_commands(cls, include_admin: bool = False) -> list[pyrogram.types.BotCommand]:
        attributes = inspect.getmembers(cls, lambda a: not (inspect.isroutine(a)))
        commands = [a for a in attributes if not (a[0].startswith('__') and a[0].endswith('__'))]

        return [
            BotCommand(command=value.command, description=value.description)
            for (name, value) in commands
            if (
                    isinstance(value, ChatCommand)
                    and not value.hidden
                    and (not value.admin or (value.admin and include_admin))
            )
        ]


class PrivateCommands(BaseCommandsSet):
    START = ChatCommand('start', description='Main menu')

    # Admin
    PROMOTE_SELF = ChatCommand('promoteself', description='Promote self to be an admin with secret code', hidden=True)
    PROMOTE = ChatCommand('promote', description='Promote user to be an admin', admin=True)
