import omni.kit.app
import omni.kit.test

import carb.windowing
import carb.settings

import omni.appwindow

WINDOW_ENABLED_PATH = "/app/window/enabled"
LINUX_WM_LATENCY_MAX = 100

class Test(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._windowing = carb.windowing.acquire_windowing_interface()
        self._app_window_factory = omni.appwindow.acquire_app_window_factory_interface()
        self._settings = carb.settings.acquire_settings_interface()

    async def tearDown(self):
        self._app_window_factory = None

    def _cmp_vectors_and_delta(self, vec_result, vec_base, delta):
        return (vec_result[0] == vec_base[0] + delta[0]) and (vec_result[1] == vec_base[1] + delta[1])

    async def test_create_os_window(self):
        self._app_window = self._app_window_factory.create_window_from_settings()
        self._app_window.startup_with_desc(
            title="Test OS window",
            width=100,
            height=100,
            x=omni.appwindow.POSITION_CENTERED,
            y=omni.appwindow.POSITION_CENTERED,
            decorations=True,
            resize=True,
            always_on_top=False,
            scale_to_monitor=False,
            dpi_scale_override=-1.0
        )

        self._native_app_window = self._app_window.get_window()
        self.assertNotEqual(self._native_app_window, None)
        self._windowing.show_window(self._native_app_window)
        await omni.kit.app.get_app().next_update_async()
        self._app_window.shutdown()
        self._app_window = None

    async def test_create_virtual_window(self):
        is_window_enabled = self._settings.get(WINDOW_ENABLED_PATH)
        self._settings.set(WINDOW_ENABLED_PATH, False)
        self._app_window = self._app_window_factory.create_window_from_settings()
        self._app_window.startup_with_desc(
            title="Test virtual window",
            width=100,
            height=100,
            x=omni.appwindow.POSITION_CENTERED,
            y=omni.appwindow.POSITION_CENTERED,
            decorations=True,
            resize=True,
            always_on_top=False,
            scale_to_monitor=False,
            dpi_scale_override=-1.0
        )
        self._native_app_window = self._app_window.get_window()
        self.assertEqual(self._native_app_window, None)
        await omni.kit.app.get_app().next_update_async()
        self._app_window.shutdown()
        self._app_window = None
        self._settings.set(WINDOW_ENABLED_PATH, is_window_enabled)

    async def test_move_os_window(self):
        self._app_window = self._app_window_factory.create_window_from_settings()
        self._app_window.startup_with_desc(
            title="Test OS window",
            width=100,
            height=100,
            x=omni.appwindow.POSITION_CENTERED,
            y=omni.appwindow.POSITION_CENTERED,
            decorations=False,
            resize=True,
            always_on_top=False,
            scale_to_monitor=False,
            dpi_scale_override=-1.0
        )
        self._native_app_window = self._app_window.get_window()
        self.assertNotEqual(self._native_app_window, None)
        self._windowing.show_window(self._native_app_window)

        await omni.kit.app.get_app().next_update_async()

        move_delta = [10, 20]
        pos = self._app_window.get_position()
        pos_native = self._windowing.get_window_position(self._native_app_window)
        self.assertEqual(pos_native[0], pos[0])
        self.assertEqual(pos_native[1], pos[1])

        self._app_window.move(pos[0] + move_delta[0], pos[1] + move_delta[1])
        for i in range(LINUX_WM_LATENCY_MAX):
            await omni.kit.app.get_app().next_update_async()

            # This code is needed due to Linux WM latency; window operations do not happen
            # immediately, and not deterministically
            new_pos = self._app_window.get_position()
            move_happened = self._cmp_vectors_and_delta(new_pos, pos, move_delta)
            if move_happened:
                break

        new_pos = self._app_window.get_position()
        new_pos_native = self._windowing.get_window_position(self._native_app_window)
        self.assertEqual(new_pos[0], pos[0] + move_delta[0])
        self.assertEqual(new_pos[1], pos[1] + move_delta[1])
        self.assertEqual(new_pos_native[0], new_pos[0])
        self.assertEqual(new_pos_native[1], new_pos[1])

        self._app_window.shutdown()
        self._app_window = None

    async def test_resize_os_window(self):
        self._app_window = self._app_window_factory.create_window_from_settings()
        self._app_window.startup_with_desc(
            title="Test OS window",
            width=100,
            height=100,
            x=omni.appwindow.POSITION_CENTERED,
            y=omni.appwindow.POSITION_CENTERED,
            decorations=True,
            resize=True,
            always_on_top=False,
            scale_to_monitor=False,
            dpi_scale_override=-1.0
        )
        self._native_app_window = self._app_window.get_window()
        self.assertNotEqual(self._native_app_window, None)
        self._windowing.show_window(self._native_app_window)

        resize_delta = [10, 20]
        size = self._app_window.get_size()
        size_native = [self._windowing.get_window_width(self._native_app_window), self._windowing.get_window_height(self._native_app_window)]
        self.assertEqual(size_native[0], size[0])
        self.assertEqual(size_native[1], size[1])

        self._app_window.resize(size[0] + resize_delta[0], size[1] + resize_delta[1])
        for i in range(LINUX_WM_LATENCY_MAX):
            await omni.kit.app.get_app().next_update_async()

            # This code is needed due to Linux WM latency; window operations do not happen
            # immediately, and not deterministically
            new_size = self._app_window.get_size()
            resize_happened = self._cmp_vectors_and_delta(new_size, size, resize_delta)
            if resize_happened:
                break

        new_size = self._app_window.get_size()
        new_size_native = [self._windowing.get_window_width(self._native_app_window), self._windowing.get_window_height(self._native_app_window)]
        self.assertEqual(new_size[0], size[0] + resize_delta[0])
        self.assertEqual(new_size[1], size[1] + resize_delta[1])
        self.assertEqual(new_size_native[0], new_size[0])
        self.assertEqual(new_size_native[1], new_size[1])

        self._app_window.shutdown()
        self._app_window = None


    async def test_multiple_os_windows(self):
        self._app_window1 = self._app_window_factory.create_window_from_settings()
        self._app_window1.startup_with_desc(
            title="Test OS window",
            width=100,
            height=100,
            x=omni.appwindow.POSITION_CENTERED,
            y=omni.appwindow.POSITION_CENTERED,
            decorations=True,
            resize=True,
            always_on_top=False,
            scale_to_monitor=False,
            dpi_scale_override=-1.0
        )
        self._native_app_window1 = self._app_window1.get_window()
        self.assertNotEqual(self._native_app_window1, None)
        self._windowing.show_window(self._native_app_window1)

        self._app_window2 = self._app_window_factory.create_window_from_settings()
        self._app_window2.startup_with_desc(
            title="Test OS window",
            width=100,
            height=100,
            x=omni.appwindow.POSITION_CENTERED,
            y=omni.appwindow.POSITION_CENTERED,
            decorations=False,
            resize=True,
            always_on_top=False,
            scale_to_monitor=False,
            dpi_scale_override=-1.0
        )
        self._native_app_window2 = self._app_window2.get_window()
        self.assertNotEqual(self._native_app_window2, None)
        self._windowing.show_window(self._native_app_window2)

        await omni.kit.app.get_app().next_update_async()

        resize_delta = [30, 40]
        size = self._app_window1.get_size()
        size_native = [self._windowing.get_window_width(self._native_app_window1), self._windowing.get_window_height(self._native_app_window1)]
        self.assertEqual(size_native[0], size[0])
        self.assertEqual(size_native[1], size[1])

        move_delta = [50, 60]
        pos = self._app_window2.get_position()
        pos_native = self._windowing.get_window_position(self._native_app_window2)
        self.assertEqual(pos_native[0], pos[0])
        self.assertEqual(pos_native[1], pos[1])

        self._app_window1.resize(size[0] + resize_delta[0], size[1] + resize_delta[1])
        self._app_window2.move(pos[0] + move_delta[0], pos[1] + move_delta[1])

        for i in range(LINUX_WM_LATENCY_MAX):
            await omni.kit.app.get_app().next_update_async()

            # This code is needed due to Linux WM latency; window operations do not happen
            # immediately, and not deterministically
            new_size = self._app_window1.get_size()
            new_pos = self._app_window2.get_position()
            resize_happened = self._cmp_vectors_and_delta(new_size, size, resize_delta)
            move_happened = self._cmp_vectors_and_delta(new_pos, pos, move_delta)

            if resize_happened and move_happened:
                break

        new_size = self._app_window1.get_size()
        new_size_native = [self._windowing.get_window_width(self._native_app_window1), self._windowing.get_window_height(self._native_app_window1)]
        self.assertEqual(new_size[0], size[0] + resize_delta[0])
        self.assertEqual(new_size[1], size[1] + resize_delta[1])
        self.assertEqual(new_size_native[0], new_size[0])
        self.assertEqual(new_size_native[1], new_size[1])

        new_pos = self._app_window2.get_position()
        new_pos_native = self._windowing.get_window_position(self._native_app_window2)
        self.assertEqual(new_pos[0], pos[0] + move_delta[0])
        self.assertEqual(new_pos[1], pos[1] + move_delta[1])
        self.assertEqual(new_pos_native[0], new_pos[0])
        self.assertEqual(new_pos_native[1], new_pos[1])

        self._app_window1.shutdown()
        self._app_window2.shutdown()
        self._app_window1 = None
        self._app_window2 = None

    async def test_create_no_cursor_blink_window(self):
        self._app_window = self._app_window_factory.create_window_from_settings()
        self._app_window.startup_with_desc(
            title="Test window, no cursor blink set",
            width=100,
            height=100,
            x=omni.appwindow.POSITION_CENTERED,
            y=omni.appwindow.POSITION_CENTERED,
            decorations=True,
            resize=True,
            always_on_top=False,
            scale_to_monitor=False,
            dpi_scale_override=-1.0,
            cursor_blink=False
        )

        self._native_app_window = self._app_window.get_window()
        self.assertNotEqual(self._native_app_window, None)
        self._windowing.show_window(self._native_app_window)
        await omni.kit.app.get_app().next_update_async()
        self.assertFalse(self._app_window.get_cursor_blink())
        self._app_window.shutdown()
        self._app_window = None
