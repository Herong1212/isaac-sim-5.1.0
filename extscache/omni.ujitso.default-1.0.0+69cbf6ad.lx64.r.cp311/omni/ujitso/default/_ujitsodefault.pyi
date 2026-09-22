"""pybind11 omni.ujitso.default bindings"""
from __future__ import annotations
import omni.ujitso.default._ujitsodefault
import typing

__all__ = [
    "DataStoreClearing",
    "DataStoreFailureInjector",
    "DataStoreOperation",
    "HashKey"
]


class DataStoreClearing():
    """
    Allows issuing synchronous data store clearing operations
    """
    def __init__(self) -> None: ...
    def clear_percentage(self, arg0: float) -> bool: ...
    pass
class DataStoreFailureInjector():
    """
    Allows issuing failure injection calls to a datastore that supports it
    """
    def __init__(self) -> None: ...
    def clear_failures(self) -> bool: ...
    def inject_failure(self, arg0: DataStoreOperation, arg1: HashKey, arg2: int, arg3: bool) -> bool: ...
    def remove_failure(self, arg0: DataStoreOperation, arg1: HashKey) -> bool: ...
    pass
class DataStoreOperation():
    """
    Members:

      Get

      Set

      Stat
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    Get: omni.ujitso.default._ujitsodefault.DataStoreOperation # value = <DataStoreOperation.Get: 0>
    Set: omni.ujitso.default._ujitsodefault.DataStoreOperation # value = <DataStoreOperation.Set: 1>
    Stat: omni.ujitso.default._ujitsodefault.DataStoreOperation # value = <DataStoreOperation.Stat: 2>
    __members__: dict # value = {'Get': <DataStoreOperation.Get: 0>, 'Set': <DataStoreOperation.Set: 1>, 'Stat': <DataStoreOperation.Stat: 2>}
    pass
class HashKey():
    """
    Wrapper for a hash key that can be constructed from an hex string
    """
    def __init__(self, hex_key: str = '') -> None: ...
    pass
