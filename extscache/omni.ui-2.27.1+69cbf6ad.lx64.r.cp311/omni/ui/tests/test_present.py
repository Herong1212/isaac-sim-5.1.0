## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from .test_base import OmniUiTest
from functools import partial
import asyncio
from carb.eventdispatcher import get_eventdispatcher
import carb.settings
import csv
import omni.appwindow
import omni.kit.app
import omni.kit.renderer
import omni.ui as ui
import os

color = 0xFF123456
color_settings_path = "/exts/omni.kit.renderer.core/imgui/csvDump/vertexColor"
dump_settings_path = "/exts/omni.kit.renderer.core/imgui/csvDump/path"
enabled_settings_path = "/exts/omni.kit.renderer.core/present/enabled"
present_settings_path = "/app/runLoops/present/rateLimitFrequency"
main_settings_path = "/app/runLoops/main/rateLimitFrequency"
busy_present_settings_path = "/app/runLoops/present/rateLimitUseBusyLoop"
busy_main_settings_path = "/app/runLoops/main/rateLimitUseBusyLoop"
sync_settings_path = "/app/runLoops/main/syncToPresent"
global_sync_settings_path = "/app/runLoopsGlobal/syncToPresent"


async def _moving_rect(window, description: str):
    """
    Setups moving rect in the given window. Setups csv dump from imgui. Reads
    the dump and returns computed FPS for the current (from ImGui renderer point
    of view present) and the main thread.
    """
    rect_size = 50
    speed = 0.02
    max_counter = 1.0
    settings = carb.settings.get_settings()

    # Get a path to dump csv in the _testoutput directory
    temp_path = os.path.join(omni.kit.test.get_test_output_path(), f"moving_rect-{description}.csv")
    # remove any existing file (it's creation will be waited on below)
    try:
        os.remove(temp_path)
    except FileNotFoundError:
        pass

    # pre-roll some frames for UI (to deal with test window resizing)
    for _ in range(90):
        await omni.kit.app.get_app().next_update_async()

    with window.frame:
        with ui.VStack():
            ui.Spacer()
            with ui.HStack(height=rect_size):
                left = ui.Spacer(width=0)
                ui.Rectangle(width=rect_size, style={"background_color": color})
                right = ui.Spacer()
            ui.Spacer()

    # pre-roll even more frames after the UI was built
    for _ in range(90):
        await omni.kit.app.get_app().next_update_async()

    settings.set(color_settings_path, color)
    settings.set(dump_settings_path, temp_path)

    # Move the rect
    counter = 0.0
    while counter <= max_counter:
        await omni.kit.app.get_app().next_update_async()
        counter += speed
        normalized = counter % 2.0
        if normalized > 1.0:
            normalized = 2.0 - normalized
        left.width = ui.Fraction(normalized)
        right.width = ui.Fraction(1.0 - normalized)

    # this is actually going to trigger the dump to temp_path
    settings.set(dump_settings_path, "")

    # now wait for temp_path to be generated
    while not os.path.isfile(temp_path):
        await omni.kit.app.get_app().next_update_async()

    # file should be atomically swapped into place fully written
    # but wait one frame before reading just in case
    await omni.kit.app.get_app().next_update_async()

    with open(temp_path, "r") as f:
        reader = csv.reader(f)
        data = [row for row in reader]

    keys, values = zip(*data)
    min_key = int(keys[0])
    keys = [float((int(x) - min_key) / 10000) for x in keys]
    values = [float(x) for x in values]

    time_delta = [keys[i] - keys[i - 1] for i in range(1, len(keys))]
    values = [values[i] - values[i - 1] for i in range(1, len(values))]
    keys = keys[1:]

    min_value, max_value = min(values), max(values)
    margin = (max_value - min_value) * 0.1
    min_value -= margin
    max_value += margin

    min_time = min(time_delta)
    max_time = max(time_delta)

    fps_current = 1000.0 / (sum(time_delta) / len(time_delta))
    fps_main = 1000.0 / (keys[-1] / (max_counter / speed))

    return fps_current, fps_main


def _on_present(future: asyncio.Future, counter, _):
    """
    Sets result of the future after `frames_to_wait` calls.
    """
    if not future.done():
        if counter[0] > 0:
            counter[0] -= 1
        else:
            future.set_result(True)


async def next_update_present_async(frames_to_wait):
    """
    Warms up the present thread because it takes long time to enable it the
    first time. It enables it and waits `frames_to_wait` frames of present
    thread. `next_update_async` doesn't work here because it's related to the
    main thread.
    """

    counter = [frames_to_wait]
    f = asyncio.Future()

    _subscription = get_eventdispatcher().observe_event(
        observer_name="omni.ui Test",
        event_name=omni.kit.renderer.bind.get_renderer_event_name(omni.kit.renderer.bind.RendererEventType.POST_PRESENT_FRAME_BUFFER),
        on_event=partial(_on_present, f, counter)
    )

    await f
    await omni.kit.app.get_app().next_update_async()


class TestPresent(OmniUiTest):
    """
    Testing how the present thread works and how main thread is synchronized to
    the present thread.
    """

    async def setup_fps_test(
        self, set_main: float, set_present: float, expect_main: float, expect_present: float, threshold: float = 0.25
    ):
        """
        Set environment and fps for present and main thread and runs the
        rectangle test. Compares the computed FPS with the given values.
        Threshold is the number FPS can be different from expected.
        """
        window = await self.create_test_window()

        # Save the environment
        settings = carb.settings.get_settings()
        buffer_enabled = settings.get(enabled_settings_path)
        buffer_present_fps = settings.get(present_settings_path)
        buffer_main_fps = settings.get(main_settings_path)
        buffer_present_busy = settings.get(busy_present_settings_path)
        buffer_main_busy = settings.get(busy_main_settings_path)
        buffer_sync = settings.get(sync_settings_path)
        buffer_global_sync = settings.get(global_sync_settings_path)
        finalized = False

        try:
            # Modify the environment
            settings.set(present_settings_path, set_present)
            settings.set(main_settings_path, set_main)
            settings.set(busy_present_settings_path, True)
            settings.set(busy_main_settings_path, True)
            settings.set(sync_settings_path, True)
            settings.set(global_sync_settings_path, True)
            settings.set(enabled_settings_path, True)

            for _ in range(2):
                await omni.kit.app.get_app().next_update_async()

            await next_update_present_async(10)

            fps_current, fps_main = await _moving_rect(
                window, f"{set_main}-{set_present}-{expect_main}-{expect_present}"
            )

            await self.finalize_test_no_image()
            finalized = True

            for _ in range(2):
                await omni.kit.app.get_app().next_update_async()

            # Check the result
            self.assertLess(abs(1.0 - expect_present / fps_current), threshold)
            self.assertLess(abs(1.0 - expect_main / fps_main), threshold)
        finally:
            # Restore the environment
            settings.set(present_settings_path, buffer_present_fps)
            settings.set(main_settings_path, buffer_main_fps)
            settings.set(busy_present_settings_path, buffer_present_busy)
            settings.set(busy_main_settings_path, buffer_main_busy)
            settings.set(sync_settings_path, buffer_sync)
            settings.set(global_sync_settings_path, buffer_global_sync)
            settings.set(enabled_settings_path, buffer_enabled)
            settings.set(dump_settings_path, "")
            settings.set(color_settings_path, "")
            if not finalized:
                await self.finalize_test_no_image()

    async def test_general_30_30(self):
        # Set main 30; present: 30
        # Expect after sync: main 30; present: 30
        await self.setup_fps_test(30.0, 30.0, 30.0, 30.0)

    async def test_general_60_30(self):
        # Set main 60; present: 30
        # Expect after sync: main 60; present: 30
        await self.setup_fps_test(60.0, 30.0, 60.0, 30.0)

    async def test_general_40_30(self):
        # Set main 40; present: 30
        # Expect after sync: main 60; present: 30
        await self.setup_fps_test(40.0, 30.0, 30.0, 30.0)

    async def test_general_20_30(self):
        # Set main 20; present: 30
        # Expect after sync: main 30; present: 30
        await self.setup_fps_test(20.0, 30.0, 15.0, 30.0)
