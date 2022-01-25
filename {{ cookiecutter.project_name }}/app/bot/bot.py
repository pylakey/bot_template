import logging
import os
from pathlib import Path
from typing import Type

import pyrogram

from app.bot.utils.chat_commands import (
    BaseCommandsSet,
    PrivateCommands,
)
from app.database.model.user import User
from app.settings import settings


class Bot(pyrogram.Client):
    def __init__(self):
        super().__init__(
            f"bot_{settings.BOT_ID}",
            api_id=settings.BOT_API_ID,
            api_hash=settings.BOT_API_HASH,
            bot_token=settings.BOT_TOKEN,
            workdir=settings.SESSIONS_DIR,
            plugins={'root': str(Path(__file__).parent.relative_to(os.getcwd()) / "plugins")},
        )
        self.set_parse_mode('html')
        self.logger = logging.getLogger('Bot')

    async def start(self):
        await super(Bot, self).start()
        await self.set_commands_for_everyone(PrivateCommands)

    async def set_commands_for_user(self, commands_class: Type[BaseCommandsSet], user: User, lang_code: str = "en"):
        commands = commands_class.to_bot_commands(include_admin=user.is_admin)

        await self.send(
            pyrogram.raw.functions.bots.SetBotCommands(
                scope=pyrogram.raw.types.BotCommandScopePeer(
                    peer=(await self.resolve_peer(user.id))
                ),
                lang_code=lang_code or "en",
                commands=[c.write() for c in commands or []]
            )
        )

    async def set_commands_for_everyone(self, commands_class: Type[BaseCommandsSet]):
        scope = pyrogram.raw.types.BotCommandScopeUsers()
        langs = ["ru", "en"]
        commands = [c.write() for c in commands_class.to_bot_commands(include_admin=False)]

        for lang in langs:
            await self.send(
                pyrogram.raw.functions.bots.SetBotCommands(
                    scope=scope,
                    lang_code=lang,
                    commands=commands
                )
            )
