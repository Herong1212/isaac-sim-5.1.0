# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.kit.app
import omni.kit.commands
import omni.kit.test


class TestPrimEditsAndAutoTarget(omni.kit.test.AsyncTestCase):
    def __init__(self, tests=None):
        super().__init__(tests if tests else ())

    # Before running each test
    async def setUp(self):
        self._usd_context = omni.usd.get_context()
        await self._usd_context.new_stage_async()
        self._stage = self._usd_context.get_stage()
        from omni.kit.test_suite.helpers import arrange_windows

        await arrange_windows(topleft_window="Property", topleft_height=64, topleft_width=800.0)
        await self.wait()

    # After running each test
    async def tearDown(self):
        from omni.kit.test_suite.helpers import wait_stage_loading

        await wait_stage_loading()

    async def wait(self, updates=3):
        for _ in range(updates):
            await omni.kit.app.get_app().next_update_async()

    async def test_built_in_camera_editing(self):
        from omni.kit import ui_test
        from omni.kit.test_suite.helpers import select_prims, wait_stage_loading

        # wait for material to load & UI to refresh
        await wait_stage_loading()

        prim_path = "/OmniverseKit_Persp"

        await select_prims([prim_path])
        # Loading all inputs
        await self.wait()

        all_widgets = ui_test.find_all("Property//Frame/**/.identifier!=''")
        self.assertNotEqual(all_widgets, [])
        for w in all_widgets:
            wid = w.widget.identifier
            if wid.startswith("float_slider_"):
                w.widget.scroll_here_y(0.5)
                await ui_test.human_delay()
                await w.input(str(0.3456))
                await ui_test.human_delay()
            elif wid.startswith("integer_slider_"):
                w.widget.scroll_here_y(0.5)
                attr = self._stage.GetPrimAtPath(prim_path).GetAttribute(wid[15:])
                await ui_test.human_delay()
                old_value = attr.Get()
                new_value = old_value + 1
                await w.input(str(new_value))
                await ui_test.human_delay()
            elif wid.startswith("drag_per_channel_int"):
                w.widget.scroll_here_y(0.5)
                await ui_test.human_delay()
                sub_widgets = w.find_all("**/IntSlider[*]")
                if sub_widgets == []:
                    sub_widgets = w.find_all("**/IntDrag[*]")
                self.assertNotEqual(sub_widgets, [])
                for child in sub_widgets:
                    child.model.set_value(0)
                    await child.input("9999")
                    await ui_test.human_delay()
            elif wid.startswith("drag_per_channel_"):
                w.widget.scroll_here_y(0.5)
                await ui_test.human_delay()
                sub_widgets = w.find_all("**/FloatSlider[*]")
                if sub_widgets == []:
                    sub_widgets = w.find_all("**/FloatDrag[*]")
                self.assertNotEqual(sub_widgets, [])
                for child in sub_widgets:
                    await child.input("0.12345")
                    await self.wait()
            elif wid.startswith("bool_"):
                w.widget.scroll_here_y(0.5)
                attr = self._stage.GetPrimAtPath(prim_path).GetAttribute(wid[5:])
                await ui_test.human_delay()
                old_value = attr.Get()
                new_value = not old_value
                w.widget.model.set_value(new_value)
            elif wid.startswith("sdf_asset_"):
                w.widget.scroll_here_y(0.5)
                await ui_test.human_delay()
                new_value = "testpath/abc.png"
                w.widget.model.set_value(new_value)
                await ui_test.human_delay()

        # All property edits to built-in cameras should be retargeted into session layer.
        root_layer = self._stage.GetRootLayer()
        prim_spec = root_layer.GetPrimAtPath("/OmniverseKit_Persp")
        self.assertTrue(bool(prim_spec))
