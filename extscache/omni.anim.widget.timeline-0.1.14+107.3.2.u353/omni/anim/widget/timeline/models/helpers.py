import math
import typing

DEFAULT_PRECISION = 2


def _pretty_print_float(
    value: float,
    fractional_suffix: str = "*",
    precision: int = DEFAULT_PRECISION,
    rounding_digits: typing.Optional[int] = None,
) -> str:
    """Return a float with 2 decimal precision as string.
    If close enough to whole number, returns whole number only as string.
    If NaN, return empty string."""
    if math.isnan(value):
        return ""
    rounded = round(value, rounding_digits)
    if math.isclose(value, rounded):
        return f"{rounded}"
    return f"{value:.{precision}f}{fractional_suffix}"
