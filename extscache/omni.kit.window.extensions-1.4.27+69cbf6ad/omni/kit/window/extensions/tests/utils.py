import asyncio

import carb
import carb.eventdispatcher
import omni.kit.app
import omni.kit.ui_test as ui_test
import omni.kit.window.extensions

first_show: bool = True

# pylint: disable=protected-access


class SyncEventHandler:  # pragma: no cover
    def __init__(self):
        print("creating SyncEventHandler")
        self._future_test = asyncio.Future()
        self._events = (
            omni.ext.GLOBAL_EVENT_EXTENSION_PULL_BEGIN_DEFERRED,
            omni.ext.GLOBAL_EVENT_EXTENSION_PULL_END_FAILURE,
            omni.ext.GLOBAL_EVENT_EXTENSION_PULL_END_SUCCESS,
            omni.ext.GLOBAL_EVENT_REGISTRY_REFRESH_BEGIN_DEFERRED,
            omni.ext.GLOBAL_EVENT_REGISTRY_REFRESH_END_FAILURE,
            omni.ext.GLOBAL_EVENT_REGISTRY_REFRESH_END_SUCCESS,
            omni.ext.GLOBAL_EVENT_FOLDER_CHANGED,
            omni.ext.GLOBAL_EVENT_SCRIPT_CHANGED,
        )
        self._sync_event_sub = [
            carb.eventdispatcher.get_eventdispatcher().observe_event(event_name=evt, on_event=self._on_sync_event)
            for evt in self._events
        ]

    def __del__(self):
        self.destroy()

    def destroy(self):
        self._future_test = None
        self._sync_event_sub = None

    def _on_sync_event(self, event):
        if event.event_name in self._events:
            print(f"got omni.ext event {event.event_name}")
        else:
            print(f"got unknown omni.ext event {event.event_name} - Skipping")
            return

        if self._future_test and not self._future_test.done():
            self._future_test.set_result(event.type)

    async def wait_for_sync_event(self, timeout=120.0) -> bool:
        print("wait_for_sync_event")

        async def wait_for_event():
            print("waiting for omni.ext event ....")
            await self._future_test

        try:
            await asyncio.wait_for(wait_for_event(), timeout=timeout)
            print("wait_for_sync_event returning True")
            return True

        except asyncio.TimeoutError:
            carb.log_warn("wait_for_sync_event timeout waiting for sync event")
            print("wait_for_sync_event returning False")
            return False
        finally:
            self._future_test = None


async def open_window_and_sync(show_properties: bool):
    global first_show

    instance = omni.kit.window.extensions.get_instance()()
    instance.show_window(True)
    if show_properties:
        instance._window._show_properties()
    await ui_test.human_delay(10)

    if not carb.settings.get_settings().get("/exts/omni.kit.window.extensions/sync_registry"):
        print("sync_registry disabled")
        return

    if first_show:  # pragma: no cover
        sync = SyncEventHandler()
        if await sync.wait_for_sync_event():
            first_show = False
        sync.destroy()
        del sync
    else:  # pragma: no cover
        print("extensions database already synced")
