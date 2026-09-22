"""Special handling for Infinity and NaN values, localized to a single file"""

from __future__ import annotations

from math import isnan


# ==============================================================================================================
class NanInfValues:
    """Handler for strings or floats with inf and nan values"""

    # These keywords are used by .ogn to represent the special values since JSON has no representation for them
    NAN = "nan"
    SNAN = "snan"
    INF = "inf"
    POS_INF = "+inf"
    NEG_INF = "-inf"
    ALL = [NAN, SNAN, POS_INF, NEG_INF]

    @classmethod
    def is_nan(cls, value: float | str) -> bool:
        return (isinstance(value, str) and (value.lower() in [cls.NAN, cls.SNAN])) or (
            isinstance(value, float) and isnan(value)
        )

    @classmethod
    def is_inf(cls, value: float | str) -> bool:
        return (isinstance(value, str) and (value.lower() in [cls.INF, cls.POS_INF])) or (value == float("Inf"))

    @classmethod
    def is_neg_inf(cls, value: float | str) -> bool:
        """Returns True if the value represents negative infinity"""
        return (isinstance(value, str) and (value.lower() == cls.NEG_INF)) or (value == float("-Inf"))

    @classmethod
    def as_float(cls, value: float | str) -> float | None:
        """Returns the special float number corresponding to the value, or None if it is not one of them"""
        if cls.is_nan(value):
            return float("NaN")
        if cls.is_inf(value):
            return float("Inf")
        if cls.is_neg_inf(value):
            return float("-Inf")
        return None

    @classmethod
    def as_repr(cls, value) -> float | None:
        """Returns the string corresponding to the value, or None if it is not one of them"""
        if cls.is_nan(value):
            return 'float("NaN")'
        if cls.is_inf(value):
            return 'float("Inf")'
        if cls.is_neg_inf(value):
            return 'float("-Inf")'
        return str(value)


# ==============================================================================================================
def repr_value(value: any) -> str:
    """Return the Python representation of a value, fixing for nan and inf values"""
    if isinstance(value, list):
        return "[" + ", ".join(repr_value(element) for element in value) + "]"
    if isinstance(value, tuple):
        return "(" + ", ".join(repr_value(element) for element in value) + ")"
    return NanInfValues.as_repr(value)


# ==============================================================================================================
def repr_as_float(value: float | str | list[str | float]) -> float:
    """Return the Python representation of a float, fixing for nan and inf values, raising ValueError if the value was
    not a float or list or tuple of floats. Float values include both native floats and string representations of
    infinity and NaN values.
    """
    if value is None:
        return value
    if isinstance(value, list):
        return [repr_as_float(element) for element in value]
    if isinstance(value, tuple):
        return tuple(repr_as_float(element) for element in value)
    if isinstance(value, (float, int)):
        return value
    if isinstance(value, str):
        float_value = NanInfValues.as_float(value)
        if float_value is not None:
            return float_value
    raise ValueError(f"Do not know how to convert {type(value)} value '{value}'")
