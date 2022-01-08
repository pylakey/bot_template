from decimal import (
    Decimal,
    ROUND_HALF_EVEN,
)
from typing import Union


def normalize_decimal(
        d: Union[float, int, str, Decimal],
        auto_round: bool = True,
        decimal_places: int = 8
) -> Decimal:
    result = Decimal(d)

    if auto_round:
        result = result.quantize(Decimal(10) ** (-decimal_places), rounding=ROUND_HALF_EVEN)

    return result.quantize(Decimal(1)) if result == result.to_integral() else result.normalize()
