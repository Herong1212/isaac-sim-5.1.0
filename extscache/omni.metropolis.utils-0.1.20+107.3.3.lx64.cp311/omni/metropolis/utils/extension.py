import omni.ext
import carb.tokens
from omni.kit.menu.utils import MenuItemDescription, MenuHelperExtensionFull, add_menu_items, remove_menu_items
from .triggers import get_all_trigger_types
from .triggers.core import TriggersManager
from .ui_util import UIUtil

class ActionAndEventDataGenerationUtils(omni.ext.IExt, MenuHelperExtensionFull):
    _ext_path: str | None = None

    @classmethod
    def get_ext_path(cls) -> str:
        if cls._ext_path is None:
            itokens = carb.tokens.get_tokens_interface()
            cls._ext_path = itokens.resolve("${omni.metropolis.utils}")
        return cls._ext_path

    def on_startup(self, ext_id):
        self._menu_items = [
            MenuItemDescription(
                name="Action and Event Data Generation",
                onclick_fn = lambda *_: UIUtil.open_action_and_event_data_generation_layout()
            )
        ]
        add_menu_items(self._menu_items, "Layouts")
        # Register triggers
        all_trigger_types = get_all_trigger_types()
        TriggersManager.get_instance().register_trigger_type(all_trigger_types)

    def on_shutdown(self):
        # Deregister triggers
        all_trigger_types = get_all_trigger_types()
        TriggersManager.get_instance().deregister_trigger_type(all_trigger_types)

        remove_menu_items(self._menu_items, "Layouts")
        self.menu_shutdown()
