import omni.kit.test
from omni.ui.tests.test_base import OmniUiTest
from omni.debugdraw import get_debug_draw_interface
from omni.debugdraw._debugDraw import SimplexPoint
import carb
from pathlib import Path
import inspect

from omni.kit.viewport.utility import get_active_viewport_window, next_viewport_frame_async
from omni.kit.viewport.utility.camera_state import ViewportCameraState
from omni.kit.viewport.utility.tests import setup_viewport_test_window, capture_viewport_and_compare


EXTENSION_ROOT = Path(carb.tokens.get_tokens_interface().resolve("${omni.debugdraw}")).resolve().absolute()
GOLDEN_IMAGES = EXTENSION_ROOT.joinpath("data", "tests")
OUTPUTS_DIR = Path(omni.kit.test.get_test_output_path())
COLOR_RED = 0xffff0000


class DebugDrawVisualTest(OmniUiTest):
    def set_camera(self):
        camera_state = ViewportCameraState("/OmniverseKit_Persp")
        camera_state.set_position_world((10, 0, 0), False)
        camera_state.set_target_world((0, 0, 0), True)

    async def setup_viewport(self, resolution_x: int = 800, resolution_y: int = 600):
        await self.create_test_area(resolution_x, resolution_y)
        return await setup_viewport_test_window(resolution_x, resolution_y)

    async def base(self, fn):
        viewport_window = await self.setup_viewport()
        viewport = viewport_window.viewport_api
        await omni.usd.get_context().new_stage_async()
        self.set_camera()

        # Wait until the Viewport has delivered some frames
        await next_viewport_frame_async(viewport, 2)

        # Draw for 20 frames (TC: Windows requires ~5 Linux requires ~20)
        for _ in range(20):
            fn()
            await omni.kit.app.get_app().next_update_async()

        # Capture and compare the image
        test_caller = inspect.stack()[1][3]
        image_name = f"{test_caller}.png"

        passed, fail_msg = await capture_viewport_and_compare(image_name=image_name, output_img_dir=OUTPUTS_DIR, golden_img_dir=GOLDEN_IMAGES, viewport=viewport)
        self.assertTrue(passed, msg=fail_msg)

    def get_point(self, pos, width=2):
        p = SimplexPoint()
        p.position = pos
        p.color = COLOR_RED
        p.width = width
        return p

    async def setUp(self):
        await super().setUp()
        self._iface = get_debug_draw_interface()

    async def test_debugdraw_visual_sphere(self):
        await self.base(lambda: self._iface.draw_sphere(carb.Float3(0.0, 0.0, 0.0), 2, COLOR_RED))

    async def test_debugdraw_visual_line(self):
        await self.base(lambda: self._iface.draw_line(
            carb.Float3(0.0, 0.0, 0.0), COLOR_RED, 2,
            carb.Float3(0.0, 2.0, 0.0), COLOR_RED, 2
        ))

    async def test_debugdraw_visual_line_list(self):
        line_list = [
            self.get_point(carb.Float3(0.0, 0.0, 0.0)),
            self.get_point(carb.Float3(0.0, -2.0, 0.0)),
            self.get_point(carb.Float3(0.0, 0.0, 0.0)),
            self.get_point(carb.Float3(0.0, 2.0, 0.0)),
        ]
        await self.base(lambda: self._iface.draw_lines(line_list))

    async def test_debugdraw_visual_point(self):
        await self.base(lambda: self._iface.draw_point(carb.Float3(0.0, 0.0, 0.0), COLOR_RED, 10))

    async def test_debugdraw_visual_box(self):
        await self.base(lambda: self._iface.draw_box(
            carb.Float3(0.0, 0.0, 0.0),
            carb.Float4(0.3535534, 0.3535534, 0.1464466, 0.8535534),
            carb.Float3(2, 2, 2),
            COLOR_RED
        ))

    async def test_debugdraw_visual_points(self):
        point_list = [
            self.get_point(carb.Float3(0.0, 0.0, 0.0), 10),
            self.get_point(carb.Float3(0.0, -2.0, 0.0), 10),
            self.get_point(carb.Float3(0.0, 2.0, 0.0), 10),
        ]
        await self.base(lambda: self._iface.draw_points(point_list))
