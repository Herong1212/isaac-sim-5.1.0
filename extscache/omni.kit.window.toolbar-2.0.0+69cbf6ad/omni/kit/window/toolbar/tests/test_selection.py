# pylint: disable=missing-function-docstring, missing-class-docstring
import asyncio
import carb
import omni.kit.test
import omni.usd
import omni.ui as ui
from omni.kit import ui_test
from omni.ui.tests.test_base import OmniUiTest
from omni.kit.test_suite.helpers import open_stage, wait_stage_loading, get_test_data_path, get_prims

class TestSelectPrims(OmniUiTest):
    async def setUp(self):
        from omni.kit.widget.toolbar.tests.helpers import reset_toolbar_settings

        reset_toolbar_settings()

        self._main_dockspace = ui.Workspace.get_window("DockSpace")
        self._toolbar_handle = ui.Workspace.get_window(omni.kit.window.toolbar.Toolbar.WINDOW_NAME)
        self._toolbar_handle.undock()
        self._toolbar_handle.dock_in(self._main_dockspace, ui.DockPosition.LEFT)

        await self._arrange_windows()

        await open_stage(get_test_data_path(__name__, "prim_selection.usda"))
        await wait_stage_loading()

    # After running each test
    async def tearDown(self):
        from omni.kit.widget.toolbar.tests.helpers import reset_toolbar_settings

        reset_toolbar_settings()
        carb.settings.get_settings().set('/persistent/app/viewport/pickingModeNoKinds', True)

    async def _arrange_windows(self):
        """Arrange UI windows in the Omni UI environment.

        Returns:
            Window: The modified viewport window.
        """
        import omni.ui as ui
        from omni.kit.viewport.utility import get_active_viewport_window

        topleft_height = 850.0
        topleft_width = 436.0
        toolbar_width = 50

        viewport_window = get_active_viewport_window()
        # omni.ui & legacy viewport synch
        await ui_test.human_delay()
        if viewport_window:
            vp_width = int(1436 - topleft_width) - toolbar_width
            viewport_window.position_x = toolbar_width
            viewport_window.position_y = 0
            viewport_window.width = vp_width
            viewport_window.height = topleft_height
            viewport_window.visible = True

        ui.Workspace.show_window("Stage")
        stage_window = ui.Workspace.get_window("Stage")
        if stage_window:
            stage_window.position_x = 1436.0 - topleft_width
            stage_window.position_y = 0.0
            stage_window.width = topleft_width
            stage_window.height = topleft_height
            await ui_test.human_delay()

        # Wait for the layout to complete
        await ui_test.human_delay()
        return viewport_window

    async def _open_menu(self):
        widget = ui_test.find(f"{omni.kit.window.toolbar.Toolbar.WINDOW_NAME}//Frame/**/ToolButton[*].identifier=='all_prim_types'")
        await widget.click(right_click=True)
        await ui_test.human_delay(10)

    async def _select_prims(self):
        selection = omni.usd.get_context().get_selection()
        stage = omni.usd.get_context().get_stage()
        prim_list = [prim.GetPath().pathString for prim in get_prims(stage) if not omni.usd.is_hidden_type(prim)]
        selection.set_selected_prim_paths(prim_list, False, type_kind_filtering=True)

    async def test_select_prims_all_prim_types(self):
        # open menu & select menu item
        await self._open_menu()
        await ui_test.select_context_menu("All Prim Types", offset=ui_test.Vec2(10, 10))
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(500, 500))

        # select prims
        await self._select_prims()

        selection = omni.usd.get_context().get_selection()
        prim_list = sorted(selection.get_selected_prim_paths())

        # verify selection
        self.assertEqual(prim_list, ['/World', '/World/Camera', '/World/CompTest', '/World/CompTest/Cone', '/World/Cylinder', '/World/CylinderLight', '/World/Group_A', '/World/Group_A/Group_A_Component', '/World/RectLight', '/World/Sphere', '/World/Unselectable', '/World/Unselectable/Xform', '/World/defaultLight'])

    async def test_select_prims_meshes(self):
        # open menu & select menu item
        await self._open_menu()
        await ui_test.select_context_menu("Meshes", offset=ui_test.Vec2(10, 10))
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(500, 500))

        # select prims
        await self._select_prims()

        selection = omni.usd.get_context().get_selection()
        prim_list = sorted(selection.get_selected_prim_paths())

        # verify selection
        self.assertEqual(prim_list, ['/World/CompTest/Cone', '/World/Cylinder'])

    async def test_select_prims_lights(self):
        # open menu & select menu item
        await self._open_menu()
        await ui_test.select_context_menu("Lights", offset=ui_test.Vec2(10, 10))
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(500, 500))

        # select prims
        await self._select_prims()

        selection = omni.usd.get_context().get_selection()
        prim_list = sorted(selection.get_selected_prim_paths())

        # verify selection
        self.assertEqual(prim_list, ['/World/CylinderLight', '/World/RectLight', '/World/defaultLight'])

    async def test_select_prims_camera(self):
        # open menu & select menu item
        await self._open_menu()
        await ui_test.select_context_menu("Camera", offset=ui_test.Vec2(10, 10))
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(500, 500))

        # select prims
        await self._select_prims()

        selection = omni.usd.get_context().get_selection()
        prim_list = sorted(selection.get_selected_prim_paths())

        # verify selection
        self.assertEqual(prim_list, ['/World/Camera'])

    async def test_select_prims_all_model_kinds(self):
        # open menu & select menu item
        await self._open_menu()
        await ui_test.select_context_menu("All Model Kinds", offset=ui_test.Vec2(10, 10))
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(500, 500))

        carb.settings.get_settings().set('/persistent/app/viewport/pickingModeNoKinds', True)

        # select prims
        await self._select_prims()

        selection = omni.usd.get_context().get_selection()
        prim_list = sorted(selection.get_selected_prim_paths())

        # verify selection
        self.assertEqual(prim_list, ['/World', '/World/CompTest', '/World/Cylinder', '/World/CylinderLight', '/World/Group_A', '/World/Group_A/Group_A_Component', '/World/RectLight', '/World/Sphere', '/World/Unselectable', '/World/Unselectable/Xform', '/World/defaultLight'])

        ## and again...
        carb.settings.get_settings().set('/persistent/app/viewport/pickingModeNoKinds', False)

        # select prims
        await self._select_prims()

        selection = omni.usd.get_context().get_selection()
        prim_list = sorted(selection.get_selected_prim_paths())

        # verify selection
        self.assertEqual(prim_list, ['/World/CompTest', '/World/Cylinder', '/World/CylinderLight', '/World/Group_A', '/World/Group_A/Group_A_Component', '/World/RectLight'])

    async def test_select_prims_assembly_kinds(self):
        # open menu & select menu item
        await self._open_menu()
        await ui_test.select_context_menu("Assembly", offset=ui_test.Vec2(10, 10))
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(500, 500))

        carb.settings.get_settings().set('/persistent/app/viewport/pickingModeNoKinds', True)

        # select prims
        await self._select_prims()

        selection = omni.usd.get_context().get_selection()
        prim_list = sorted(selection.get_selected_prim_paths())

        # verify selection
        self.assertEqual(prim_list, ['/World', '/World/Cylinder', '/World/Sphere', '/World/Unselectable', '/World/Unselectable/Xform', '/World/defaultLight'])

        ## and again...
        carb.settings.get_settings().set('/persistent/app/viewport/pickingModeNoKinds', False)

        # select prims
        await self._select_prims()

        selection = omni.usd.get_context().get_selection()
        prim_list = sorted(selection.get_selected_prim_paths())

        # verify selection
        self.assertEqual(prim_list, ['/World/Cylinder'])

    async def test_select_prims_group_kinds(self):
        # open menu & select menu item
        await self._open_menu()
        await ui_test.select_context_menu("Group", offset=ui_test.Vec2(10, 10))
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(500, 500))

        carb.settings.get_settings().set('/persistent/app/viewport/pickingModeNoKinds', True)

        # select prims
        await self._select_prims()

        selection = omni.usd.get_context().get_selection()
        prim_list = sorted(selection.get_selected_prim_paths())

        # verify selection
        self.assertEqual(prim_list, ['/World', '/World/Group_A', '/World/RectLight', '/World/Sphere', '/World/Unselectable', '/World/Unselectable/Xform', '/World/defaultLight'])

        ## and again...
        carb.settings.get_settings().set('/persistent/app/viewport/pickingModeNoKinds', False)

        # select prims
        await self._select_prims()

        selection = omni.usd.get_context().get_selection()
        prim_list = sorted(selection.get_selected_prim_paths())

        # verify selection
        self.assertEqual(prim_list, ['/World/Group_A', '/World/RectLight'])

    async def test_select_prims_component_kinds(self):
        # open menu & select menu item
        await self._open_menu()
        await ui_test.select_context_menu("Component", offset=ui_test.Vec2(10, 10))
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(500, 500))

        carb.settings.get_settings().set('/persistent/app/viewport/pickingModeNoKinds', True)

        # select prims
        await self._select_prims()

        selection = omni.usd.get_context().get_selection()
        prim_list = sorted(selection.get_selected_prim_paths())

        # verify selection
        self.assertEqual(prim_list, ['/World', '/World/CompTest', '/World/CylinderLight', '/World/Group_A/Group_A_Component', '/World/Sphere', '/World/Unselectable', '/World/Unselectable/Xform', '/World/defaultLight'])

        ## and again...
        carb.settings.get_settings().set('/persistent/app/viewport/pickingModeNoKinds', False)

        # select prims
        await self._select_prims()

        selection = omni.usd.get_context().get_selection()
        prim_list = sorted(selection.get_selected_prim_paths())

        # verify selection
        self.assertEqual(prim_list, ['/World/CompTest', '/World/CylinderLight', '/World/Group_A/Group_A_Component'])

    async def test_select_prims_subcomponent_kinds(self):
        # open menu & select menu item
        await self._open_menu()
        await ui_test.select_context_menu("Subcomponent", offset=ui_test.Vec2(10, 10))
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(500, 500))

        carb.settings.get_settings().set('/persistent/app/viewport/pickingModeNoKinds', True)

        # select prims
        await self._select_prims()

        selection = omni.usd.get_context().get_selection()
        prim_list = sorted(selection.get_selected_prim_paths())

        # verify selection
        self.assertEqual(prim_list, ['/World', '/World/Camera', '/World/CompTest/Cone', '/World/Sphere', '/World/Unselectable', '/World/Unselectable/Xform', '/World/defaultLight'])

        ## and again...
        carb.settings.get_settings().set('/persistent/app/viewport/pickingModeNoKinds', False)

        # select prims
        await self._select_prims()

        selection = omni.usd.get_context().get_selection()
        prim_list = sorted(selection.get_selected_prim_paths())

        # verify selection
        self.assertEqual(prim_list, ['/World/Camera', '/World/CompTest/Cone'])
