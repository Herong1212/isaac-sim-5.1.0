# pylint: disable=missing-function-docstring, missing-class-docstring, invalid-overridden-method
from unittest.mock import patch

import carb
import omni.kit.test
import omni.kit.ui_test as ui_test
import omni.usd
from omni import ui
from omni.kit.test_suite.helpers import (
    arrange_windows,
    get_test_data_path,
    open_stage,
    select_prims,
    wait_stage_loading,
)
from omni.kit.window.content_browser.test_helper import ContentBrowserTestHelper
from omni.kit.window.file_importer.test_helper import FileImporterTestHelper
from omni.ui.tests.test_base import OmniUiTest
from pxr import Sdf


class TestDragDropFileToReference(OmniUiTest):
    # Before running each test
    async def setUp(self):
        carb.settings.get_settings().set("/persistent/app/stage/dragDropImport", "reference")
        await arrange_windows("Stage", 200)

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()

    async def test_drag_drop_single_usda_to_reference(self):
        await open_stage(get_test_data_path(__name__, "usd/reference_prim.usda"))
        await wait_stage_loading()

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        await select_prims(["/World/XformReference"])
        await wait_stage_loading()

        # verify refs are correct
        prim = stage.GetPrimAtPath("/World/XformReference")
        ref_and_layers = omni.usd.get_composed_references_from_prim(prim)
        self.assertEqual(len(ref_and_layers), 1)
        self.assertEqual(ref_and_layers[0][0], Sdf.Reference("./cube.usda"))

        # drag from content window and drop into reference path
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
        prim = stage.GetPrimAtPath("/World/XformReference")
        ref_and_layers = omni.usd.get_composed_references_from_prim(prim)
        self.assertEqual(len(ref_and_layers), 1)
        self.assertEqual(ref_and_layers[0][0], Sdf.Reference("./sphere.usda"))

    async def test_drag_drop_multi_usda_to_reference(self):
        await open_stage(get_test_data_path(__name__, "usd/reference_prim.usda"))
        await wait_stage_loading()

        # Test that dropping multiple usd files results in no changes.
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        await select_prims(["/World/XformReference"])
        await wait_stage_loading()

        # verify refs are correct
        prim = stage.GetPrimAtPath("/World/XformReference")
        ref_and_layers = omni.usd.get_composed_references_from_prim(prim)
        self.assertEqual(len(ref_and_layers), 1)
        self.assertEqual(ref_and_layers[0][0], Sdf.Reference("./cube.usda"))

        # drag from content window and drop into reference path
        for w in ui_test.find_all("Property//Frame/**/StringField[*]"):
            if w.widget.has_drop_fn() and w.model.get_value_as_string() == "./cube.usda":
                drag_target = w.center
                break

        async with ContentBrowserTestHelper() as content_browser_helper:
            usd_path = get_test_data_path(__name__, "usd")
            await content_browser_helper.drag_and_drop_tree_view(
                usd_path,
                names=["sphere.usda", "locate_file_material.usda"],
                drag_target=drag_target,
                focus_treeview_items=False,
            )

        # verify refs are correct
        prim = stage.GetPrimAtPath("/World/XformReference")
        ref_and_layers = omni.usd.get_composed_references_from_prim(prim)
        self.assertEqual(len(ref_and_layers), 1)
        self.assertEqual(ref_and_layers[0][0], Sdf.Reference("./cube.usda"))


class TestAddReference(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._context = omni.usd.get_context()
        await arrange_windows("Stage", 200)
        await open_stage(get_test_data_path(__name__, "usd/reference_prim.usda"))
        await wait_stage_loading()

    async def tearDown(self):
        await wait_stage_loading()

    async def test_add_reference_single_selection(self):
        """Test that add reference with single selection works."""
        await open_stage(get_test_data_path(__name__, "usd/reference_prim.usda"))
        await wait_stage_loading()

        stage = self._context.get_stage()
        stage_window = ui_test.find("Stage")
        await stage_window.focus()

        prim_path = "/World/XformReference"
        # right click on a prim
        stage_widget = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        await stage_widget.find(f"**/StringField[*].model.path=='{prim_path}'").right_click()

        async with FileImporterTestHelper() as file_importer:
            await ui_test.select_context_menu("Add/Reference", offset=ui_test.Vec2(25, 10))
            await file_importer.wait_for_popup()
            usd_path = get_test_data_path(__name__, "usd/sphere.usda")
            await file_importer.click_apply_async(filename_url=usd_path)

        await ui_test.human_delay(10)

        # verify refs are correct
        prim = stage.GetPrimAtPath(prim_path)
        ref_and_layers = omni.usd.get_composed_references_from_prim(prim)
        self.assertEqual(len(ref_and_layers), 1)
        self.assertEqual(ref_and_layers[0][0], Sdf.Reference("./sphere.usda"))

        await select_prims(["/World/XformReference"])
        await ui_test.human_delay(10)
        reference_frame = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='References'")
        # sometimes reference frame is not refreshed immediately, so we need to check it to avoid flacky test failure
        if reference_frame:
            widget = reference_frame.find("**/StringField[*].identifier=='path_field'")
            self.assertEqual(widget.widget.style, None)

    async def test_add_reference_multi_selection(self):
        """Test that when selecting multiple files to reference, it adds only one file (the sorted last)."""
        await open_stage(get_test_data_path(__name__, "usd/reference_prim.usda"))
        await wait_stage_loading()

        stage = self._context.get_stage()
        stage_window = ui_test.find("Stage")
        await stage_window.focus()

        prim_path = "/World/XformReference"
        # right click on a prim
        stage_widget = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        await stage_widget.find(f"**/StringField[*].model.path=='{prim_path}'").right_click()

        async with FileImporterTestHelper() as file_importer:
            await ui_test.select_context_menu("Add/Reference", offset=ui_test.Vec2(25, 10))
            await file_importer.wait_for_popup()
            usd_path = get_test_data_path(__name__, "usd")
            await file_importer.select_items_async(usd_path, ["sphere.usda", "cube.usda", "types.usda"])
            await file_importer.click_apply_async()

        await ui_test.human_delay(10)

        # verify refs are correct
        prim = stage.GetPrimAtPath(prim_path)
        ref_and_layers = omni.usd.get_composed_references_from_prim(prim)
        self.assertEqual(len(ref_and_layers), 1)
        # should only add the sorted last file
        self.assertEqual(ref_and_layers[0][0], Sdf.Reference("./types.usda"))

    async def test_add_reference_blocks_invalid_file(self):
        """Test that when an invalid filepath is typed in, it will be blocked."""
        await open_stage(get_test_data_path(__name__, "usd/reference_prim.usda"))
        await wait_stage_loading()

        stage_window = ui_test.find("Stage")
        await stage_window.focus()

        prim_path = "/World/XformReference"
        # right click on a prim
        stage_widget = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        await stage_widget.find(f"**/StringField[*].model.path=='{prim_path}'").right_click()

        async with FileImporterTestHelper() as file_importer:
            await ui_test.select_context_menu("Add/Reference", offset=ui_test.Vec2(25, 10))
            await file_importer.wait_for_popup()
            usd_path = get_test_data_path(__name__, "usd")
            await file_importer.select_items_async(usd_path, [])
            await ui_test.human_delay()
            await file_importer.click_apply_async(filename_url=f"{usd_path}/random name")
            await ui_test.human_delay()
            # verify that file importer window is not closed
            self.assertTrue(ui.Workspace.get_window("Select Reference...").visible)
            await file_importer.click_cancel_async()

    async def test_large_references(self):
        """test that large number of references result in References frame being collapsed"""
        # load list of 10 references
        await open_stage(get_test_data_path(__name__, "usd_references/small_references.usda"))
        await wait_stage_loading()

        stage_window = ui_test.find("Stage")
        await stage_window.focus()

        await select_prims(["/World/XformReference"])
        await ui_test.human_delay(10)

        widget = ui_test.find("Property//Frame/**/CollapsableFrame[*].title == 'References'")
        self.assertTrue(widget)
        self.assertEqual(widget.widget.collapsed, False)

        # load list of ~55 references
        await open_stage(get_test_data_path(__name__, "usd_references/large_references.usda"))
        await wait_stage_loading()

        await select_prims(["/MY24_CAR"])
        await ui_test.human_delay(10)

        frame = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='References'")
        self.assertEqual(frame.widget.collapsed, True)
        frame.widget.collapsed = False
        await ui_test.human_delay(50)

        # verify cheese is red and others are white
        frames = frame.find_all("**/StringField[*].identifier!=''")
        self.assertGreater(len(frames), 50)
        for w in frames:
            text = w.model.get_value_as_string()
            if ".usd" not in text and text in ("/cheese", "/MY24_CAR"):
                self.assertEqual(w.widget.style, {"color": 4285494015})

    async def test_nested_payload(self):
        """test that nested payloads are handled correctly"""
        await open_stage(get_test_data_path(__name__, "usd_references/nested_payload/Scene.usda"))
        await wait_stage_loading()

        stage_window = ui_test.find("Stage")
        await stage_window.focus()

        await select_prims(["/World/Asset/Shape"])
        await ui_test.human_delay(10)

        frame = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Payloads'")
        frame.widget.collapsed = False
        await ui_test.human_delay(50)

        # verify cheese is red and others are white
        frames = frame.find_all("**/StringField[*].identifier!=''")
        for w in frames:
            text = w.model.get_value_as_string()
            if ".usd" not in text:
                self.assertEqual(w.widget.style, None)

    async def test_reference_local_file_in_non_local_layer(self):
        """test that reference of local file in non-local layer resolves correctly"""
        await open_stage(get_test_data_path(__name__, "usd/reference_prim.usda"))
        await wait_stage_loading()

        stage = self._context.get_stage()
        stage_window = ui_test.find("Stage")
        await stage_window.focus()

        prim_path = "/World/XformReference"
        # right click on a prim
        stage_widget = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        await stage_widget.find(f"**/StringField[*].model.path=='{prim_path}'").right_click()

        def mock_is_local_url(path: str):
            # Pretend that our stage is non-local
            if path.endswith("reference_prim.usda"):
                return False
            return True

        with patch("omni.client.is_local_url", side_effect=mock_is_local_url):
            usd_path = get_test_data_path(__name__, "usd/sphere.usda")
            async with FileImporterTestHelper() as file_importer:
                await ui_test.select_context_menu("Add/Reference", offset=ui_test.Vec2(25, 10))
                await file_importer.wait_for_popup()
                await file_importer.click_apply_async(filename_url=usd_path)

            await ui_test.human_delay(10)

            # verify refs are correct
            prim = stage.GetPrimAtPath(prim_path)
            ref_and_layers = omni.usd.get_composed_references_from_prim(prim)
            self.assertEqual(len(ref_and_layers), 1)
            local_file_path = omni.client.make_file_url_if_possible(usd_path)
            self.assertEqual(ref_and_layers[0][0], Sdf.Reference(local_file_path))
