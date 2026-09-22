import pathlib

import carb.settings
import omni.kit.app
import omni.kit.commands
import omni.kit.test
import omni.kit.ui
import omni.renderer_capture
import omni.ui as ui
from omni.kit import ui_test
from omni.ui.tests.test_base import OmniUiTest

EXTENSION_FOLDER_PATH = pathlib.Path(
    omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
)
TEST_DATA_PATH = EXTENSION_FOLDER_PATH.joinpath("data").joinpath("tests")


class TestPointCloudPropertyWidget(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()

        self._usd_context = omni.usd.get_context()
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()
        self._usd_path = TEST_DATA_PATH.absolute()
        self._timeline = omni.timeline.get_timeline_interface()

        settings = carb.settings.get_settings()

        def setup_settings(settings_dict):
            for name, value in settings_dict.items():
                if settings.get(name) != value[0]:
                    settings.set(name, value[0])

        self._viewport_settings = {
            "/persistent/app/viewport/displayOptions": ((1 << 7) | (1 << 10), (1 << 7) | (1 << 10)),
            "/app/viewport/grid/enabled": (False, True),
            "/app/viewport/snapEnabled": (False, False),
            "/app/asyncRendering": (False, True),
            "/persistent/app/viewport/gizmo/constantScaleCamera": (False, False),
            "/persistent/app/viewport/gizmo/constantScaleEnabled": (True, True),
            "/persistent/app/viewport/gizmo/constantScale": (10.0, 10.0),
            "/persistent/app/viewport/gizmo/scale": (1.0, 1.0),
            "/persistent/app/viewport/gizmo/lineWidth": (10, 10),
            "/persistent/app/viewport/gizmo/minFadeOut": (1, 1),
            "/persistent/app/viewport/gizmo/maxFadeOut": (50, 50),
            "/renderer/enabled": ("rtx", "rtx"),
            "/renderer/active": ("rtx", "rtx"),
        }

        setup_settings(self._viewport_settings)
        await ui_test.wait_n_updates(1)

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    async def _capture_golden_image(self, filename):
        await ui_test.wait_n_updates(10)

        capture_next_frame = omni.renderer_capture.acquire_renderer_capture_interface().capture_next_frame_swapchain
        wait_async_capture = omni.renderer_capture.acquire_renderer_capture_interface().wait_async_capture

        capture_next_frame(str(self._golden_img_dir.joinpath(filename)))

        await omni.kit.app.get_app().next_update_async()

        wait_async_capture()

    async def _test_golden_image(self, test_usd_file, test_image, wait_frames=50, threshold=1):

        await self.docked_test_window(window=ui.Workspace.get_window("Viewport"), width=1280, height=720)

        test_file_path = self._usd_path.joinpath(test_usd_file).absolute()
        await self._usd_context.open_stage_async(str(test_file_path))
        await omni.kit.app.get_app().next_update_async()

        self._timeline.play()

        await ui_test.wait_n_updates(wait_frames)

        # This is here to update the golden image.  NEVER CHECK IN WITH THE FOLLOWING LINE UNCOMMENTED
        # await self._capture_golden_image(test_image)

        await self.finalize_test(
            threshold=threshold, use_log=True, golden_img_dir=self._golden_img_dir, golden_img_name=test_image
        )

    async def test_fire_preset_golden_image(self):
        await self._test_golden_image("FirePreset.usda", "test_fire_preset.png", wait_frames=220, threshold=0.2)

    async def test_fire_with_disk_golden_image(self):
        await self._test_golden_image("FireWithDisk.usda", "test_fire_with_disk.png", wait_frames=50, threshold=1.8)

    async def test_fire_with_glass_golden_image(self):
        await self._test_golden_image("FireWithGlass.usda", "test_fire_with_glass.png", wait_frames=150, threshold=3.9)
