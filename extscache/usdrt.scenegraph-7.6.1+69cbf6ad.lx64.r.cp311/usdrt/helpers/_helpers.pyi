from __future__ import annotations
import usdrt.helpers._helpers
import typing

__all__ = [
    "FabricId",
    "PathC",
    "StageReaderWriterId",
    "UsdStageId"
]


class FabricId():
    @property
    def id(self) -> int:
        """
        :type: int
        """
    pass
class PathC():
    @staticmethod
    def __init__(*args, **kwargs) -> typing.Any: ...
    @property
    def path(self) -> int:
        """
        :type: int
        """
    pass
class StageReaderWriterId():
    @property
    def id(self) -> int:
        """
        :type: int
        """
    pass
class UsdStageId():
    def __init__(self, arg0: int) -> None: ...
    @property
    def id(self) -> int:
        """
        :type: int
        """
    pass
