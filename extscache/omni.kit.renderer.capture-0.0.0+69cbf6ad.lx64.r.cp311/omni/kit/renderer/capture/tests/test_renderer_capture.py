import os
import sys
import inspect
import pathlib
import importlib

import carb
import carb.dictionary
import carb.settings
import carb.tokens

import omni.appwindow
import omni.kit.app
import omni.kit.test
import omni.kit.renderer.bind
import omni.kit.renderer_capture
import omni.kit.renderer_capture_test

OUTPUTS_DIR = omni.kit.test.get_test_output_path()
USE_TUPLES = True
# Ancient hack coming from dark times
SET_ALPHA_TO_1_SETTING_PATH = "/app/captureFrame/setAlphaTo1"

class RendererCaptureTest(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._settings = carb.settings.get_settings()
        self._dict = carb.dictionary.acquire_dictionary_interface()
        self._app_window_factory = omni.appwindow.acquire_app_window_factory_interface()
        self._renderer = omni.kit.renderer.bind.acquire_renderer_interface()
        self._renderer_capture = omni.kit.renderer_capture.acquire_renderer_capture_interface()
        self._renderer_capture_test = omni.kit.renderer_capture_test.acquire_renderer_capture_test_interface()
        self._renderer.startup()
        self._renderer_capture.startup()
        self._renderer_capture_test.startup()

    def __test_name(self) -> str:
        return f"{self.__class__.__name__}.{inspect.stack()[1][3]}"

    async def tearDown(self):
        self._renderer_capture_test.shutdown()
        self._renderer_capture.shutdown()
        self._renderer.shutdown()

        self._renderer_capture_test = None
        self._renderer_capture = None
        self._renderer = None
        self._app_window_factory = None
        self._settings = None

    def _create_and_attach_window(self, w, h, window_type):
        app_window = self._app_window_factory.create_window_by_type(window_type)
        app_window.startup_with_desc(
            title="Renderer capture test OS window",
            width=w,
            height=h,
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

        return app_window

    def _detach_and_destroy_window(self, app_window):
        self._app_window_factory.set_default_window(None)
        self._renderer.detach_app_window(app_window)
        app_window.shutdown()

    def _capture_callback(self, buf, buf_size, w, h, fmt):
        if USE_TUPLES:
            self._captured_buffer = omni.kit.renderer_capture.convert_raw_bytes_to_rgba_tuples(buf, buf_size, w, h, fmt)
        else:
            self._captured_buffer = omni.kit.renderer_capture.convert_raw_bytes_to_list(buf, buf_size, w, h, fmt)
        self._captured_buffer_w = w
        self._captured_buffer_h = h
        self._captured_buffer_fmt = fmt

    def _get_pil_image_from_captured_data(self):
        from PIL import Image
        image = Image.new('RGBA', [self._captured_buffer_w, self._captured_buffer_h])

        if USE_TUPLES:
            image.putdata(self._captured_buffer)
        else:
            buf_channel_it = iter(self._captured_buffer)
            captured_buffer_tuples = list(zip(buf_channel_it, buf_channel_it, buf_channel_it, buf_channel_it))
            image.putdata(captured_buffer_tuples)

        return image

    def _get_pil_image_size_data(self, path):
        from PIL import Image
        image = Image.open(path)
        image_data = list(image.getdata())
        image_w, image_h = image.size
        image.close()
        return image_w, image_h, image_data

    def _disable_alpha_to_1(self):
        self._settings.set_default(SET_ALPHA_TO_1_SETTING_PATH, False)
        self._setAlphaTo1 = self._settings.get(SET_ALPHA_TO_1_SETTING_PATH)
        self._settings.set(SET_ALPHA_TO_1_SETTING_PATH, False)

    def _restore_alpha_to_1(self):
        self._settings.set(SET_ALPHA_TO_1_SETTING_PATH, self._setAlphaTo1)


    async def test_0001_capture_swapchain_to_file(self):
        test_name = self.__test_name()
        TEST_IMG_PATH = os.path.join(OUTPUTS_DIR, test_name + ".png")
        TEST_IMG_W = 8
        TEST_IMG_H = 8
        TEST_COLOR = (255, 0, 0, 255)

        app_window = self._create_and_attach_window(TEST_IMG_W, TEST_IMG_H, omni.appwindow.WindowType.VIRTUAL)

        test_color_unit = tuple(c / 255.0 for c in TEST_COLOR)
        self._renderer.set_clear_color(app_window, test_color_unit)
        self._renderer_capture.capture_next_frame_swapchain(TEST_IMG_PATH, app_window)

        await omni.kit.app.get_app().next_update_async()

        self._renderer_capture.wait_async_capture(app_window)

        image_size_data = self._get_pil_image_size_data(TEST_IMG_PATH)

        self.assertEqual(len(image_size_data), 3)
        self.assertEqual(image_size_data[0], TEST_IMG_W)
        self.assertEqual(image_size_data[1], TEST_IMG_H)
        self.assertEqual(image_size_data[2][0], TEST_COLOR)

        self._detach_and_destroy_window(app_window)
        app_window = None

    async def test_0002_capture_swapchain_callback(self):
        test_name = self.__test_name()
        TEST_IMG_PATH = os.path.join(OUTPUTS_DIR, test_name + ".png")
        TEST_IMG_W = 16
        TEST_IMG_H = 16
        TEST_COLOR = (0, 255, 255, 255)

        app_window = self._create_and_attach_window(TEST_IMG_W, TEST_IMG_H, omni.appwindow.WindowType.VIRTUAL)

        test_color_unit = tuple(c / 255.0 for c in TEST_COLOR)
        self._renderer.set_clear_color(app_window, test_color_unit)
        self._renderer_capture.capture_next_frame_swapchain_callback(self._capture_callback, app_window)

        await omni.kit.app.get_app().next_update_async()

        self._renderer_capture.wait_async_capture(app_window)

        image = self._get_pil_image_from_captured_data()
        image.save(TEST_IMG_PATH)

        self.assertEqual(self._captured_buffer_w, TEST_IMG_W)
        self.assertEqual(self._captured_buffer_h, TEST_IMG_H)
        if USE_TUPLES:
            self.assertEqual(self._captured_buffer[0], TEST_COLOR)
        else:
            self.assertEqual(self._captured_buffer[0], TEST_COLOR[0])
            self.assertEqual(self._captured_buffer[1], TEST_COLOR[1])
            self.assertEqual(self._captured_buffer[2], TEST_COLOR[2])
            self.assertEqual(self._captured_buffer[3], TEST_COLOR[3])

        self._detach_and_destroy_window(app_window)
        app_window = None

    async def test_0003_capture_texture_to_file(self):
        test_name = self.__test_name()
        TEST_IMG_PATH = os.path.join(OUTPUTS_DIR, test_name + ".png")
        TEST_IMG_W = 4
        TEST_IMG_H = 4
        TEST_COLOR = (255, 255, 0, 255)
        app_window = self._create_and_attach_window(12, 12, omni.appwindow.WindowType.VIRTUAL)

        test_color_unit = tuple(c / 255.0 for c in TEST_COLOR)
        texture = self._renderer_capture_test.create_solid_color_texture(test_color_unit, TEST_IMG_W, TEST_IMG_H)
        self._renderer_capture.capture_next_frame_texture(TEST_IMG_PATH, texture)

        await omni.kit.app.get_app().next_update_async()

        self._renderer_capture.wait_async_capture(app_window)

        image_size_data = self._get_pil_image_size_data(TEST_IMG_PATH)

        self.assertEqual(len(image_size_data), 3)
        self.assertEqual(image_size_data[0], TEST_IMG_W)
        self.assertEqual(image_size_data[1], TEST_IMG_H)
        self.assertEqual(image_size_data[2][0], TEST_COLOR)

        self._renderer_capture_test.cleanup_gpu_resources()
        self._detach_and_destroy_window(app_window)
        app_window = None

    async def test_0004_capture_texture_callback(self):
        test_name = self.__test_name()
        TEST_IMG_PATH = os.path.join(OUTPUTS_DIR, test_name + ".png")
        TEST_IMG_W = 6
        TEST_IMG_H = 6
        TEST_COLOR = (255, 0, 255, 255)

        app_window = self._create_and_attach_window(12, 12, omni.appwindow.WindowType.VIRTUAL)

        test_color_unit = tuple(c / 255.0 for c in TEST_COLOR)
        texture = self._renderer_capture_test.create_solid_color_texture(test_color_unit, TEST_IMG_W, TEST_IMG_H)
        self._renderer_capture.capture_next_frame_texture_callback(self._capture_callback, texture)

        await omni.kit.app.get_app().next_update_async()

        self._renderer_capture.wait_async_capture(app_window)

        image = self._get_pil_image_from_captured_data()
        image.save(TEST_IMG_PATH)

        self.assertEqual(self._captured_buffer_w, TEST_IMG_W)
        self.assertEqual(self._captured_buffer_h, TEST_IMG_H)
        if USE_TUPLES:
            self.assertEqual(self._captured_buffer[0], TEST_COLOR)
        else:
            self.assertEqual(self._captured_buffer[0], TEST_COLOR[0])
            self.assertEqual(self._captured_buffer[1], TEST_COLOR[1])
            self.assertEqual(self._captured_buffer[2], TEST_COLOR[2])
            self.assertEqual(self._captured_buffer[3], TEST_COLOR[3])

        self._renderer_capture_test.cleanup_gpu_resources()
        self._detach_and_destroy_window(app_window)
        app_window = None

    async def test_0005_capture_rp_resource_to_file(self):
        test_name = self.__test_name()
        TEST_IMG_PATH = os.path.join(OUTPUTS_DIR, test_name + ".png")
        TEST_IMG_W = 5
        TEST_IMG_H = 5
        TEST_COLOR = (0, 255, 0, 255)
        app_window = self._create_and_attach_window(12, 12, omni.appwindow.WindowType.VIRTUAL)

        test_color_unit = tuple(c / 255.0 for c in TEST_COLOR)
        rp_resource = self._renderer_capture_test.create_solid_color_rp_resource(test_color_unit, TEST_IMG_W, TEST_IMG_H)
        self._renderer_capture.capture_next_frame_rp_resource(TEST_IMG_PATH, rp_resource)

        await omni.kit.app.get_app().next_update_async()

        self._renderer_capture.wait_async_capture(app_window)

        image_size_data = self._get_pil_image_size_data(TEST_IMG_PATH)

        self.assertEqual(len(image_size_data), 3)
        self.assertEqual(image_size_data[0], TEST_IMG_W)
        self.assertEqual(image_size_data[1], TEST_IMG_H)
        self.assertEqual(image_size_data[2][0], TEST_COLOR)

        self._renderer_capture_test.cleanup_gpu_resources()
        self._detach_and_destroy_window(app_window)
        app_window = None

    async def test_0006_capture_rp_resource_callback(self):
        test_name = self.__test_name()
        TEST_IMG_PATH = os.path.join(OUTPUTS_DIR, test_name + ".png")
        TEST_IMG_W = 6
        TEST_IMG_H = 6
        TEST_COLOR = (0, 0, 255, 255)

        app_window = self._create_and_attach_window(12, 12, omni.appwindow.WindowType.VIRTUAL)

        test_color_unit = tuple(c / 255.0 for c in TEST_COLOR)
        rp_resource = self._renderer_capture_test.create_solid_color_rp_resource(test_color_unit, TEST_IMG_W, TEST_IMG_H)
        self._renderer_capture.capture_next_frame_rp_resource_callback(self._capture_callback, rp_resource)

        await omni.kit.app.get_app().next_update_async()

        self._renderer_capture.wait_async_capture(app_window)

        image = self._get_pil_image_from_captured_data()
        image.save(TEST_IMG_PATH)

        self.assertEqual(self._captured_buffer_w, TEST_IMG_W)
        self.assertEqual(self._captured_buffer_h, TEST_IMG_H)
        if USE_TUPLES:
            self.assertEqual(self._captured_buffer[0], TEST_COLOR)
        else:
            self.assertEqual(self._captured_buffer[0], TEST_COLOR[0])
            self.assertEqual(self._captured_buffer[1], TEST_COLOR[1])
            self.assertEqual(self._captured_buffer[2], TEST_COLOR[2])
            self.assertEqual(self._captured_buffer[3], TEST_COLOR[3])

        self._renderer_capture_test.cleanup_gpu_resources()
        self._detach_and_destroy_window(app_window)
        app_window = None

    async def test_0007_capture_os_swapchain_to_file(self):
        test_name = self.__test_name()
        TEST_IMG_PATH = os.path.join(OUTPUTS_DIR, test_name + ".png")
        TEST_IMG_W = 256
        TEST_IMG_H = 32
        TEST_COLOR = (255, 128, 0, 255)

        app_window = self._create_and_attach_window(TEST_IMG_W, TEST_IMG_H, omni.appwindow.WindowType.OS)

        test_color_unit = tuple(c / 255.0 for c in TEST_COLOR)
        self._renderer.set_clear_color(app_window, test_color_unit)
        self._renderer_capture.capture_next_frame_swapchain(TEST_IMG_PATH, app_window)

        await omni.kit.app.get_app().next_update_async()

        self._renderer_capture.wait_async_capture(app_window)

        image_size_data = self._get_pil_image_size_data(TEST_IMG_PATH)

        self.assertEqual(len(image_size_data), 3)
        self.assertEqual(image_size_data[0], TEST_IMG_W)
        self.assertEqual(image_size_data[1], TEST_IMG_H)
        self.assertEqual(image_size_data[2][0], TEST_COLOR)

        self._detach_and_destroy_window(app_window)
        app_window = None

    async def test_0008_capture_transparent_swapchain_to_file(self):
        self._disable_alpha_to_1()

        test_name = self.__test_name()
        TEST_IMG_PATH = os.path.join(OUTPUTS_DIR, test_name + ".png")
        TEST_IMG_W = 8
        TEST_IMG_H = 8
        TEST_COLOR = (255, 0, 0, 0)

        app_window = self._create_and_attach_window(TEST_IMG_W, TEST_IMG_H, omni.appwindow.WindowType.VIRTUAL)

        test_color_unit = tuple(c / 255.0 for c in TEST_COLOR)
        self._renderer.set_clear_color(app_window, test_color_unit)
        self._renderer_capture.capture_next_frame_swapchain(TEST_IMG_PATH, app_window)

        await omni.kit.app.get_app().next_update_async()

        self._renderer_capture.wait_async_capture(app_window)

        image_size_data = self._get_pil_image_size_data(TEST_IMG_PATH)

        self.assertEqual(len(image_size_data), 3)
        self.assertEqual(image_size_data[0], TEST_IMG_W)
        self.assertEqual(image_size_data[1], TEST_IMG_H)
        self.assertEqual(image_size_data[2][0], TEST_COLOR)

        self._detach_and_destroy_window(app_window)
        app_window = None

        self._restore_alpha_to_1()

    async def test_0009_capture_transparent_swapchain_callback(self):
        self._disable_alpha_to_1()

        test_name = self.__test_name()
        TEST_IMG_PATH = os.path.join(OUTPUTS_DIR, test_name + ".png")
        TEST_IMG_W = 16
        TEST_IMG_H = 16
        TEST_COLOR = (0, 255, 255, 0)

        app_window = self._create_and_attach_window(TEST_IMG_W, TEST_IMG_H, omni.appwindow.WindowType.VIRTUAL)

        test_color_unit = tuple(c / 255.0 for c in TEST_COLOR)
        self._renderer.set_clear_color(app_window, test_color_unit)
        self._renderer_capture.capture_next_frame_swapchain_callback(self._capture_callback, app_window)

        await omni.kit.app.get_app().next_update_async()

        self._renderer_capture.wait_async_capture(app_window)

        image = self._get_pil_image_from_captured_data()
        image.save(TEST_IMG_PATH)

        self.assertEqual(self._captured_buffer_w, TEST_IMG_W)
        self.assertEqual(self._captured_buffer_h, TEST_IMG_H)
        if USE_TUPLES:
            self.assertEqual(self._captured_buffer[0], TEST_COLOR)
        else:
            self.assertEqual(self._captured_buffer[0], TEST_COLOR[0])
            self.assertEqual(self._captured_buffer[1], TEST_COLOR[1])
            self.assertEqual(self._captured_buffer[2], TEST_COLOR[2])
            self.assertEqual(self._captured_buffer[3], TEST_COLOR[3])

        self._detach_and_destroy_window(app_window)
        app_window = None

        self._restore_alpha_to_1()

    async def __test_capture_rp_resource_with_format(self, format_desc_item):
        test_name = self.__test_name()
        TEST_IMG_PATH_NOEXT = os.path.join(OUTPUTS_DIR, test_name)
        TEST_IMG_W = 15
        TEST_IMG_H = 15
        TEST_COLOR = (12.34, 34.56, 67.89, 128.0)
        app_window = self._create_and_attach_window(12, 12, omni.appwindow.WindowType.VIRTUAL)

        files = {}

        format_desc_item["format"] = "exr"

        rp_resource = self._renderer_capture_test.create_solid_color_rp_resource_hdr(TEST_COLOR, TEST_IMG_W, TEST_IMG_H)

        async def capture():
            filename = TEST_IMG_PATH_NOEXT + "_" + format_desc_item["compression"] + ".exr"
            files[format_desc_item["compression"]] = filename
            self._renderer_capture.capture_next_frame_rp_resource_to_file(filename, rp_resource, None, format_desc_item)
            await omni.kit.app.get_app().next_update_async()
            self._renderer_capture.wait_async_capture(app_window)


        format_desc_item["compression"] = "none"
        await capture()

        format_desc_item["compression"] = "rle"
        await capture()

        format_desc_item["compression"] = "b44"
        await capture()

        file_sizes = {}
        for file_key, file_path in files.items():
            file_sizes[file_key] = os.path.getsize(file_path)

        self.assertNotEqual(file_sizes["none"], file_sizes["rle"])
        self.assertNotEqual(file_sizes["none"], file_sizes["b44"])
        self.assertNotEqual(file_sizes["rle"], file_sizes["b44"])

        self._renderer_capture_test.cleanup_gpu_resources()
        self._detach_and_destroy_window(app_window)
        app_window = None

    async def test_0010_capture_rp_resource_hdr_to_file_carb_dict(self):
        format_desc_item = self._dict.create_item(None, "", carb.dictionary.ItemType.DICTIONARY)
        await self.__test_capture_rp_resource_with_format(format_desc_item)

    async def test_0010_capture_rp_resource_hdr_to_file_py_dict(self):
        format_desc_item = {}
        await self.__test_capture_rp_resource_with_format(format_desc_item)
