import asyncio
import logging
import math
from typing import (
    Any,
    Callable,
    Coroutine,
    Optional,
    Union,
)

import async_lru
import peewee
import pyrogram
from pyrogram.errors import (
    MessageEditTimeExpired,
    MessageNotModified,
)

from app.database.database import objects

logger = logging.getLogger(__name__)

ItemSerializer = Callable[[peewee.Model], Coroutine[Any, Any, str]]
ItemMarkupMaker = Callable[[peewee.Model], Coroutine[Any, Any, list[list[pyrogram.types.InlineKeyboardButton]]]]


async def to_string(item: peewee.Model) -> str:
    return str(item)


class Pagination:
    def __init__(
            self,
            command: str,
            query: peewee.Query,
            item_serializer: ItemSerializer = to_string,
            item_keyboard_maker: ItemMarkupMaker = None,
            page: Union[int, str] = 1,
            page_size: int = 5,
            custom_buttons: list[pyrogram.types.InlineKeyboardButton] = None,
            header: str = None,
            hide_fast_forward: bool = False,
            fast_forward_min_pages: int = 10,
            separator: str = "\n\n",
    ):
        self.command = command
        self.query = query
        self.page_size = page_size
        self.custom_buttons = custom_buttons or []
        self.header = header
        self.hide_fast_forward = hide_fast_forward
        self.separator = separator
        self.fast_forward_min_pages = fast_forward_min_pages
        self.item_serializer = item_serializer
        self.item_keyboard_maker = item_keyboard_maker

        try:
            self.page = abs(int(page))
        except (ValueError, TypeError):
            self.page = 1

    @property
    def is_single_page(self):
        return self.page_size == 1

    @async_lru.alru_cache
    async def get_total_pages(self) -> int:
        total_count = await objects.count(self.query)
        return max(1, math.ceil(total_count / self.page_size))

    @async_lru.alru_cache
    async def get_page(self) -> int:
        total_pages = await self.get_total_pages()
        return min(max(1, self.page), total_pages)

    async def get_text(self) -> str:
        _text = f"{self.header}\n\n" if self.header else ""
        page = await self.get_page()

        query = self.query.paginate(page, self.page_size)
        items = await objects.execute(query)
        items_strings = await asyncio.gather(*[self.item_serializer(item) for item in items])
        _text += self.separator.join(items_strings) or "Nothing to show"

        return _text

    async def get_reply_markup(self) -> Optional[pyrogram.types.InlineKeyboardMarkup]:
        command = self.command.lower()

        total_pages = await self.get_total_pages()
        page = await self.get_page()

        if '?' in command:
            command = command + "&"
        elif not command.endswith("?"):
            command = command + "?"

        next_page = 1 if page + 1 > total_pages else page + 1
        prev_page = total_pages if page - 1 < 1 else page - 1

        buttons = [
            [
                pyrogram.types.InlineKeyboardButton(
                    text=pyrogram.emoji.REVERSE_BUTTON,
                    callback_data=f'{command}p={prev_page}'
                ),
                pyrogram.types.InlineKeyboardButton(
                    text=f"{page} / {total_pages}",
                    callback_data=f'{command}p={page}'
                ),
                pyrogram.types.InlineKeyboardButton(
                    text=pyrogram.emoji.PLAY_BUTTON,
                    callback_data=f'{command}p={next_page}'
                ),
            ]
        ]

        if not self.hide_fast_forward and total_pages >= self.fast_forward_min_pages:
            buttons.append(
                [
                    pyrogram.types.InlineKeyboardButton(
                        text=pyrogram.emoji.FAST_REVERSE_BUTTON,
                        callback_data=f'{command}p={1}'
                    ),
                    pyrogram.types.InlineKeyboardButton(
                        text=pyrogram.emoji.FAST_FORWARD_BUTTON,
                        callback_data=f'{command}p={total_pages}'
                    ),
                ]
            )

        buttons += [[button] for button in self.custom_buttons]

        if self.is_single_page:
            try:
                item = await self.get_item()
                item_keyboard = await self.item_keyboard_maker(item)

                if item_keyboard:
                    buttons += item_keyboard
            except Exception as e:
                logger.warning(f'Unable to append custom buttons. {type(e)}. {e}')
                pass

        return pyrogram.types.InlineKeyboardMarkup(buttons) if buttons else None

    async def get_item(self) -> Optional[peewee.Model]:
        if not self.is_single_page:
            raise ValueError("get_item method is available only when page_size=1")

        try:
            query = self.query.paginate(self.page, self.page_size)
            items = await objects.execute(query)
            return items[0]
        except IndexError:
            return None

    async def reply(
            self,
            update: Union[pyrogram.types.CallbackQuery, pyrogram.types.Message]
    ) -> pyrogram.types.Message:
        is_message = isinstance(update, pyrogram.types.Message)
        message = update if is_message else update.message
        message_author = update.from_user if is_message else update.message.from_user

        [total_pages, page, text, reply_markup] = await asyncio.gather(
            self.get_total_pages(),
            self.get_page(),
            self.get_text(),
            self.get_reply_markup(),
        )

        if not is_message:
            asyncio.create_task(update.answer(f"Страница {page} из {total_pages}"))

        if message_author.is_self:
            try:
                return await message.edit_text(text, reply_markup=reply_markup, disable_web_page_preview=True)
            except MessageEditTimeExpired:
                asyncio.create_task(message.delete())
            except MessageNotModified:
                if is_message:
                    return update
                else:
                    return update.message

        return await message.reply(text, reply_markup=reply_markup, disable_web_page_preview=True, quote=True)
