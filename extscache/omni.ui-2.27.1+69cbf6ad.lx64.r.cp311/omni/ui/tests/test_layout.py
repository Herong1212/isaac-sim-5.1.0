## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
from .test_base import OmniUiTest
import omni.kit.app
import omni.ui as ui


class TestLayout(OmniUiTest):
    """Testing the layout"""

    async def test_general(self):
        """Testing general layout and number of calls of setComputedWidth"""
        window = await self.create_test_window()

        with window.frame:
            with ui.VStack():
                with ui.HStack():
                    ui.Button("NVIDIA")
                    ui.Button("Omniverse")
                bottom_stack = ui.HStack()
                with bottom_stack:
                    ui.Button("omni")
                    button = ui.Button("ui")

        await omni.kit.app.get_app().next_update_async()

        # 21 is because the window looks like this:
        # MenuBar
        # Frame
        #     VStack
        #         HStack
        #             Button
        #                 Stack
        #                     Label
        #                     Rectangle
        #             Button
        #                 Stack
        #                     Label
        #                     Rectangle
        #         HStack
        #             Button
        #                 Stack
        #                     Label
        #                     Rectangle
        #             Button
        #                 Stack
        #                     Label
        #                     Rectangle
        should_be_called = [21] + [0] * 20
        for i in should_be_called:
            ui.Inspector.begin_computed_width_metric()
            ui.Inspector.begin_computed_height_metric()

            await omni.kit.app.get_app().next_update_async()

            width_calls = ui.Inspector.end_computed_width_metric()
            height_calls = ui.Inspector.end_computed_height_metric()

            self.assertEqual(width_calls, i)
            self.assertEqual(height_calls, i)

        button.height = ui.Pixel(25)

        # 11 becuse we changed the height of the button and this is the list of
        # changed widgets:
        # 4 Button
        # 4 Neighbour button because it's Fraction(1)
        # 1 HStack becuase min size could change
        # 1 VStack becuase min size could change
        # 1 Frame becuase min size could change
        should_be_called = [11] + [0] * 20
        for i in range(10):
            ui.Inspector.begin_computed_width_metric()
            ui.Inspector.begin_computed_height_metric()

            await omni.kit.app.get_app().next_update_async()

            width_calls = ui.Inspector.end_computed_width_metric()
            height_calls = ui.Inspector.end_computed_height_metric()

        bottom_stack.height = ui.Pixel(50)

        # 16 because 20 (total wingets minus MenuBar) - 4 (Button is in pixels,
        # the size of pixels don't change if parent changes) and we only changed
        # heights and width should not be called
        should_be_called = [16] + [0] * 20
        for i in should_be_called:
            ui.Inspector.begin_computed_width_metric()
            ui.Inspector.begin_computed_height_metric()

            await omni.kit.app.get_app().next_update_async()

            width_calls = ui.Inspector.end_computed_width_metric()
            height_calls = ui.Inspector.end_computed_height_metric()

            self.assertEqual(width_calls, 0)
            self.assertEqual(height_calls, i)

        button.width = ui.Pixel(25)

        # 20 because everything except MenuBar could change:
        # Neighbour button is changed
        # Stack could change if button.width is very big
        # Neighbour stack could change if current stack is changed
        # Parent stack
        # Root frame
        #
        # Height shouldn't change
        should_be_called = [20] + [0] * 20
        for i in should_be_called:
            ui.Inspector.begin_computed_width_metric()
            ui.Inspector.begin_computed_height_metric()

            await omni.kit.app.get_app().next_update_async()

            width_calls = ui.Inspector.end_computed_width_metric()
            height_calls = ui.Inspector.end_computed_height_metric()

            self.assertEqual(width_calls, i)
            self.assertEqual(height_calls, 0)

        await self.finalize_test()

    async def test_send_mouse_events_to_back(self):
        """Testing send_mouse_events_to_back of ui.ZStack"""
        import omni.kit.ui_test as ui_test

        window = await self.create_test_window(block_devices=False)

        clicked = [0, 0]

        def clicked_fn(i):
            clicked[i] += 1

        with window.frame:
            stack = ui.ZStack()
            with stack:
                ui.Button(clicked_fn=lambda: clicked_fn(0))
                button = ui.Button(clicked_fn=lambda: clicked_fn(1))

        await omni.kit.app.get_app().next_update_async()

        refButton = ui_test.WidgetRef(button, "")

        await omni.kit.app.get_app().next_update_async()
        await ui_test.emulate_mouse_move_and_click(refButton.center)
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(clicked[0], 1)

        stack.send_mouse_events_to_back = False

        await omni.kit.app.get_app().next_update_async()
        await ui_test.emulate_mouse_move_and_click(refButton.center)
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(clicked[1], 1)

        await self.finalize_test_no_image()

    async def test_visibility(self):
        window = await self.create_test_window()
        with window.frame:
            with ui.HStack(height=32):
                with ui.VStack(width=80):
                    ui.Spacer(height=10)
                    c1 = ui.ComboBox(0, "NVIDIA", "OMNIVERSE", width=100)
                with ui.VStack(width=80):
                    ui.Spacer(height=10)
                    ui.ComboBox(0, "NVIDIA", "OMNIVERSE", width=100)

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        c1.visible = not c1.visible

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        c1.visible = not c1.visible

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()
