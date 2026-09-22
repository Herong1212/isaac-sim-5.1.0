from functools import partial

import carb
import omni.ext
from omni import ui
from omni.kit.menu.utils import MenuItemDescription, add_menu_items, remove_menu_items
from omni.warehouse_creator.widgets.WarehouseBuilderWidget import WarehouseBuilderWidget
from omni.warehouse_creator.widgets.WarehouseVariantWidget import WarehouseVariantWidget

# from omni.warehouse_creator.widgets import WarehouseVariantGrid


# Functions and vars are available to other extension as usual in python: `example.python_ext.some_public_function(x)`
def some_public_function(x: int):
    return x**x


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class WarehouseCreatorExtension(omni.ext.IExt):
    def __init__(self):
        super().__init__()
        self.window = None

    def on_startup(self, ext_id):
        self.ext_id = ext_id
        self.widget = None
        ext_path = omni.kit.app.get_app().get_extension_manager().get_extension_path(ext_id)
        self.mdl_file = ext_path + "/data/GhostVolumetric.mdl"
        self._register_widget()
        self._register_window()

    def on_shutdown(self):
        self._unregister_widget()
        self._unregister_window()
        if self.widget:
            self.widget.shutdown()
        del self.window
        self.window = None

    def _register_window(self):
        action_registry = omni.kit.actions.core.get_action_registry()
        action_registry.register_action(
            self.ext_id,
            "warehouse_creator",
            partial(self.menu_click, None, True),
            display_name="Modular Warehouse Creator",
            description="Creates warehouse environments using the modular warehouse assets",
            tag="Warehouse Creator",
        )
        self._menu = [
            MenuItemDescription(
                name="Modular Warehouse Creator",
                # glyph="none.svg",
                onclick_action=(self.ext_id, "warehouse_creator"),
            )
        ]
        add_menu_items(self._menu, "Tools")

    def menu_click(self, menu, value):
        if self.window:
            self.window.visible = value
        else:
            if self.widget:
                self.widget.shutdown()
            self.window = ui.Window("Modular Warehouse Creator", width=400, height=300)
            with self.window.frame:
                self.widget = WarehouseBuilderWidget()

    def _unregister_window(self):
        action_registry = omni.kit.actions.core.get_action_registry()
        action_registry.deregister_all_actions_for_extension(self.ext_id)
        self.window = None

    def _register_widget(self):
        import omni.kit.window.property as p

        w = p.get_window()
        w.register_widget(
            "prim",
            "warehouse_creator",
            WarehouseVariantWidget(title="Modular Warehouse Creator", collapsed=False),
            False,
        )

    def _unregister_widget(self):
        import omni.kit.window.property as p

        w = p.get_window()
        if w:
            w.unregister_widget("prim", "warehouse_creator")
