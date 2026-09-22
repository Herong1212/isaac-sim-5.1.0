from pxr import Tf, Trace, Usd

import carb.settings
import carb.eventdispatcher

import omni.kit
import omni.ext

# legacy extension export
from . import helpers
from . import visualize
from . import sensors
from .SyntheticData import *

EXTENSION_NAME = "Synthetic Data"
_extension_instance = None


class Extension(omni.ext.IExt):
    def __init__(self):
        super().__init__()
        self.__viewport_legacy_event_sub = None
        self.__viewport_legacy_close = None
        self.__extension_loaded = None
        self.__menu_container = None

    def __menubar_core_loaded(self):
        from .menu import SynthDataMenuContainer
        self.__menu_container = SynthDataMenuContainer()

    def __menubar_core_unloaded(self):
        if self.__menu_container:
            self.__menu_container.destroy()
        self.__menu_container = None

    def __viewport_legcy_loaded(self):
        from .viewport_legacy import ViewportLegacy
        self.__viewport_legacy_event_sub = ViewportLegacy.create_update_subscription()
        self.__viewport_legacy_close = ViewportLegacy.close_viewports

    def __viewport_legcy_unloaded(self):
        if self.__viewport_legacy_event_sub:
            self.__viewport_legacy_event_sub = None
        if self.__viewport_legacy_close:
            self.__viewport_legacy_close()
            self.__viewport_legacy_close = None

    def on_startup(self, ext_id):
        global _extension_instance
        _extension_instance = self
        carb.log_info("[omni.syntheticdata] SyntheticData startup")

        settings = carb.settings.get_settings()
        settings.set_default("/exts/omni.syntheticdata/menubar/visible", True)
        settings.set_default("/exts/omni.syntheticdata/menubar/order", -1)
        settings.set_default("/exts/omni.syntheticdata/menubar/showSensorDefaultButton", False)

        settings.set_default("/exts/omni.syntheticdata/graphBackedByUsd", True)

        settings.set_default("/exts/omni.syntheticdata/renderVarTextureToBuffer/cudaCopyNoStride", True)
        settings.set_default("/exts/omni.syntheticdata/renderVarToHost/usePinnedMemory", True)
        settings.set_default("/exts/omni.syntheticdata/renderVarCopyToDisk/detachResourceBeforeDispatch", False)

        manager = omni.kit.app.get_app().get_extension_manager()
        self.__extension_loaded = (
            manager.subscribe_to_extension_enable(
                lambda _: self.__menubar_core_loaded(),
                lambda _: self.__menubar_core_unloaded(),
                ext_name="omni.kit.viewport.menubar.core",
                hook_name=f"{ext_id} omni.kit.viewport.menubar.core listener",
            ),
        )

        usd = omni.usd.get_context()
        self._stage_event_sub = [
            carb.eventdispatcher.get_eventdispatcher().observe_event(
                observer_name="omni.syntheticdata",
                event_name=usd.stage_event_name(event),
                on_event=func
            )
            for event, func in (
                (omni.usd.StageEventType.CLOSING, lambda _: self._on_stage_closing()),
                (omni.usd.StageEventType.OPENED, lambda _: self._on_stage_opened())
            )
        ]
        # force settings
        stageHistoryFrameCount = settings.get_as_int("/app/settings/fabricDefaultStageFrameHistoryCount")
        if not stageHistoryFrameCount or (int(stageHistoryFrameCount) < 3):
            carb.log_error(f"SyntheticData extension needs at least a stageFrameHistoryCount of 3")
        if settings.get_as_bool("/rtx/gatherColorToDisplayDevice") and settings.get_as_bool("/renderer/multiGpu/enabled"):
            carb.log_error("SyntheticData extension does not support /rtx/gatherColorToDisplayDevice=true with multiple GPUs.")
        SyntheticData.Initialize()

    def _on_stage_opened(self):
        # this is fishy but if we reset the graphs in the closing event the rendering is not happy
        SyntheticData.Get().reset(False)
        if self.__menu_container:
            self.__menu_container.clear_all()

    def _on_stage_closing(self):
        if self.__viewport_legacy_close:
            self.__viewport_legacy_close()
        # FIXME : this cause rendering issues (added for unittests)
        SyntheticData.Get().reset(False)

    def on_shutdown(self):
        global _extension_instance
        _extension_instance = None

        self.__extension_loaded = None
        self._stage_event_sub = None

        self.__viewport_legcy_unloaded()
        self.__menubar_core_unloaded()

        SyntheticData.Reset()

    def get_name(self):
        return EXTENSION_NAME

    @staticmethod
    def get_instance():
        return _extension_instance
