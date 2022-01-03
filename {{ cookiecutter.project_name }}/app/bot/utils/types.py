from typing import Union

import pyrogram

UpdateFromUser = Union[
    pyrogram.types.CallbackQuery,
    pyrogram.types.InlineQuery,
    pyrogram.types.Message,
]
