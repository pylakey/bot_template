from urllib.parse import (
    parse_qsl,
    urlencode,
    urlparse,
)

import pyrogram


class CallbackData:
    @staticmethod
    def pack(callback_action: str, params: dict = None) -> str:
        if not params:
            params = {}

        return f"{callback_action}?{urlencode(params)}"

    @staticmethod
    def unpack(cq: pyrogram.types.CallbackQuery) -> dict:
        parsed_data = urlparse(cq.data)
        params = {}

        if parsed_data and parsed_data.query:
            params = dict(parse_qsl(parsed_data.query))

        return params
