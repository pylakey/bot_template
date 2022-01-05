import pyrogram

from app.bot.utils.callback_data import CallbackData
from app.bot.utils.custom_filters import CustomFilters


class CallbackAction(str):
    def __new__(cls, command: str, *, admin: bool = False):
        obj = super(CallbackAction, cls).__new__(cls, command)
        obj.admin = admin
        return obj

    @property
    def filter(self) -> pyrogram.filters.Filter:
        _filter = CustomFilters.callback_data(self)

        if self.admin:
            _filter = CustomFilters.admin & _filter

        return _filter

    def button(self, text: str, data: dict = None, **kwargs) -> pyrogram.types.InlineKeyboardButton:
        return pyrogram.types.InlineKeyboardButton(text, self.pack(data), **kwargs)

    def pack(self, data: dict = None) -> str:
        data = data or {}
        return CallbackData.pack(self, data)

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

        return pyrogram.Client.on_callback_query(_filter, group=group)


class CallbackActions:
    HELLO = CallbackAction('hello')
