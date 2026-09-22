import asyncio
import os
import carb.settings
import omni.usd
import omni.kit.commands
import omni.client
import omni.kit.test
import omni.ui as ui
import omni.kit.viewport_widgets_manager as wm
from omni.kit.viewport.utility.tests import setup_viewport_test_window

import sys
import unittest

from omni.ui.tests.test_base import OmniUiTest
from pathlib import Path
from pxr import Usd, UsdGeom, Gf


CURRENT_PATH = Path(__file__).parent.joinpath("../../../../data")
CAMERA_WIDGET_STYLING = {
    "Rectangle::background": {"background_color": 0x7F808080, "border_radius": 5}
}


class LabelWidget(wm.WidgetProvider):
    def __init__(self, text):
        self._text = text

    def build_widget(self, window):
        with ui.ZStack(width=0, height=0, style=CAMERA_WIDGET_STYLING):
            ui.Rectangle(name="background")
            with ui.VStack(width=0, height=0):
                ui.Spacer(height=4)
                with ui.HStack(width=0, height=0):
                    ui.Spacer(width=4)
                    ui.Label(self._text, width=0, height=0, name="user_name")
                    ui.Spacer(width=4)
                ui.Spacer(height=4)


class TestWidgetsManagerUI(OmniUiTest):
    async def setUp(self):
        await super().setUp()
        self._golden_img_dir = CURRENT_PATH.absolute().resolve().joinpath("tests")
        # viewport_next golden images are different
        vp_window_name = carb.settings.get_settings().get('/exts/omni.kit.viewport.window/startup/windowName')
        if not (vp_window_name and (vp_window_name == 'Viewport')):
            self._golden_img_dir = self._golden_img_dir.joinpath("viewport_1")

        self._all_widgets = []
        await omni.usd.get_context().new_stage_async()
        await self.wait_frames()

    # After running each test
    async def tearDown(self):
        self._golden_img_dir = None
        for widget_id in self._all_widgets:
            wm.remove_widget(widget_id)
        await super().tearDown()

    async def wait_frames(self, n_frame: int = 10):
        app = omni.kit.app.get_app()
        while n_frame > 0:
            await app.next_update_async()
            n_frame = n_frame - 1

    async def create_text_widget(self, text, alignment, width: int = 320, height: int = 240):
        try:
            from omni.kit.mainwindow import get_main_window
            get_main_window().get_main_menu_bar().visible = False
        except (ImportError, AttributeError):
            pass

        # Create test area
        await self.create_test_area(width, height)
        # Fill the area with the Viewport
        viewport_window = await setup_viewport_test_window(width, height)

        # Add scene objects
        usd_context = viewport_window.viewport_api.usd_context
        stage = usd_context.get_stage()
        prim_path = "/World/widget_prim"
        prim = UsdGeom.Xform.Define(stage, prim_path)
        await self.wait_frames()
        usd_context.get_selection().clear_selected_prim_paths()
        self._all_widgets.append(wm.add_widget(prim_path, LabelWidget(text), alignment))

        # Sleep 1s to wait for drawing
        await asyncio.sleep(1.0)

        return prim

    async def test_create_widget_top(self):
        await self.create_text_widget("Sphere", wm.WidgetAlignment.TOP)
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="test_create_widget_top.png")

    async def test_create_widget_bottom(self):
        await self.create_text_widget("Cone", wm.WidgetAlignment.BOTTOM)
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="test_create_widget_bottom.png")

    async def test_create_widget_center(self):
        await self.create_text_widget("Cube", wm.WidgetAlignment.CENTER)
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="test_create_widget_center.png")

    async def test_widget_translate(self):
        prim = await self.create_text_widget("Sphere", wm.WidgetAlignment.TOP)
        translation = Gf.Vec3d(-200, 0.0, 0.0)
        common_api = UsdGeom.XformCommonAPI(prim)
        common_api.SetTranslate(translation)
        await self.wait_frames()
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="test_widget_translate.png")

    async def test_widget_out_of_viewport(self):
        prim = await self.create_text_widget("Sphere", wm.WidgetAlignment.TOP)
        translation = Gf.Vec3d(-200000, 0.0, 0.0)
        common_api = UsdGeom.XformCommonAPI(prim)
        common_api.SetTranslate(translation)
        await self.wait_frames()
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="test_widget_out_of_viewport.png")
