# SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from __future__ import annotations

from enum import IntEnum

import omni.ui
from omni.asset_validator.core import ValidationEngine
from omni.kit.window.file_importer import get_file_importer
from pxr import Usd

from .model import ApplicationModel

__all__ = ["AssetMode", "UriModel", "StageModel", "ModeModel", "AssetWidget"]


class AssetMode(IntEnum):
    Uri = 0
    """
    The asset is a URI
    """

    Stage = 1
    """
    The asset is a stage in memory.
    """


EMPTY_URI: str = ""


class UriModel(omni.ui.SimpleStringModel):
    def __init__(self):
        super().__init__(EMPTY_URI)

    @property
    def uri(self) -> str:
        return self.get_value_as_string()

    @uri.setter
    def uri(self, uri: str) -> None:
        self.set_value(uri)


class StageModel(omni.ui.AbstractValueModel):
    def __init__(self):
        super().__init__()
        self._stage = omni.usd.get_context().get_stage()

    @property
    def stage(self) -> Usd.Stage | None:
        return self._stage or omni.usd.get_context().get_stage()

    @stage.setter
    def stage(self, stage: Usd.Stage | None) -> None:
        self._stage = stage or omni.usd.get_context().get_stage()
        self._value_changed()

    def get_value_as_string(self) -> str:
        if self.stage is None:
            return "Current stage is not available. Open a stage from the Stage or Layer Windows."
        # it may be the main stage
        elif self.stage == omni.usd.get_context().get_stage():
            return "Validate the Main Stage. This will set Authoring to the Session Layer temporarily."
        # it may be a bespoke stage based with an in-memory layer
        elif self.stage.GetRootLayer().anonymous:
            return f'Anonymous Stage using "{self._stage.GetRootLayer().GetDisplayName()}"'
        else:
            return Usd.Describe(self.stage)


class ModeModel(omni.ui.SimpleIntModel):
    def __init__(self) -> None:
        super().__init__(AssetMode.Stage.value)

    @property
    def mode(self) -> AssetMode:
        return AssetMode(self.get_value_as_int())

    @mode.setter
    def mode(self, mode: AssetMode) -> None:
        self.set_value(mode.value)


class AssetModeModel(omni.ui.AbstractItemModel):
    class Item(omni.ui.AbstractItem):
        def __init__(self, name: str):
            super().__init__()
            self.model = omni.ui.SimpleStringModel(name)

    def __init__(self):
        super().__init__()
        self._subscription = ApplicationModel.get().mode_model.subscribe_value_changed_fn(
            lambda _: self._item_changed(None)
        )
        self._items = [AssetModeModel.Item(AssetMode.Uri.name), AssetModeModel.Item(AssetMode.Stage.name)]

    def get_item_children(self, item):
        if item is None:
            return self._items
        return []

    def get_item_value_model(self, item, _):
        if item is None:
            return ApplicationModel.get().mode_model
        return item.model


class AssetWidget:
    def __init__(self, *, visible: bool = True):
        # Models
        self._model = AssetModeModel()
        self._subscription = self._model.get_item_value_model(None, None).subscribe_value_changed_fn(
            self._refresh_asset_mode
        )

        self._visible = omni.ui.SimpleBoolModel(visible)
        self._visible.add_value_changed_fn(self._on_visible_change)

        # Widgets
        self._main_stack = omni.ui.HStack(height=30, visible=visible)
        with self._main_stack:
            self._asset_mode_combo_box = omni.ui.ComboBox(
                self._model, width=100, tooltip="Select the type of Asset to validate"
            )
            omni.ui.Spacer(width=10)
            with omni.ui.ZStack():
                with omni.ui.HStack():
                    self._asset_uri_field = omni.ui.StringField(ApplicationModel.get().uri_model, height=0)
                    self._asset_uri_button = omni.ui.Button(
                        width=30,
                        height=27,
                        image_url="resources/icons/folder_gray.png",
                        tooltip="Browse for an Asset to Validate",
                        clicked_fn=self._show_asset_uri_picker,
                    )
                self._asset_stage_field = omni.ui.StringField(ApplicationModel.get().stage_model, height=0)
                self._asset_stage_field.read_only = True

        # Stage is default
        self._refresh_asset_mode(AssetMode.Stage)

    def _on_visible_change(self, model):
        self._main_stack.visible = model.as_bool

    def _show_asset_uri_picker(self):
        file_importer = get_file_importer()
        file_importer.show_window(
            title="Select an Asset to Validate",
            import_handler=self._asset_uri_selected,
            file_filter_handler=self._asset_uri_filter,
            filename_url=self._asset_uri_field.model.get_value_as_string(),
        )
        # folder is selectable too
        file_importer._dialog._widget.file_bar.enable_apply_button(True)

    @classmethod
    def _asset_uri_filter(cls, filename: str, *_) -> bool:
        return ValidationEngine.is_asset_supported(filename) if filename else True

    def _asset_uri_selected(self, file_name: str, dir_name: str, selections: list[str]) -> None:
        # file_name is not reliable, it doesn't track selection of folders at all,
        # so we query the selection directly and allow it to override file_name
        # TODO: remove all this if FilePickerDialog or a similar class can support folder picking.
        file_url = omni.client.combine_urls(dir_name, file_name)
        if selections:
            if file_url.startswith(selections[-1]):
                # use file_name when it is aligned with selection as it may provide
                # extra information such as checkpoint version
                ApplicationModel.get().uri = file_url
            else:
                ApplicationModel.get().uri = selections[-1]
        else:
            # fallback when nothing is selected
            ApplicationModel.get().uri = file_url

    @property
    def visible(self) -> bool:
        return self._visible.as_bool

    @visible.setter
    def visible(self, flag: bool) -> None:
        self._visible.as_bool = flag

    def _refresh_asset_mode(self, _) -> None:
        asset_mode: AssetMode = self._model.get_item_value_model(None, None).mode
        self._asset_uri_field.visible = asset_mode is AssetMode.Uri
        self._asset_uri_button.visible = asset_mode is AssetMode.Uri
        self._asset_stage_field.visible = asset_mode is AssetMode.Stage
