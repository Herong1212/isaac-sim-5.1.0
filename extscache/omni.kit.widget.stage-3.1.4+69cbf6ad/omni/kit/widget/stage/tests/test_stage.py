## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
from pathlib import Path
from omni.kit.widget.stage import StageWidget, DefaultSelectionWatch
from omni.kit.widget.stage.stage_icons import StageIcons
from omni.ui.tests.test_base import OmniUiTest
from pxr import Usd, UsdGeom
from omni.kit import ui_test
from omni.kit.test_suite.helpers import (
    open_stage,
    get_test_data_path,
    get_prims,
    select_prims,
    wait_stage_loading,
    arrange_windows
    )
import omni.kit.app

CURRENT_PATH = Path(__file__).parent
REPO_PATH = CURRENT_PATH
for i in range(10):
    REPO_PATH = REPO_PATH.parent
BOWL_STAGE = REPO_PATH.joinpath("data/usd/tests/bowl.usd")
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.joinpath("data").joinpath("tests")

STYLE = {"Field": {"background_color": 0xFF24211F, "border_radius": 2}}


class TestStage(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        await arrange_windows(hide_viewport=True)
        self._golden_img_dir = TEST_DATA_PATH.absolute()
        # OM-122334: Since icon paths are not calculated at load time, here only remove icon paths for non-visibility
        #  releated icon paths
        for k in StageIcons()._icons:
            if not k.startswith('eye'):
                StageIcons()._icons[k] = ''

    # After running each test
    async def tearDown(self):
        await super().tearDown()
        # ASSET_LOADED never gets sent during tearDown so ignore
        await wait_stage_loading(timeout=100, timeout_error=False)

    async def test_general(self):
        """Testing general look of StageWidget"""
        window = await self.create_test_window()

        stage = Usd.Stage.Open(f"{BOWL_STAGE}")
        if not stage:
            self.fail(f"Stage {BOWL_STAGE} doesn't exist")
            return

        with window.frame:
            stage_widget = StageWidget(stage, style=STYLE)

        # 5 frames to rasterize the icons
        for _ in range(5):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_visibility(self):
        """Testing visibility of StageWidget"""
        window = await self.create_test_window()

        stage = Usd.Stage.CreateInMemory("test.usd")

        with window.frame:
            stage_widget = StageWidget(stage, style=STYLE)

        UsdGeom.Mesh.Define(stage, "/A")
        UsdGeom.Mesh.Define(stage, "/A/B")
        UsdGeom.Mesh.Define(stage, "/C").MakeInvisible()

        # 5 frames to rasterize the icons
        for _ in range(5):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_widget_selection(self):
        window = await self.create_test_window()

        stage = Usd.Stage.CreateInMemory("test.usd")

        with window.frame:
            stage_widget = StageWidget(stage, style=STYLE)
            selection = DefaultSelectionWatch()
            stage_widget.set_selection_watch(selection)

        xform_a = UsdGeom.Xform.Define(stage, "/A/B/C/D")
        xform_b = UsdGeom.Xform.Define(stage, "/E/B/C/D")

        # Wait one frame to be sure other objects created after initialization
        await omni.kit.app.get_app().next_update_async()

        stage_model = stage_widget.get_model()
        self.assertTrue(stage_model)

        # Creates and gets two items without expanding their parent
        item_a = stage_model._get_stage_item_from_cache(xform_a.GetPath(), True)
        item_b = stage_model._get_stage_item_from_cache(xform_b.GetPath(), True)

        # Selects the two items to ensure their parents are expanded
        stage_model.set_selected_stage_items([item_a, item_b])
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        selected_items = stage_widget._tree_view.selection
        self.assertEqual(set([item_a, item_b]), set(selected_items))

        stage.RemovePrim(xform_a.GetPath())
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        selected_items = stage_widget._tree_view.selection
        self.assertEqual(set([item_b]), set(selected_items))

        xform_a = UsdGeom.Xform.Define(stage, "/A/B/C/D")
        item_a = stage_model._get_stage_item_from_cache(xform_a.GetPath(), True)
        xform_a.GetPrim().SetActive(False)
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        stage_model.set_selected_stage_items([item_a, item_b])
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        # Item can still be selected even it's deactivated.
        selected_items = stage_widget._tree_view.selection
        self.assertEqual(set([item_a, item_b]), set(selected_items))

        await self.finalize_test_no_image()

    async def test_dynamic(self):
        """Testing the ability to watch the stage"""
        window = await self.create_test_window()

        stage = Usd.Stage.CreateInMemory("test.usd")

        with window.frame:
            stage_widget = StageWidget(stage, style=STYLE)

        UsdGeom.Mesh.Define(stage, "/A")

        # Wait one frame to be sure other objects created after initialization
        await omni.kit.app.get_app().next_update_async()

        UsdGeom.Mesh.Define(stage, "/B")
        mesh = UsdGeom.Mesh.Define(stage, "/C")

        # Wait one frame to be sure other objects created after initialization
        await omni.kit.app.get_app().next_update_async()

        mesh.MakeInvisible()
        UsdGeom.Mesh.Define(stage, "/D")

        # 5 frames to rasterize the icons
        for _ in range(5):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_instanceable(self):
        """Testing the ability to watch the instanceable state"""
        window = await self.create_test_window()

        stage = Usd.Stage.CreateInMemory("test.usd")

        with window.frame:
            stage_widget = StageWidget(stage, style=STYLE)

        UsdGeom.Xform.Define(stage, "/A")
        UsdGeom.Mesh.Define(stage, "/A/Shape")

        prim = UsdGeom.Xform.Define(stage, "/B").GetPrim()
        prim.GetReferences().AddInternalReference("/A")

        # Wait one frame to be sure other objects created after initialization
        await omni.kit.app.get_app().next_update_async()

        stage_widget.expand("/B")

        await omni.kit.app.get_app().next_update_async()

        prim.SetInstanceable(True)

        # 5 frames to rasterize the icons
        for _ in range(5):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test(golden_img_dir=self._golden_img_dir)


    async def test_stage_widget_without_selection(self):
        # OMPE-8698: No assert checks but to ensure it will not throw exceptions.
        stage = Usd.Stage.CreateInMemory("test.usd")
        stage_widget = StageWidget(stage, style=STYLE)

        stage_widget.open_stage(stage)

    async def test_root_selection(self):
        """Test clicking on root"""
        await arrange_windows()

        stage_window = ui_test.find("Stage")
        await stage_window.focus()
        root_visible = stage_window.window._stage_widget._tree_view.root_visible

        try:
            stage_window.window._stage_widget._tree_view.root_visible = True
            await open_stage(get_test_data_path(__name__, "4Lights.usda"))
            await wait_stage_loading()

            # select root - should be no errors
            stage_widget = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
            await stage_widget.find("**/Label[*].text=='Root:'").click()
        finally:
            stage_window.window._stage_widget._tree_view.root_visible = root_visible
