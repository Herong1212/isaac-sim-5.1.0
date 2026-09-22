## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
__all__ = ["TestSceneViewIntegration"]

from pathlib import Path
import carb

from omni.kit.widget.viewport import ViewportWidget
from omni.ui.tests.test_base import OmniUiTest
import omni.usd


CURRENT_PATH = Path(carb.tokens.get_tokens_interface().resolve("${omni.kit.widget.viewport}/data")).absolute().resolve()
TEST_FILES_DIR = CURRENT_PATH.joinpath('tests')
USD_FILES_DIR = TEST_FILES_DIR.joinpath('usd')

TEST_WIDTH, TEST_HEIGHT = 360, 240


class TestSceneViewIntegration(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        await omni.usd.get_context().new_stage_async()

    # After running each test
    async def tearDown(self):
        await super().tearDown()
        await self.linux_gpu_shutdown_workaround()

    async def linux_gpu_shutdown_workaround(self, usd_context_name : str = ''):
        await self.wait_n_updates(10)
        omni.usd.release_all_hydra_engines(omni.usd.get_context(usd_context_name))
        await self.wait_n_updates(10)

    async def open_usd_file(self, filename: str, resolved: bool = False):
        usd_context = omni.usd.get_context()
        usd_path = str(USD_FILES_DIR.joinpath(filename) if not resolved else filename)
        await usd_context.open_stage_async(usd_path)
        return usd_context

    def assertAlmostEqual(self, a, b, places: int = 4):
        if isinstance(a, (float, int)):
            super().assertAlmostEqual(a, b, places)
        else:
            for va, vb in zip(a, b):
                super().assertAlmostEqual(va, vb, places)

    async def test_scene_view_single_cam_model_enabled(self):
        """Test the setting to enable single view camera model matches whether extension is enabled or not"""
        settings = carb.settings.get_settings()
        ext_mgr = omni.kit.app.get_app().get_extension_manager()
        setting_enabled = bool(settings.get("/exts/omni.kit.widget.viewport/sceneView/singleCameraModel/enabled"))
        ext_enabled = bool(ext_mgr.is_extension_enabled("omni.kit.viewport.scene_camera_model"))
        self.assertEqual(setting_enabled, ext_enabled)

    async def test_scene_view_compositing(self):
        """Test adding a SceneView to the Viewport will draw correctly"""

        await self.open_usd_file("cube.usda")

        import omni.ui
        import omni.ui.scene

        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)

        # Need a Window otherwise the ui size calculations won't run
        window_flags = omni.ui.WINDOW_FLAGS_NO_RESIZE | omni.ui.WINDOW_FLAGS_NO_SCROLLBAR | omni.ui.WINDOW_FLAGS_NO_TITLE_BAR
        style = {"border_width": 0}
        window = omni.ui.Window("Test", width=TEST_WIDTH, height=TEST_HEIGHT, flags=window_flags, padding_x=0, padding_y=0)
        with window.frame:
            window.frame.set_style(style)

            with omni.ui.ZStack():
                viewport_widget = ViewportWidget(resolution=(TEST_WIDTH, TEST_HEIGHT), style=style)
                scene_view = omni.ui.scene.SceneView(style=style)
                with scene_view.scene:
                    size = 50
                    vertex_indices = [0, 1, 3, 2, 4, 6, 7, 5, 6, 2, 3, 7, 4, 5, 1, 0, 4, 0, 2, 6, 5, 7, 3, 1]
                    points = [(-size, -size, size), (size, -size, size), (-size, size, size),
                              (size, size, size), (-size, -size, -size), (size, -size, -size),
                              (-size, size, -size), (size, size, -size)]

                    omni.ui.scene.PolygonMesh(points,
                                              [[1.0, 0.0, 1.0, 0.5]] * len(vertex_indices),
                                              vertex_counts=[4] * 6,
                                              vertex_indices=vertex_indices,
                                              wireframe=True,
                                              thicknesses=[2] * len(vertex_indices))

                viewport_widget.viewport_api.add_scene_view(scene_view)

        await self.wait_n_updates(32)
        await self.finalize_test(golden_img_dir=TEST_FILES_DIR, golden_img_name="test_scene_view_compositing.png")

        viewport_widget.viewport_api.remove_scene_view(scene_view)
        viewport_widget.destroy()
        del viewport_widget
