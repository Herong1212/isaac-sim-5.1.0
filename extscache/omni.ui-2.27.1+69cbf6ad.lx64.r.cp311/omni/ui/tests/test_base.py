## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
__all__ = ["OmniUiTest"]

"""The base class for all the visual tests in omni.ui"""
from .compare_utils import capture_and_compare, CompareMetric
import carb
import carb.input
import carb.windowing
import omni.appwindow
import omni.kit.test
import omni.ui as ui
from functools import lru_cache
import pathlib
from carb.input import MouseEventType

DEVICE_TO_BLOCK = [carb.input.DeviceType.GAMEPAD, carb.input.DeviceType.KEYBOARD, carb.input.DeviceType.MOUSE]

@lru_cache()
def _get_windowing() -> carb.windowing.IWindowing:
    try:
        return carb.windowing.acquire_windowing_interface()
    except RuntimeError:
        # OVC: RuntimeError: Failed to acquire interface: card::windowing::IWindowing
        return None


async def next_resize_async():
    """
    Wait for the next event in the resize event stream of IAppWindow::getWindowResizeEventStream.

    We need it because the window resize event stream is independent of IApp::getUpdateEventStream. Without this
    function it's possible that resize happens several updates after. It's reproducible on Linux Release build.
    """
    return await omni.appwindow.get_default_app_window().get_window_resize_event_stream().next_event()


class OmniUiTest(omni.kit.test.AsyncTestCase):
    """
    Base class for testing Omni::UI.

    Has methods to initialize/return window and compare images.
    """

    # Maximum allowed difference when comparing two images, default compare metric is mean error.
    # Set a default threshold that is enough to filter out the artifacts of antialiasing on the different systems.
    MEAN_ERROR_THRESHOLD = 0.01
    MEAN_ERROR_SQUARED_THRESHOLD = 1e-5
    THRESHOLD = MEAN_ERROR_THRESHOLD  # default threshold
    SYNCTEXTURELOAD = "/exts/omni.ui/Image/syncTextureLoad"

    def __init__(self, tests=()):
        super().__init__(tests)
        self._saved_width = None
        self._saved_height = None
        self._restore_window = None
        self._restore_position = None
        self._restore_dock_window = None
        self._need_finalize = False
        self.__device_state = [None for _ in DEVICE_TO_BLOCK]
        self.__syncTextureLoad_orig = carb.settings.get_settings().get(self.SYNCTEXTURELOAD)
        carb.settings.get_settings().set(self.SYNCTEXTURELOAD, True)
        if self.__syncTextureLoad_orig != True:
            carb.log_warn(f"OMPE-38818: [{self.SYNCTEXTURELOAD}] is being set to True to workaround test instability")

    def __del__(self):
        carb.settings.get_settings().set(self.SYNCTEXTURELOAD, self.__syncTextureLoad_orig)

    async def setUp(self):
        """Before running each test"""
        self._need_finalize = False

    async def tearDown(self):
        """After running each test"""
        if self._need_finalize:  # keep track of whether we get our closing finalize function
            carb.log_warn(
                "After a create_test_area, create_test_window, or docked_test_window call, finish the test with a finalize_test or finalize_test_no_image "
                "call, to restore the window and settings."
            )
            self._need_finalize = False

    async def wait_n_updates(self, n_frames: int = 3):
        app = omni.kit.app.get_app()
        for _ in range(n_frames):
            await app.next_update_async()

    @property
    def __test_name(self) -> str:
        """
        The full name of the test.

        It has the name of the module, class and the current test function
        """
        return f"{self.__module__}.{self.__class__.__name__}.{self._testMethodName}"

    def __get_golden_img_name(self, golden_img_name: str, golden_img_dir: str, test_name: str):
        if not golden_img_name:
            golden_img_name = f"{test_name}.png"
            # Test name includes a module, which makes it long. Filepath length can exceed path limit on windows.
            # We want to trim it, but for backward compatibility by default keep golden image name the same. But when
            # golden image does not exist and generated first time use shorter name.
            if golden_img_dir and not golden_img_dir.joinpath(golden_img_name).exists():
                # Example: omni.example.ui.tests.example_ui_test.TestExampleUi.test_ScrollingFrame -> test_ScrollingFrame
                pos = test_name.rfind(".test_")
                if pos > 0:
                    test_name = test_name[(pos + 1) :]
                    golden_img_name = f"{test_name}.png"
        return golden_img_name

    def __block_devices(self, app_window):
        # Save the state
        self.__device_state = [app_window.get_input_blocking_state(device) for device in DEVICE_TO_BLOCK]

        # Set the new state
        for device in DEVICE_TO_BLOCK:
            app_window.set_input_blocking_state(device, True)

    def __restore_devices(self, app_window):
        for device, state in zip(DEVICE_TO_BLOCK, self.__device_state):
            if state is not None:
                app_window.set_input_blocking_state(device, state)
        self.__device_state = [None for _ in DEVICE_TO_BLOCK]

    async def create_test_area(
        self,
        width: int = 256,
        height: int = 256,
        block_devices: bool = True,
    ):
        """Resize the main window"""
        app_window = omni.appwindow.get_default_app_window()
        dpi_scale = ui.Workspace.get_dpi_scale()

        # requested size scaled with dpi
        width_with_dpi = int(width * dpi_scale)
        height_with_dpi = int(height * dpi_scale)

        # Current main window size
        current_width = app_window.get_width()
        current_height = app_window.get_height()

        # If the main window is already has requested size, do nothing
        if width_with_dpi == current_width and height_with_dpi == current_height:
            self._saved_width = None
            self._saved_height = None
        else:
            # Save the size of the main window to be able to restore it at the end of the test
            self._saved_width = current_width
            self._saved_height = current_height

            app_window.resize(width_with_dpi, height_with_dpi)

            # Wait for getWindowResizeEventStream
            await next_resize_async()

        windowing = _get_windowing()
        os_window = app_window.get_window()

        # Move the cursor away to avoid hovering on element and trigger tooltips that break the tests
        if block_devices:
            input_provider = carb.input.acquire_input_provider()
            mouse = app_window.get_mouse()
            input_provider.buffer_mouse_event(mouse, MouseEventType.MOVE, (0, 0), 0, (0, 0))
            if windowing:
                windowing.set_cursor_position(os_window, (0, 0))

        # One frame to move mouse cursor
        await omni.kit.app.get_app().next_update_async()

        if block_devices:
            self.__block_devices(app_window)

        self._restore_window = None
        self._restore_position = None
        self._restore_dock_window = None
        self._need_finalize = True  # keep track of whether we get our closing finalize function

    async def create_test_window(
        self, width: int = 256, height: int = 256, block_devices: bool = True, window_flags=None
    ) -> ui.Window:
        """
        Resize the main window and create a window with the given resolution.

        Returns:
            ui.Window with black background, expended to fill full main window and ready for testing.
        """
        await self.create_test_area(width, height, block_devices=block_devices)

        if window_flags is None:
            window_flags = ui.WINDOW_FLAGS_NO_SCROLLBAR | ui.WINDOW_FLAGS_NO_TITLE_BAR | ui.WINDOW_FLAGS_NO_RESIZE
        window = ui.Window(
            f"{self.__test_name} Test",
            dockPreference=ui.DockPreference.DISABLED,
            flags=window_flags,
            width=width,
            height=height,
            position_x=0,
            position_y=0,
        )

        # Override default background
        window.frame.set_style({"Window": {"background_color": 0xFF000000, "border_color": 0x0, "border_radius": 0}})
        self._need_finalize = True  # keep track of whether we get our closing finalize function

        return window

    async def docked_test_window(
        self,
        window: ui.Window,
        width: int = 256,
        height: int = 256,
        restore_window: ui.Window = None,
        restore_position: ui.DockPosition = ui.DockPosition.SAME,
        block_devices: bool = True,
    ) -> None:
        """
        Resize the main window and use docked window with the given resolution.
        """
        window.undock()

        # Wait for the window to be undocked
        await omni.kit.app.get_app().next_update_async()

        window.focus()

        app_window = omni.appwindow.get_default_app_window()
        dpi_scale = ui.Workspace.get_dpi_scale()

        # requested size scaled with dpi
        width_with_dpi = int(width * dpi_scale)
        height_with_dpi = int(height * dpi_scale)

        # Current main window size
        current_width = app_window.get_width()
        current_height = app_window.get_height()

        # If the main window is already has requested size, do nothing
        if width_with_dpi == current_width and height_with_dpi == current_height:
            self._saved_width = None
            self._saved_height = None
        else:
            # Save the size of the main window to be able to restore it at the end of the test
            self._saved_width = current_width
            self._saved_height = current_height

            app_window.resize(width_with_dpi, height_with_dpi)

            # Wait for getWindowResizeEventStream
            await app_window.get_window_resize_event_stream().next_event()

        if isinstance(window, ui.Window):
            window.flags = ui.WINDOW_FLAGS_NO_SCROLLBAR | ui.WINDOW_FLAGS_NO_TITLE_BAR | ui.WINDOW_FLAGS_NO_RESIZE
        window.width = width
        window.height = height
        window.position_x = 0
        window.position_y = 0

        windowing = _get_windowing()
        os_window = app_window.get_window()

        # Move the cursor away to avoid hovering on element and trigger tooltips that break the tests
        if block_devices:
            input_provider = carb.input.acquire_input_provider()
            mouse = app_window.get_mouse()
            input_provider.buffer_mouse_event(mouse, MouseEventType.MOVE, (0, 0), 0, (0, 0))
            if windowing:
                windowing.set_cursor_position(os_window, (0, 0))

        # One frame to move mouse cursor
        await omni.kit.app.get_app().next_update_async()

        if block_devices:
            self.__block_devices(app_window)

        self._restore_dock_window = window
        self._restore_window = restore_window
        self._restore_position = restore_position
        self._need_finalize = True  # keep track of whether we get our closing finalize function

    async def finalize_test_no_image(self):
        """Restores the main window once a test is complete."""
        # Restore main window resolution if it was saved
        if self._saved_width is not None and self._saved_height is not None:
            app_window = omni.appwindow.get_default_app_window()
            app_window.resize(self._saved_width, self._saved_height)
            # Wait for getWindowResizeEventStream
            await next_resize_async()

        if self._restore_dock_window and self._restore_window:
            self._restore_dock_window.dock_in(self._restore_window, self._restore_position)

        self._restore_window = None
        self._restore_position = None
        self._restore_dock_window = None

        app_window = omni.appwindow.get_default_app_window()
        self.__restore_devices(app_window)
        self._need_finalize = False

    async def capture_and_compare(
        self,
        threshold=None,
        golden_img_dir: pathlib.Path = None,
        golden_img_name=None,
        use_log: bool = True,
        cmp_metric=CompareMetric.MEAN_ERROR,
        test_name: str = None,
        hide_menu_bar: bool = True
    ):
        """Capture current frame and compare it with the golden image. Assert if the diff is more than given threshold."""
        test_name = test_name or f"{self.__test_name}"
        golden_img_name = self.__get_golden_img_name(golden_img_name, golden_img_dir, test_name)

        menu_bar = None
        old_visible = None
        try:
            try:
                from omni.kit.mainwindow import get_main_window
                main_window = get_main_window()
                menu_bar = main_window.get_main_menu_bar()
                old_visible = menu_bar.visible
                if hide_menu_bar:
                    menu_bar.visible = False
            except ImportError:
                pass

            # set default threshold for each compare metric
            if threshold is None:
                if cmp_metric == CompareMetric.MEAN_ERROR:
                    threshold = self.MEAN_ERROR_THRESHOLD
                elif cmp_metric == CompareMetric.MEAN_ERROR_SQUARED:
                    threshold = self.MEAN_ERROR_SQUARED_THRESHOLD
                elif cmp_metric == CompareMetric.PIXEL_COUNT:
                    threshold = 10  # arbitrary number

            diff = await capture_and_compare(
                golden_img_name, threshold, golden_img_dir, use_log=use_log, cmp_metric=cmp_metric
            )
            if diff != 0:
                carb.log_warn(f"[{test_name}] the generated image has difference {diff}")

            self.assertTrue(
                (diff is not None and diff < threshold),
                msg=f"The image for test '{test_name}' doesn't match the golden one. Difference of {diff} is is not less than threshold of {threshold}.",
            )
        finally:
            if menu_bar:
                menu_bar.visible = old_visible

    async def finalize_test(
        self,
        threshold=None,
        golden_img_dir: pathlib.Path = None,
        golden_img_name=None,
        use_log: bool = True,
        cmp_metric=CompareMetric.MEAN_ERROR,
        test_name: str = None,
        hide_menu_bar: bool = True,
        zero_mouse: bool = False
    ):
        if zero_mouse:
            # mouse position can effect UI due to hovered color, so move mouse to 0, 0
            app_window = omni.appwindow.get_default_app_window()
            windowing = _get_windowing()
            if windowing:
                windowing.set_cursor_position(app_window.get_window(), (int(0), int(0)))
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()

        try:
            test_name = test_name or f"{self.__test_name}"
            golden_img_name = self.__get_golden_img_name(golden_img_name, golden_img_dir, test_name)

            await self.capture_and_compare(threshold,
                                        golden_img_dir,
                                        golden_img_name,
                                        use_log,
                                        cmp_metric,
                                        test_name,
                                        hide_menu_bar)
        finally:
            await self.finalize_test_no_image()
