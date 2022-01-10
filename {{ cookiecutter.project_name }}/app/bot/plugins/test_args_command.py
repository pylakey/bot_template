import pydantic
import pyrogram.filters
from pyrogram.errors import BadRequest

from app.bot.bot import Bot
from app.bot.utils import constraints
from app.bot.utils.chat_commands import PrivateCommands


class TestArgs(pydantic.BaseModel):
    username: str = pydantic.Field(..., **constraints.username, description='Username of Telegram user')


@PrivateCommands.TEST_ARGS_COMMAND(args_model=TestArgs)
async def test_args_command(bot: Bot, message: pyrogram.types.Message):
    args: TestArgs = message.bucket.args

    try:
        user = await bot.get_users(args.username)
        await message.reply(str(user))
    except BadRequest as e:
        await message.reply(str(e))

    message.stop_propagation()
