# Copyright (c) 2024-2025, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from pathlib import Path
import carb
from omni.kit.test.async_unittest import AsyncTestCase
import omni.usd
from pxr import Usd

# Those imports only available when "omni.kit.test_suite.helpers" is included, which is not the case for NO GPU test.
try:
    from omni.kit.test_suite.helpers import wait_stage_loading, arrange_windows
except ImportError:
    pass


class TestSelection(AsyncTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._settings = carb.settings.get_settings()

    async def setUp(self):
        await arrange_windows()
        self._context = omni.usd.get_context()
        self._settings.set("/persistent/app/viewport/pickingMode", "type:ALL")
        self._settings.set("/persistent/app/viewport/pickingModeNoKinds", False)
        self._settings.set("/persistent/app/viewport/pickingModeIncludeRef", False)
        self._selection = self._context.get_selection()

    async def tearDown(self):
        await self._context.close_stage_async()
        self._settings.set("/persistent/app/viewport/pickingMode", "type:ALL")
        self._settings.set("/persistent/app/viewport/pickingModeNoKinds", True)
        self._settings.set("/persistent/app/viewport/pickingModeIncludeRef", True)

    async def open_scene(self, test_scene: str = None):
        if not test_scene:
            test_scene = str(Path(__file__).parent.joinpath("data").joinpath("test_selection.usda"))

        result, err = await omni.usd.get_context().open_stage_async(test_scene, omni.usd.UsdContextInitialLoadSet.LOAD_ALL)
        self.assertTrue(result)
        await wait_stage_loading()
        self._stage = self._context.get_stage()
        self._all_prims = []
        for prim in self._stage.Traverse():
            self._all_prims.append(prim.GetPath().pathString)

    async def select_all_prims(self, single_call: bool = False):
        self._selection.clear_selected_prim_paths()
        if not single_call:
            for prim_path in self._all_prims:
                self._selection.set_prim_path_selected(prim_path, True, False, False)
        else:
            self._selection.set_selected_prim_paths(self._all_prims, type_kind_filtering=True)
        await self._context.selection_changed_async()

    def validate_selection(self, allowed_kinds = [], allowed_types = [], expected_paths = None, exclusive = True):
        selected_prim_paths = self._selection.get_selected_prim_paths()
        if exclusive:
            if allowed_kinds:
                for prim_path in selected_prim_paths:
                    kind = Usd.ModelAPI(self._stage.GetPrimAtPath(prim_path)).GetKind()
                    self.assertIn(kind, allowed_kinds, f"Prim {prim_path} has kind {kind}, which is not in the allowed kinds: {allowed_kinds}")
            if allowed_types:
                for prim_path in selected_prim_paths:
                    type_name = self._stage.GetPrimAtPath(prim_path).GetTypeName()
                    self.assertIn(type_name, allowed_types, f"Prim {prim_path} has type {type_name}, which is not in the allowed types: {allowed_types}")
        else:
            for prim_path in selected_prim_paths:
                prim = self._stage.GetPrimAtPath(prim_path)
                kind = Usd.ModelAPI(prim).GetKind()
                type_name = prim.GetPrimAtPath(prim_path).GetTypeName()
                if not kind:
                    valid = type_name in allowed_types
                else:
                    valid = kind in allowed_kinds or type_name in allowed_types
                self.assertTrue(valid,
                    f"Prim {prim_path} has kind {kind} and type {type_name}, which is not in the allowed kinds: {allowed_kinds} or allowed types: {allowed_types}")

        if expected_paths:
            self.assertSetEqual(set(selected_prim_paths), expected_paths)

        for prim_path in self._all_prims:
            if prim_path in selected_prim_paths:
                continue
            prim = self._stage.GetPrimAtPath(prim_path)
            kind = Usd.ModelAPI(prim).GetKind()
            type_name = prim.GetPrimAtPath(prim_path).GetTypeName()
            if allowed_kinds:
                self.assertNotIn(kind, allowed_kinds, f"Prim {prim_path} has kind {kind}, which should be selected")
            if allowed_types:
                self.assertNotIn(type_name, allowed_types, f"Prim {prim_path} has type {type_name}, which should be selected")

    async def test_selection(self):
        # The default USD kinds have this hierarchy :
        # model
        #     component
        #     group
        #         assembly
        # subcomponent

        await self.open_scene()

        tests = [
            # By type selections
            ("type:Mesh", (
                [], ["Mesh"],
                {"/World/Cube", "/World/Plane", "/World/Xform/Torus", "/World/Scope/Xform/Disk"},
                True
            )),
            ("type:CylinderLight;type:DistantLight", (
                [], ["CylinderLight", "DistantLight"],
                {"/Environment/defaultLight", "/World/CylinderLight"},
                True
            )),
            ("type:Camera", (
                [], ["Camera"],
                {"/World/Camera"},
                True
            )),

            # By kind selections
            ("kind:model.ALL", (
                ["group", "component", "assembly"], [],
                {"/World/group", "/World/component", "/World/assembly"},
                True
            )),
            ("kind:assembly", (
                ["assembly"], [],
                {"/World/assembly"},
                True
            )),
            ("kind:group", (
                ["group"], [],
                {"/World/group"},
                True
            )),
            ("kind:component", (
                ["component"], [],
                {"/World/component"},
                True
            )),
            ("kind:subcomponent", (
                ["subcomponent"], [],
                {"/World/subcomponent"},
                True
            )),

            # Custom selections
            ("type:Camera;kind:subcomponent", (
                ["subcomponent"], ["Camera"],
                {"/World/Camera", "/World/subcomponent"},
                False
            )),
        ]

        for filter, data in tests:
            self._settings.set("/persistent/app/viewport/pickingMode", filter)
            await self.select_all_prims()
            self.validate_selection(*data)
            await self.select_all_prims(True)
            self.validate_selection(*data)

    async def test_include_ref(self):
        await self.open_scene()

        self._settings.set("/persistent/app/viewport/pickingMode", "type:Mesh")
        self._settings.set("/persistent/app/viewport/pickingModeIncludeRef", True)
        expected_selection = {'/World/Cube', '/World/Plane', '/World/Xform/Torus', '/World/Scope/Xform/Disk'}

        await self.select_all_prims()
        self.validate_selection(None, ["Mesh"], expected_selection)
        await self.select_all_prims(True)
        self.validate_selection(None, ["Mesh"], expected_selection)

    async def test_include_no_kinds(self):
        await self.open_scene()

        self._settings.set("/persistent/app/viewport/pickingMode", "kind:group")
        self._settings.set("/persistent/app/viewport/pickingModeNoKinds", True)
        expected_selection = {'/World', '/World/Camera', '/World/Cube', '/World/CylinderLight', '/World/group', '/World/Plane', '/World/Xform', '/World/Xform/Torus', '/World/Scope', '/World/Scope/Xform', '/World/Scope/Xform/Disk', '/Environment', '/Environment/defaultLight'}

        await self.select_all_prims()
        self.validate_selection(["group", ""], None, expected_selection)
        await self.select_all_prims(True)
        self.validate_selection(["group", ""], None, expected_selection)
