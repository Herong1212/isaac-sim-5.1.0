import typing

from idl.types import initialize
# noinspection PyUnresolvedReferences
from idl.types.initialization import undefined, ValidationError, ValidationTypeError

T = typing.TypeVar("T")


def validate(value: typing.Any, value_type: typing.Type[T] = None, value_name: str = None) -> T:
    return initialize(value, value_type, value_name, force_validation=True)
