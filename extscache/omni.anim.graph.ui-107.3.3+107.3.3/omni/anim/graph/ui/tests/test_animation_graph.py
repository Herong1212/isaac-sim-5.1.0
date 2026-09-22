import AnimGraphSchema
from pxr import UsdGeom, Sdf
import omni.kit.ui_test as ui_test
import omni.ui as ui
import omni.usd
from .base_ui_test import BaseUiTest
from ..scripts.extension import get_graph_manager, get_graph_window


class TestAnimationGraph(BaseUiTest):

    def _check_prim_valid(self, prim_name, valid=True):
        prim = self._stage.GetPrimAtPath(prim_name)
        if valid:
            self.assertTrue(prim.IsValid())
        else:
            self.assertFalse(prim.IsValid())

    async def _click_menu_create_animation_graph(self, menu_widget):
        await menu_widget.find_menu("Create").click()
        await ui_test.human_delay()
        await menu_widget.find_menu("Animation").click()
        await ui_test.human_delay()
        await menu_widget.find_menu("Animation Graph").click()
        await ui_test.human_delay()

    async def _create_anim_graph_setup(self):
        ui.Workspace.show_window("Property", True)
        await ui_test.find("Property").focus()

        await omni.usd.get_context().new_stage_async()
        self._stage = self._context.get_stage()
        menu_widget = ui_test.get_menubar()
        await self._click_menu_create_animation_graph(menu_widget)
        button = ui_test.find("Create Animation Graph//Frame/**/Button[*].text=='Create'")
        await button.click()
        await ui_test.human_delay(20)

    async def _create_and_destroy_node(self, node_type: str, graph, prefix = ""):
        created_node = graph.create_node(node_type, (0.0, 0.0))
        prim_path = Sdf.Path("/AnimationGraph/" + prefix + node_type)
        self._check_prim_valid(prim_path)
        found_node = graph.get_node(prim_path)
        self.assertEqual(created_node, found_node)
        await ui_test.human_delay(20)
        graph.delete_node(created_node)
        self._check_prim_valid(prim_path, False)
        await ui_test.human_delay()

    async def test_menu_create_animation_graph_with_cancel(self):
        await omni.usd.get_context().new_stage_async()
        self._stage = self._context.get_stage()
        menu_widget = ui_test.get_menubar()
        await self._click_menu_create_animation_graph(menu_widget)
        button = ui_test.find("Create Animation Graph//Frame/**/Button[*].text=='Cancel'")
        await button.click()
        await ui_test.human_delay(20)
        self._check_prim_valid("/AnimationGraph", False)

    async def test_menu_create_animation_graph_no_default_prim(self):
        await omni.usd.get_context().new_stage_async()
        self._stage = self._context.get_stage()
        menu_widget = ui_test.get_menubar()
        await self._click_menu_create_animation_graph(menu_widget)
        button = ui_test.find("Create Animation Graph//Frame/**/Button[*].text=='Create'")
        await button.click()
        await ui_test.human_delay(20)
        self._check_prim_valid("/AnimationGraph")

    async def test_menu_create_animation_graph_with_default_prim(self):
        await omni.usd.get_context().new_stage_async()
        self._stage = self._context.get_stage()
        world = UsdGeom.Xform.Define(self._stage, "/World").GetPrim()
        self._stage.SetDefaultPrim(world)
        menu_widget = ui_test.get_menubar()
        await self._click_menu_create_animation_graph(menu_widget)
        button = ui_test.find("Create Animation Graph//Frame/**/Button[*].text=='Create'")
        await button.click()
        await ui_test.human_delay(20)
        self._check_prim_valid("/World/AnimationGraph")

    # async def test_menu_create_animation_graph_change_path(self):
    #     await omni.usd.get_context().new_stage_async()
    #     self._stage = self._context.get_stage()
    #     world = UsdGeom.Xform.Define(self._stage, "/World").GetPrim()
    #     self._stage.SetDefaultPrim(world)
    #     menu_widget = ui_test.get_menubar()
    #     await self._click_menu_create_animation_graph(menu_widget)
    #     path_field = ui_test.find("Create Animation Graph//Frame/**/StringField[*].identifier=='animation_graph_path'")
    #     await path_field.click(double=True)
    #     await ui_test.emulate_keyboard_press(KeyboardInput.DEL)
    #     await ui_test.human_delay(20)
    #     await path_field.input("/World/Test")
    #     await ui_test.human_delay()
    #     button = ui_test.find("Create Animation Graph//Frame/**/Button[*].text=='Create'")
    #     await button.click()
    #     await ui_test.human_delay()
    #     prim = self._stage.GetPrimAtPath("/World/Test")
    #     self.assertTrue(prim.IsValid())

    async def test_apply_graph(self):
        # TODO: make the property window part of the overall setup. This helps view the Graph API
        ui.Workspace.show_window("Property", True)
        await ui_test.find("Property").focus()

        await self.load_stage(self.usd_data_dir, "TestApplyGraph.usda")
        self._stage = self._context.get_stage()

        stage_window = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        label = stage_window.find("**/Label[*].text=='TestSkeleton'")
        await label.right_click()
        await ui_test.human_delay(10)
        await ui_test.select_context_menu("Add/Animation/Animation Graph", None, ui_test.Vec2(10, 10))
        await ui_test.human_delay()

        select_window_treeview = ui_test.find("Select Animation Graph//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        graph_label = select_window_treeview.find("**/Label[*].text=='TestAnimationGraph'")
        await graph_label.click()
        await ui_test.human_delay(20)

        button = ui_test.find("Select Animation Graph//Frame/**/Button[*].text=='Select'")
        await button.click()
        await ui_test.human_delay(20)

        prim = self._stage.GetPrimAtPath("/World/TestSkeleton")
        self.assertTrue(prim.HasAPI(AnimGraphSchema.AnimationGraphAPI))

        anim_graph_api = AnimGraphSchema.AnimationGraphAPI(prim)
        rel = anim_graph_api.GetAnimationGraphRel()
        self.assertTrue(rel.GetTargets()[0] == "/World/TestAnimationGraph")

    async def test_create_animation_graph_blend_nodes(self):
        await self._create_anim_graph_setup()

        manager = get_graph_manager()

        graph = manager.get_node_graph("/AnimationGraph")
        self.assertTrue(graph)

        # Create blend nodes.
        await self._create_and_destroy_node("AnimationClip", graph)
        await self._create_and_destroy_node("Blend", graph)
        await self._create_and_destroy_node("LookAtIK", graph)
        await self._create_and_destroy_node("TwoBoneIK", graph)
        await self._create_and_destroy_node("Filter", graph)
        await self._create_and_destroy_node("PoseProvider", graph)

        # TODO: Would be nice to include some tests of the joint and clip properties
        await self._create_and_destroy_node("MotionMatching", graph)

    async def test_create_animation_graph_state_nodes(self):
        await self._create_anim_graph_setup()

        manager = get_graph_manager()

        graph = manager.get_node_graph("/AnimationGraph")
        self.assertTrue(graph)

        # Create a state machine, test the start node is created.
        state_machine_node = graph.create_node("StateMachine", (-100.0, 0.0))
        self._check_prim_valid("/AnimationGraph/StateMachine")
        self._check_prim_valid("/AnimationGraph/StateMachine/Start")
        await ui_test.human_delay(10)

        graph_window = get_graph_window()
        graph_widget = graph_window._main_widget
        graph_widget.set_current_compound(state_machine_node)
        await ui_test.human_delay(10)

        # Create additional states.
        state_machine = state_machine_node.sub_graph
        state_node = state_machine.create_node("State", (-100.0, 0.0))
        self._check_prim_valid("/AnimationGraph/StateMachine/State")
        state_01_node = state_machine.create_node("State", (100.0, 0.0))
        self._check_prim_valid("/AnimationGraph/StateMachine/State_01")
        await ui_test.human_delay(10)

        # Create a transition.
        state_machine.create_connection(state_node.output, state_01_node.input)

        # Test transition node types.
        transition = graph.search_node(Sdf.Path("/AnimationGraph/StateMachine/Transition"))[2]
        graph_widget.set_current_compound(transition)

        transition_graph = transition.sub_graph
        await self._create_and_destroy_node("ConditionCompareVariable", transition_graph, "StateMachine/Transition/")
        await self._create_and_destroy_node("ConditionTimeFractionCrossed", transition_graph, "StateMachine/Transition/")
        await self._create_and_destroy_node("ConditionSpeed", transition_graph, "StateMachine/Transition/")
        await self._create_and_destroy_node("ConditionAND", transition_graph, "StateMachine/Transition/")
        await self._create_and_destroy_node("ConditionOR", transition_graph, "StateMachine/Transition/")
        await ui_test.human_delay(10)

        graph_widget.set_current_compound(None)
        await ui_test.human_delay(10)

        graph.delete_node(state_machine_node)
        self._check_prim_valid("/AnimationGraph/StateMachine", False)

    async def test_create_animation_graph_variables(self):
        await self._create_anim_graph_setup()

        manager = get_graph_manager()

        graph = manager.get_node_graph("/AnimationGraph")
        self.assertTrue(graph)

        variables_tab = ui_test.find("Animation Graph//Frame/**/RadioButton[*].text=='Variables'")
        await variables_tab.click()
        await ui_test.human_delay()

        # Create a variable.
        # TODO: this should go through the UI click, but couldn't get it to work
        graph_window = get_graph_window()
        graph_widget = graph_window._main_widget
        graph_widget._create_variable(Sdf.ValueTypeNames.Float)
        await ui_test.human_delay(10)

        new_variable = ui_test.find("Animation Graph//Frame/**/Label[*].text=='NewVariable'")
        await new_variable.click()

        self.assertTrue(graph.has_variable("NewVariable"))
        self.assertTrue(graph.get_variable_type("NewVariable") == Sdf.ValueTypeNames.Float)

        # Rename the variable.
        graph.rename_variable("NewVariable", "RenamedVariable")
        await ui_test.human_delay(10)
        self.assertFalse(graph.has_variable("NewVariable"))
        self.assertTrue(graph.has_variable("RenamedVariable"))

        # Change the variable type.
        graph.change_variable_type("RenamedVariable", Sdf.ValueTypeNames.String)
        await ui_test.human_delay(10)
        self.assertTrue(graph.get_variable_type("RenamedVariable") == Sdf.ValueTypeNames.String)

        # Delete the variable.
        graph.delete_variable("RenamedVariable")
        await ui_test.human_delay(10)
        self.assertFalse(graph.has_variable("RenamedVariable"))

    async def test_open_animation_graph_from_context_menu(self):
        await self.load_stage(self.usd_data_dir, "TestBlend.usda")

        stage_window = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        label = stage_window.find_first("**/Label[*].text=='AnimationGraph'")
        await label.right_click()
        await ui_test.human_delay(10)
        await ui_test.select_context_menu("Open Animation Graph")
        await ui_test.human_delay(10)
        _graph_canvas = "Animation Graph//Frame/**/Frame[1]/**/Frame[0]/ZStack[0]/ZStack[0]/CanvasFrame[0]"
        _graph_graph = _graph_canvas + "/**/node_graph"
        graph_view = ui_test.find(_graph_graph)
        self.assertIsNotNone(graph_view)
