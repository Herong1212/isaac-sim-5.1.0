import abc
from typing import List

from omni.kit.viewport.menubar.core import USDAttributeModel
import omni.ui as ui

__all__ = ["AbstractCameraSetting"]


class AbstractCameraSetting:
    def __init__(self, model: USDAttributeModel, enabled: bool = True):
        self._property_model = model
        self._enabled = enabled

        self._delegates = self._build_ui()

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value
        for delegate in self._delegates:
            delegate.enabled = value

    @abc.abstractmethod
    def _build_ui(self) -> List[ui.MenuDelegate]:
        return []
