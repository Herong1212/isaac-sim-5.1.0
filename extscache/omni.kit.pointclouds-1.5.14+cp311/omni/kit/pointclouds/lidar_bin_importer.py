# Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import asyncio
import os
from functools import partial
from pathlib import Path
from typing import Dict, List, Union

import carb
import omni.kit.app
import omni.kit.tool.asset_importer as ai
import omni.ui as ui
import omni.usd
from pxr import Gf, Sdf, Tf, Usd, UsdGeom

from .progress_window import ProgressWindow
from .render import run_flow_renderer, run_index_renderer


class LidarBINImporter(ai.AbstractImporterDelegate):
    def __init__(self, extension_path) -> None:
        super().__init__()
        self._name = "Lidar BIN Importer"
        self._filters = [".*\\.bin$"]
        self._descriptions = ["Lidar BIN Files (*.bin)"]
        self._create_renderer = True
        self._file_up_axis = "Y"
        self._default_color = [200, 200, 200]
        # used for icon paths
        self._extension_path = extension_path
        self._default_color_widget_item_changed = None

    def destroy(self):
        self._default_color_widget_item_changed = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def filter_regexes(self) -> List[str]:
        return self._filters

    @property
    def filter_descriptions(self) -> List[str]:
        return self._descriptions

    async def _show_progress_window(self, title):
        """Progress window shown while copying to the stage"""

        progress_window = ProgressWindow(title, status_text="Preparing...")
        progress_window.status_text = "Preparing..."
        progress_window.show()
        # wait for the progress window to appear
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        return progress_window

    def _cancel_operation(self):
        self._cancelled = True

    def build_options(self, paths: List[str]) -> None:
        LABEL_FONT_SIZE = 14
        CHECKBOX_FONT_SIZE = 14
        RADIOBUTTON_STYLE = {
            "": {"background_color": 0x0, "image_url": f"{self._extension_path}/icons/radio_off.svg"},
            ":checked": {"image_url": f"{self._extension_path}/icons/radio_on.svg"},
        }

        def up_axis_changed(file_up_axis):
            self._file_up_axis = file_up_axis

        def on_color_changed(model, children):
            self._default_color = []
            for child_item in children:
                component = model.get_item_value_model(child_item)
                self._default_color.append(int(255 * component.as_float))

        def toggle_renderer(box):
            self._create_renderer = box.get_value_as_bool()

        with ui.VStack(height=0, spacing=5):

            collection = ui.RadioCollection()
            with ui.HStack(width=ui.Percent(100), style=RADIOBUTTON_STYLE):
                ui.Label("Source file up axis:", width=0)

                radio_axis_up_z = ui.RadioButton(radio_collection=collection, width=30, height=30)
                ui.Label("Z", name="text")

                radio_axis_up_y = ui.RadioButton(radio_collection=collection, width=30, height=30)
                ui.Label("Y", name="text")
                ui.Spacer()

                up_axis_changed("Z")

            radio_axis_up_y.set_clicked_fn(partial(up_axis_changed, "Y"))
            radio_axis_up_z.set_clicked_fn(partial(up_axis_changed, "Z"))

            with ui.HStack(width=ui.Percent(100)):
                ui.Label("Default color:", width=0, style={"font_size": LABEL_FONT_SIZE}, alignment=ui.Alignment.LEFT)
                ui.Spacer(width=8)
                default_color_widget = ui.ColorWidget(
                    self._default_color[0] / 255.0, self._default_color[1] / 255.0, self._default_color[2] / 255.0
                )
                self._default_color_widget_item_changed = default_color_widget.model.subscribe_item_changed_fn(
                    lambda model, _, children=default_color_widget.model.get_item_children(): on_color_changed(
                        model, children
                    )
                )
                ui.Spacer()

            with ui.HStack(width=ui.Percent(100)):
                ui.Spacer(width=8)
                renderer_checkbox = ui.CheckBox(width=20, style={"font_size": CHECKBOX_FONT_SIZE})
                ui.Label(
                    "Create Flow renderer",
                    width=0,
                    style={"font_size": LABEL_FONT_SIZE},
                    alignment=ui.Alignment.LEFT,
                    tooltip="If unchecked, IndeX renderer will be used",
                )
                ui.Spacer()
                renderer_checkbox.model.set_value(self._create_renderer)
                renderer_checkbox.model.add_value_changed_fn(lambda box: toggle_renderer(box))

            ui.Spacer()

        return True

    async def convert_assets(self, paths: List[str]) -> Dict[str, Union[str, None]]:
        """The real worker to convert assets."""

        absolute_paths = []
        converted_assets = {}

        for file_path in paths:
            if self.is_supported_format(file_path):
                absolute_paths.append(file_path)

        self._cancelled = False
        progress_window = await self._show_progress_window("PTS File Import")

        if progress_window and not progress_window.is_visible():
            carb.log_error("Error showing progress window")
        elif progress_window:
            progress_window.set_cancel_fn(self._cancel_operation)
        else:
            carb.log_error("Error creating progress window")
            return []

        stage = omni.usd.get_context().get_stage()
        self._create_import_prim(stage)
        await self._transform(self._target_path)

        for absolute_path in absolute_paths:
            basename = os.path.basename(absolute_path)

            progress_window.status_text = f"Copying data from {basename}..."
            await omni.kit.app.get_app().next_update_async()

            prim = await self._import_assets(absolute_path)
            if not prim:
                progress_window.hide()
                return converted_assets

            # Return empty list so the import manager does not create any references
            converted_assets[absolute_path] = []

            await omni.kit.app.get_app().next_update_async()
            if self._cancelled:
                break

        await self._render([self._target_path])

        progress_window.hide()
        if self._cancelled:
            return []

        return converted_assets

    def _create_import_prim(self, target_stage):
        prim_path = "/World/ImportedPoints"
        # prim_path = omni.usd.get_stage_next_free_path(target_stage, prim_path, True)

        if self._cancelled:
            return None

        # Create the parent xform
        xform_prim = target_stage.DefinePrim(prim_path, "Xform")

        stage = omni.usd.get_context().get_stage()
        scale = 1.0 / UsdGeom.GetStageMetersPerUnit(stage)

        xform_prim.CreateAttribute("xformOp:translate", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 0, 0))
        xform_prim.CreateAttribute("xformOp:rotateZYX", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 0, 0))
        xform_prim.CreateAttribute("xformOp:scale", Sdf.ValueTypeNames.Double3, False).Set(
            Gf.Vec3d(scale, scale, scale)
        )
        xform_prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.String, False).Set(
            ["xformOp:translate", "xformOp:rotateZYX", "xformOp:scale"]
        )

        self._target_path = str(xform_prim.GetPath()) + "/pointcloud"
        # self._target_path = omni.usd.get_stage_next_free_path(stage, target_path, False)
        point_prim = target_stage.DefinePrim(self._target_path, "Points")
        if not point_prim:
            carb.log_error(f"Point prim at path '{self._target_path}' could not be created")

    async def _import_assets(self, absolute_path):
        """Imports assets to the target stage. We build our own parent xform and import the data."""
        args = {
            "path": str(self._target_path),
            "defaultR": str(self._default_color[0]),
            "defaultG": str(self._default_color[1]),
            "defaultB": str(self._default_color[2]),
        }
        source_layer = Sdf.Layer.FindOrOpen(absolute_path, args)

        with omni.kit.undo.group():
            Usd.Stage.Open(source_layer)

        return self._target_path

    async def _transform(self, parent_prim_path):
        # Let file format plugin process the PTS stage update to create a point cloud prim
        await omni.kit.app.get_app().next_update_async()

        stage = omni.usd.get_context().get_stage()
        parent_prim = stage.GetPrimAtPath(parent_prim_path)
        if not parent_prim:
            carb.log_error(f"Prim at path '{parent_prim_path}' does not exist")
            return

        stage_up_axis = UsdGeom.GetStageUpAxis(stage)
        if stage_up_axis != self._file_up_axis:
            adj_mat = Gf.Matrix4d().SetIdentity()

            if stage_up_axis == "Y" and self._file_up_axis == "Z":
                # Rotate from z-axis up to y-axis up
                carb.log_info("Rotating asset from Z to Y axis")
                # fmt: off
                adj_mat = Gf.Matrix4d(
                    0.0, 0.0, 1.0, 0.0,
                    1.0, 0.0, 0.0, 0.0,
                    0.0, 1.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 1.0)
                # fmt: on
            elif stage_up_axis == "Z" and self._file_up_axis == "Y":
                # Rotate from y-axis up to z-axis up
                carb.log_info("Rotating asset from Y to Z axis")
                # fmt: off
                adj_mat = Gf.Matrix4d(
                    0.0, 1.0, 0.0, 0.0,
                    0.0, 0.0, 1.0, 0.0,
                    1.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 1.0)
                # fmt: on

            with omni.kit.undo.group():
                omni.kit.commands.execute("TransformPrim", path=parent_prim_path, new_transform_matrix=adj_mat)

        await omni.kit.app.get_app().next_update_async()

    async def _render(self, prim_paths):
        stage = omni.usd.get_context().get_stage()
        for prim_path in prim_paths:
            parent_prim = stage.GetPrimAtPath(prim_path)
            if not parent_prim:
                carb.log_error(f"Prim at path '{prim_path}' does not exist")
                continue

            # wait for finished import
            while True:
                points = parent_prim.GetAttribute("points").Get()
                if points:
                    break
                await asyncio.sleep(10)

        with omni.kit.undo.group():
            if self._create_renderer:
                await run_flow_renderer(prim_paths)
            else:
                await run_index_renderer(prim_paths)
