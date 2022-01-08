from decimal import Decimal
from typing import Union


def normalize_decimal(d: Union[float, int, str, Decimal]) -> Decimal:
    d = Decimal(d)
    return d.quantize(Decimal(1)) if d == d.to_integral() else d.normalize()
