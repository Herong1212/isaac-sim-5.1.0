# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from typing import List, Union

from omni.kit.manipulator.prim.core import PrimTransformManipulator
from omni.kit.manipulator.transform import get_default_style
from omni.kit.manipulator.transform import Constants as transform_c
from omni.kit.viewport.registry import RegisterScene
from pxr import Sdf, Usd, UsdGeom


# Creates a test manipulator that is white and half in size when selecting a mesh
class PrimTransformManipulatorMeshTest(PrimTransformManipulator):
    def __init__(self, usd_context_name: str = "", viewport_api=None):
        super().__init__(
            usd_context_name=usd_context_name,
            viewport_api=viewport_api,
            name="omni.kit.manipulator.test_mesh_prim",
            size=0.5,
        )

    def _create_local_global_styles(self):
        super()._create_local_global_styles()

        global_style = get_default_style()
        global_style["Translate.Axis::x"]["color"] = 0xFFFFFFFF
        global_style["Translate.Axis::y"]["color"] = 0xFFFFFFFF
        global_style["Translate.Axis::z"]["color"] = 0xFFFFFFFF

        self._styles[transform_c.TRANSFORM_MODE_GLOBAL] = global_style

    def on_selection_changed(self, stage: Usd.Stage, selection: Union[List[Sdf.Path], None], *args, **kwargs) -> bool:
        if selection is None:
            self.model.on_selection_changed([])
            return False

        self.model.on_selection_changed(selection)
        for path in selection:
            prim = stage.GetPrimAtPath(path)
            if prim.IsA(UsdGeom.Mesh):
                return True

        return False


class PrimTransformManipulatorScene:
    def __init__(self, desc: dict):
        usd_context_name = desc.get("usd_context_name")
        self.__transform_manip_override = PrimTransformManipulatorMeshTest(
            usd_context_name=usd_context_name, viewport_api=desc.get("viewport_api")
        )

    def destroy(self):
        if self.__transform_manip_override:
            self.__transform_manip_override.destroy()
            self.__transform_manip_override = None

    # PrimTransformManipulator & TransformManipulator don't have their own visibility
    @property
    def visible(self):
        return True

    @visible.setter
    def visible(self, value):
        pass

    @property
    def categories(self):
        return ("manipulator",)

    @property
    def name(self):
        return "Test Mesh Prim Transform"


class TransformManipulatorRegistry:
    def __init__(self):
        self._scene = RegisterScene(PrimTransformManipulatorScene, "omni.kit.manipulator.test_mesh_prim")

    def __del__(self):
        self.destroy()

    def destroy(self):
        self._scene = None
