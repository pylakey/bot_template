import os
from pathlib import Path
from typing import (
    Optional,
    Union,
)

import pyrogram

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

    async def set_bot_commands(
            self,
            commands: Optional[list[pyrogram.types.BotCommand]],
            lang_code: str = "en",
            scope: Union[
                pyrogram.raw.types.BotCommandScopeChatAdmins,
                pyrogram.raw.types.BotCommandScopeChats,
                pyrogram.raw.types.BotCommandScopeDefault,
                pyrogram.raw.types.BotCommandScopePeer,
                pyrogram.raw.types.BotCommandScopePeerAdmins,
                pyrogram.raw.types.BotCommandScopePeerUser,
                pyrogram.raw.types.BotCommandScopeUsers
            ] = pyrogram.raw.types.BotCommandScopeUsers(),
    ):
        return await self.send(
            pyrogram.raw.functions.bots.SetBotCommands(
                scope=scope,
                lang_code=lang_code,
                commands=[c.write() for c in commands or []]
            )
        )
