# pylint: disable=missing-function-docstring, missing-class-docstring
import asyncio
import carb
import omni.kit.test
import omni.usd
import omni.ui as ui
from omni.kit import ui_test
from omni.kit.test_suite.helpers import arrange_windows
from omni.ui.tests.test_base import OmniUiTest


class SelectOccludedObjectstest(OmniUiTest):
    async def setUp(self):
        self._main_dockspace = ui.Workspace.get_window("DockSpace")
        self._toolbar_handle = ui.Workspace.get_window(omni.kit.window.toolbar.Toolbar.WINDOW_NAME)
        self._toolbar_handle.undock()
        self._toolbar_handle.dock_in(self._main_dockspace, ui.DockPosition.LEFT)

    # After running each test
    async def tearDown(self):
        pass

    async def test_select_occluded_objects(self):
        settings = carb.settings.get_settings()
        settings.set("/persistent/app/viewport/pickOccluded", False)

        async def open_menu():
            await ui_test.find(f"{omni.kit.window.toolbar.Toolbar.WINDOW_NAME}//Frame/**/ToolButton[*].identifier=='select_op_prims'").click(right_click=True)
            await ui_test.human_delay(10)

        self.assertEqual(settings.get_as_bool("/persistent/app/viewport/pickOccluded"), False)
        self.assertEqual(settings.get_as_bool("/rtx/raytracing/picking/occluded/enabled"), False)

        await open_menu()
        await ui_test.select_context_menu("Area Select Occluded Objects", offset=ui_test.Vec2(10, 10))
        self.assertEqual(settings.get_as_bool("/persistent/app/viewport/pickOccluded"), True)
        self.assertEqual(settings.get_as_bool("/rtx/raytracing/picking/occluded/enabled"), True)

        await open_menu()
        await ui_test.select_context_menu("Area Select Occluded Objects", offset=ui_test.Vec2(10, 10))
        self.assertEqual(settings.get_as_bool("/persistent/app/viewport/pickOccluded"), False)
        self.assertEqual(settings.get_as_bool("/rtx/raytracing/picking/occluded/enabled"), False)

        await open_menu()
        await ui_test.select_context_menu("Area Select Occluded Objects", offset=ui_test.Vec2(10, 10))
        self.assertEqual(settings.get_as_bool("/persistent/app/viewport/pickOccluded"), True)
        self.assertEqual(settings.get_as_bool("/rtx/raytracing/picking/occluded/enabled"), True)

        # click "reset all" but cannot access button directly
        from omni.kit.ui_test import emulate_mouse_move_and_click

        await open_menu()
        await ui_test.human_delay(10)
        window = ui_test.find(f"{omni.kit.window.toolbar.Toolbar.WINDOW_NAME}")
        await emulate_mouse_move_and_click(ui_test.Vec2(window.position.x+(window.size.x-50), window.position.y+30))
        await ui_test.human_delay(10)

        self.assertEqual(settings.get_as_bool("/persistent/app/viewport/pickOccluded"), False)
        self.assertEqual(settings.get_as_bool("/rtx/raytracing/picking/occluded/enabled"), False)

        await emulate_mouse_move_and_click(ui_test.Vec2(470, 470))
