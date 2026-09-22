## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

import asyncio
import pathlib

import omni.kit.app
import omni.kit.ui_test as ui_test
from omni.kit.test_suite.helpers import select_prims, wait_stage_loading
from omni.kit.ui_test import Vec2
from omni.ui.tests.test_base import OmniUiTest


class TestVariantPresenterWidget(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()

        import omni.kit.variant.presenter as vp

        self._w = vp.get_window()
        self._m = vp.get_model()

        extension_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        test_data_path = pathlib.Path(extension_path).joinpath("data").joinpath("tests")

        self.__golden_img_dir = test_data_path.absolute().joinpath("golden_img").absolute()
        self.__usd_path = str(test_data_path.joinpath("variant_test_stage.usda").absolute())

        await self.docked_test_window(window=self._w._window, width=450, height=350, block_devices=False)
        self._usd_context = omni.usd.get_context()
        await self._usd_context.open_stage_async(self.__usd_path)
        await wait_stage_loading()

        self._stage = self._usd_context.get_stage()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    # Test(s)
    async def test_variant_presenter_1_prims(self):
        cone_path = "/World/variant_cone_test"

        # Select the prim.
        await select_prims([cone_path])
        await ui_test.human_delay()

        # Test View Selected
        self._w._set_view(1)
        await ui_test.human_delay()
        list_len = len(self._m.prims)
        self.assertTrue(list_len == 1, msg=f"View Selected shows {list_len} prims instead of the expected 1.")

        # Test View All
        self._w._set_view(0)
        await ui_test.human_delay()
        list_len = len(self._m.prims)
        self.assertTrue(list_len == 2, msg=f"View All shows {list_len} prims instead of the expected 2.")

        # Test Search
        try:
            from omni.kit.widget.searchfield import SearchField

            await ui_test.emulate_mouse_move_and_click(Vec2(114, 82))
            await ui_test.emulate_char_press("cone\n")
            await ui_test.human_delay()
            list_len = len(self._m.prims)
            for prim in self._m.prims:
                list_len += len(prim.variants)
            self.assertTrue(
                list_len == 2, msg=f"Searching for 'cone' yields {list_len} items instead of the expected 2."
            )
            await ui_test.emulate_mouse_move_and_click(Vec2(434, 82))
            await ui_test.human_delay()
        except ImportError:
            pass

        # Test Edit Variant
        try:
            import omni.kit.variant.editor as ve

            await ui_test.emulate_mouse_move_and_click(Vec2(420, 114))
            await ui_test.human_delay()
            await ui_test.emulate_mouse_move_and_click(Vec2(420, 118))
            await ui_test.human_delay()
            variant_editor_window = ve.get_window()
            self.assertTrue(variant_editor_window._window.visible, msg="Variant Editor window is not visible.")
            variant_editor_window.hide()
        except ModuleNotFoundError:
            carb.log_warn("Variant Editor extension not found.")
            pass

        # Test Locate File
        try:
            from omni.kit.window.content_browser import get_content_window

            content_browser = get_content_window()
            if content_browser:
                await ui_test.emulate_mouse_move_and_click(Vec2(420, 176))
                await ui_test.human_delay()
                await ui_test.emulate_mouse_move_and_click(Vec2(420, 186))
                filename = content_browser.get_filename()
                self.assertTrue(filename == "variant_cone_test", msg=f"cbresult: {filename}")
                await ui_test.human_delay()
        except Exception as exc:
            pass

        # Test select prim in stage
        await ui_test.emulate_mouse_move_and_click(Vec2(10, 10))
        await ui_test.human_delay()
        await ui_test.emulate_mouse_move_and_click(Vec2(114, 202), right_click=True)
        await ui_test.human_delay()
        await ui_test.emulate_mouse_move_and_click(Vec2(114, 236))
        await ui_test.human_delay()
        selection = self._usd_context.get_selection().get_selected_prim_paths()
        self.assertTrue(
            selection == [cone_path], msg=f"Selection is currently {selection} instead of '/World/variant_cone_test'"
        )

        # Test change variant
        vset = self._m._prims[0].variants[0]._vset
        newVar = vset.GetVariantNames()[0]
        vset.SetVariantSelection(newVar)

        # Test lock variant
        await ui_test.emulate_mouse_move_and_click(Vec2(20, 200))

        await ui_test.human_delay(30)

        await self.finalize_test(
            golden_img_dir=self.__golden_img_dir, golden_img_name="variant_presenter_prim.png", threshold=25
        )

    async def test_variant_presenter_2_groups(self):
        self._w.toggle_tabs(True)

        # Test Search
        try:
            from omni.kit.widget.searchfield import SearchField

            await ui_test.emulate_mouse_move_and_click(Vec2(114, 82))
            await ui_test.emulate_char_press("cone\n")
            await ui_test.human_delay()
            list_len = len(self._m.groups)
            for group in self._m.groups:
                list_len += len(group.variants)
            self.assertTrue(
                list_len == 2, msg=f"Searching for 'cone' yields {list_len} items instead of the expected 2."
            )
            await ui_test.emulate_mouse_move_and_click(Vec2(434, 82))
            await ui_test.human_delay(10)
        except ImportError:
            pass

        # Test Create Group
        self._m.add_group()
        await ui_test.human_delay()
        self.assertTrue(
            len(self._m.groups) == 4, msg=f"'Create Group' results in {list_len} groups instead of the expected 4."
        )

        # Test Rename Group
        cone_group = [g for g in self._m.groups if g.group_name == "cone"]
        self._m.rename_group(cone_group[0], "cone_new_name")
        await ui_test.human_delay()
        cone_group = [g for g in self._m.groups if g.group_name == "cone_new_name"]
        self.assertTrue(len(cone_group) > 0, msg=f"'cone' group was not successfully renamed to 'cone_new_name'")

        # Test Remove From Group
        cube_group = [g for g in self._m.groups if g.group_name == "cube"]
        cube_variants = [v for v in cube_group[0].variants]
        for variant in cube_variants:
            self._m.remove_variant_from_group(variant)
            await ui_test.human_delay()
        cube_group = [g for g in self._m.groups if g.group_name == "cube"]
        self.assertTrue(
            len(cube_group[0].variants) == 0,
            msg=f"'Remove From Group' results in {list_len} variants in this group instead of the expected 0.",
        )

        # Test Delete Group
        self._m.remove_group(cube_group[0])
        await ui_test.human_delay()
        self.assertTrue(
            len(self._m.groups) == 3, msg=f"'Delete Group' results in {list_len} groups instead of the expected 3."
        )

        # Test change variant
        vset = cone_group[0].variants[0]._vset
        newVar = vset.GetVariantNames()[0]
        vset.SetVariantSelection(newVar)
        await ui_test.human_delay()
        await ui_test.emulate_mouse_move_and_click(Vec2(114, 142))

        # Test hide locked variants
        await ui_test.emulate_mouse_move_and_click(Vec2(307, 52))

        await ui_test.human_delay(30)

        await self.finalize_test(
            golden_img_dir=self.__golden_img_dir, golden_img_name="variant_presenter_group.png", threshold=25
        )
