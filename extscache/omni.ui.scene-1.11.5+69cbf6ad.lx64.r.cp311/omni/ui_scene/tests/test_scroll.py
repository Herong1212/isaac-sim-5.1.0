## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
__all__ = ["TestScroll"]

import omni.kit.test
from omni.ui import scene as sc
from omni.ui.tests.test_base import OmniUiTest
import omni.kit.app
import omni.ui as ui


class TestScroll(OmniUiTest):
    async def test_scroll(self):
        import omni.kit.ui_test as ui_test

        window = await self.create_test_window(block_devices=False)

        scrolled = [0, 0]

        class Scroll(sc.ScrollGesture):
            def on_ended(self):
                scrolled[0] += self.scroll[0]
                scrolled[1] += self.scroll[1]

        with window.frame:
            # Camera matrices
            projection = [1e-2, 0, 0, 0]
            projection += [0, 1e-2, 0, 0]
            projection += [0, 0, 2e-7, 0]
            projection += [0, 0, 1, 1]
            view = sc.Matrix44.get_translation_matrix(0, 0, -5)

            scene_view = sc.SceneView(sc.CameraModel(projection, view))
            with scene_view.scene:
                sc.Screen(gesture=Scroll())

        await self.wait_n_updates(1)

        ref = ui_test.WidgetRef(scene_view, "")

        await ui_test.emulate_mouse_move(ref.center)
        await ui_test.emulate_mouse_scroll(ui_test.Vec2(1, 0))

        await self.wait_n_updates(1)

        self.assertTrue(scrolled[0] == 0)
        self.assertTrue(scrolled[1] > 0)

        await self.finalize_test_no_image()

    async def test_scroll_another_window(self):
        import omni.kit.ui_test as ui_test

        window = await self.create_test_window(block_devices=False)

        scrolled = [0, 0]

        class Scroll(sc.ScrollGesture):
            def on_ended(self):
                scrolled[0] += self.scroll[0]
                scrolled[1] += self.scroll[1]

        with window.frame:
            # Camera matrices
            projection = [1e-2, 0, 0, 0]
            projection += [0, 1e-2, 0, 0]
            projection += [0, 0, 2e-7, 0]
            projection += [0, 0, 1, 1]
            view = sc.Matrix44.get_translation_matrix(0, 0, -5)

            scene_view = sc.SceneView(sc.CameraModel(projection, view))
            with scene_view.scene:
                sc.Screen(gesture=Scroll())

        another_window = ui.Window("cover it", width=128, height=128, position_x=64, position_y=64)

        await self.wait_n_updates(1)

        ref = ui_test.WidgetRef(scene_view, "")

        await ui_test.emulate_mouse_move(ref.center)
        await ui_test.emulate_mouse_scroll(ui_test.Vec2(1, 1))

        await self.wait_n_updates(1)

        # Window covers SceneView. Scroll is not expected.
        self.assertTrue(scrolled[0] == 0)
        self.assertTrue(scrolled[1] == 0)

        await self.finalize_test_no_image()
