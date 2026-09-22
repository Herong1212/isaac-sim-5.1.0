from typing import List
import omni.ui as ui
from omni.kit.viewport.menubar.core import SpinnerMenuDelegate, USDAttributeModel
from .camera_setting import AbstractCameraSetting

__all__ = ["CameraFStop"]


class CameraFStop(AbstractCameraSetting):
    def __init__(self, model: USDAttributeModel, enabled: bool = True):
        super().__init__(model, enabled=enabled)

    def destroy(self):
        pass

    def _build_ui(self) -> List[ui.MenuDelegate]:
        self._fstop_delegate = SpinnerMenuDelegate(
            model=self._property_model,
            min=0.0,
            max=22.0,
            step=0.1,
            height=26,
            enabled=self._enabled,
            text=False,
            icon_name="FStop",
            tooltip="Camera F Stop",
            icon_height=26,
            use_in_menubar=True,
        )
        ui.MenuItem("F Stop", delegate=self._fstop_delegate, identifier="viewport.camera.f_stop")

        return [self._fstop_delegate]
