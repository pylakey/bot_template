from typing import (
    List,
    Union,
)

import pyrogram
from pyrogram.types import BotCommand

from app.bot.utils.custom_filters import CustomFilters


class BaseCommand:
    def __init__(self, command: str, *, description: str = "Undocumented", admin: bool = False, hidden: bool = False):
        self.command = command
        self.admin = admin
        self.hidden = hidden
        self.description = description

    @property
    def filter(self) -> pyrogram.filters.Filter:
        _filter = pyrogram.filters.all

        if self.admin:
            _filter = CustomFilters.admin & _filter

        return _filter

    def __invert__(self):
        return self.filter.__invert__()

    def __and__(self, other):
        return self.filter.__and__(other)

    def __or__(self, other):
        return self.filter.__or__(other)

    def __call__(
            self,
            custom_filter: pyrogram.filters.Filter = None,
            group: int = 0,
            admin: bool = None,
            state: str = '*'
    ):
        _filter = self.filter

        if custom_filter is not None:
            _filter = custom_filter & _filter

        if state != '*':
            _filter = CustomFilters.state(state) & _filter

        if not self.admin and admin:
            _filter = CustomFilters.admin & _filter

        return pyrogram.Client.on_message(_filter, group=group)


class ChatCommand(BaseCommand):
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
    ):
        super(ChatCommand, self).__init__(command, description=description, admin=admin, hidden=hidden)
        self.prefix = prefix
        self.private = private

    @property
    def filter(self) -> pyrogram.filters.Filter:
        _filter = super(ChatCommand, self).filter

        if self.private:
            _filter = pyrogram.filters.private & _filter

        return pyrogram.filters.command(self.command, prefixes=self.prefix) & _filter


class BaseCommandsSet:
    @classmethod
    def get_all_commands(cls) -> list[ChatCommand]:
        return [
            v
            for k, v in cls.__dict__.items()
            if not k.startswith('_') and isinstance(v, ChatCommand)
        ]

    @classmethod
    def to_bot_commands(cls, include_admin: bool = False) -> list[pyrogram.types.BotCommand]:
        commands = cls.get_all_commands()

        return [
            BotCommand(command=c.command, description=c.description)
            for c in commands
            if not c.hidden and (not c.admin or (c.admin and include_admin))
        ]

    @classmethod
    def stringify(cls, include_admin: bool = False) -> str:
        commands = cls.get_all_commands()

        return "\n".join(
            f"{c.prefix}{c.command} - {c.description}"
            for c in commands
            if not c.hidden and (not c.admin or (c.admin and include_admin))
        )


class PrivateCommands(BaseCommandsSet):
    START = ChatCommand('start', description='Main menu')
    TEST_DIALOG = ChatCommand('testdialog', description='Command to test dialog with bot')
    CANCEL = ChatCommand('cancel', description='Cancel current operation')

    # Admin
    PROMOTE_SELF = ChatCommand('promoteself', description='Promote self to be an admin with secret code', hidden=True)
    PROMOTE = ChatCommand('promote', description='Promote user to be an admin', admin=True)
