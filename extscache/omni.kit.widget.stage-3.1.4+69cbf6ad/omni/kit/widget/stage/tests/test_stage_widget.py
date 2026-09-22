import carb
import omni
import omni.kit.test
import omni.usd
import omni.client
import omni.kit.widget.stage
import omni.kit.app
import omni.kit.ui_test as ui_test
import omni.ui as ui

from omni.kit.widget.stage import StageWidget, DefaultSelectionWatch
from omni.kit.test_suite.helpers import arrange_windows
from pxr import UsdGeom, Usd


class TestStageWidget(omni.kit.test.AsyncTestCase):

    async def setUp(self):
        self.app = omni.kit.app.get_app()
        await arrange_windows("Stage", 800, 600)

        self.usd_context = omni.usd.get_context()
        await self.usd_context.new_stage_async()
        self.stage = omni.usd.get_context().get_stage()

    async def tearDown(self):
        pass

    async def wait(self, frames=4):
        for i in range(frames):
            await self.app.next_update_async()

    async def test_visibility_toggle(self):
        stage_tree = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        prim = self.stage.DefinePrim("/prim0", "Xform")
        await self.wait()

        # In current test, 4 ToolButtons whose name is 'visibility' will be found.
        # Pick the first one for testing.
        prim_visibility_widget = stage_tree.find_all("**/ToolButton[*].name=='visibility'")[0]
        self.assertTrue(prim_visibility_widget)
        await prim_visibility_widget.click()
        await self.wait()
        self.assertEqual(UsdGeom.Imageable(prim).ComputeVisibility(), UsdGeom.Tokens.invisible)

        prim_visibility_widget = stage_tree.find_all("**/ToolButton[*].name=='visibility'")[0]
        self.assertTrue(prim_visibility_widget)
        await prim_visibility_widget.click()
        await self.wait()
        self.assertEqual(UsdGeom.Imageable(prim).ComputeVisibility(), UsdGeom.Tokens.inherited)

    async def test_search_widget(self):
        stage_tree = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        self.assertTrue(stage_tree)
        stage_model = stage_tree.widget.model

        search_field = ui_test.find("Stage//Frame/**/StringField[*].style_type_name_override=='SearchField'")
        self.assertTrue(search_field)

        prim1 = self.stage.DefinePrim("/prim", "Xform")
        prim2 = self.stage.DefinePrim("/prim/prim1", "Xform")
        prim3 = self.stage.DefinePrim("/prim/prim2", "Xform")
        prim4 = self.stage.DefinePrim("/other", "Xform")
        await self.wait()

        await search_field.input("prim")
        await ui_test.emulate_keyboard_press(carb.input.KeyboardInput.ENTER)
        await self.wait()
        all_children = stage_model.get_item_children(None)
        all_names = [child.name for child in all_children]
        search_field.widget.model.set_value("")
        await search_field.input("")
        await self.wait()
        await ui_test.emulate_keyboard_press(carb.input.KeyboardInput.ENTER)
        await self.wait()
        self.assertTrue(prim4.GetName() not in all_names)

    # OMPE-15459: Add test for update_filter_menu_state
    async def test_filter_update(self):
        window = ui.Window("test", position_x = 0, position_y = 0)
        with window.frame:
            widget = StageWidget(None, columns_enabled=["Type"])

        self.assertFalse(widget._filter_button._get_item("Meshes").value)
        widget.update_filter_menu_state([UsdGeom.Mesh])
        self.assertTrue(widget._filter_button._get_item("Meshes").value)

    # OMPE-16039: Test the filter audio works with no error
    async def test_filter_Audio(self):
        window = ui.Window("test", position_x = 0, position_y = 0)
        with window.frame:
            widget = StageWidget(None, columns_enabled=["Type"])
        window_ref = ui_test.WindowRef(window, "")
        filter_button = window_ref.find_first("**/Button[*].identifier=='filter'")
        await self.wait(frames=2)
        await filter_button.click()
        # select 'Audio' item should be no errors
        await ui_test.select_context_menu("Audio", human_delay_speed=1)
        await self.wait(frames=2)

    # OMPE-15720: Test the options reset works with no error
    async def test_options(self):
        window = ui.Window("test", position_x = 0, position_y = 0)
        with window.frame:
            widget = StageWidget(None, columns_enabled=["Type"])
        window_ref = ui_test.WindowRef(window, "")
        filter_button = window_ref.find_first("**/Button[*].identifier=='settings_icon'")
        await self.wait(frames=2)
        await filter_button.click()
        # select "Auto Reload Primitives" item and then select "Reset" item should be no errors
        await ui_test.select_context_menu("Auto Reload Primitives", human_delay_speed=1)
        await self.wait(frames=2)
        await ui_test.select_context_menu("Reset", human_delay_speed=1)
        await self.wait(frames=2)

    async def test_search_widget_newstage(self):
        stage_tree = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        self.assertTrue(stage_tree)
        stage_model = stage_tree.widget.model

        search_field = ui_test.find("Stage//Frame/**/StringField[*].style_type_name_override=='SearchField'")
        self.assertTrue(search_field)

        prim1 = self.stage.DefinePrim("/prim", "Xform")
        prim2 = self.stage.DefinePrim("/prim/prim1", "Xform")
        prim3 = self.stage.DefinePrim("/prim/prim2", "Xform")
        prim4 = self.stage.DefinePrim("/other", "Xform")
        await self.wait()

        await search_field.input("prim")
        await ui_test.emulate_keyboard_press(carb.input.KeyboardInput.ENTER)
        await self.wait()

        # search_field should be "prim"
        search_field = ui_test.find("Stage//Frame/**/StringField[*].style_type_name_override=='SearchField'")
        self.assertTrue(search_field)
        self.assertEqual(search_field.widget.model.get_value_as_string(), "prim")

        await self.usd_context.new_stage_async()
        await self.wait()

        # search_field should be "" as new stage cleared string
        search_field = ui_test.find("Stage//Frame/**/StringField[*].style_type_name_override=='SearchField'")
        self.assertTrue(search_field)
        self.assertEqual(search_field.widget.model.get_value_as_string(), "")
