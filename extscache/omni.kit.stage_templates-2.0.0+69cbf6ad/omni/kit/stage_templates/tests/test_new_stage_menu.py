import omni.kit.test
import carb
import omni.usd
import omni.ui as ui
from omni.kit.test_suite.helpers import StageEventHandler
from omni.kit import ui_test
from omni.kit.menu.utils import MenuItemDescription, MenuLayout


class TestMenuFile(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        # wait for material to be preloaded so create menu is complete & menus don't rebuild during tests
        await omni.kit.material.library.get_mdl_list_async()
        await ui_test.human_delay()

        self._stage_event_handler = StageEventHandler("omni.kit.stage_templates")

    async def tearDown(self):
        pass

    async def test_file_new_from_stage_template_empty(self):
        stage =  omni.usd.get_context().get_stage()
        layer_name =  stage.GetRootLayer().identifier if stage else "None"
        await self._stage_event_handler.reset_stage_event(omni.usd.StageEventType.OPENED)

        menu_widget = ui_test.get_menubar()
        await menu_widget.find_menu("File").click()
        await menu_widget.find_menu("New From Stage Template").click()

        # select empty and wait for stage open
        await menu_widget.find_menu("Empty").click()
        await self._stage_event_handler.wait_for_stage_event()

        # verify Empty stage
        stage =  omni.usd.get_context().get_stage()
        self.assertFalse(stage.GetRootLayer().identifier == layer_name)
        prim_list = [prim.GetPath().pathString for prim in stage.TraverseAll()]
        self.assertTrue(prim_list == ['/World'])


    async def test_file_new_from_stage_template_sunlight(self):
        stage =  omni.usd.get_context().get_stage()
        layer_name =  stage.GetRootLayer().identifier if stage else "None"
        await self._stage_event_handler.reset_stage_event(omni.usd.StageEventType.OPENED)

        menu_widget = ui_test.get_menubar()
        await menu_widget.find_menu("File").click()
        await menu_widget.find_menu("New From Stage Template").click()

        # select Sunlight and wait for stage open
        await menu_widget.find_menu("Sunlight").click()
        await self._stage_event_handler.wait_for_stage_event()

        # verify Sunlight stage
        stage =  omni.usd.get_context().get_stage()
        self.assertFalse(stage.GetRootLayer().identifier == layer_name)
        prim_list = [prim.GetPath().pathString for prim in stage.TraverseAll()]
        self.assertTrue(prim_list == ['/World', '/Environment', '/Environment/defaultLight'])
