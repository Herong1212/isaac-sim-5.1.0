# Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import re
from functools import partial

import carb
import omni.ui as ui
import omni.usd as ou
from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidgetBuilder
from omni.kit.widget.text_editor import TextEditor
from omni.kit.window.property.templates import HORIZONTAL_SPACING
from pxr import Sdf, Usd

from .singleton import Singleton

LABEL = {"alignment": ui.Alignment.RIGHT_CENTER}


class TimeSampleEditor(metaclass=Singleton):
    def __init__(self):
        self._window = None
        self._attr_model = None
        self._attr_value_widget_model = None
        self._attr_value_widget_sub = None
        self._value_widget_sub = None
        self._usd_subscription = None

    def show(self, attr_path: Sdf.Path):
        """Build and display the window contents"""
        stage = ou.get_context().get_stage()
        assert stage
        self._attr = stage.GetPropertyAtPath(attr_path)

        usd_watcher = ou.get_watcher()

        if self._usd_subscription:
            self._usd_subscription = None
        self._usd_subscription = usd_watcher.subscribe_to_change_info_path(attr_path, self._on_attr_changed)

        if not self._window:
            self._window = ui.Window(
                "Time Sample Editor",
                width=640,
                height=480,
                dockPreference=ui.DockPreference.MAIN,
                raster_policy=ui.RasterPolicy.NEVER,
            )

        self._build_ui()
        self.load_time_samples()
        self._window.visible = True

    def close(self):
        """Close the window and destroy the window elements"""
        self._window.destroy()
        self._window = None

        if self._attr_value_widget_sub:
            self._attr_value_widget_sub = None

        if self._usd_subscription:
            self._usd_subscription = None

    @staticmethod
    def get_asset(value):
        # timeSamples type is asset written between first and last @
        value = value.replace(" ", "")
        start = 1 if value[0] == "@" else 0
        last = len(value) - 1
        end = last if value[last] == "@" else last + 1
        asset_value = value[start:end]
        if len(asset_value) > 0:
            return Sdf.AssetPath(asset_value)
        else:
            return Sdf.AssetPath()

    @staticmethod
    def get_time_code(value):
        return Usd.TimeCode(float(re.sub("[^.\-\d]", "", value)))

    def load_time_samples(self):
        time_samples = self._attr.GetMetadata("timeSamples")

        text_lines = []
        if time_samples:
            for key, value in time_samples.items():
                text_lines.append(f"{key:g}: {str(value)}")

        self.text_editor.text_lines = text_lines

    def _on_attr_changed(self, *_):
        if self._attr_value_widget_model:
            value = "@" + self._attr_value_widget_model.get_value_as_string() + "@"
            if value != str(self._attr.Get()):
                self._build_ui()

    def _clear_asset_path(self):
        self._attr.Clear()
        self._build_ui()

    def _create_time_samples(self):
        path = self.path.model.get_value_as_string()
        begin = self.begin.model.get_value_as_float()
        step = self.step.model.get_value_as_float()
        first = self.first.model.get_value_as_int()
        last = self.last.model.get_value_as_int()
        zeros = self.zeros.model.get_value_as_int()

        if first > last:
            carb.log_warn("First frame number is larger than last frame number")
            return

        self._attr.ClearMetadata("timeSamples")
        text_lines = []
        key = begin
        for index in range(first, last + 1):
            if zeros != 0:
                zeros_offset = zeros + len(f"{first}")
                format = f"%0{zeros_offset}d"
                path = re.sub("%.*?d", format, path)
            try:
                value = path % index
            except TypeError:
                carb.log_warn("To generate a sequence of assets, please replace number with %d")
                return

            asset = TimeSampleEditor.get_asset(value)
            self._attr.Set(asset, Usd.TimeCode(float(key)))

            text_lines.append(f"{key}: {value}")
            key += step

        self.text_editor.text_lines = text_lines

        self._save_time_samples()

    def _load_time_samples(self):
        self.load_time_samples()

        carb.log_info(f"TimeSamples metadata loaded from: {self._attr}")

    def _save_time_samples(self):
        self._attr.ClearMetadata("timeSamples")
        text_lines = self.text_editor.text_lines
        if text_lines == [""]:
            return True

        for line in text_lines:
            line_split = line.split(":", 1)
            try:
                if len(line_split) < 2:
                    raise ValueError()

                time_code = TimeSampleEditor.get_time_code(line_split[0])
                asset = TimeSampleEditor.get_asset(line_split[1])
                self._attr.Set(asset, time_code)
            except ValueError:
                carb.log_error(f"TimeSamples metadata not saved, wrong format in line: {line}")
                return False

        carb.log_info(f"TimeSamples metadata saved to: {self._attr}")
        return True

    def _clear_time_samples(self):
        self._attr.ClearMetadata("timeSamples")
        self.text_editor.text = ""

    def _build_ui(self):
        stage = ou.get_context().get_stage()

        with self._window.frame:
            with ui.VStack(spacing=HORIZONTAL_SPACING, height=0):
                with ui.HStack(spacing=HORIZONTAL_SPACING, height=0):
                    with ui.VStack(spacing=HORIZONTAL_SPACING, height=0):
                        widget_model = UsdPropertiesWidgetBuilder._sdf_asset_path_builder(
                            stage,
                            self._attr.GetName(),
                            Sdf.ValueTypeNames.Asset,
                            {},
                            [self._attr.GetPrimPath()],
                        )
                        self._attr_value_widget_model = (
                            widget_model[0] if isinstance(widget_model, list) else widget_model
                        )

                        def value_changed(model):
                            self.path.model.set_value("@" + model.get_value_as_string() + "@")

                        self._attr_value_widget_sub = self._attr_value_widget_model.subscribe_value_changed_fn(
                            value_changed
                        )

                    ui.Button(
                        "Clear",
                        tooltip="Clear time samples metadata and the asset attribute value",
                        width=70,
                        clicked_fn=self._clear_asset_path,
                    )

                with ui.HStack(spacing=HORIZONTAL_SPACING, height=0):
                    ui.Label("Asset Path (replace number with %d)", style=LABEL, width=100)
                    self.path = ui.StringField(height=0)
                    self.path.model.set_value(str(self._attr.Get()))

                with ui.HStack(spacing=HORIZONTAL_SPACING, height=0):
                    ui.Label("First TimeCode", style=LABEL)
                    self.begin = ui.FloatDrag(min=0.0001, max=10000)
                    ui.Label("TimeCode Step", style=LABEL)
                    self.step = ui.FloatDrag(min=0.0001, max=10000)
                    self.step.model.set_value(1)
                    ui.Label("First Frame", style=LABEL, width=50)
                    self.first = ui.UIntDrag()
                    ui.Label("Last Frame", style=LABEL)
                    self.last = ui.UIntDrag()
                    ui.Label("Leading Zeros", style=LABEL, width=50)
                    self.zeros = ui.UIntDrag()

                with ui.HStack(spacing=HORIZONTAL_SPACING, height=0):
                    ui.Button(
                        "Generate Sequence",
                        tooltip="Generate and set time sample metadata",
                        clicked_fn=self._create_time_samples,
                    )

                with ui.HStack(spacing=HORIZONTAL_SPACING, height=0):
                    ui.Label("Time Samples Metadata:")
                    ui.Button("Load", tooltip="Get attribute time samples metadata", clicked_fn=self._load_time_samples)
                    ui.Button("Save", tooltip="Set attribute time samples metadata", clicked_fn=self._save_time_samples)
                    ui.Button(
                        "Clear", tooltip="Clear attribute time samples metadata", clicked_fn=self._clear_time_samples
                    )

                ui.Label("Time Sample Format: {time_code}: @{asset_path}@", height=0)
                self.text_editor = TextEditor()

        self.load_time_samples()
