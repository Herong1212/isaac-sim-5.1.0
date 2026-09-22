# Copyright (c) 2020-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import asyncio
import copy
import math
import traceback
from pathlib import Path
from typing import Tuple

import carb
import numpy as np
import omni.kit.commands
import omni.kit.undo
import omni.kit.usd.layers
import omni.usd

# from omni.curve.manipulator.scripts.tool_settings import ToolSettingsWindow
from omni.curve.manipulator.bindings import CurveEditingModeType, CurvesEventType, get_interface

# import omni.curve.manipulator.bindings as curman
# from ..bindings import CurveEditingModeType
from omni.curve.manipulator.scripts.bezier_curve_edits_context import BezierCurveEditsContextManager
from omni.kit.manipulator.tool.snap import settings_constants as snap_c
from omni.kit.manipulator.tool.snap.builtin_snap_tools import GRID_SNAP_NAME
from omni.usd._impl.utils import get_local_transform_matrix
from omni.warehouse_creator.utils import get_assets_root_path, set_pose
from pxr import Gf, Kind, Sdf, Tf, Usd, UsdGeom, Vt

CURRENT_PATH = Path(carb.tokens.get_tokens_interface().resolve("${omni.curve.manipulator}/data"))
CAMERA_PATH = "/Camera"
CURVE_PATH = "BasisCurves"
WAREHOUSE_FLOORPLAN_PATH = f"warehouse_floorplan"

# Custom Attributes
from omni.warehouse_creator.utils import (
    WAREHOUSE_IDX,
    WAREHOUSE_SHAPE,
    WAREHOUSE_TILE_DIM,
    WAREHOUSE_X_EXTENT,
    WAREHOUSE_Y_EXTENT,
    get_column_map,
)


class WarehouseBuilder:
    async def get_assets_path(self):
        self.asset_folder = get_assets_root_path()
        self.wall_asset_x = self.asset_folder + "warehouse_h10m_straight_90.usd"
        self.wall_asset_y = self.asset_folder + "warehouse_h10m_straight.usd"
        self.cornerin_asset = self.asset_folder + "warehouse_h10m_corner_in.usd"
        self.cornerout_asset = self.asset_folder + "warehouse_h10m_corner_out.usd"
        self.center_tile_asset = self.asset_folder + "warehouse_h10m_center.usd"

    def __init__(self, **kwargs) -> None:
        self._settings = carb.settings.get_settings()
        self.prev_settings = {}
        self.asset_folder = ""
        self._current_curve_sub = None

        # Fill grid map that tells which portion of the matrix a tile covers based on its position, assuming zero rotation
        self.fill_map = {
            "warehouse_h10m_straight.usd": [{0: [0, -1], 180: [-1, 0]}],
            "warehouse_h10m_straight_90.usd": [{0: [-1, -1], 180: [0, 0]}],
            "warehouse_h10m_center.usd": [{0: [0, -1]}],
            "warehouse_h10m_corner_in.usd": [{0: [0, -1], 90: [0, 0], 180: [-1, 0], 270: [-1, -1]}],
            "warehouse_h10m_corner_out.usd": [
                {0: [0, -1], 90: [0, 0], 180: [-1, 0], 270: [-1, -1]},
                {0: [1, -1], 90: [0, 1], 180: [-2, 0], 270: [-1, -2]},
                {0: [1, 0], 90: [-1, 1], 180: [-2, -1], 270: [-0, -2]},
            ],
        }
        self.tile_dimension = 10
        asyncio.ensure_future(self.get_assets_path())
        self._warehouse_prim = None
        self.on_finish_edit_fn = kwargs.get("finish_edit_fn", None)
        return

    def get_base_asset_names(self):
        return self.fill_map.keys()

    def set_setting(self, setting, value):
        self.prev_settings[setting] = self._settings.get(setting)
        self._settings.set(setting, value)

    def reset_settings(self):
        for setting, value in self.prev_settings.items():
            self._settings.set(setting, value)

    def begin_edit(self):
        self._curve_manip = get_interface()
        self._context = omni.usd.get_context()
        _curve_context = BezierCurveEditsContextManager.get_context().curve_edits.curve_context
        self._curve_points = []

        self._stage = omni.usd.get_context().get_stage()
        UsdGeom.SetStageMetersPerUnit(self._stage, UsdGeom.LinearUnits.meters)
        UsdGeom.SetStageUpAxis(self._stage, "Z")
        default_path = Sdf.Path("/")
        if self._stage.GetDefaultPrim():
            default_path = self._stage.GetDefaultPrim().GetPath()
        self._warehouse_prim = UsdGeom.Xform.Define(
            self._stage,
            omni.usd.get_stage_next_free_path(self._stage, default_path.AppendPath(WAREHOUSE_FLOORPLAN_PATH), True),
        )
        with omni.kit.usd.layers.active_authoring_layer_context(self._context):

            # self.set_setting("/exts/omni.curve.manipulator/showPrompt", False)
            basis_path = "/"
            self.set_setting(snap_c.SNAP_PROVIDER_NAME_SETTING_PATH, [GRID_SNAP_NAME])
            self.set_setting("/persistent/app/viewport/grid/scale", self.tile_dimension)
            _selection = omni.usd.get_context().get_selection()
            sels = _selection.get_selected_prim_paths()
            if sels:
                if UsdGeom.BasisCurves(self._stage.GetPrimAtPath(sels[0])):
                    self._basis_curve = UsdGeom.BasisCurves(self._stage.GetPrimAtPath(sels[0]))
                    basis_path = sels[0]
                    transform = omni.usd.get_world_transform_matrix(self._basis_curve.GetPrim())
                    set_pose(
                        self._warehouse_prim,
                        transform.ExtractTranslation(),
                        transform.ExtractRotation().Decompose(Gf.Vec3d(1, 0, 0), Gf.Vec3d(0, 1, 0), Gf.Vec3d(0, 0, 1)),
                    )
            else:
                self._basis_curve = None
                basiscurve = UsdGeom.BasisCurves.Define(
                    self._stage,
                    omni.usd.get_stage_next_free_path(self._stage, default_path.AppendPath(CURVE_PATH), True),
                )

                basis_path = basiscurve.GetPath()
                _selection.set_selected_prim_paths([str(basis_path)], False)
                basiscurve.GetBasisAttr().Set(UsdGeom.Tokens.bezier)
                basiscurve.GetTypeAttr().Set(UsdGeom.Tokens.linear)
                basiscurve.GetWrapAttr().Set(UsdGeom.Tokens.nonperiodic)
                basiscurve.GetPurposeAttr().Set(UsdGeom.Tokens.render)
                self._curve_manip.enable_curve_editing_mode(
                    _curve_context, [str(basis_path)], CurveEditingModeType.DRAG
                )
                BezierCurveEditsContextManager.get_context().curve_edits.set_curve_type([basiscurve], "linear")

                async def updatemode():
                    await omni.kit.app.get_app().next_update_async()
                    # omni.kit.commands.execute("SetCurveEditingMode", curve_context=self._curve_context, mode=CurveEditingModeType.DRAG)
                    self.set_setting("/app/viewport/snapEnabled", True)
                    self.set_setting("/persistent/exts/omni.curve.manipulator/curveDrawPoints", True)
                    self.set_setting("/persistent/exts/omni.curve.manipulator/pencilToolInterpolateMode", "linear")
                    self.set_setting("/persistent/exts/omni.curve.manipulator/pencilToolSpacing", self.tile_dimension)

                asyncio.ensure_future(updatemode())

                self._current_curve_sub = self._curve_manip.get_curves_event_stream(
                    _curve_context
                ).create_subscription_to_pop(self._on_curves_event, name="curve_events")

            # TODO: zoom camera out
            self._basis_curves = basis_path
            self._curve_current_point = 0
            self._wall_segment_id = 0
            self._three_dots_straight_line = False
            self._corner_types = []

            if self._basis_curve:
                self._curve_points = np.array(self._basis_curve.GetPointsAttr().Get())
                if len(self._curve_points) > 0:
                    for i in range(len(self._curve_points)):
                        if self.add_point():
                            return

            # UsdGeom.BasisCurves(curve_prim).SetWidthsInterpolation("constant")
            # UsdGeom.BasisCurves(curve_prim).CreateWidthsAttr().Set([0.1])
            # UsdGeom.BasisCurves(curve_prim).CreateTypeAttr().Set("linear")
            # set_camera_view(eye=[0, 0, 500], target=[0, 0, 0], camera_prim_path="/OmniverseKit_Persp")

        return

    def add_point(self):
        _basis_curve = UsdGeom.BasisCurves(self._stage.GetPrimAtPath(self._basis_curves))
        self._curve_points = np.array(_basis_curve.GetPointsAttr().Get())
        is_wrap = (
            _basis_curve.GetWrapAttr().Get() == UsdGeom.Tokens.periodic
            and len(self._curve_points) - self._curve_current_point == 0
        )
        if len(self._curve_points) > 1 or is_wrap:
            self._three_dots_straight_line = False
            prev_point = None
            current_point = copy.deepcopy(self._curve_points[self._curve_current_point])
            next_point = copy.deepcopy(
                self._curve_points[int((self._curve_current_point + 1) % (len(self._curve_points)))]
            )
            if self._curve_current_point > 0:
                prev_point = copy.deepcopy(self._curve_points[self._curve_current_point - 1])
                prev_point[2] = 0
            current_point[2] = 0
            next_point[2] = 0

            is_valid_points, updated_next_point = self.validate_points(
                prev_point, current_point, next_point, not is_wrap
            )
            if is_valid_points:
                ret = self.add_wall(prev_point, current_point, updated_next_point)
                self._curve_current_point = self._curve_current_point + 1
                widths = _basis_curve.GetWidthsAttr().Get()
                _basis_curve.GetWidthsAttr().Set(widths[: len(self._curve_points)])
                return ret

        return False

    def _on_curves_event(self, event: carb.events.IEvent):
        try:
            from omni.curve.manipulator.bindings import CurvesEventType

            curve_event_type = CurvesEventType(event.type)
            if curve_event_type == CurvesEventType.BEGIN_ADD:
                self.add_point()
        except Exception as e:
            carb.log_warn(f"Import error: {e}")
            traceback_str = traceback.format_exc()
            carb.log_error(traceback_str)

    def invalidate_point(self):
        new_points = copy.deepcopy(self._curve_points[:-1])
        _basis_curve = UsdGeom.BasisCurves(self._stage.GetPrimAtPath(self._basis_curves))
        _basis_curve.GetCurveVertexCountsAttr().Set(_basis_curve.GetCurveVertexCountsAttr().Get() - 1)
        _basis_curve.GetPointsAttr().Set(new_points)

    def finish_edit(self):
        try:
            basiscurve = UsdGeom.BasisCurves(self._stage.GetPrimAtPath(self._basis_curves))
            basiscurve.GetTypeAttr().Set(UsdGeom.Tokens.linear)
            basiscurve.GetWrapAttr().Set(UsdGeom.Tokens.periodic)
            self.add_point()
        except:
            pass
        if self.on_finish_edit_fn:
            self.on_finish_edit_fn()
        self.reset_settings()  # Return to settings from before editing.

    def validate_points(self, prev_point, current_point, next_point, invalidate=True) -> Tuple[bool, np.ndarray]:
        _basis_curve = UsdGeom.BasisCurves(self._stage.GetPrimAtPath(self._basis_curves))

        # assuming counter-clockwise drawing
        if abs(next_point[1] - current_point[1]) > 0 or abs(next_point[0] - current_point[0]) > 0:
            # invalidate diagonal points
            if abs(next_point[1] - current_point[1]) == abs(next_point[0] - current_point[0]):
                self.invalidate_point()
                return False, None

            elif abs(next_point[1] - current_point[1]) > abs(next_point[0] - current_point[0]):
                next_point[0] = current_point[0]
                new_value = [current_point[0], next_point[1], next_point[2]]
            else:  # abs(next_point[1] - current_point[1]) < abs(next_point[0] - current_point[0]):
                next_point[1] = current_point[1]
                new_value = [next_point[0], current_point[1], next_point[2]]

            if self._curve_current_point + 1 < len(self._curve_points):
                new_points = copy.deepcopy(self._curve_points)
                new_points[self._curve_current_point + 1] = new_value
                _basis_curve.GetPointsAttr().Set(new_points)

        # invalidate reverse points
        if prev_point is not None:
            if math.isclose(abs(next_point[1] - current_point[1]), 0.0) and abs(next_point[0] - current_point[0]) > 0:
                if current_point[0] - prev_point[0] > 0 and next_point[0] - current_point[0] < 0:
                    if invalidate:
                        self.invalidate_point()
                    return False, None
                elif current_point[0] - prev_point[0] < 0 and next_point[0] - current_point[0] > 0:
                    if invalidate:
                        self.invalidate_point()
                    return False, None
            if math.isclose(abs(next_point[0] - current_point[0]), 0.0) and abs(next_point[1] - current_point[1]) > 0:
                if current_point[1] - prev_point[1] > 0 and next_point[1] - current_point[1] < 0:
                    if invalidate:
                        self.invalidate_point()
                    return False, None
                elif current_point[1] - prev_point[1] < 0 and next_point[1] - current_point[1] > 0:
                    if invalidate:
                        self.invalidate_point()
                    return False, None
        return True, next_point

    def add_wall(self, prev_point, current_point, next_point):
        # Future TODO: one tile quarter (overlaying two out/in corners)
        # TODO: set to instanceable before adding as reference - define prim then other loop for reference
        rot_quat, axis, num_of_wall_segments = self.get_wall_data(current_point, next_point)
        if self._curve_current_point > 0:
            self.add_corner(prev_point, current_point, next_point)
        self.add_wall_segments(rot_quat, axis, num_of_wall_segments, current_point)
        if self._curve_current_point > 0 and np.allclose(next_point, self._curve_points[0]):
            final_next_point = copy.deepcopy(self._curve_points[1])
            if np.allclose(self._curve_points[-1], self._curve_points[0]):
                self.invalidate_point()
            self.add_corner(current_point, self._curve_points[0], final_next_point)
            self.fill_inside_tiles()
            curve_context = BezierCurveEditsContextManager.get_context().curve_edits.curve_context
            basis_curve = UsdGeom.BasisCurves(self._stage.GetPrimAtPath(self._basis_curves))
            BezierCurveEditsContextManager.get_context().curve_edits.set_curve_type([basis_curve], "linear")
            BezierCurveEditsContextManager.get_context().curve_edits.open_close_curve(basis_curve)

            async def delayed_disable_editing():
                for i in range(200):
                    await omni.kit.app.get_app().next_update_async()
                if self._curve_manip.is_in_curve_editing_mode(curve_context):
                    cv_selection = BezierCurveEditsContextManager.get_context().selection
                    cv_selection.clear_all_selection()
                    self._curve_manip.disable_curve_editing_mode(curve_context)
                    for i in range(200):
                        await omni.kit.app.get_app().next_update_async()
                    _selection = omni.usd.get_context().get_selection()
                    _selection.set_selected_prim_paths([str(self._warehouse_prim.GetPath())])
                    self._current_curve_sub = None
                    basiscurve = UsdGeom.BasisCurves(self._stage.GetPrimAtPath(self._basis_curves))
                    basiscurve.GetTypeAttr().Set(UsdGeom.Tokens.linear)
                    basiscurve.GetWrapAttr().Set(UsdGeom.Tokens.periodic)
                    # self._curve_manip.disable_curve_editing_mode(curve_context)

            asyncio.ensure_future(delayed_disable_editing())

            if self.on_finish_edit_fn:
                self.on_finish_edit_fn()
            self.reset_settings()  # Return to settings from before editing.
            return True  # Done building warehouse
        return False

    def add_wall_segments(self, rot_quat, axis, num_of_wall_segments, current_point):
        wall_asset_path = None
        wall_type = "straight"
        if not self._three_dots_straight_line:
            num_of_wall_segments = num_of_wall_segments - 2
        wall_step_increment = self.tile_dimension
        for _ in range(num_of_wall_segments):
            if self._three_dots_straight_line:
                wall_step_increment = -self.tile_dimension
            if axis == "x":
                current_point[0] = current_point[0] + wall_step_increment
                wall_asset_path = self.wall_asset_x
                wall_type = "straight"
            elif axis == "-x":
                current_point[0] = current_point[0] - wall_step_increment
                wall_asset_path = self.wall_asset_x
                wall_type = "straight"
            elif axis == "y":
                current_point[1] = current_point[1] + wall_step_increment
                wall_asset_path = self.wall_asset_y
                wall_type = "straight"
            elif axis == "-y":
                current_point[1] = current_point[1] - wall_step_increment
                wall_asset_path = self.wall_asset_y
                wall_type = "straight"
            self._three_dots_straight_line = False
            wall_step_increment = self.tile_dimension
            self._wallXform = UsdGeom.Xform.Define(
                self._stage,
                self._warehouse_prim.GetPath().AppendPath("wall_" + wall_type + f"_{self._wall_segment_id}"),
            )
            set_pose(self._wallXform, current_point, rot_quat)
            self._wallXform.GetPrim().GetReferences().AddReference(wall_asset_path)
            self._wall_segment_id = self._wall_segment_id + 1

    def add_corner(self, prev_point, current_point, next_point):
        # 1)+y-x
        if current_point[1] - prev_point[1] > 0 and next_point[0] - current_point[0] < 0:
            # inner || rot 0.7,0,0,-0.7
            self._wallXform = UsdGeom.Xform.Define(
                self._stage, self._warehouse_prim.GetPath().AppendPath(f"wallcornerin_{self._wall_segment_id}")
            )
            set_pose(self._wallXform, current_point, [0.0, 0.0, -90])
            self._wallXform.GetPrim().GetReferences().AddReference(self.cornerin_asset)
            self._corner_types.append("inner")
        # 2)-x+y
        elif current_point[0] - prev_point[0] < 0 and next_point[1] - current_point[1] > 0:
            # outer || rot 0.7,0,0,-0.7 || pos currentpoint[1] + 10
            oc_pos = np.array([current_point[0], current_point[1] + self.tile_dimension, 0])
            self._wallXform = UsdGeom.Xform.Define(
                self._stage, self._warehouse_prim.GetPath().AppendPath(f"wallcornerout_{self._wall_segment_id}")
            )
            set_pose(self._wallXform, oc_pos, [0.0, 0.0, -90])
            self._wallXform.GetPrim().GetReferences().AddReference(self.cornerout_asset)
            self._corner_types.append("outer")
        # 3)+y+x
        elif current_point[1] - prev_point[1] > 0 and next_point[0] - current_point[0] > 0:
            # outer || rot 0,0,0,1 || currpoint[0] + 10
            oc_pos = np.array([current_point[0] + self.tile_dimension, current_point[1], 0])
            self._wallXform = UsdGeom.Xform.Define(
                self._stage, self._warehouse_prim.GetPath().AppendPath(f"wallcornerout_{self._wall_segment_id}")
            )
            set_pose(self._wallXform, oc_pos, [0.0, 0.0, 180])
            self._wallXform.GetPrim().GetReferences().AddReference(self.cornerout_asset)
            self._corner_types.append("outer")
        # 4)+x+y
        elif current_point[0] - prev_point[0] > 0 and next_point[1] - current_point[1] > 0:
            # inner || #rot 0,0,0,1
            self._wallXform = UsdGeom.Xform.Define(
                self._stage, self._warehouse_prim.GetPath().AppendPath(f"wallcornerin_{self._wall_segment_id}")
            )
            set_pose(self._wallXform, current_point, [0.0, 0.0, 180])
            self._wallXform.GetPrim().GetReferences().AddReference(self.cornerin_asset)
            self._corner_types.append("inner")
        # 5)-x-y
        elif current_point[0] - prev_point[0] < 0 and next_point[1] - current_point[1] < 0:
            # inner || 1,0,0,0
            self._wallXform = UsdGeom.Xform.Define(
                self._stage, self._warehouse_prim.GetPath().AppendPath(f"wallcornerin_{self._wall_segment_id}")
            )
            set_pose(self._wallXform, current_point, [0.0, 0.0, 0.0])
            self._wallXform.GetPrim().GetReferences().AddReference(self.cornerin_asset)
            self._corner_types.append("inner")
        # 6)-y+x
        elif current_point[1] - prev_point[1] < 0 and next_point[0] - current_point[0] > 0:
            # inner || -0.7,0,0-0.7
            self._wallXform = UsdGeom.Xform.Define(
                self._stage, self._warehouse_prim.GetPath().AppendPath(f"wallcornerin_{self._wall_segment_id}")
            )
            set_pose(self._wallXform, current_point, [0.0, 0.0, 90])
            self._wallXform.GetPrim().GetReferences().AddReference(self.cornerin_asset)
            self._corner_types.append("inner")
        # 7)+x-y
        elif current_point[0] - prev_point[0] > 0 and next_point[1] - current_point[1] < 0:
            # outer || 0.7,0,0,0.7 || pos[1] - 10
            oc_pos = np.array([current_point[0], current_point[1] - 10, 0])
            self._wallXform = UsdGeom.Xform.Define(
                self._stage, self._warehouse_prim.GetPath().AppendPath(f"wallcornerout_{self._wall_segment_id}")
            )
            set_pose(self._wallXform, oc_pos, [0.0, 0.0, 90])
            self._wallXform.GetPrim().GetReferences().AddReference(self.cornerout_asset)
            self._corner_types.append("outer")
        # 8)-y-x
        elif current_point[1] - prev_point[1] < 0 and next_point[0] - current_point[0] < 0:
            # outer || 1,0,0,0 || pos[0] - 10
            oc_pos = np.array([current_point[0] - 10, current_point[1], 0])
            self._wallXform = UsdGeom.Xform.Define(
                self._stage, self._warehouse_prim.GetPath().AppendPath(f"wallcornerout_{self._wall_segment_id}")
            )
            set_pose(self._wallXform, oc_pos, [0.0, 0.0, 0])
            self._wallXform.GetPrim().GetReferences().AddReference(self.cornerout_asset)
            self._corner_types.append("outer")
        elif (
            (current_point[1] - prev_point[1] < 0 and next_point[0] - current_point[0] == 0)
            or (current_point[1] - prev_point[1] > 0 and next_point[0] - current_point[0] == 0)
            or (current_point[1] - prev_point[1] == 0 and next_point[0] - current_point[0] < 0)
            or (current_point[1] - prev_point[1] == 0 and next_point[0] - current_point[0] > 0)
        ):
            self._three_dots_straight_line = True
            self._corner_types.append("skip")

        self._wall_segment_id = self._wall_segment_id + 1

    def get_wall_data(self, first_point, second_point) -> Tuple[str, int]:
        axis = None
        num_of_wall_segments = 0

        if second_point[1] - first_point[1] > 0:
            axis = "y"
            num_of_wall_segments = int(round(abs(second_point[1] - first_point[1]) / self.tile_dimension))
            return [0, 0, 180], axis, num_of_wall_segments

        if second_point[1] - first_point[1] < 0:
            axis = "-y"
            num_of_wall_segments = int(round(abs(second_point[1] - first_point[1]) / self.tile_dimension))
            return [0, 0, 0], axis, num_of_wall_segments

        if second_point[0] - first_point[0] > 0:
            axis = "x"
            num_of_wall_segments = int(round(abs(second_point[0] - first_point[0]) / self.tile_dimension))
            return [0, 0, 180], axis, num_of_wall_segments

        if second_point[0] - first_point[0] < 0:
            axis = "-x"
            num_of_wall_segments = int(round(abs(second_point[0] - first_point[0]) / self.tile_dimension))
            return [0, 0, 0], axis, num_of_wall_segments

    def get_directions(self, point_prev, point_next):
        dx, dy = 0, 0
        if point_next[0] - point_prev[0] > 0 and point_next[1] - point_prev[1] > 0:
            dx, dy = -1, 0
        elif point_next[0] - point_prev[0] > 0 and point_next[1] - point_prev[1] < 0:
            dx, dy = 0, 0
        elif point_next[0] - point_prev[0] < 0 and point_next[1] - point_prev[1] < 0:
            dx, dy = 0, -1
        elif point_next[0] - point_prev[0] < 0 and point_next[1] - point_prev[1] > 0:
            dx, dy = -1, -1

        return dx, dy

    def fill_inside_tiles(self):
        # xmin,xmax,ymin,ymax,x_height,y_width should not be selfs. get from attribute
        x_max = int(np.max(self._curve_points[:, 0]))
        x_min = int(np.min(self._curve_points[:, 0]))
        y_max = int(np.max(self._curve_points[:, 1]))
        y_min = int(np.min(self._curve_points[:, 1]))
        x_height = int(round((x_max - x_min) / self.tile_dimension))
        y_width = int(round((y_max - y_min) / self.tile_dimension))

        wh_floorplan = self._warehouse_prim.GetPrim()
        wh_floorplan.CreateAttribute(WAREHOUSE_X_EXTENT, Sdf.ValueTypeNames.IntArray, True).Set(
            Vt.IntArray([x_min, x_max])
        )
        wh_floorplan.CreateAttribute(WAREHOUSE_Y_EXTENT, Sdf.ValueTypeNames.IntArray, True).Set(
            Vt.IntArray([y_min, y_max])
        )
        wh_floorplan.CreateAttribute(WAREHOUSE_TILE_DIM, Sdf.ValueTypeNames.Int, True).Set(self.tile_dimension)
        wh_floorplan.CreateAttribute(WAREHOUSE_SHAPE, Sdf.ValueTypeNames.IntArray, True).Set(
            Vt.IntArray([x_height, y_width])
        )

        self.space_matrix = np.zeros((x_height, y_width))
        points_xy = self._curve_points.copy()
        points_xy = points_xy[:, :2]
        if np.allclose(points_xy[0], points_xy[-1]):
            points_xy = points_xy[:-1, :]
        num_of_points = len(points_xy)
        i = 0
        matrix_corners = []
        for i in range(num_of_points):
            prev_point = points_xy[i]
            current_point = points_xy[(i + 1) % num_of_points]
            next_point = points_xy[(i + 2) % num_of_points]
            # remove non-corner points for filling upcoming filling algorithms
            if (
                math.isclose(abs(next_point[1] - current_point[1]), 0.0)
                and abs(next_point[0] - current_point[0]) > 0
                and math.isclose(abs(next_point[1] - prev_point[1]), 0.0)
            ) or (
                math.isclose(abs(next_point[0] - current_point[0]), 0.0)
                and abs(next_point[1] - current_point[1]) > 0
                and math.isclose(abs(next_point[0] - prev_point[0]), 0.0)
            ):
                continue
            dx, dy = self.get_directions(prev_point, next_point)
            point_in_matrix = [
                int(round((current_point[0] - x_min) / self.tile_dimension)) + dx,
                int(round((current_point[1] - y_min) / self.tile_dimension)) + dy,
            ]
            matrix_corners.append(point_in_matrix)

        num_of_corners = len(matrix_corners)
        for j in range(num_of_corners):
            self.fill_borders_in_space_matrix(matrix_corners[j], matrix_corners[(j + 1) % num_of_corners])

        self.inside_cubes_matrix = self.find_enclosed_space(self.space_matrix)

        rows = len(self.inside_cubes_matrix)
        cols = len(self.inside_cubes_matrix[0])

        counter = self._wall_segment_id
        for i in range(rows):
            for j in range(cols):
                if self.inside_cubes_matrix[i][j] == 3:
                    self._stage.DefinePrim(self._warehouse_prim.GetPath().AppendPath(f"inside_tile_{counter}"), "Xform")
                    counter = counter + 1

        with Sdf.ChangeBlock():
            for i in range(rows):
                for j in range(cols):
                    if self.inside_cubes_matrix[i][j] == 3:
                        x = x_min + (i * self.tile_dimension)
                        y = y_min + ((j + 1) * self.tile_dimension)
                        self._wallXform = UsdGeom.Xform(
                            self._stage.GetPrimAtPath(
                                self._warehouse_prim.GetPath().AppendPath(f"inside_tile_{self._wall_segment_id}")
                            )
                        )
                        set_pose(self._wallXform, np.array([x, y, 0]), [0.0, 0.0, 0])
                        self._wallXform.GetPrim().GetReferences().AddReference(self.center_tile_asset)
                        # add_reference_to_stage(usd_path=self.center_tile_asset, prim_path=f"/inside_tile_{self._wall_segment_id}")
                        # self._world.scene.add(XFormPrim(prim_path=f"/inside_tile_{self._wall_segment_id}", name=f"/inside_tile_{self._wall_segment_id}"))
                        # self._insideTileXform = self._world.scene.get_object(name=f"/inside_tile_{self._wall_segment_id}")
                        # self._insideTileXform.set_world_pose(position=np.array([x,y,0]), orientation=np.array([SQRT2_2, 0.0, 0.0, SQRT2_2]))
                        # self._insideTileXform.set_default_state(position=np.array([x,y,0]), orientation=np.array([SQRT2_2, 0.0, 0.0, SQRT2_2]))
                        self._wall_segment_id = self._wall_segment_id + 1

            # print(matrix_paths)

            # refs = wh_floorplan_parent.CreateRelationship("space_matrix_map", True)
            # paths_list = matrix_paths.flatten().tolist()
            # counter = 0
            # for p in paths_list:
            #     if p:
            #         refs.AddTarget(p)
            #     else:
            #         refs.AddTarget(Sdf.Path(f"None_{counter}"))
            #         counter +=1

            # a = wh_floorplan_parent.GetRelationship("space_matrix_map").GetTargets()
            # new_matrix = np.array(a)
            # new_matrix = new_matrix.reshape(x_height, y_width)
            # print(matrix_paths)
            # print(new_matrix)

        self.set_matrix_indices()
        # print(get_warehouse_matrix(self._warehouse_prim.GetPrim()))
        get_column_map(self._warehouse_prim.GetPrim())

    def set_matrix_indices(self):

        wh_floorplan_parent = self._warehouse_prim.GetPrim()
        x_min = wh_floorplan_parent.GetAttribute(WAREHOUSE_X_EXTENT).Get()[0]
        y_min = wh_floorplan_parent.GetAttribute(WAREHOUSE_Y_EXTENT).Get()[0]
        children = [c for c in wh_floorplan_parent.GetChildren() if omni.usd.get_composed_references_from_prim(c)]
        segment_id = 0
        for wh_floorplan_asset in children:
            path = wh_floorplan_asset.GetPath()
            transform = omni.usd.get_local_transform_matrix(wh_floorplan_asset)
            position = transform.ExtractTranslation()
            offsets = self.get_deltas_for_mapping(path=path)
            idx_list = []
            for offset in offsets:
                dx = offset[0]
                dy = offset[1]
                x, y = int(round((position[0] - x_min) / self.tile_dimension + dx)), int(
                    round((position[1] - y_min) / self.tile_dimension + dy)
                )
                # matrix_paths[x][y] = path
                idx_list.append(Gf.Vec2i(x, y))
            if idx_list:
                idxs = wh_floorplan_asset.CreateAttribute(WAREHOUSE_IDX, Sdf.ValueTypeNames.Int2Array, True)
                idxs.Set(idx_list)
            segment_id = segment_id + 1

    def get_deltas_for_mapping(self, path):
        # path_string = str(path)
        prim = self._stage.GetPrimAtPath(path)
        rel, _ = omni.usd.get_composed_references_from_prim(prim)[0]
        asset_name = rel.assetPath
        slash_index = asset_name.rfind("/")
        asset_name = asset_name[slash_index + 1 :]
        r = get_local_transform_matrix(prim).ExtractRotation()
        rotation = int(round(r.GetAxis()[2] * r.GetAngle())) % 360
        offsets = [a[rotation] for a in self.fill_map[asset_name]]
        return offsets

    def fill_borders_in_space_matrix(self, pointa, pointb):
        # Compute the differences between the start and end points
        x0, y0 = pointa
        x1, y1 = pointb
        dx = 1 if x1 > x0 else -1 if x1 < x0 else 0
        dy = 1 if y1 > y0 else -1 if y1 < y0 else 0
        length_x = abs(x1 - x0)
        length_y = abs(y1 - y0)
        # Iterate over the line points and set the corresponding positions in the matrix to 1
        for _ in range(max(length_x, length_y)):
            # Set the current point in the matrix to 1
            self.space_matrix[x0][y0] = 1
            # Move to the next point along the line
            if length_x != 0:
                x0 += dx
            elif length_y != 0:
                y0 += dy

    def find_enclosed_space(self, matrix):
        rows, cols = matrix.shape
        matrix_copy = np.copy(matrix)

        stack = []
        # Iterate over the first and last row
        for i in range(cols):
            if matrix_copy[0, i] == 0:
                stack.append((0, i))
            if matrix_copy[rows - 1, i] == 0:
                stack.append((rows - 1, i))

        # Iterate over the first and last column (excluding corners already covered)
        for i in range(1, rows - 1):
            if matrix_copy[i, 0] == 0:
                stack.append((i, 0))
            if matrix_copy[i, cols - 1] == 0:
                stack.append((i, cols - 1))

        while stack:
            x, y = stack.pop()
            matrix_copy[x, y] = 2

            # Check adjacent cells
            if x > 0 and matrix_copy[x - 1, y] == 0:
                stack.append((x - 1, y))
            if x < rows - 1 and matrix_copy[x + 1, y] == 0:
                stack.append((x + 1, y))
            if y > 0 and matrix_copy[x, y - 1] == 0:
                stack.append((x, y - 1))
            if y < cols - 1 and matrix_copy[x, y + 1] == 0:
                stack.append((x, y + 1))

        # Overlap borders and center tiles and 0 outside areas
        matrix_copy = np.where(matrix_copy == 0, 3, matrix_copy)
        matrix_copy = np.where(matrix_copy == 2, 0, matrix_copy)

        return matrix_copy
