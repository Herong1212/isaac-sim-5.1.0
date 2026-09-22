import carb
import omni.ext
import os

class Ext(omni.ext.IExt):
    def on_startup(self, ext_id):
        self._setup_usd_env_settings()

        # Start the rtx.usdmdl.plugin.
        # This will load the USD SDR MDL discovery and parser plugins.
        carb.get_framework().start_plugin("rtx.usdmdl.plugin")

    def _setup_usd_env_settings(self):
        ENABLE_OMNI_USD_MDL_DISCOVER_ON_STARTUP = "/usd/enableOmniUsdMdlDiscoverOnStartup"
        ENABLE_OMNI_USD_MDL_LOAD_PREVIEW_SURFACE_MODULES = "/usd/enableOmniUsdMdlLoadPreviewSurfaceModules"

        settings = carb.settings.acquire_settings_interface()

        if settings.get(ENABLE_OMNI_USD_MDL_DISCOVER_ON_STARTUP):
            os.environ["OMNI_USD_MDL_DISCOVER_ON_STARTUP"] = "1"

        if settings.get(ENABLE_OMNI_USD_MDL_LOAD_PREVIEW_SURFACE_MODULES):
            os.environ["OMNI_USD_MDL_LOAD_PREVIEW_SURFACE_ON_STARTUP"] = "1"