import pyrogram.filters

from app.bot.bot import Bot
from app.bot.dialogs.test_dialog import test_dialog
from app.bot.utils.chat_commands import PrivateCommands


@PrivateCommands.TEST_DIALOG()
async def test_dialog_command(bot: Bot, message: pyrogram.types.Message):
    await test_dialog.start(message)
    message.stop_propagation()
