# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["SettingsRendererMenuItem"]

from functools import partial
from typing import Any, Dict, Tuple, Optional

import carb
from omni.kit.viewport.menubar.core import (
    CheckboxMenuDelegate,
    ComboBoxMenuDelegate,
    ComboBoxModel,
    SettingComboBoxModel,
    ComboBoxItem,
    ResetHelper,
)
import omni.ui as ui
from pxr import Sdf

from .custom_resolution.custom_resolution_menu_item import CustomResolutionMenuItem
from .resolution_collection.menu import ResolutionCollectionMenu
from .resolution_collection.model import ComboBoxResolutionModel


SETTING_APERTURE = "/app/hydra/aperture/conform"
SETTING_RENDER_SCALE_LIST = "/app/renderer/resolution/multiplierList"


def _resolve_viewport_setting(viewport_id: str, setting_name: str, isettings: carb.settings.ISettings,
                              legacy_key: Optional[str] = None):
    # Resolve a default Viewport setting from the most specific to the most general
    #  /app/viewport/Viewport/Viewport0/setting  => Startup value for this specific Viewport
    #  /app/viewport/defaults/setting  => Startup value targetting all Viewports
    # Next check if a non-persitent viewport-specific default exists via toml / start-up settings
    dflt_setting_key = f"/app/viewport/{viewport_id}/{setting_name}"
    pers_setting_key = "/persistent" + dflt_setting_key
    # 1. Get the persistant per-viewport value that is saved (may be non-existant)
    cur_value = isettings.get(pers_setting_key)
    # 2. Get the per-viewport default that the setting should restore to
    dflt_value = isettings.get(f"/app/viewport/{viewport_id}/{setting_name}")
    # 3. If there is no per-viewport default, try to restore to a value for all Viewports
    if dflt_value is None:
        dflt_value = isettings.get(f"/app/viewport/defaults/{setting_name}")
        # 4. If still no value to restore to, check for a legacy setting that represnts this
        if dflt_value is None:
            if legacy_key:
                dflt_value = isettings.get(legacy_key)
            elif setting_name == "resolution":
                width = isettings.get("/app/renderer/resolution/width")
                height = isettings.get("/app/renderer/resolution/height")
                # When either width or height is 0 or less, Viewport will be set to use UI size
                if (width is not None) and (height is not None) and width > 0 and height > 0:
                    dflt_value = (width, height)
                if dflt_value is None:
                    dflt_value = (0, 0)

    if cur_value is None:
        cur_value = dflt_value

    return (
        (pers_setting_key, cur_value),
        (dflt_setting_key, dflt_value)
    )


class _ViewportResolutionSetter:
    """Simple class that forwards resolution menu item changes to the proper underlying object"""

    def __init__(self, factory_dict: dict, fill_viewport: bool):
        self.__factory_dict = factory_dict

        # Set the Viewport's fill_frame to False as we are controlling it fully
        viewport_api = self.viewport_api
        if viewport_api and viewport_api.fill_frame:
            viewport_api.fill_frame = False

        viewport_widget = self.viewport_widget
        if viewport_widget:
            viewport_widget.expand_viewport = fill_viewport

    @property
    def viewport_api(self):
        return self.__factory_dict.get("viewport_api")

    @property
    def viewport_widget(self):
        return self.__factory_dict.get("layer_provider").viewport_widget

    @property
    def fill_frame(self) -> bool:
        return self.viewport_widget.fill_frame

    @property
    def fill_viewport(self) -> bool:
        return self.viewport_widget.expand_viewport

    @fill_viewport.setter
    def fill_viewport(self, value: bool):
        self.viewport_widget.expand_viewport = value

    def set_resolution(self, resolution) -> None:
        self.viewport_widget.set_resolution(resolution)

    @property
    def full_resolution(self) -> Tuple[float, float]:
        return self.viewport_widget.full_resolution


class _ComboBoxResolutionScaleModel(SettingComboBoxModel, ResetHelper):
    """The resolution scale model has all the resolution scales and sets the viewport resolution scale"""

    def __init__(self, viewport_api, resolution_scale_setting, settings):
        self.__viewport_api = viewport_api

        # Get the list of available multipliers or a default
        values = settings.get(SETTING_RENDER_SCALE_LIST) or [2.0, 1.0, 0.666666666666, 0.5, 0.333333333333, 0.25]

        # Check if the legacy per-app multiplier is set and use that if it is
        default = resolution_scale_setting[1][1]
        self.__default = default if default and default > 0 else 1.0

        current_value = resolution_scale_setting[0][1]
        # Push current_value into resolution_scale if not set to it already
        if (current_value is not None) and (current_value > 0) and (current_value != self.__viewport_api.resolution_scale):
            self.__viewport_api.resolution_scale = current_value

        SettingComboBoxModel.__init__(
            self,
            # Set the key to set to to the persistent per-viewport key
            setting_path=resolution_scale_setting[0][0],
            texts=[str(int(value * 100)) + "%" for value in values],
            values=values,
            # This is passed to avoid defaulting the per-viewport persistent key to a value so that changes to the
            # setting when not adjusted/saved will pick up the new default
            current_value=self.__viewport_api.resolution_scale,
        )
        ResetHelper.__init__(self)

    def _on_current_item_changed(self, item: ComboBoxItem) -> None:
        super()._on_current_item_changed(item)
        self.__viewport_api.resolution_scale = item.value
        self._update_reset_button()

    # for ResetHelper
    def get_default(self):
        return self.__default

    def restore_default(self) -> None:
        if self.__default is not None:
            current_index = self.current_index
            if current_index:
                current = current_index.as_int
                items = self.get_item_children(None)
                # Early exit if the model is already correct
                if items[current].value == self.__default:
                    return
                # Iterate all items, and select the first match to the real value
                for index, item in enumerate(items):
                    if item.value == self.__default:
                        current_index.set_value(index)
                        return

    def get_value(self):
        return self.__viewport_api.resolution_scale


class _ComboBoxApertureFitModel(ComboBoxModel):  # pragma: no cover
    """The aperture model"""

    def __init__(self, viewport_api, settings):
        self.__viewport_api = viewport_api
        values = [0, 1, 2, 3, 4]
        texts = ["Match Vertical", "Match Horizontal", "Fit", "Crop", "Stretch"]
        current_value = settings.get(SETTING_APERTURE) or 1
        super().__init__(texts, values=values, current_value=current_value)

    def _on_current_item_changed(self, item: ComboBoxItem) -> None:
        # TODO: Add to Python bindings for UsdContext or HydraTexture
        # self.__viewport_api.set_aperture_conform_policy(item.value)
        pass


class _FillViewportModel(ui.AbstractValueModel, ResetHelper):
    def __init__(self, resolution_setter, fill_viewport_settings, isettings: carb.settings.ISettings):
        self.__resolution_setter = resolution_setter
        # Get the default value that this item should reset/restore to
        self.__default = bool(fill_viewport_settings[1][1])
        self.__saved_value = self.__default
        # This is the per-viewport persistent path this item will save to
        self.__setting_path = fill_viewport_settings[0][0]

        ui.AbstractValueModel.__init__(self)
        ResetHelper.__init__(self)

        self.__sub_model = self.subscribe_value_changed_fn(self.__on_value_changed)
        self.__sub_setting = isettings.subscribe_to_node_change_events(self.__setting_path, self.__on_setting_changed)

    def destroy(self):
        self.__sub_model = None
        if self.__sub_setting:
            carb.settings.get_settings().unsubscribe_to_change_events(self.__sub_setting)
            self.__sub_setting = None

    def get_value_as_bool(self) -> bool:
        return self.__resolution_setter.fill_viewport

    def set_value(self, value: bool, save_restore: bool = False):
        value = bool(value)
        if save_restore:
            if value:
                value = self.__saved_value
            else:
                self.__saved_value = self.get_value_as_bool()

        if value != self.get_value_as_bool():
            self.__resolution_setter.fill_viewport = value
            self._value_changed()

    # for ResetHelper
    def get_default(self):
        return self.__default

    def restore_default(self) -> None:
        self.set_value(self.__default)

    def get_value(self):
        return self.get_value_as_bool()

    def __on_setting_changed(self, *args, **kwargs):
        if self.__sub_model:
            self.set_value(carb.settings.get_settings().get(self.__setting_path))

    def __on_value_changed(self, model: ui.AbstractValueModel):
        # Use self.__sub_setting as a signal to process change in carb subscription
        settings = carb.settings.get_settings()
        model_sub, self.__sub_model = self.__sub_model, None
        try:
            value = model.as_bool
            if bool(settings.get(self.__setting_path)) != value:
                settings.set(self.__setting_path, value)
            self._update_reset_button()
        finally:
            # Make sure to put the subscription back
            self.__sub_model = model_sub


class SettingsRendererMenuItem(ui.Menu):
    """The menu with the viewport settings"""
    def __init__(self, text: str = "", factory: Optional[Dict] = None, **kwargs):
        self.__resolution_model: Optional[ComboBoxResolutionModel] = None
        self.__resolution_menu: Optional[ResolutionCollectionMenu] = None
        self.__render_scale_model: Optional[_ComboBoxResolutionScaleModel] = None
        self.__fill_viewport_model: Optional[_FillViewportModel] = None
        self.__fill_viewport_item: Optional[ui.MenuItem] = None
        self.__custom_menu_item: Optional[CustomResolutionMenuItem] = None
        self.__viewport_api_id: Optional[str] = None
        self.__sub_render_settings = None
        self.__sub_resolution_index = None
        if factory is None:
            factory = {}

        super().__init__(text, on_build_fn=partial(self.build_fn, factory), **kwargs)

    def build_fn(self, factory: Dict):
        # Create the model and the delegate here, not in __init__ to make the
        # objects unique per viewport.
        viewport_api = factory["viewport_api"]
        viewport_api_id = viewport_api.id
        isettings = carb.settings.get_settings()

        self.__viewport_api_id = viewport_api_id

        resolution_settings = _resolve_viewport_setting(viewport_api_id, "resolution", isettings)
        fill_viewport_settings = _resolve_viewport_setting(viewport_api_id, "fillViewport", isettings)
        resolution_scale_settings = _resolve_viewport_setting(viewport_api_id, "resolutionScale", isettings)

        resolution_delegate = _ViewportResolutionSetter(factory, fill_viewport_settings[0][1])

        self.__resolution_model = ComboBoxResolutionModel(resolution_delegate, resolution_settings, isettings)
        self.__resolution_menu = ResolutionCollectionMenu("Render Resolution", self.__resolution_model)

        self.__custom_menu_item = CustomResolutionMenuItem(self.__resolution_model, resolution_delegate)
        self.__custom_menu_item.resolution = resolution_delegate.full_resolution

        self.__render_scale_model = _ComboBoxResolutionScaleModel(viewport_api, resolution_scale_settings, isettings)
        ui.MenuItem(
            "Render Scale",
            delegate=ComboBoxMenuDelegate(model=self.__render_scale_model, has_reset=True),
            hide_on_click=False,
            identifier='RenderScale'
        )

        # Requires Python bindings to set this through to the renderer
        # ui.MenuItem(
        #     "Aperture Policy",
        #     delegate=ComboBoxMenuDelegate(model=_ComboBoxApertureFitModel(viewport_api, settings)),
        #     hide_on_click=False,
        #     identifier='AperturePolicy'
        # )

        self.__fill_viewport_model = _FillViewportModel(resolution_delegate, fill_viewport_settings, isettings)
        self.__fill_viewport_item = ui.MenuItem(
            "Fill Viewport",
            delegate=CheckboxMenuDelegate(model=self.__fill_viewport_model, width=310, has_reset=True),
            hide_on_click=False,
            identifier='FillViewport'
        )

        # Watch for an index change to disable / enable 'Fill Viewport' checkbox
        self.__sub_resolution_index = self.__resolution_model.current_index.subscribe_value_changed_fn(
            self.__on_resolution_index_changed
        )

        # Viewport can be changed externally, watch for any resolution changes to sync back into our models
        self.__sub_render_settings = viewport_api.subscribe_to_render_settings_change(
            self.__on_render_settings_changed
        )

    def __del__(self):
        self.destroy()

    def destroy(self):
        self.__sub_render_settings = None
        self.__sub_resolution_index = None
        if self.__resolution_model:
            self.__resolution_model.destroy()
            self.__resolution_model = None
        if self.__render_scale_model:
            self.__render_scale_model.destroy()
            self.__render_scale_model = None
        if self.__fill_viewport_model:
            self.__fill_viewport_model.destroy()
            self.__fill_viewport_model = None
        if self.__resolution_menu:
            self.__resolution_menu.destroy()
            self.__resolution_menu = None
        if self.__custom_menu_item:
            self.__custom_menu_item.destroy()
            self.__custom_menu_item = None
        super().destroy()

    def reset(self) -> None:
        # When _default_resolution is None, them fill-frame is default on, off otherwise
        if self.__fill_viewport_model:
            self.__fill_viewport_model.restore_default()

        # Restore resolution scale based on setting
        if self.__render_scale_model:
            self.__render_scale_model.restore_default()

        # Restore resolution scale based on setting
        if self.__resolution_model:
            self.__resolution_model.restore_default()

    def __sync_model(self, combo_model: ComboBoxModel, value: Any, select_first: bool = False):
        current_index = combo_model.current_index
        # Special case for forcing "Viewport" selection to be checked
        if select_first:
            if current_index.as_int != 0:
                current_index.set_value(0)
            return

        items = combo_model.get_item_children(None)
        if items and items[current_index.as_int].value != value:
            # Iterate all items, and select the first match to the real value
            index_custom = -1
            for index, item in enumerate(items):
                if item.value == value:
                    current_index.set_value(index)
                    return
                if item.model.as_string == "Custom":
                    index_custom = index

            if index_custom != -1:
                current_index.set_value(index_custom)

    def __on_resolution_index_changed(self, index_model: ui.SimpleIntModel) -> None:
        # Enable or disable the 'Fill Viewport' option based on whether using Widget size for render resolution
        # XXX: Changing visibility causes the menu to resize, which isn't great
        index = index_model.as_int
        fill_enabled = index != 0 if index_model else False
        if fill_enabled != self.__fill_viewport_item.delegate.enabled:
            self.__fill_viewport_model.set_value(fill_enabled, True)
            self.__fill_viewport_item.delegate.enabled = fill_enabled
            # When fillViewport is turned off, try to restore to last resolution
            if not fill_enabled:
                resolution = carb.settings.get_settings().get(f"/persistent/app/viewport/{self.__viewport_api_id}/resolution")
                if resolution:
                    self.__sync_model(self.__resolution_model, tuple(resolution))

        items = self.__resolution_model.get_item_children(None)
        if index >= 0 and index < len(items):
            item = items[index]
            self.__custom_menu_item.resolution = item.value

    def __on_render_settings_changed(self, camera_path: Sdf.Path, resolution: Tuple[int, int], viewport_api):
        full_resolution = viewport_api.full_resolution
        if self.__custom_menu_item.resolution != full_resolution:
            # Update the custom_menu_item resolution entry boxes.
            self.__custom_menu_item.resolution = full_resolution
        # Sync the resolution to any existing settings (accounting for "Viewport" special case)
        self.__sync_model(self.__resolution_model, full_resolution, self.__resolution_model.fill_frame)
        # Sync the resolution scale menu item
        self.__sync_model(self.__render_scale_model, viewport_api.resolution_scale)
