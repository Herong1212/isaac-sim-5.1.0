import carb
import carb.settings
import omni.kit.app
import omni.ui as ui
from ..preferences_window import PreferenceBuilder, SettingType, PERSISTENT_SETTINGS_PREFIX
from typing import Any
from typing import Dict
from typing import Optional


THREAD_SYNC_PRESETS = [
    (
        "No Pacing",
        {
            "/app/runLoops/main/rateLimitEnabled": True,
            "/app/runLoops/main/rateLimitFrequency": 120,
            "/app/runLoops/main/rateLimitUsePrecisionSleep": True,
            "/app/runLoops/main/syncToPresent": False,
            "/app/runLoops/present/rateLimitEnabled": True,
            "/app/runLoops/present/rateLimitFrequency": 120,
            "/app/runLoops/present/rateLimitUsePrecisionSleep": True,
            "/app/runLoops/rendering_0/rateLimitEnabled": True,
            "/app/runLoops/rendering_0/rateLimitFrequency": 120,
            "/app/runLoops/rendering_0/rateLimitUsePrecisionSleep": True,
            "/app/runLoops/rendering_0/syncToPresent": False,
            "/app/runLoops/rendering_1/rateLimitEnabled": True,
            "/app/runLoops/rendering_1/rateLimitFrequency": 120,
            "/app/runLoops/rendering_1/rateLimitUsePrecisionSleep": True,
            "/app/runLoops/rendering_1/syncToPresent": False,
            "/app/runLoopsGlobal/syncToPresent": False,
            "/app/vsync": False,
            "/exts/omni.kit.renderer.core/present/enabled": True,
            "/exts/omni.kit.renderer.core/present/presentAfterRendering": False,
            "/persistent/app/viewport/defaults/tickRate": 120,
            "/rtx-transient/dlssg/enabled": True,
        },
    ),
    (
        "30x2",
        {
            "/app/runLoops/main/rateLimitEnabled": True,
            "/app/runLoops/main/rateLimitFrequency": 60,
            "/app/runLoops/main/rateLimitUsePrecisionSleep": True,
            "/app/runLoops/main/syncToPresent": True,
            "/app/runLoops/present/rateLimitEnabled": True,
            "/app/runLoops/present/rateLimitFrequency": 60,
            "/app/runLoops/present/rateLimitUsePrecisionSleep": True,
            "/app/runLoops/rendering_0/rateLimitEnabled": True,
            "/app/runLoops/rendering_0/rateLimitFrequency": 30,
            "/app/runLoops/rendering_0/rateLimitUsePrecisionSleep": True,
            "/app/runLoops/rendering_0/syncToPresent": True,
            "/app/runLoops/rendering_1/rateLimitEnabled": True,
            "/app/runLoops/rendering_1/rateLimitFrequency": 30,
            "/app/runLoops/rendering_1/rateLimitUsePrecisionSleep": True,
            "/app/runLoops/rendering_1/syncToPresent": True,
            "/app/runLoopsGlobal/syncToPresent": True,
            "/app/vsync": True,
            "/exts/omni.kit.renderer.core/present/enabled": True,
            "/exts/omni.kit.renderer.core/present/presentAfterRendering": True,
            "/persistent/app/viewport/defaults/tickRate": 30,
            "/rtx-transient/dlssg/enabled": True,
        },
    ),
    (
        "60",
        {
            "/app/runLoops/main/rateLimitEnabled": True,
            "/app/runLoops/main/rateLimitFrequency": 60,
            "/app/runLoops/main/rateLimitUsePrecisionSleep": True,
            "/app/runLoops/main/syncToPresent": True,
            "/app/runLoops/present/rateLimitEnabled": True,
            "/app/runLoops/present/rateLimitFrequency": 60,
            "/app/runLoops/present/rateLimitUsePrecisionSleep": True,
            "/app/runLoops/rendering_0/rateLimitEnabled": True,
            "/app/runLoops/rendering_0/rateLimitFrequency": 60,
            "/app/runLoops/rendering_0/rateLimitUsePrecisionSleep": True,
            "/app/runLoops/rendering_0/syncToPresent": True,
            "/app/runLoops/rendering_1/rateLimitEnabled": True,
            "/app/runLoops/rendering_1/rateLimitFrequency": 60,
            "/app/runLoops/rendering_1/rateLimitUsePrecisionSleep": True,
            "/app/runLoops/rendering_1/syncToPresent": True,
            "/app/runLoopsGlobal/syncToPresent": True,
            "/app/vsync": True,
            "/exts/omni.kit.renderer.core/present/enabled": True,
            "/exts/omni.kit.renderer.core/present/presentAfterRendering": True,
            "/persistent/app/viewport/defaults/tickRate": 60,
            "/rtx-transient/dlssg/enabled": False,
        },
    ),
    (
        "60x2",
        {
            "/app/runLoops/main/rateLimitEnabled": True,
            "/app/runLoops/main/rateLimitFrequency": 60,
            "/app/runLoops/main/rateLimitUsePrecisionSleep": True,
            "/app/runLoops/main/syncToPresent": True,
            "/app/runLoops/present/rateLimitEnabled": True,
            "/app/runLoops/present/rateLimitFrequency": 120,
            "/app/runLoops/present/rateLimitUsePrecisionSleep": True,
            "/app/runLoops/rendering_0/rateLimitEnabled": True,
            "/app/runLoops/rendering_0/rateLimitFrequency": 60,
            "/app/runLoops/rendering_0/rateLimitUsePrecisionSleep": True,
            "/app/runLoops/rendering_0/syncToPresent": True,
            "/app/runLoops/rendering_1/rateLimitEnabled": True,
            "/app/runLoops/rendering_1/rateLimitFrequency": 60,
            "/app/runLoops/rendering_1/rateLimitUsePrecisionSleep": True,
            "/app/runLoops/rendering_1/syncToPresent": True,
            "/app/runLoopsGlobal/syncToPresent": True,
            "/app/vsync": True,
            "/exts/omni.kit.renderer.core/present/enabled": True,
            "/exts/omni.kit.renderer.core/present/presentAfterRendering": True,
            "/persistent/app/viewport/defaults/tickRate": 60,
            "/rtx-transient/dlssg/enabled": True,
        },
    ),
    (
        "120",
        {
            "/app/runLoops/main/rateLimitEnabled": True,
            "/app/runLoops/main/rateLimitFrequency": 120,
            "/app/runLoops/main/rateLimitUsePrecisionSleep": True,
            "/app/runLoops/main/syncToPresent": True,
            "/app/runLoops/present/rateLimitEnabled": True,
            "/app/runLoops/present/rateLimitFrequency": 120,
            "/app/runLoops/present/rateLimitUsePrecisionSleep": True,
            "/app/runLoops/rendering_0/rateLimitEnabled": True,
            "/app/runLoops/rendering_0/rateLimitFrequency": 120,
            "/app/runLoops/rendering_0/rateLimitUsePrecisionSleep": True,
            "/app/runLoops/rendering_0/syncToPresent": True,
            "/app/runLoops/rendering_1/rateLimitEnabled": True,
            "/app/runLoops/rendering_1/rateLimitFrequency": 120,
            "/app/runLoops/rendering_1/rateLimitUsePrecisionSleep": True,
            "/app/runLoops/rendering_1/syncToPresent": True,
            "/app/runLoopsGlobal/syncToPresent": True,
            "/app/vsync": True,
            "/exts/omni.kit.renderer.core/present/enabled": True,
            "/exts/omni.kit.renderer.core/present/presentAfterRendering": True,
            "/persistent/app/viewport/defaults/tickRate": 120,
            "/rtx-transient/dlssg/enabled": False,
        },
    ),
]


class ThreadSyncPresets:
    def __init__(self):
        # Get all the settings to watch
        names = []
        paths = set()

        for name, setting in THREAD_SYNC_PRESETS:
            names.append(name)
            for key, default in setting.items():
                paths.add(key)

        self._settings = carb.settings.get_settings()
        self._subscriptions = []

        for path in paths:
            self._subscriptions.append(self._settings.subscribe_to_node_change_events(path, self._on_setting_changed))

        combo = ui.ComboBox(*([0, ""] + names), height=0)
        self._model = combo.model
        self._sub = self._model.subscribe_item_changed_fn(self._on_model_changed)

    def _on_setting_changed(self, item, event_type):
        for name, setting in THREAD_SYNC_PRESETS:
            all_is_good = True
            for key, default in setting.items():
                if self._settings.get(key) != default:
                    all_is_good = False
                    break

            if all_is_good:
                self._on_preset_changed(name)
                return

        self._on_preset_changed(None)

    def _on_preset_changed(self, preset: Optional[str]):
        # Find ID
        for i, child_item in enumerate(self._model.get_item_children()):
            if self._model.get_item_value_model(child_item).as_string == preset:
                self._set_preset_id(i)

    def _set_preset_id(self, preset_id: int):
        self._model.get_item_value_model().as_int = preset_id

    def _on_model_changed(self, model: ui.AbstractItemModel, item: ui.AbstractItem):
        preset_id = self._model.get_item_value_model().as_int
        child_item = self._model.get_item_children()[preset_id]
        child_name = self._model.get_item_value_model(child_item).as_string
        if not child_name:
            return

        # Find prest
        for name, setting in THREAD_SYNC_PRESETS:
            if name == child_name:
                self._set_settings(setting)
                break

    def _set_settings(self, batch: Dict[str, Any]):
        for key, value in batch.items():
            if self._settings.get(key) != value:
                self._settings.set(key, value)
                carb.log_info(f"Present Sets Setting {key} -> {value}")


class DeveloperPreferences(PreferenceBuilder):
    def __init__(self):
        super().__init__("Developer")

    def show_page(self) -> bool:
        return carb.settings.get_settings().get("/app/show_developer_preference_section")

    def build(self):
        with ui.VStack(height=0):
            """ Throttle Rendering """
            with self.add_frame("Throttle Rendering"):
                with ui.VStack():
                    with ui.HStack():
                        self.label("Global Thread Synchronization Preset")
                        self.__presets = ThreadSyncPresets()

                    self.create_setting_widget("Async Rendering", "/app/asyncRendering", SettingType.BOOL)
                    self.create_setting_widget(
                        "Skip Rendering While Minimized", "/app/renderer/skipWhileMinimized", SettingType.BOOL
                    )
                    self.create_setting_widget(
                        "Yield 'ms' while in focus",
                        "/app/renderer/sleepMsOnFocus",
                        SettingType.INT,
                        range_from=0,
                        range_to=50,
                    )
                    self.create_setting_widget(
                        "Yield 'ms' while not in focus",
                        "/app/renderer/sleepMsOutOfFocus",
                        SettingType.INT,
                        range_from=0,
                        range_to=200,
                    )
                    self.create_setting_widget(
                        "Enable UI FPS Limit", "/app/runLoops/main/rateLimitEnabled", SettingType.BOOL
                    )
                    self.create_setting_widget(
                        "UI FPS Limit uses Busy Loop", "/app/runLoops/main/rateLimitUseBusyLoop", SettingType.BOOL
                    )
                    self.create_setting_widget(
                        "UI FPS Limit",
                        "/app/runLoops/main/rateLimitFrequency",
                        SettingType.FLOAT,
                        range_from=10,
                        range_to=360,
                    )
                    self.create_setting_widget(
                        "Use Fixed Time Stepping", "/app/player/useFixedTimeStepping", SettingType.BOOL
                    )

                    # Present thread
                    self.create_setting_widget(
                        "Use Present Thread", "/exts/omni.kit.renderer.core/present/enabled", SettingType.BOOL
                    )
                    self.create_setting_widget(
                        "Sync Threads and Present Thread", "/app/runLoopsGlobal/syncToPresent", SettingType.BOOL
                    )
                    self.create_setting_widget(
                        "Present Thread FPS Limit",
                        "/app/runLoops/present/rateLimitFrequency",
                        SettingType.FLOAT,
                        range_from=10,
                        range_to=360,
                    )
                    self.create_setting_widget(
                        "Sync Present Thread to Present After Rendering",
                        "/exts/omni.kit.renderer.core/present/presentAfterRendering",
                        SettingType.BOOL
                    )
                    self.create_setting_widget(
                        "Vsync",
                        "/app/vsync",
                        SettingType.BOOL
                    )
