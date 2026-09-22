import omni.usd
from omni.kit import ui_test
from omni.kit.test_suite.helpers import arrange_windows, wait_stage_loading
from omni.kit.window.content_browser.test_helper import ContentBrowserTestHelper
from pxr import UsdShade

from .test_base import MaterialPropertiesTestBase
from .utils import time_logger


@time_logger
class TestAddMDLFile(MaterialPropertiesTestBase):
    async def test_add_mdl_file(self):
        await arrange_windows()
        await ui_test.find("Stage").focus()
        await ui_test.find("Content").focus()

        mdl_path = self._get_mdl_path("TESTEXPORT.mdl")

        # create prims
        omni.kit.commands.execute("CreatePrimWithDefaultXform", prim_type="Sphere")
        await self._select_prims(["/Sphere"])

        # drag/drop
        async with ContentBrowserTestHelper() as content_browser_helper:
            property_widget = ui_test.find("Property//Frame/**/Button[*].identifier=='preview_drop_target'")
            await content_browser_helper.drag_and_drop_tree_view(
                str(mdl_path), drag_target=property_widget.center, focus_treeview_items=False
            )

        # wait for material to load & UI to refresh
        await wait_stage_loading()

        while True:
            await ui_test.human_delay(10)
            prim = self._stage.GetPrimAtPath("/Looks/Material/Shader")
            if prim.IsValid():
                await ui_test.human_delay(10)
                break

        # verify
        # NOTE: TESTEXPORT.mdl material is named "Material" so that is the prim created
        prim = self._stage.GetPrimAtPath("/Looks/Material/Shader")
        self.assertTrue(prim.IsValid())
        shader = UsdShade.Shader(prim)
        self.assertIsNotNone(shader)
        identifier = shader.GetSourceAssetSubIdentifier("mdl")
        self.assertTrue(identifier == "Material")
