import inspect
import pathlib

import carb
import carb.settings
import carb.tokens
import carb.windowing

import omni.kit.app
import omni.kit.test
import omni.kit.test_helpers_gfx

import omni.kit.renderer.bind
import omni.kit.imgui_renderer
import omni.kit.imgui_renderer_test

# Maximum allowed difference of the same pixel between two images. If the object is moved, the difference will be
# close to 255. 10 is enough to filter out the artifacts of antialiasing on the different systems.
THRESHOLD = 10
OUTPUTS_DIR = omni.kit.test.get_test_output_path()

EXTENSION_FOLDER_PATH = pathlib.Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__))
GOLDEN_DIR = EXTENSION_FOLDER_PATH.joinpath("data/tests")

RENDERER_CAPTURE_EXT_NAME = "omni.kit.renderer.capture"

class ImGuiRendererTest(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._settings = carb.settings.acquire_settings_interface()
        self._app_window_factory = omni.appwindow.acquire_app_window_factory_interface()
        self._renderer = omni.kit.renderer.bind.acquire_renderer_interface()
        self._imgui_renderer = omni.kit.imgui_renderer.acquire_imgui_renderer_interface()
        self._imgui_renderer_test = omni.kit.imgui_renderer_test.acquire_imgui_renderer_test_interface()
        self._renderer.startup()
        self._imgui_renderer.startup()
        self._imgui_renderer_test.startup()

    async def tearDown(self):
        self._imgui_renderer_test.shutdown()
        self._imgui_renderer.shutdown()
        self._renderer.shutdown()

        self._imgui_renderer_test = None
        self._imgui_renderer = None
        self._renderer = None
        self._app_window_factory = None
        self._settings = None

    async def __create_app_window(self, title: str, width: int = 300, height: int = 300):
        app_window = self._app_window_factory.create_window_from_settings()
        app_window.startup_with_desc(
            title=f"ImGui renderer test {title}",
            width=width,
            height=height,
            x=omni.appwindow.POSITION_CENTERED,
            y=omni.appwindow.POSITION_CENTERED,
            decorations=True,
            resize=True,
            always_on_top=False,
            scale_to_monitor=False,
            dpi_scale_override=1.0
        )

        self._app_window_factory.set_default_window(app_window)
        self._renderer.attach_app_window(app_window)
        self._imgui_renderer.attach_app_window(app_window)

        self._imgui_renderer_test.register_empty_window(
            app_window,
            50,
            50,
            200,
            200,
            title
        )

        # Test the carb.imgui is_valid returns True since it is now properly setup
        await self.test_carb_imgui_is_valid(True)

        await omni.kit.app.get_app().next_update_async()
        return app_window

    async def __destroy_app_window(self, app_window):
        self._app_window_factory.set_default_window(None)
        self._imgui_renderer.detach_app_window(app_window)
        self._renderer.detach_app_window(app_window)
        app_window.shutdown()
        await omni.kit.app.get_app().next_update_async()
        return None

    async def test_1000_empty_imgui_window(self):
        TESTNAME = "test_1000_empty_imgui_window"
        FILENAME = f"{TESTNAME}.png"

        app_window = await self.__create_app_window("Test Empty Window")

        try:
            diff = await omni.kit.test_helpers_gfx.capture_and_compare(FILENAME, THRESHOLD, OUTPUTS_DIR, GOLDEN_DIR, app_window)
            if diff != 0:
                carb.log_warn(f"[TEST_NAME] the generated image has max difference {diff}")
                if diff > THRESHOLD:
                    carb.log_error(f'The generated image {FILENAME} has a difference of {diff}, but max difference is {THRESHOLD}')
                    self.assertTrue(False)
        finally:
            app_window = await self.__destroy_app_window(app_window)

    async def test_japanese_font(self):
        TESTNAME = "test_japanese_font"
        FILENAME = f"{TESTNAME}.png"

        app_window = await self.__create_app_window("日本語フォントをテスト")

        try:
            diff = await omni.kit.test_helpers_gfx.capture_and_compare(FILENAME, THRESHOLD, OUTPUTS_DIR, GOLDEN_DIR, app_window)
            if diff != 0:
                carb.log_warn(f"[TEST_NAME] the generated image has max difference {diff}")
                if diff > THRESHOLD:
                    carb.log_error(f'The generated image {FILENAME} has a difference of {diff}, but max difference is {THRESHOLD}')
                    self.assertTrue(False)
        finally:
            app_window = await self.__destroy_app_window(app_window)

    async def test_null_app_window_0(self):
        """Test crash avoidance on API abuse 0"""
        result = self._imgui_renderer_test.attach_null_window(0)
        self.assertTrue(result)

    async def test_null_app_window_1(self):
        """Test crash avoidance on API abuse 1"""
        result = self._imgui_renderer_test.attach_null_window(1)
        self.assertTrue(result)

    async def test_set_cursor_shape_override(self):
        """Test crash avoidance on set_cursor_shape_override"""
        app_window = await self.__create_app_window("Test Empty Window")
        self._imgui_renderer.set_cursor_shape_override(app_window, carb.windowing.CursorStandardShape.HAND)
        app_window = await self.__destroy_app_window(app_window)

    async def test_cursor_shape_override_extend(self):
        """Test crash avoidance on set_cursor_shape_override_extend"""
        app_window = await self.__create_app_window("Test Empty Window")
        self._imgui_renderer.get_all_cursor_shape_names()
        self._imgui_renderer.set_cursor_shape_override_extend(app_window, "Arrow")
        self._imgui_renderer.get_cursor_shape_override_extend(app_window)
        self._imgui_renderer.register_cursor_shape_extend("test_cursor", r"${exe-path}/resources/icons/Ok_64.png")
        self._imgui_renderer.unregister_cursor_shape_extend("test_cursor")
        app_window = await self.__destroy_app_window(app_window)

    async def test_carb_imgui_is_valid(self, should_be_valid: bool = False):
        """Test low level carb.imgui is_valid API"""
        import omni.kit.imgui
        imgui = omni.kit.imgui.acquire_imgui()
        self.assertIsNotNone(imgui)
        self.assertEqual(imgui.is_valid(), should_be_valid)
