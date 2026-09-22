# pylint: disable=missing-function-docstring, missing-class-docstring
import weakref

import omni.kit.test


class TestPathMenu(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        from omni.kit.test_suite.helpers import arrange_windows

        await arrange_windows()

    async def tearDown(self):
        pass

    async def test_path_menu(self):
        from omni.kit import ui_test
        from omni.kit.property.usd import PrimPathWidget
        from omni.kit.property.usd.prim_selection_payload import PrimSelectionPayload
        from omni.kit.test_suite.helpers import get_test_data_path, open_stage, select_prims

        test_path_fn_clicked = False
        menu_path = "PxrHydraEngine/does/not/support/divergent/render/and/simulation/times"

        # setup path button
        def test_path_fn(payload: PrimSelectionPayload):
            nonlocal test_path_fn_clicked
            test_path_fn_clicked = True

        self._button_menu_entry = PrimPathWidget.add_button_menu_entry(
            menu_path,
            onclick_fn=test_path_fn,
        )

        # load stage
        await open_stage(get_test_data_path(__name__, "usd/cube.usda"))
        await select_prims(["/Xform/Cube"])

        # test "+add" menu
        test_path_fn_clicked = False
        for widget in ui_test.find_all("Property//Frame/**/Button[*]"):
            if widget.widget.text.endswith(" Add"):
                await widget.click()
                await ui_test.human_delay()
                await ui_test.select_context_menu(menu_path, offset=ui_test.Vec2(10, 10))

        # verify clicked
        self.assertTrue(test_path_fn_clicked)

        # test stage window context menu
        test_path_fn_clicked = False

        # right click on Cube
        stage_widget = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        await stage_widget.find("**/StringField[*].model.path=='/Xform/Cube'").right_click()
        await ui_test.human_delay()
        # click on context menu item
        await ui_test.select_context_menu(f"Add/{menu_path}", offset=ui_test.Vec2(10, 10))

        # verify clicked
        self.assertTrue(test_path_fn_clicked)

    async def test_payload(self):
        from omni.kit.property.usd.prim_selection_payload import PrimSelectionPayload
        from omni.kit.test_suite.helpers import get_prims, get_test_data_path, open_stage

        # load stage
        await open_stage(get_test_data_path(__name__, "usd/cube.usda"))

        # get stage prims
        stage = omni.usd.get_context().get_stage()
        prim_list = [prim.GetPath().pathString for prim in get_prims(stage) if not omni.usd.is_hidden_type(prim)]

        # create PrimSelectionPayload with additional none-stage prims
        payload = PrimSelectionPayload(
            weakref.ref(stage), prim_list + ["/not/a/prim", "/usd/cube/usda", "/my/hovercraft/is/full/of/eels/"]
        )
        self.assertNotEqual(payload._payload, prim_list)

        # remove none-stage prims
        payload = payload.cleanup_payload()
        self.assertEqual(payload._payload, prim_list)
