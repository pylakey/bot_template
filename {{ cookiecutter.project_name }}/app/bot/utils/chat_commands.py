from typing import (
    List,
    Union,
)

import pyrogram
from pyrogram.types import BotCommand

from app.bot.bot import Bot
from app.bot.utils.custom_filters import CustomFilters


class _BaseCommand:
    # Под админом подразумевается проверка прав админа в системе, а не в чате
    command: str = None
    admin: bool = False
    custom_filter: pyrogram.filters.Filter = None

    def __init__(
            self,
            command: str,
            *,
            description: str = "Undocumented",
            admin: bool = False,
            custom_filter: pyrogram.filters.Filter = None
    ):
        self.command = command
        self.admin = admin
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
        return Bot.on_message(self.filter, group=group)


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
            custom_filter: pyrogram.filters.Filter = None,
    ):
        super(ChatCommand, self).__init__(
            command,
            description=description,
            admin=admin,
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


class PrivateCommands:
    START = ChatCommand('start', description='Main menu')

    @classmethod
    def to_bot_commands(cls, include_admin: bool = False) -> list[pyrogram.types.BotCommand]:
        commands = [
            cls.START
        ]

        return [
            BotCommand(command=c.command, description=c.description)
            for c in commands
            if not c.admin or (c.admin and include_admin)
        ]
