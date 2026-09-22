# SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
import webbrowser
from dataclasses import dataclass
from typing import List

import omni.kit.app
from omni import ui
from pxr import UsdGeom

from .minimal_model import MinimalItem, MinimalModal

__all__ = ["CadConverterOptionsBuilder"]


@dataclass
class CadOptionsMap:
    """Class to map generic option names to concrete option names"""

    surface_tolerance: str = "dSurfaceTolerance"
    tessellation_level: str = "iTessLOD"
    convert_hidden: str = "bConvertHidden"
    generate_uvs: str = "bOptimize"
    instancing: str = "bInstancing"
    merge_meshes: str = "bMergeMeshes"
    convert_metadata: str = "bConvertMetadata"
    meters_per_unit: str = "dMetersPerUnit"
    up_axis: str = "iUpAxis"
    material_selection: str = "materialSelection"


class CadConverterOptionsBuilder:
    def __init__(self, options_model=None, options_map: CadOptionsMap = None):
        super().__init__()
        self._options_model = options_model
        self._options_map = options_map or CadOptionsMap()

        self._surface_tolerance_model = ui.SimpleFloatModel(default_value=0.2)
        self._surface_tolerance_field_sub = self._surface_tolerance_model.subscribe_value_changed_fn(
            self._surface_tolerance_changed
        )

        self._tessellation_model = MinimalModal(
            default_index=2, item_labels=["ExtraLow", "Low", "Medium", "High", "ExtraHigh"]
        )
        self._tess_change_sub = self._tessellation_model.subscribe_item_changed_fn(self._tessellation_combo_changed)

        self._enable_convert_visible_only = ui.SimpleBoolModel(default_value=True)
        self._convert_visible_only_sub = self._enable_convert_visible_only.subscribe_value_changed_fn(
            self._convert_hidden_model_changed
        )

        self._enable_generate_uvs = ui.SimpleBoolModel(default_value=True)
        self._generate_uvs_sub = self._enable_generate_uvs.subscribe_value_changed_fn(self._generate_uvs_model_changed)

        self._enable_instancing = ui.SimpleBoolModel(default_value=True)
        self._instancing_sub = self._enable_instancing.subscribe_value_changed_fn(self._instancing_model_changed)

        self._enable_convert_metadata = ui.SimpleBoolModel(default_value=False)
        self._convert_metadata_sub = self._enable_convert_metadata.subscribe_value_changed_fn(
            self._convert_metadata_model_changed
        )

        self._enable_merge_meshes = ui.SimpleBoolModel(default_value=True)
        self._merge_meshes_sub = self._enable_merge_meshes.subscribe_value_changed_fn(self._merge_meshes_model_changed)
        self._up_axis_model = MinimalModal(default_index=0, item_labels=["File Default", "Y-Axis", "Z-Axis"])
        self._up_axis_change_sub = self._up_axis_model.subscribe_item_changed_fn(self._up_axis_combo_changed)

        kit_version = omni.kit.app.get_app().get_kit_version()
        if kit_version.startswith("106.5"):
            self._material_selection_model = MinimalModal(default_index=1, item_labels=["None", "Preview Surface"])
        else:
            self._material_selection_model = MinimalModal(
                default_index=1, item_labels=["None", "Preview Surface", "OmniPBR"]
            )
        self._material_selection_change_sub = self._material_selection_model.subscribe_item_changed_fn(
            self._material_selection_combo_changed
        )

        # if unit is set to "Use Model Units", the converted USD will retain the meters per unit from conversion
        self._unit_scale_factors = [
            0,
            UsdGeom.LinearUnits.meters,
            UsdGeom.LinearUnits.feet,
            UsdGeom.LinearUnits.inches,
            UsdGeom.LinearUnits.centimeters,
            UsdGeom.LinearUnits.millimeters,
            UsdGeom.LinearUnits.micrometers,
            UsdGeom.LinearUnits.nanometers,
        ]
        self._mpu_model = MinimalModal(
            default_index=0,
            item_labels=[
                "Use Model Units",
                "Meters",
                "Feet",
                "Inches",
                "Centimeters",
                "Millimeters",
                "Micrometers",
                "Nanometers",
            ],
        )
        self._mpu_change_sub = self._mpu_model.subscribe_item_changed_fn(self._mpu_combo_changed)

        self._instancing_tooltip = None

    def _surface_tolerance_changed(self, model: ui.SimpleFloatModel):
        if hasattr(self._options_model, self._options_map.surface_tolerance):
            if model.as_float > 1.0:
                model.as_float = 1.0
            elif model.as_float < 0.0:
                model.as_float = 0.0
            setattr(self._options_model, self._options_map.surface_tolerance, model.as_float)

    def _tessellation_combo_changed(self, combo_model: MinimalModal, _: MinimalItem):
        if hasattr(self._options_model, self._options_map.tessellation_level):
            setattr(self._options_model, self._options_map.tessellation_level, combo_model.current_index)

    def _generate_uvs_model_changed(self, model: ui.SimpleBoolModel):
        if hasattr(self._options_model, self._options_map.generate_uvs):
            setattr(self._options_model, self._options_map.generate_uvs, model.as_bool)

    def _convert_hidden_model_changed(self, model: ui.SimpleBoolModel):
        if hasattr(self._options_model, self._options_map.convert_hidden):
            setattr(self._options_model, self._options_map.convert_hidden, not model.as_bool)

    def _instancing_model_changed(self, model: ui.SimpleBoolModel):
        if hasattr(self._options_model, self._options_map.instancing):
            setattr(self._options_model, self._options_map.instancing, model.as_bool)

    def _convert_metadata_model_changed(self, model: ui.SimpleBoolModel):
        if hasattr(self._options_model, self._options_map.convert_metadata):
            setattr(self._options_model, self._options_map.convert_metadata, model.as_bool)

    def _merge_meshes_model_changed(self, model: ui.SimpleBoolModel):
        if hasattr(self._options_model, self._options_map.merge_meshes):
            setattr(self._options_model, self._options_map.merge_meshes, model.as_bool)

    def _up_axis_combo_changed(self, combo_model: MinimalModal, _: MinimalItem):
        if hasattr(self._options_model, self._options_map.up_axis):
            setattr(self._options_model, self._options_map.up_axis, combo_model.current_index)

    def _mpu_combo_changed(self, combo_model: MinimalModal, _: MinimalItem):
        if hasattr(self._options_model, self._options_map.meters_per_unit):
            mpu = self._unit_scale_factors[combo_model.current_index]
            setattr(self._options_model, self._options_map.meters_per_unit, mpu)

    def _material_selection_combo_changed(self, combo_model: MinimalModal, _: MinimalItem):
        if hasattr(self._options_model, self._options_map.material_selection):
            setattr(self._options_model, self._options_map.material_selection, combo_model.current_index)

    def set_instancing_tooltip(self, tooltip):
        self._instancing_tooltip = tooltip

    def destroy(self) -> None:
        self._generate_uvs_sub = None
        self._instancing_sub = None
        self._convert_visible_only_sub = None
        self._surface_tolerance_field_sub = None
        self._meters_per_unit_field_sub = None
        self._up_axis_change_sub = None
        self._convert_metadata_sub = None
        self._merge_meshes_sub = None
        self._material_selection_change_sub = None

    def _has_tessellation_options(self) -> bool:
        """Return True if the options include tessellation options"""
        return hasattr(self._options_model, self._options_map.tessellation_level) or hasattr(
            self._options_model, self._options_map.surface_tolerance
        )

    def _build_tessellation_options(self) -> None:
        """Build tessellation options ui"""
        if hasattr(self._options_model, self._options_map.surface_tolerance):
            with ui.HStack(width=0, spacing=4):
                field = ui.FloatField(
                    model=self._surface_tolerance_model,
                    width=80,
                    min=0.0,
                    max=1.0,
                    identifier="field_surface_tolerance",
                    tooltip="Surface Tolerance - maximum distance between tessellated mesh and surface. \nIf a value of 0 is provided, then surface tolerance of an object is calculated as the diagonal its extents multiplied by 0.025.",
                )
                field.model.set_value(0.2)
                ui.Label("Surface Tolerance")
        elif hasattr(self._options_model, self._options_map.tessellation_level):
            with ui.HStack(width=0, spacing=4):
                # can't use model= due to bug OM-43014
                ui.ComboBox(self._tessellation_model, width=80, identifier="combo_tessellation")
                ui.Label("Tessellation Level")

    def build_pane(self, asset_paths: List[str]) -> None:
        """
        Helper function to build options pane.
        """
        with ui.VStack(height=0, spacing=4):
            if hasattr(self._options_model, self._options_map.convert_hidden):
                with ui.HStack(width=0, spacing=4):
                    ui.CheckBox(
                        model=self._enable_convert_visible_only,
                        identifier="check_convert_visible_only",
                        tooltip="Convert Visible Only -\nIf true, skip hidden elements;\nelse, convert hidden elements but set to invisible. \nNOTE: If the 'Scene Optimizer Config' field is provided, \nthis may be overridden.",
                    )
                    ui.Label("Convert Visible Only")
            if hasattr(self._options_model, self._options_map.generate_uvs):
                with ui.HStack(width=0, spacing=4):
                    ui.CheckBox(
                        model=self._enable_generate_uvs,
                        identifier="check_generate_uvs",
                        tooltip="Generate Projection UVs -\nIf true, use Scene Optimizer to generate uvs for any Mesh prims that do not have them",
                    )
                    # For Hoops Converter this is all the scene optimizer does:
                    ui.Label("Generate Projection UVs")
                    info_btn = ui.Button(
                        height=12,
                        width=12,
                        text="?",
                        tooltip="View documentation",
                    )
                    info_btn.set_clicked_fn(self._open_generate_projection_uvs_doc)
            if hasattr(self._options_model, self._options_map.instancing):
                with ui.HStack(width=0, spacing=4):
                    if self._instancing_tooltip is None:
                        ui.CheckBox(model=self._enable_instancing, identifier="check_instancing")
                    else:
                        ui.CheckBox(
                            model=self._enable_instancing,
                            identifier="check_instancing",
                            tooltip=self._instancing_tooltip,
                        )
                    ui.Label("Enable Instancing")
            if hasattr(self._options_model, self._options_map.convert_metadata):
                with ui.HStack(width=0, spacing=4):
                    ui.CheckBox(
                        model=self._enable_convert_metadata,
                        identifier="check_convert_metadata",
                        tooltip="If true, then metadata, including PMI, are imported as USD Attributes",
                    )
                    ui.Label("Convert Metadata")
            if hasattr(self._options_model, self._options_map.merge_meshes):
                with ui.HStack(width=0, spacing=4):
                    ui.CheckBox(
                        model=self._enable_merge_meshes,
                        identifier="check_merge_meshes",
                        tooltip="If true, then meshes are merged for optimization",
                    )
                    ui.Label("Merge Meshes")
            if hasattr(self._options_model, self._options_map.up_axis) or hasattr(
                self._options_model, self._options_map.meters_per_unit
            ):
                with ui.HStack(width=0, spacing=4):
                    ui.Label("Edit Stage Metrics:")
                    info_btn = ui.Button(
                        height=12,
                        width=12,
                        text="?",
                        tooltip="View documentation",
                    )
                    info_btn.set_clicked_fn(self._open_edit_stage_metrics_doc)
            if hasattr(self._options_model, self._options_map.up_axis):
                with ui.HStack(width=0, spacing=4):
                    # can't use model= due to bug OM-43014
                    ui.ComboBox(
                        self._up_axis_model,
                        width=100,
                        identifier="combo_up_axis",
                        tooltip="Override Up-Axis - override the up-axis of the converted USD's stage to Y-up, Z-up, or default to the converter's up-axis setting.",
                    )
                    ui.Label("Override Up-Axis")
            if hasattr(self._options_model, self._options_map.meters_per_unit):
                with ui.HStack(width=0, spacing=4):
                    ui.ComboBox(
                        self._mpu_model,
                        width=150,
                        identifier="field_meters_per_unit",
                        tooltip="Set the unit to use for the conversion.",
                    )
                    ui.Label("Unit")
            if hasattr(self._options_model, self._options_map.material_selection):
                with ui.HStack(width=0, spacing=4):
                    ui.ComboBox(
                        self._material_selection_model,
                        width=150,
                        identifier="combo_material_selection",
                        tooltip="Sets material type for the converted USD. \nNone - no materials are created. \nPreview Surface - create a simple preview surface material compatible with Universal renderer. \nOmniPBR - create a physically based material compatible for RTX and Universal renderers.",
                    )
                    ui.Label("Material Type")
                    info_btn = ui.Button(
                        height=12,
                        width=12,
                        text="?",
                        tooltip="View documentation",
                    )
                    info_btn.set_clicked_fn(self._open_material_selection_doc)

            # Tessellation Options
            if self._has_tessellation_options():
                ui.Spacer(width=4)
                ui.Label("Tessellation:")
                self._build_tessellation_options()

    def get_import_options(self):
        return self._options_model

    def _open_edit_stage_metrics_doc(self):
        webbrowser.open(
            "https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/operations.html#edit-stage-metrics"
        )

    def _open_generate_projection_uvs_doc(self):
        webbrowser.open(
            "https://docs.omniverse.nvidia.com/extensions/latest/ext_scene-optimizer/operations.html#generate-projection-uvs"
        )

    def _open_material_selection_doc(self):
        webbrowser.open("https://docs.omniverse.nvidia.com/materials-and-rendering/latest/materials_templates.html")
