import argparse
import asyncio
import json
import time
from pathlib import Path

import carb
import omni.kit
import omni.renderer_capture
import omni.stats
import omni.usd
from carb.eventdispatcher import Event, get_eventdispatcher
from omni.hydra.engine.stats import get_device_info, get_mem_stats
from omni.kit.test_suite.helpers import wait_stage_loading


class StageLoader:
    def __init__(self) -> None:
        self._current_url = ""
        usd = omni.usd.get_context()
        self._stage_event_sub = [
            get_eventdispatcher().observe_event(
                observer_name="omni.hsscclient:load_usd", event_name=usd.stage_event_name(event), on_event=func
            )
            for event, func in (
                (omni.usd.StageEventType.OPENING, self.on_stage_opening),
                (omni.usd.StageEventType.ASSETS_LOADED, lambda _: self.on_assets_loaded()),
                (omni.usd.StageEventType.OPEN_FAILED, lambda _: self.on_load_failed()),
            )
        ]
        self._loading = False
        self._future_usd_loaded = asyncio.Future()
        self._start_ts = 0
        self._duration = 0

    def duration(self):
        return self._duration

    async def wait(self):
        await self._future_usd_loaded

    def result(self):
        return self._future_usd_loaded.result()

    def load(self, url: str) -> None:
        if self._loading:
            carb.log_error("*** Cannot load a new stage while one is loading")
            return

        # enable the flag, track the current url being loaded
        self._loading = True
        self._current_url = url

        omni.usd.get_context().open_stage(self._current_url)

        return

    def on_stage_opening(self, e: Event):
        url = e["val"]
        if self._loading and url and url in self._current_url:
            self._start_ts = time.monotonic()

    def on_assets_loaded(self):
        if self._loading:
            self._loading = False
            self._duration = time.monotonic() - self._start_ts
            carb.log_warn(f"{self._current_url} is loaded in {self._duration}s.")
            self._future_usd_loaded.set_result(True)

    def on_load_failed(self):
        if self._loading:
            self._loading = False
            carb.log_error(f"{self._current_url} failed to load.")
            self._future_usd_loaded.set_result(False)


usd_loader = StageLoader()


def get_omni_stats():
    stats_value = {}
    _stats = omni.stats.get_stats_interface()

    scopes = _stats.get_scopes()
    for scope in scopes:
        scope_name = scope["name"]
        # print(scope_name)
        stats_value[scope_name] = {}
        stat_nodes = _stats.get_stats(scope["scopeId"])
        for stat in stat_nodes:
            stat_item = {
                "name": stat["name"],
                "value": stat["value"],
                "description": stat["description"],
            }
            stats_value[scope_name][stat["name"]] = stat_item

    return stats_value


async def main(largs):

    try:
        app = omni.kit.app.get_app()
        settings_interface = carb.settings.get_settings()
    except AttributeError:
        app = omni.kit.app.get_app_interface()
        settings_interface = omni.kit.settings.get_settings_interface()

    usd_context = omni.usd.get_context()
    await usd_context.new_stage_async()
    carb.log_warn("NEW STAGE ASYNC")
    await wait_stage_loading(120)

    carb.log_warn("WAIT STAGE LOADING")
    output_path = Path(largs.output_folder)
    # load the scene
    usd_loader.load(largs.stage)

    carb.log_warn("Start loading")
    await usd_loader.wait()
    carb.log_warn("End loading")
    if not usd_loader.result():
        app.post_quit()
        return

    # set renderer mode
    if largs.renderer == "rt":
        settings_interface.set_string("/rtx/rendermode", "RaytracedLighting")
    elif largs.renderer == "pt":
        settings_interface.set_string("/rtx/rendermode", "PathTracing")
        settings_interface.set_float("/rtx/pathtracing/totalSpp", 0)

    from omni.kit.viewport.utility import get_active_viewport_window

    viewport_window = get_active_viewport_window()
    resolution = viewport_window.viewport_api.resolution

    await asyncio.sleep(largs.screenshot_pause)
    if largs.fps:
        # measure FPS
        carb.log_warn("Start FPS measuring")
        frame_info = viewport_window.viewport_api.frame_info
        multiplier = frame_info.get("subframe_count", 1)
        fps = viewport_window.viewport_api.fps * multiplier
        carb.log_warn(f"End FPS measuring: {fps}")
    else:
        fps = None

    renderer = omni.renderer_capture.acquire_renderer_capture_interface()
    renderer.capture_next_frame_swapchain(str(output_path / largs.screenshot_file))
    carb.log_warn("PRE-CAPTURE")
    await app.next_update_async()
    renderer.wait_async_capture()
    carb.log_warn("POST-CAPTURE")
    stats_file = output_path / "stats.json"
    stats = {
        "load_time": usd_loader.duration(),
        "fps": fps,
        "resolution": resolution,
        "omni.hydra.engine.stats.get_device_info()": get_device_info(),
        "omni.hydra.engine.stats.get_mem_stats()": get_mem_stats(detailed=False),
        "omni.stats.get_stats_interface()": get_omni_stats(),
    }

    stats_file.write_text(json.dumps(stats, indent=4))
    carb.log_warn(f"Stats are saved to: {stats_file}")

    if largs.keep_running:
        carb.log_warn("You can quit Kit manually.")
    else:
        app.post_uncancellable_quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", help="Full path to USD stage to render", required=True)
    parser.add_argument("--output_folder", help="Full path to the Output Folder", required=True)
    parser.add_argument("--renderer", help="Renderer mode, rt or pt", default="rt")
    parser.add_argument("--screenshot_file", help="Name of screenshot file to dump", default="screenshot.png")
    parser.add_argument("--screenshot_pause", help="Seconds to wait before taking screenshot", default=5, type=int)
    parser.add_argument("--fps", help="Collect FPS", default=False)
    parser.add_argument(
        "--keep_running", help="Whether to keep Kit running after benchmark is complete.", action="store_true"
    )

    args, unknown = parser.parse_known_args()
    asyncio.ensure_future(main(args))
