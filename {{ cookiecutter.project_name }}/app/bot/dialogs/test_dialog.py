import pyrogram.types

from app.bot.utils.dialog import (
    Dialog,
    DialogActionInput,
    DialogActionPrompt,
)
from app.utils import json


class TestDialog(Dialog):
    first_name = DialogActionInput("Enter your first name")
    last_name = DialogActionInput("Enter your last name")
    age = DialogActionInput("Enter your age", cast=int)
    is_eighteen = DialogActionPrompt("Is everything right?")

    async def on_finish(self, message: pyrogram.types.Message, final_data: dict):
        await message.reply(
            f"<b>Done:</b>\n"
            f"{json.dumps(final_data, indent=4)}"
        )


test_dialog = TestDialog()
