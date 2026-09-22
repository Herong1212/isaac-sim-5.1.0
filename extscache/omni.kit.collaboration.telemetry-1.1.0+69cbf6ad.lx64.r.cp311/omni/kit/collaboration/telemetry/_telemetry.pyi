"""bindings for structured log schema omni.kit.collaboration"""
from __future__ import annotations
import omni.kit.collaboration.telemetry._telemetry
import typing

__all__ = [
    "Schema_omni_kit_collaboration_1_0",
    "Struct_liveEdit_liveEdit"
]


class Schema_omni_kit_collaboration_1_0():
    def __init__(self) -> None: ...
    def liveEdit_sendEvent(self, cloud_link_id: str, liveEdit: Struct_liveEdit_liveEdit) -> None: ...
    pass
class Struct_liveEdit_liveEdit():
    def __init__(self) -> None: ...
    @property
    def action(self) -> str:
        """
        :type: str
        """
    @action.setter
    def action(self, arg0: str) -> None:
        pass
    @property
    def id(self) -> str:
        """
        :type: str
        """
    @id.setter
    def id(self, arg0: str) -> None:
        pass
    pass
