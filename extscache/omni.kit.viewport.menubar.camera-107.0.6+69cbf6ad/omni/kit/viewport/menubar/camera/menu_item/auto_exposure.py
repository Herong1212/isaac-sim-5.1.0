from typing import List, Optional

import omni.ui as ui
from omni.kit.viewport.menubar.core import (
    CheckboxMenuDelegate,
    SpinnerMenuDelegate,
    SliderMenuDelegate,
    USDAttributeModel,
    SettingModel,
)

from .camera_setting import AbstractCameraSetting

SETTING_AUTO_EXPOSURE = "/rtx/post/histogram/enabled"
SETTING_ISO = "/rtx/post/tonemap/filmIso"
SETTING_WHITE_SCALE = "/rtx/post/histogram/whiteScale"

__all__ = ["CameraAutoExposure", "SETTING_ISO", "SETTING_WHITE_SCALE"]


class CameraAutoExposure(AbstractCameraSetting):
    def __init__(self, model: USDAttributeModel, enabled: bool = True):
        self._auto_exposure_delegate: Optional[CheckboxMenuDelegate] = None
        self._white_scale_item: Optional[ui.MenuItem] = None
        self._iso_item: Optional[ui.MenuItem] = None
        self._auto_exposure_model = SettingModel(SETTING_AUTO_EXPOSURE)
        self._white_scale_model = SettingModel(SETTING_WHITE_SCALE)
        self._iso_model = SettingModel(SETTING_ISO)

        self._sub = self._auto_exposure_model.subscribe_value_changed_fn(self._on_auto_exposure_changed)

        super().__init__(model, enabled=enabled)

    def destroy(self):
        self._sub = None

    def _build_ui(self) -> List[ui.MenuDelegate]:
        self._auto_exposure_delegate = CheckboxMenuDelegate(
            model=self._auto_exposure_model, width=0, height=26, enabled=self._enabled, use_in_menubar=True
        )
        ui.MenuItem("AE", delegate=self._auto_exposure_delegate, identifier="viewport.camera.auto_exposure")
        self._white_scale_item = ui.MenuItem(
            "",
            delegate=SliderMenuDelegate(model=self._white_scale_model, min=00, max=20, width=0),
            visible=self._auto_exposure_model.as_bool,
        )
        self._iso_item = ui.MenuItem(
            "ISO",
            delegate=SpinnerMenuDelegate(
                model=self._iso_model, min=50, max=1600, height=26, use_in_menubar=True,
            ),
            visible=not self._auto_exposure_model.as_bool,
            identifier="viewport.camera.iso",
        )

        return [self._auto_exposure_delegate, self._white_scale_item.delegate, self._iso_item.delegate]

    def _on_auto_exposure_changed(self, model: ui.AbstractValueModel) -> None:
        self._white_scale_item.visible = model.as_bool
        self._iso_item.visible = not model.as_bool
