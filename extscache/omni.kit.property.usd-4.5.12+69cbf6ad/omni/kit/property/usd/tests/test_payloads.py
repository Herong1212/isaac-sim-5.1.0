# pylint: disable=missing-function-docstring, missing-class-docstring
import carb
import omni.kit.test
import omni.usd
from omni.kit import ui_test
from omni.kit.test_suite.helpers import (
    arrange_windows,
    get_test_data_path,
    open_stage,
    select_prims,
    wait_stage_loading,
)
from omni.kit.window.content_browser.test_helper import ContentBrowserTestHelper
from omni.ui.tests.test_base import OmniUiTest
from pxr import Sdf


class TestDragDropFileToPayload(OmniUiTest):
    # Before running each test
    async def setUp(self):
        carb.settings.get_settings().set("/persistent/app/stage/dragDropImport", "payload")
        await arrange_windows("Stage", 200)
        await open_stage(get_test_data_path(__name__, "usd/reference_prim.usda"))
        await wait_stage_loading()

    # After running each test
    async def tearDown(self):
        carb.settings.get_settings().set("/persistent/app/stage/dragDropImport", "reference")
        await wait_stage_loading()

    async def test_drag_drop_single_usda_to_payload(self):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        await select_prims(["/World/XformPayload"])
        await wait_stage_loading()

        # verify refs are correct
        prim = stage.GetPrimAtPath("/World/XformPayload")
        ref_and_layers = omni.usd.get_composed_payloads_from_prim(prim)
        self.assertEqual(len(ref_and_layers), 1)
        self.assertEqual(ref_and_layers[0][0], Sdf.Payload("./cube.usda"))

        # drag & drop into payloads path
        for w in ui_test.find_all("Property//Frame/**/StringField[*]"):
            if w.widget.has_drop_fn() and w.model.get_value_as_string() == "./cube.usda":
                drag_target = w.center
                break

        async with ContentBrowserTestHelper() as content_browser_helper:
            await content_browser_helper.toggle_grid_view_async(show_grid_view=False)
            await ui_test.human_delay(50)
            usd_path = get_test_data_path(__name__, "usd/sphere.usda")
            await content_browser_helper.drag_and_drop_tree_view(
                usd_path, drag_target=drag_target, focus_treeview_items=False
            )

        # verify refs are correct
        prim = stage.GetPrimAtPath("/World/XformPayload")
        ref_and_layers = omni.usd.get_composed_payloads_from_prim(prim)
        self.assertEqual(len(ref_and_layers), 1)
        self.assertEqual(ref_and_layers[0][0], Sdf.Payload("./sphere.usda"))

    async def test_drag_drop_multi_usda_to_payload(self):
        # Test that drag and drop of multiple selections results in warning and no subsequent changes.
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        await select_prims(["/World/XformPayload"])
        await wait_stage_loading()

        # verify refs are correct
        prim = stage.GetPrimAtPath("/World/XformPayload")
        ref_and_layers = omni.usd.get_composed_payloads_from_prim(prim)
        self.assertEqual(len(ref_and_layers), 1)
        self.assertEqual(ref_and_layers[0][0], Sdf.Payload("./cube.usda"))

        # drag & drop into payloads path
        for w in ui_test.find_all("Property//Frame/**/StringField[*]"):
            if w.widget.has_drop_fn() and w.model.get_value_as_string() == "./cube.usda":
                drag_target = w.center
                break

        async with ContentBrowserTestHelper() as content_browser_helper:
            usd_path = get_test_data_path(__name__, "usd")
            await content_browser_helper.drag_and_drop_tree_view(
                usd_path,
                names=["locate_file_material.usda", "sphere.usda"],
                drag_target=drag_target,
                focus_treeview_items=False,
            )

        # Should result in warning and no changes
        prim = stage.GetPrimAtPath("/World/XformPayload")
        ref_and_layers = omni.usd.get_composed_payloads_from_prim(prim)
        self.assertEqual(len(ref_and_layers), 1)
        self.assertEqual(ref_and_layers[0][0], Sdf.Payload("./cube.usda"))
