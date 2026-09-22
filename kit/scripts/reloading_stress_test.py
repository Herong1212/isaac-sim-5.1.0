import argparse
import asyncio
import time
import carb
import carb.eventdispatcher
import carb.events
import omni.kit
import omni.usd
import omni.renderer_capture

from datetime import datetime
from omni.rtx.tests.test_common import wait_for_streaming
from omni.kit.widget.nucleus_connector.connector import NucleusConnector

on_rendering_sub = None
frameCounter = 0
waitFrames = 10
nucleus_success = False

class StageLoader:
    def __init__(self, usd_context) -> None:
        self._usd_context = usd_context
        self._current_url = ""
        ed = carb.eventdispatcher.get_eventdispatcher()
        self._stage_event_sub = [
            ed.observe_event(
                event_name=usd_context.stage_event_name(event),
                on_event=func
            )
            for event, func in (
                (omni.usd.StageEventType.OPENING, self.on_opening),
                (omni.usd.StageEventType.ASSETS_LOADED, lambda _: self.on_assets_loaded()),
                (omni.usd.StageEventType.OPEN_FAILED, lambda _: self.on_open_failed())
            )
        ]
        self._loading = False
        self._future_usd_loaded = asyncio.Future()
        self._start_ts = 0
        self._duration = 0

    def loading(self):
        return self._loading

    def duration(self):
        return self._duration

    async def wait(self, timeout: float = 60.0):
        try:
            await asyncio.wait_for(self._future_usd_loaded, timeout=timeout)
            return self._future_usd_loaded.result()
        except asyncio.TimeoutError:
            self._loading = False
            await self._reset_future(False)


    async def _reset_future(self, result: bool) -> None:
        """Helper method to safely reset the future"""
        if self._future_usd_loaded.done():
            self._future_usd_loaded = asyncio.Future()
        try:
            self._future_usd_loaded.set_result(result)
        except asyncio.InvalidStateError:
            carb.log_warn("Future was in invalid state, created new one")
            self._future_usd_loaded = asyncio.Future()
            self._future_usd_loaded.set_result(result)

    def result(self):
        return self._future_usd_loaded.result()

    def load(self, url: str) -> None:
        if self._loading:
            carb.log_error("*** Cannot load a new stage while one is loading")
            return

        # enable the flag, track the current url being loaded
        self._loading = True
        self._current_url = url

        # Reset the future
        self._future_usd_loaded = asyncio.Future()

        omni.usd.get_context().open_stage(self._current_url)

        return

    def on_opening(self, e):
        url = e["val"]
        if self._loading and url and url in self._current_url:
            self._start_ts = time.monotonic()

    def on_assets_loaded(self):
        if self._loading:
            self._loading = False
            self._duration = time.monotonic() - self._start_ts
            carb.log_info(f"{self._current_url} is loaded in {self._duration}s.")
            self._future_usd_loaded.set_result(True)
        
    def on_open_failed(self):
        if self._loading:
            self._loading = False
            carb.log_error(f"{self._current_url} failed to load.")
            self._future_usd_loaded.set_result(False)


def on_rendering_event(e: carb.eventdispatcher.Event):
    global frameCounter
    frame_number = e["frame_number"]
    if frame_number is not None:
        frameCounter += 1


def on_connect_success(name, url):
    global nucleus_success
    nucleus_success = True
    return


def on_connect_failure(name, url):
    return


async def main(args):
    global on_rendering_sub
    global frameCounter
    global waitFrames
    global nucleus_success

    iteration_times = []  # Track all iteration times
    start_datetime = datetime.now()
    # Next time related vars. are in seconds
    avg_time = 0
    elapsed = 0
    start_time = time.monotonic()
    kit_start_time = 30 # Account for test.unit / kit initialization
    wrapping_out_time = 60 # Account for shutting down
    test_timeout = max(args.timeout/1000 - kit_start_time - wrapping_out_time, 0)

    usdContext = omni.usd.get_context()
    app = omni.kit.app.get_app()
    renderer = omni.renderer_capture.acquire_renderer_capture_interface()

    on_rendering_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
        event_name=usdContext.stage_rendering_event_name(omni.usd.StageRenderingEventType.NEW_FRAME, True),
        on_event=on_rendering_event,
        observer_name="reloading_stress_test"
    )

    print("=" * 70)
    print(f"{args.name} Loading: {args.stage}")

    for i in range(args.iterations):
        iteration_start = time.monotonic()
        time_remaining = test_timeout - elapsed

        print(f"{args.name} Iteration {i + 1} of {args.iterations}")

        # Check if nucleus is reachable
        broken_url = omni.client.break_url(args.stage)
        if broken_url.scheme == 'omniverse':
            server_url = omni.client.make_url(scheme='omniverse', host=broken_url.host)
            nc = NucleusConnector()
            await nc.connect_server_async(broken_url.host, server_url,
                                         on_success_fn=on_connect_success,
                                         on_failed_fn=on_connect_failure)

        if nucleus_success:
            usd_loader = StageLoader(usdContext)
            usd_loader.load(args.stage)
            load_success = await usd_loader.wait(timeout=time_remaining)

            # Exit if file not found or loading takes the remaining time of the test
            if not load_success:
                if usd_loader.result() is False:
                    carb.log_error(f"{args.name} Stage not loaded. Finalizing test.")
                    await app.next_update_async()
                    app.post_uncancellable_quit(-1)
                    return
                else:
                    print(f"{args.name} Stage loading timeout after {time_remaining:.2f}s. Finalizing test.")

                end_datetime = datetime.now()
                print(f"{args.name} Test script started at {start_datetime:%H:%M:%S}. Ended at {end_datetime:%H:%M:%S}")
                await app.next_update_async()
                app.post_uncancellable_quit(0)
                return
        else:
            carb.log_error(f"{args.name} Failed to connect to {broken_url.host} at {server_url}")
            await app.next_update_async()
            app.post_uncancellable_quit(-1)
            return

        # Allow to render n-waitFrames
        frameCounter = 0
        while frameCounter < waitFrames:
            await app.next_update_async()

        # Capture frame if requested during first iteration
        if args.output is not None and i == 0:
            if args.ujitso:
                await wait_for_streaming()
            renderer.capture_next_frame_swapchain(str(args.output))
            await app.next_update_async()
            renderer.wait_async_capture()

        iteration_end = time.monotonic()
        iteration_time = iteration_end - iteration_start
        iteration_times.append(iteration_time)
        elapsed = time.monotonic() - start_time
        avg_time = elapsed / (i + 1)

        print(f"{args.name} Iteration {i + 1} took {iteration_time:.2f}s (avg: {avg_time:.2f}s elapsed: {elapsed:.2f}s)")

        # Exit if the estimated time (elapsed + avg_time)
        # to complete the iteration i+1 is greater than the test timeout
        if test_timeout > 0 and i+1 <= args.iterations:
            if elapsed + avg_time >= test_timeout:
                print(f"{args.name} Timeout likely to be reached for iteration {i+2}. Finalizing test before timeout occurs.")
                break

    # Print final statistics
    if iteration_times:
        print(f"{args.name} Total iterations: {len(iteration_times)}. Avg time per iteration: {avg_time:.2f}s. Total time: {elapsed:.2f}s")

    end_datetime = datetime.now()
    print(f"{args.name} Test script started at {start_datetime:%H:%M:%S}. Ended at {end_datetime:%H:%M:%S}")

    await app.next_update_async()
    app.post_uncancellable_quit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--name", help="Name of the test", type=str, default="", required=False)
    parser.add_argument("--iterations", help="Number of iterations.", type=int, default=100, required=True)
    parser.add_argument("--timeout", help="Maximum time in milliseconds to run iterations", type=int, default=0, required=False)
    parser.add_argument("--stage", help="Full path to USD stage to render", required=False)
    parser.add_argument("--output", help="Prefix path to captured golden including path", required=False)
    parser.add_argument("--ujitso", help="Flag that indicates UJITSO is enabled or disabled", type=bool, default=False, required=False)
    args, unknown = parser.parse_known_args()

    asyncio.ensure_future(main(args))
