import asyncio, logging, os
import warp as wp
import carb.settings
import omni.ext
from .constants import EXTENSION_NAME
from .simulate import on_simulate_dev
from .simulate import clean_up_embedded
from .ui.object_detection_sdg_window import ObjectDetectionSDGWindow, DistributionVisualizerWindow
from omni.kit.menu.utils import MenuHelperExtensionFull


class OmniReplicatorObjectExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        # for debug purpose modifying here triggers hot reload
        self.embedded_scene = None
        self.embedded_description = None
        self.embedded_index = 0

        self.is_environment_setup = False
        wp.init()

        function_name = "on_startup"
        logging.getLogger().setLevel(logging.INFO)

        logging.info(f"{EXTENSION_NAME} [{function_name}]: isaac sim replicator object startup")

        settings = carb.settings.get_settings()
        if settings.get("/isTest"):
            return

        if settings.get("/deep/debug") is not None:
            if settings.get("/deep/debug") > 0:
                settings.set("/crashreporter/enabled", True)
                settings.set("/crashreporter/url", "https://services.nvidia.com/submit")
                settings.set("/crashreporter/product", "Omniverse-oro-debug")
                settings.set("/crashreporter/version", "dev")
                settings.set("/privacy/performance", True)
                # settings.set("/crashreporter/data/debuggingCrash", "1")
                settings.set("/crashreporter/devOnlyOverridePrivacyAndForceUpload", True)
                settings.set("/crashreporter/alwaysUpload", True)
            if settings.get("/deep/debug") > 1:
                settings.set("/persistent/physics/omniPvdOvdRecordingDirectory", "/tmp/")
                settings.set("/physics/omniPvdOutputEnabled", True)

        settings.set("/omni/replicator/asyncRendering", False)
        settings.set("/app/settings/flatCacheStageFrameHistoryCount", 3)
        windowless = settings.get("/windowless")

        # this is for osmo workflows
        data_in = settings.get("/data/in")
        data_out = settings.get("/data/out")
        images_root = settings.get("/images/root")
        assets_root = settings.get("/assets/root")
        binary_obj_detection = settings.get("/binary")
        if windowless is not None and windowless:
            logging.info(f"{EXTENSION_NAME} [{function_name}]: windowless mode on")
            config_path_from_argument = settings.get("/config/file")
            if config_path_from_argument is None:
                config_path = f"{os.path.dirname(__file__)}/configs/minimum.yaml"
                asyncio.ensure_future(
                    on_simulate_dev(
                        self, config_path, None, True, data_in, data_out, images_root, assets_root, binary_obj_detection
                    )
                )
            else:
                logging.info(f"{EXTENSION_NAME} [{function_name}]: config file is {config_path_from_argument}.")
                asyncio.ensure_future(
                    on_simulate_dev(
                        self,
                        config_path_from_argument,
                        None,
                        True,
                        data_in,
                        data_out,
                        images_root,
                        assets_root,
                        binary_obj_detection,
                    )
                )
        else:
            logging.info(f"{EXTENSION_NAME} [{function_name}]: windowless mode off")
            self.default_values = [data_in, data_out, images_root, assets_root, binary_obj_detection]
            self._menu_helper = MenuHelperExtensionFull()
            self.start_extension()

    def start_extension(self):
        """Initialize extension variables and UI elements"""
        self._object_detection_sdg_idx = self._menu_helper.menu_startup(
            lambda: ObjectDetectionSDGWindow(self),
            "Object SDG",
            "Object SDG",
            "Tools/Action and Event Data Generation",
            verbose=False
        )

        self._distribution_visualizer_idx = self._menu_helper.menu_startup(
            lambda: DistributionVisualizerWindow(self),
            "Distribution Visualizer",
            "Distribution Visualizer",
            "Tools/Action and Event Data Generation",
            verbose=False
        )
        if self._object_detection_sdg_idx is not None:
            self._menu_helper.show_window("", True, self._object_detection_sdg_idx)
        if self._distribution_visualizer_idx is not None:
            self._menu_helper.show_window("", False, self._distribution_visualizer_idx)

        # Trigger menu refresh
        import omni.kit.menu.utils
        omni.kit.menu.utils.rebuild_menus()

    def on_shutdown(self):
        """Cleanup objects on extension shutdown"""
        clean_up_embedded(self)

        async def shutdown_menu_helper(menu_helper):
            if menu_helper is None:
                return

            # First make sure all windows are closed
            if menu_helper._window_list is not None:
                for i in range(len(menu_helper._window_list)):
                    menu_helper.show_window(None, False, i)

            # Wait for window destruction to complete
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()

            # Finally shutdown the menu
            menu_helper.menu_shutdown()

            # Clear window indices
            if hasattr(self, '_object_detection_sdg_idx'):
                delattr(self, '_object_detection_sdg_idx')
            if hasattr(self, '_distribution_visualizer_idx'):
                delattr(self, '_distribution_visualizer_idx')

            # Clear menu helper
            self._menu_helper = None

        asyncio.ensure_future(shutdown_menu_helper(self._menu_helper))
        logging.info(f"{EXTENSION_NAME} [on_shutdown]: isaac sim replicator object shutdown")
