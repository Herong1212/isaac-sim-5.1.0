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


class TestLabel(OmniUiTest):
    """Testing ui.Label"""

    async def test_general(self):
        """Testing general properties of ui.Label"""
        window = await self.create_test_window()

        with window.frame:
            with ui.VStack(height=0):
                # Simple text
                ui.Label("Hello world")

                # Word wrap
                ui.Label(
                    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut "
                    "labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco "
                    "laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in "
                    "voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat "
                    "non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
                    word_wrap=True,
                )

                # Computing text size
                with ui.HStack(width=0):
                    ui.Label("A")
                    ui.Label("BC")
                    ui.Label("DEF")
                    ui.Label("GHIjk")
                    ui.Label("lmnopq")
                    ui.Label("rstuvwxyz")

                # Styling
                ui.Label("Red", style={"color": 0xFF0000FF})
                ui.Label("Green", style={"Label": {"color": 0xFF00FF00}})
                ui.Label("Blue", style_type_name_override="TreeView", style={"TreeView": {"color": 0xFFFF0000}})

        await self.finalize_test()

    async def test_alignment(self):
        """Testing alignment of ui.Label"""
        window = await self.create_test_window()

        with window.frame:
            with ui.ZStack():
                ui.Label("Left Top", alignment=ui.Alignment.LEFT_TOP)
                ui.Label("Center Top", alignment=ui.Alignment.CENTER_TOP)
                ui.Label("Right Top", alignment=ui.Alignment.RIGHT_TOP)

                ui.Label("Left Center", alignment=ui.Alignment.LEFT_CENTER)
                ui.Label("Center", alignment=ui.Alignment.CENTER)
                ui.Label("Right Center", alignment=ui.Alignment.RIGHT_CENTER)

                ui.Label("Left Bottom", alignment=ui.Alignment.LEFT_BOTTOM)
                ui.Label("Center Bottom", alignment=ui.Alignment.CENTER_BOTTOM)
                ui.Label("Right Bottom", alignment=ui.Alignment.RIGHT_BOTTOM)

        await self.finalize_test()

    async def test_wrap_alignment(self):
        """Testing alignment of ui.Label with word_wrap"""
        window = await self.create_test_window()

        with window.frame:
            ui.Label(
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut "
                "labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco "
                "laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in "
                "voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat "
                "non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
                word_wrap=True,
                style={"Label": {"alignment": ui.Alignment.CENTER}},
            )

        await self.finalize_test()

    async def test_elide(self):
        """Testing ui.Label with elided_text"""
        window = await self.create_test_window()

        with window.frame:
            with ui.VStack():
                ui.Label(
                    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut "
                    "labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco "
                    "laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in "
                    "voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat "
                    "non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
                    elided_text=True,
                    height=0,
                )
                ui.Label(
                    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut "
                    "labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco "
                    "laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in "
                    "voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat "
                    "non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
                    word_wrap=True,
                    elided_text=True,
                )
                ui.Label(
                    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut "
                    "labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco "
                    "laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in "
                    "voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat "
                    "non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
                    alignment=ui.Alignment.CENTER,
                    word_wrap=True,
                    elided_text=True,
                )

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_change_size(self):
        """Testing how ui.Label dynamically changes size"""
        window = await self.create_test_window()

        with window.frame:
            with ui.VStack(style={"Rectangle": {"background_color": 0xFFFFFFFF}}):
                with ui.HStack(height=0):
                    with ui.Frame(width=0):
                        line1 = ui.Label("Test")
                    ui.Rectangle()
                with ui.HStack(height=0):
                    with ui.Frame(width=0):
                        line2 = ui.Label("Test")
                    ui.Rectangle()

                with ui.Frame(height=0):
                    line3 = ui.Label("Test", word_wrap=True)
                ui.Rectangle()

        for i in range(2):
            await omni.kit.app.get_app().next_update_async()

        # Change the text
        line1.text = "Bigger than before"
        line2.text = "a"
        line3.text = (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut "
            "labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco "
            "laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in "
            "voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat "
            "non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
        )

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_font(self):
        window = await self.create_test_window()

        with window.frame:
            ui.Label(
                "The quick brown fox jumps over the lazy dog",
                style={"font_size": 55, "font": "${fonts}/OpenSans-SemiBold.ttf", "alignment": ui.Alignment.CENTER},
                word_wrap=True,
            )

        await self.finalize_test()

    async def test_invalid_font(self):
        window = await self.create_test_window()

        with window.frame:
            ui.Label(
                "The quick brown fox jumps over the lazy dog",
                style={"font_size": 55, "font": "${fonts}/IDoNotExist.ttf", "alignment": ui.Alignment.CENTER},
                word_wrap=True,
            )

        await self.finalize_test()

    async def test_mouse_released_fn(self):
        """Test mouse_released_fn only triggers on widget which was pressed"""
        import omni.kit.ui_test as ui_test

        window = await self.create_test_window(block_devices=False)

        release_count = [0, 0]

        def release(i):
            release_count[i] += 1

        with window.frame:
            with ui.VStack():
                label1 = ui.Label("1", mouse_released_fn=lambda *_: release(0))
                label2 = ui.Label("2", mouse_released_fn=lambda *_: release(1))

        try:
            await omni.kit.app.get_app().next_update_async()
            refLabel1 = ui_test.WidgetRef(label1, "")
            refLabel2 = ui_test.WidgetRef(label2, "")
            await omni.kit.app.get_app().next_update_async()

            # Left button
            await ui_test.emulate_mouse_drag_and_drop(refLabel1.center, refLabel2.center)
            await omni.kit.app.get_app().next_update_async()
            self.assertEqual(release_count[0], 1)
            self.assertEqual(release_count[1], 0)

            # Right button
            release_count = [0, 0]
            await ui_test.emulate_mouse_drag_and_drop(refLabel1.center, refLabel2.center, right_click=True)
            await omni.kit.app.get_app().next_update_async()
            self.assertEqual(release_count[0], 1)
            self.assertEqual(release_count[1], 0)

        finally:
            await self.finalize_test_no_image()

    async def test_exact_content_size(self):
        """Test the exact content width/height properties"""
        CHAR_WIDTH = 7
        CHAR_HEIGHT = 14

        window = await self.create_test_window()
        with window.frame:
            with ui.VStack(height=0):
                with ui.HStack():
                    label1 = ui.Label("1")
                    label10 = ui.Label("10")
                    label1234 = ui.Label("1234")
                label_wrap = ui.Label(
                    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut "
                    "labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco "
                    "laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in "
                    "voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat "
                    "non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
                    word_wrap=True,
                )
                label_elided = ui.Label(
                    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut "
                    "labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco "
                    "laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in "
                    "voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat "
                    "non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
                    elided_text=True,
                )
        await omni.kit.app.get_app().next_update_async()

        # Verify width of text
        self.assertEqual(label1.exact_content_width, CHAR_WIDTH)
        self.assertEqual(label10.exact_content_width, CHAR_WIDTH*2)
        self.assertEqual(label1234.exact_content_width, CHAR_WIDTH*4)
        self.assertEqual(label_wrap.exact_content_width, CHAR_WIDTH*35)
        self.assertAlmostEqual(label_elided.computed_content_width, 248.0, 3)

        # Verify height
        self.assertEqual(label1.exact_content_height, CHAR_HEIGHT)
        self.assertEqual(label10.exact_content_height, CHAR_HEIGHT)
        self.assertEqual(label1234.exact_content_height, CHAR_HEIGHT)
        self.assertEqual(label_wrap.exact_content_height, CHAR_HEIGHT*11)
        self.assertEqual(label_elided.exact_content_height, CHAR_HEIGHT)

        # Change the text
        label1.text = "12345"
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(label1.exact_content_width, CHAR_WIDTH*5)
        self.assertEqual(label1.exact_content_height, CHAR_HEIGHT)

        # Change text (no word wrap), should just resize the label
        label10.text = (
            "1234567890"
            "1234567890"
            "1234567890"
        )
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(label10.exact_content_width, CHAR_WIDTH*30)
        self.assertEqual(label10.exact_content_height, CHAR_HEIGHT)

        await self.finalize_test_no_image()
