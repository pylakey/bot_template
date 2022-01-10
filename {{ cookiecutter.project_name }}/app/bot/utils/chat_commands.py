from functools import cached_property
from typing import (
    List,
    Optional,
    Type,
    Union,
)

import pydantic
import pydash
import pyrogram
from pyrogram.types import BotCommand

from app.bot.utils.custom_filters import CustomFilters


class ChatCommand:
    def __init__(
            self,
            command: str,
            *,
            description: str = "Undocumented",
            prefix: Union[str, List[str]] = "/",
            admin: bool = False,
            hidden: bool = False,
            private: bool = True,
            args_model: Union[dict, Type[pydantic.BaseModel]] = None
    ):
        self.command = command
        self.admin = admin
        self.hidden = hidden
        self.description = description
        self.prefix = prefix
        self.private = private
        self.args_model = (
            pydantic.create_model('ArgsModel', **args_model)
            if isinstance(args_model, dict)
            else args_model
        )

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
            private: bool = None,
            state: str = '*',
            args_model: Union[dict, Type[pydantic.BaseModel]] = None
    ):
        self.args_model = (
            pydantic.create_model('ArgsModel', **args_model)
            if isinstance(args_model, dict)
            else args_model
        )
        _filter = self.filter

        if custom_filter is not None:
            _filter = custom_filter & _filter

        if state != '*':
            _filter = CustomFilters.state(state) & _filter

        if not self.admin and admin:
            _filter = CustomFilters.admin & _filter

        if not self.private and private:
            _filter = pyrogram.filters.private & _filter

        command = self

        def decorator(func: callable):
            @pyrogram.Client.on_message(_filter)
            async def decorated(_, message: pyrogram.types.Message):
                try:
                    message.bucket.args = await command.parse_args(message.command[1:])
                except ValueError as e:
                    await message.reply(f"{e}", quote=True, disable_web_page_preview=True)
                    return message.stop_propagation()

                await func(_, message)

            return decorated

        return decorator

    @property
    def filter(self) -> pyrogram.filters.Filter:
        _filter = pyrogram.filters.all

        if self.admin:
            _filter = CustomFilters.admin & _filter

        if self.private:
            _filter = pyrogram.filters.private & _filter

        _filter = pyrogram.filters.command(self.command, prefixes=self.prefix) & _filter

        return _filter

    @property
    def usage(self) -> str:
        return (
            f"{self.description}\n\n"
            f"<b>Usage:</b>\n"
            f"{self.prefix}{self.command} {self.args_syntax}\n\n"
            f"{self.args_help}"
        ).strip()

    @cached_property
    def args_syntax(self) -> str:
        results = []

        for field in self.args_model.__fields__.values():  # type: pydantic.fields.ModelField
            upper_name = field.name.upper()

            if field.shape == pydantic.fields.SHAPE_LIST:
                field_text = f"{upper_name}_1 {upper_name}_2 ... {upper_name}_N"
            else:
                field_text = f"{upper_name}"

            if not field.required:
                field_text = f"[{field_text}]"

            results.append(field_text)

        return " ".join(results)

    @cached_property
    def args_help(self) -> str:
        results = []

        for field in self.args_model.__fields__.values():  # type: pydantic.fields.ModelField
            if not bool(field.field_info.description):
                continue

            field_text = f"{field.name.upper()}"

            if not field.required:
                optional = "Optional"

                if bool(field.default):
                    optional += f", Default: {field.default}"

                field_text += f"<i>({optional})</i>"

            field_text += f" - {field.field_info.description}"

            results.append(field_text)

        return "<b>Parameters:</b>\n" + "\n".join(results)

    async def parse_args(self, command_params: list[str] = None) -> Optional[pydantic.BaseModel]:
        if self.args_model is None:
            return None

        data = {}

        for field in self.args_model.__fields__.values():
            if field.required and len(command_params) == 0:
                raise ValueError(str(self.usage))

            if field.shape == pydantic.fields.SHAPE_LIST:
                if len(command_params) > 0:
                    data[field.name] = command_params
                elif not field.required:
                    data[field.name] = []

                break

            try:
                data[field.name] = command_params.pop(0)
            except IndexError:
                break

        try:
            return self.args_model.parse_obj(data)
        except pydantic.ValidationError as e:
            errors = e.errors()

            if len(errors) > 0:
                errs = []

                for err in errors:
                    err_msg = err.get('msg').capitalize()
                    err_val = pydash.get(data, list(err.get('loc')))
                    field_name = err.get('loc')[0].upper()

                    if bool(err_val):
                        errs.append(f"{err_val} - {err_msg}")
                    else:
                        errs.append(f"{field_name} - {err_msg}")

                errs_string = "\n".join(errs)
                raise ValueError(str(
                    f"<b>Error:</b>\n"
                    f"{errs_string}\n\n"
                    f"{self.usage}",
                ))

            raise ValueError("Incorrect value")


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
    TEST_ARGS_COMMAND = ChatCommand('testargs', description='Command to test command with arguments')
    CANCEL = ChatCommand('cancel', description='Cancel current operation')

    # Admin
    PROMOTE_SELF = ChatCommand('promoteself', description='Promote self to be an admin with secret code', hidden=True)
    PROMOTE = ChatCommand('promote', description='Promote user to be an admin', admin=True)
