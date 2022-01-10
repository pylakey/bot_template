import pyrogram.types

from app.bot.utils.dialog import (
    Dialog,
    DialogActionBoolPrompt,
    DialogActionInlineSelect,
    DialogActionReplySelect,
    DialogActionText,
)
from app.bot.utils.dialog.types import DialogChoice
from app.utils import json


class TestDialog(Dialog):
    first_name = DialogActionText("Enter your first name", min_length=3)
    age = DialogActionText("Enter your age", result_type=int)
    favorite_color = DialogActionReplySelect(
        "Choose your favorite color",
        choices=["Red", "Green", "Blue", "Yellow", "Pink"]
    )
    another_color = DialogActionInlineSelect(
        "Choose another color",
        choices=[
            DialogChoice(title="Red", value="red"),
            DialogChoice(title="Green", value="green"),
            DialogChoice(title="Blue", value="blue"),
            DialogChoice(title="Yellow", value="yellow"),
            DialogChoice(title="Pink", value="pink"),
        ],
        columns=2
    )
    is_everything_right = DialogActionBoolPrompt("Is everything right?")

    async def on_finish(self, message: pyrogram.types.Message, final_data: dict):
        await message.reply(
            f"<b>Done</b>\n"
            f"{json.dumps(final_data, indent=4)}"
        )


test_dialog = TestDialog()
