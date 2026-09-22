import omni.usd
from omni.kit import ui_test
from omni.kit.test_suite.helpers import arrange_windows
from omni.kit.window.content_browser.test_helper import ContentBrowserTestHelper

from .test_base import MaterialPropertiesTestBase
from .utils import time_logger


@time_logger
class TestDragDropMDLFile(MaterialPropertiesTestBase):
    async def setUp(self):
        await super().setUp()
        await arrange_windows()  # docks all windows so they aren't overlapping each other
        await ui_test.find("Stage").focus()
        await ui_test.find("Content").focus()

        # create prims
        omni.kit.commands.execute("CreatePrimWithDefaultXform", prim_type="Sphere")
        await self._select_prims(["/Sphere"])
        self._prim = self._get_prim_at_path("/Sphere")

        self._mdl_file_path = self._get_mdl_path("TESTEXPORT.mdl")

    async def test_drag_drop_single_mdl_file_target(self):
        # drag/drop
        async with ContentBrowserTestHelper() as content_browser_helper:
            property_widget = ui_test.find("Property//Frame/**/Button[*].identifier=='preview_drop_target'")
            await content_browser_helper.drag_and_drop_tree_view(
                self._mdl_file_path, drag_target=property_widget.center
            )

        # verify - TESTEXPORT should be bound
        # NOTE: TESTEXPORT.mdl material is named "Material" so that is the prim created
        mat, _ = self._get_bound_material(self._prim)
        self.assertEqual(mat.GetPrim().GetPrimPath().pathString, "/Looks/Material")

    async def test_drag_drop_multi_mdl_file_target(self):
        # drag/drop
        async with ContentBrowserTestHelper() as content_browser_helper:
            property_widget = ui_test.find("Property//Frame/**/Button[*].identifier=='preview_drop_target'")
            await content_browser_helper.drag_and_drop_tree_view(
                str(self._mdl_dir),
                names=["TESTEXPORT.mdl", "TESTEXPORT2.mdl"],
                drag_target=property_widget.center,
                focus_treeview_items=False,
            )

        # verify - nothing should be bound as 2 items where selected
        self._get_bound_material(self._prim, False)

    async def test_drag_drop_single_mdl_file_combo(self):
        # drag/drop
        async with ContentBrowserTestHelper() as content_browser_helper:
            property_widget = ui_test.find("Property//Frame/**/StringField[*].identifier=='combo_drop_target'")
            await content_browser_helper.drag_and_drop_tree_view(
                self._mdl_file_path, drag_target=property_widget.center
            )

        # verify - TESTEXPORT should be bound
        # NOTE: TESTEXPORT.mdl material is named "Material" so that is the prim created
        mat, _ = self._get_bound_material(self._prim)
        self.assertEqual(mat.GetPrim().GetPrimPath().pathString, "/Looks/Material")

    async def test_drag_drop_multi_mdl_file_combo(self):
        # drag/drop
        async with ContentBrowserTestHelper() as content_browser_helper:
            property_widget = ui_test.find("Property//Frame/**/StringField[*].identifier=='combo_drop_target'")
            await content_browser_helper.drag_and_drop_tree_view(
                str(self._mdl_dir),
                names=["TESTEXPORT.mdl", "TESTEXPORT2.mdl"],
                drag_target=property_widget.center,
                focus_treeview_items=False,
            )

        # verify - nothing should be bound as 2 items where selected
        self._get_bound_material(self._prim, False)
