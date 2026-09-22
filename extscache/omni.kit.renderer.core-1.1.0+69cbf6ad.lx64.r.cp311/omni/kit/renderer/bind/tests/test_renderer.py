import inspect
import pathlib

import carb
import carb.settings
import carb.tokens

import omni.kit.app
import omni.kit.test
import omni.kit.test_helpers_gfx

import omni.kit.renderer.bind
import omni.kit.renderer_test

# Maximum allowed difference of the same pixel between two images. If the object is moved, the difference will be
# close to 255. 10 is enough to filter out the artifacts of antialiasing on the different systems.
THRESHOLD = 10
OUTPUTS_DIR = omni.kit.test.get_test_output_path()

EXTENSION_FOLDER_PATH = pathlib.Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__))
GOLDEN_DIR = EXTENSION_FOLDER_PATH.joinpath("data/tests")

RENDERER_CAPTURE_EXT_NAME = "omni.kit.renderer.capture"

class RendererTest(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._settings = carb.settings.acquire_settings_interface()
        self._app_window_factory = omni.appwindow.acquire_app_window_factory_interface()
        self._renderer = omni.kit.renderer.bind.acquire_renderer_interface()
        self._renderer_test = omni.kit.renderer_test.acquire_renderer_test_interface()
        self._renderer.startup()
        self._renderer_test.startup()

    def __test_name(self) -> str:
        return f"{self.__module__}.{self.__class__.__name__}.{inspect.stack()[2][3]}"

    async def tearDown(self):
        self._renderer_test.shutdown()
        self._renderer.shutdown()

        self._renderer_test = None
        self._renderer = None
        self._app_window_factory = None
        self._settings = None


    async def test_1_render_triangle(self):
        app_window = self._app_window_factory.create_window_from_settings()
        app_window.startup_with_desc(
            title="Renderer test OS window",
            width=300,
            height=300,
            x=omni.appwindow.POSITION_CENTERED,
            y=omni.appwindow.POSITION_CENTERED,
            decorations=True,
            resize=True,
            always_on_top=False,
            scale_to_monitor=False,
            dpi_scale_override=-1.0
        )
        self._renderer.attach_app_window(app_window)
        self._app_window_factory.set_default_window(app_window)

        self._renderer_test.startup_graphics_resources_for_app_window(app_window, 0)

        test_name = self.__test_name()
        FILENAME = "test_1_render_triangle.png"

        await self.wait_n_updates()
        diff = await omni.kit.test_helpers_gfx.capture_and_compare(FILENAME, THRESHOLD, OUTPUTS_DIR, GOLDEN_DIR, app_window)
        if diff != 0: # pragma: no cover
            carb.log_warn(f"[{test_name}] the generated image has max difference {diff}")
            if diff > THRESHOLD:
                carb.log_error(f'The generated image {FILENAME} has a difference of {diff}, but max difference is {THRESHOLD}')
                self.assertTrue(False)

        self._renderer_test.shutdown_graphics_resources_for_app_window(app_window)

        self._app_window_factory.set_default_window(None)
        self._renderer.detach_app_window(app_window)
        app_window.shutdown()
        app_window = None

    async def test_2_multiwnd_render_triangle(self):
        app_window1 = self._app_window_factory.create_window_from_settings()
        app_window1.startup_with_desc(
            title="Renderer test OS window 1",
            width=250,
            height=250,
            x=omni.appwindow.POSITION_CENTERED,
            y=omni.appwindow.POSITION_CENTERED,
            decorations=True,
            resize=True,
            always_on_top=False,
            scale_to_monitor=False,
            dpi_scale_override=-1.0
        )
        self._renderer.attach_app_window(app_window1)

        pos = app_window1.get_position()
        app_window2 = self._app_window_factory.create_window_from_settings()
        app_window2.startup_with_desc(
            title="Renderer test OS window 2",
            width=350,
            height=350,
            x=pos[0] + 30,
            y=pos[1] + 40,
            decorations=True,
            resize=True,
            always_on_top=False,
            scale_to_monitor=False,
            dpi_scale_override=-1.0
        )
        self._renderer.attach_app_window(app_window2)

        self._app_window_factory.set_default_window(app_window1)

        self._renderer_test.startup_graphics_resources_for_app_window(app_window1, 0)
        self._renderer_test.startup_graphics_resources_for_app_window(app_window2, 3)

        test_name = self.__test_name()

        FILENAME1 = "test_2_multiwnd_render_triangle_1.png"
        FILENAME2 = "test_2_multiwnd_render_triangle_2.png"

        omni.kit.test_helpers_gfx.capture(FILENAME1, OUTPUTS_DIR, app_window1)
        omni.kit.test_helpers_gfx.capture(FILENAME2, OUTPUTS_DIR, app_window2)

        await self.wait_n_updates()

        diff1 = omni.kit.test_helpers_gfx.finalize_capture_and_compare(FILENAME1, THRESHOLD, OUTPUTS_DIR, GOLDEN_DIR, app_window1)
        if diff1 != 0: # pragma: no cover
            carb.log_warn(f"[{test_name}] the generated image has max difference {diff1}")
            if diff1 > THRESHOLD:
                carb.log_error(f'The generated image {FILENAME1} has a difference of {diff1}, but max difference is {THRESHOLD}')
                self.assertTrue(False)

        diff2 = omni.kit.test_helpers_gfx.finalize_capture_and_compare(FILENAME2, THRESHOLD, OUTPUTS_DIR, GOLDEN_DIR, app_window2)
        if diff2 != 0: # pragma: no cover
            carb.log_warn(f"[{test_name}] the generated image has max difference {diff2}")
            if diff2 > THRESHOLD:
                carb.log_error(f'The generated image {FILENAME2} has a difference of {diff2}, but max difference is {THRESHOLD}')
                self.assertTrue(False)

        self._renderer_test.shutdown_graphics_resources_for_app_window(app_window2)
        self._renderer_test.shutdown_graphics_resources_for_app_window(app_window1)

        self._app_window_factory.set_default_window(None)

        self._renderer.detach_app_window(app_window2)
        app_window2.shutdown()
        app_window2 = None
        self._renderer.detach_app_window(app_window1)
        app_window1.shutdown()
        app_window1 = None
