import asyncio
import omni.ext
import isaacsim.replicator.agent.core
from isaacsim.replicator.agent.core.simulation import SimulationManager
from isaacsim.replicator.agent.ui.agent_sdg.agent_sdg_window import AgentSDGWindow
from isaacsim.replicator.agent.ui.command_injection.command_injection_window import CommandInjectionWindow
from isaacsim.replicator.agent.ui.command_setting.command_setting_window import CommandSettingWindow
from isaacsim.replicator.agent.ui.settings import *
from omni.kit.menu.utils import MenuHelperExtensionFull


class Extension(omni.ext.IExt):
    def on_startup(self, ext_id: str):
        self._ext_id = ext_id

        self._core_ext = None
        self._sim_manager = None

        self._menu_helper = MenuHelperExtensionFull()
        # UI extension waits for core extension startup async
        self._core_ext = isaacsim.replicator.agent.core.get_instance()
        self.start_extension()

    def on_shutdown(self):
        """Cleanup objects on extension shutdown"""

        async def shutdown_menu_helper(menu_helper):
            # First make sure all windows are closed
            for i in range(len(menu_helper._window_list)):
                menu_helper.show_window(None, False, i)
            # Wait for MenuHelperExtensionFull._destroy_window_async to trigger
            await omni.kit.app.get_app().next_update_async()
            # Wait for MenuHelperExtensionFull._destroy_window_async to finish
            await omni.kit.app.get_app().next_update_async()
            # Finally we shutdown the menu
            menu_helper.menu_shutdown()

        asyncio.ensure_future(shutdown_menu_helper(self._menu_helper))

        # Clean variables
        self._core_ext = None
        self._sim_manager = None

    def start_extension(self):
        """Initialize extension variables and UI elements"""

        self._sim_manager = SimulationManager()

        idx = self._menu_helper.menu_startup(
            lambda s=self._sim_manager: AgentSDGWindow(s), "Actor SDG", "Actor SDG", "Tools/Action and Event Data Generation", verbose=False
        )
        self._menu_helper.menu_startup(
            lambda s=self._sim_manager: CommandInjectionWindow(s),
            "Command Injection",
            "Command Injection",
            "Tools/Action and Event Data Generation",
            verbose=False,
        )
        self._menu_helper.menu_startup(
            lambda s=self._sim_manager: CommandSettingWindow(s),
            "Command Setting",
            "Command Setting",
            "Tools/Action and Event Data Generation",
            verbose=False,
        )

        self._menu_helper.show_window("", True, idx)

        # Temporary solution to trigger menu refresh
        # since menu helper doest not trigger it at start
        import omni.kit.menu.utils

        omni.kit.menu.utils.rebuild_menus()