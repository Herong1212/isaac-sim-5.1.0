import asyncio
from typing import Tuple, List

import omni.kit.app
from omni.kit.viewport.menubar.core import (
    SeparatorDelegate,
    SliderMenuDelegate,
    ComboBoxMenuDelegate,
    USDAttributeModel,
    USDFloatAttributeModel,
    ComboBoxItem,
    ComboBoxModel,
)
import omni.ui as ui

from .camera_setting import AbstractCameraSetting

DEFAULT_LENS = [8, 15, 24, 28, 35, 50, 85, 105, 135, 200, (17, 35), (35, 70), (70, 200), (0, 300)]


class _CameraLensModel(ComboBoxModel):
    """The camera lens model has all the lens"""

    def __init__(self, lens_model: USDFloatAttributeModel):
        self._values = DEFAULT_LENS
        self._lens_model = lens_model
        self.range: Tuple(float, float) = ()

        texts = []
        for value in self._values:
            if isinstance(value, int):
                texts.append(f"{value} mm")
            else:
                texts.append(f"{value[0]} - {value[1]} mm")

        self._lens_model.add_value_changed_fn(self.__on_lens_changed)

        super().__init__(texts, self._values, self.display)

    def destroy(self):
        super().destroy()
        self._lens_model.remove_value_changed_fn(self.__on_lens_changed)

    @property
    def display(self):
        lens = self._lens_model.as_float
        for value in self._values:
            if isinstance(value, int):
                if lens == float(value):
                    self.range = (value, value)
                    return value
            else:
                min_value = value[0]
                max_value = value[1]
                if min_value <= lens <= max_value:
                    self.range = (min_value, max_value)
                    return value
        default = self._values[-1]
        return default

    def _on_current_item_changed(self, item: ComboBoxItem) -> None:
        if isinstance(item.value, int):
            self.range = (item.value, item.value)
            self._lens_model.set_value(float(item.value))
        else:
            # Don't allow 0 for focalLength
            self.range = (max(0.00001, item.value[0]), item.value[1])
            value = self._lens_model.as_float
            if value > self.range[1] or value < self.range[0]:
                self._lens_model.set_value(float(self.range[0]))

    def __on_lens_changed(self, model: ui.AbstractValueModel):
        # If current value still in current lens range, keep range no change
        value = self._values[self.current_index.as_int]
        if isinstance(value, int):
            if model.as_float == float(value):
                return
        elif float(value[0]) <= model.as_float and float(value[1]) >= model.as_float:
            return

        self.current_index.set_value(self._get_current_index_by_value(self.display))


class CameraLens(AbstractCameraSetting):
    def __init__(self, model: USDAttributeModel, enabled: bool = True):
        self._lens_model = _CameraLensModel(model)
        self._sub = self._lens_model.subscribe_item_changed_fn(self._on_lens_changed)

        super().__init__(model, enabled=enabled)

    def destroy(self):
        self._lens_model.destroy()
        self._sub = None

    def _build_ui(self) -> List[ui.MenuDelegate]:
        self._lens_delegate = ComboBoxMenuDelegate(
            model=self._lens_model,
            height=26,
            icon_height=26,
            enabled=self._enabled,
            text=False,
            icon_name="Lens",
            tooltip="Camera Lens",
            use_in_menubar=True,
        )
        ui.MenuItem("Lens", delegate=self._lens_delegate, identifier="viewport.camera.lens")

        self._separator = ui.MenuItem("", delegate=SeparatorDelegate())
        self._zoom_delegate = SliderMenuDelegate(model=self._property_model, width=0, enabled=self._enabled, tooltip="Camera Zoom")
        self._zoom_menu = ui.MenuItem("Zoom", delegate=self._zoom_delegate, enabled=self._enabled, identifier="viewport.camera.zoom")

        async def __delay_init():
            await omni.kit.app.get_app().next_update_async()
            self._on_lens_changed(self._lens_model, None)

        asyncio.ensure_future(__delay_init())

        return [self._lens_delegate, self._zoom_delegate]

    def _on_lens_changed(self, model: _CameraLensModel, item: ComboBoxItem):
        lens_range = self._lens_model.range
        if lens_range[0] == lens_range[1]:
            self._zoom_delegate.visible = False
            self._separator.visible = False
        else:
            self._zoom_delegate.visible = True
            self._separator.visible = True
            self._zoom_delegate.set_range(lens_range[0], lens_range[1])
