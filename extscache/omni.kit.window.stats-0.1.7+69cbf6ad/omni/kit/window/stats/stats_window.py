import carb
from carb.eventdispatcher import get_eventdispatcher
import sys
import os
import omni.ext
import omni.ui
import omni.kit.app
import omni.stats
import carb.settings
from omni.kit.menu.utils import MenuHelperExtension

WINDOW_NAME = "Statistics"
MENU_GROUP = "Window"

class Extension(omni.ext.IExt, MenuHelperExtension):
    """Statistics view extension"""

    class ComboBoxItem(omni.ui.AbstractItem):
        def __init__(self, text):
            super().__init__()
            self.model = omni.ui.SimpleStringModel(text)

    class ComboBoxModel(omni.ui.AbstractItemModel):
        def __init__(self):
            super().__init__()
            self._current_index = omni.ui.SimpleIntModel()
            self._id_fn = self._current_index.add_value_changed_fn(self._changed_model)
            self._items = []
            self._items_scopes_index = [] # mapping of _items to scope index
            self._scopes_flags = []

        def destroy(self):
            self._items = []
            self._items_scopes_index = []
            self._scopes_flags = []
            self._current_index.remove_value_changed_fn(self._id_fn)
            self._current_index = None
            super().destroy()

        def _changed_model(self, model):
            # update stats at the end of the frame instead
            self._item_changed(None)

        def get_item_children(self, item):
            return self._items

        def get_item_value_model(self, item, column_id):
            if item is None:
                return self._current_index
            return item.model

        def get_current_scope_index(self):
            if len(self._items_scopes_index) == 0:
                return None
            return self._items_scopes_index[self._current_index.as_int]

        def _update_scopes(self, stat_iface):
            scopes = stat_iface.get_scopes()
            scope_count = len(scopes)
            scope_count_prev = len(self._scopes_flags)
            item_count = len(self._items)

            # if scope count changes or visibility of scope changes trigger an update.
            force_update = False
            if scope_count != scope_count_prev:
                force_update = True
            else:
                for i in range(scope_count):
                    scope = scopes[i]
                    if scope["flags"] != self._scopes_flags[i]:
                        force_update = True
                        break

            if force_update:
                item_index = 0 # visible scope count
                selected_scope = self.get_current_scope_index()
                selected_scope_updated = False

                if item_count != 0 or scope_count_prev != 0:
                    self._items.clear()
                    self._scopes_flags.clear()
                    self._items_scopes_index.clear()
                for i in range(scope_count):
                    scope = scopes[i]
                    self._scopes_flags.append(scope["flags"])
                    if not (scope["flags"] & omni.stats.SCOPE_FLAG_HIDE):
                        self._items.append(Extension.ComboBoxItem(scope["name"]))
                        self._items_scopes_index.append(i)
                        # verify if a scope is already selected
                        if selected_scope == i:
                            self._current_index.as_int = item_index
                            selected_scope_updated = True
                        item_index += 1
                # A default selection if it is not already picked
                if not selected_scope_updated:
                    self._current_index.as_int = 0

            # update stats
            if scope_count != 0 and len(self._items) != 0:
                selected_scope_node = scopes[self.get_current_scope_index()]
                self._item_changed(None)
                return selected_scope_node
            elif force_update:
                # reset the empty combobox
                self._item_changed(None)
            return None

    def __init__(self):
        self._window = None
        self._app = None
        self._stats_mode = None
        self._scope_description = None
        self._stats = None
        self._stat_grid = None
        self._scope_combo_model = None
        self._stats_names = None
        self._stats_values = None
        self._stats_desc = None
        self._show_names = False  # Don't show names by default, just descriptions
        super().__init__()

    def get_name(self):
        return WINDOW_NAME

    def on_startup(self):
        self._app = omni.kit.app.get_app()
        self._ed = get_eventdispatcher()
        self._stats = omni.stats.get_stats_interface()
        self._window = omni.ui.Window(
            WINDOW_NAME,
            width=600,
            height=600,
            padding_x=10,
            visible=False,
            dockPreference=omni.ui.DockPreference.RIGHT_TOP,
        )
        self._window.deferred_dock_in("Details", omni.ui.DockPolicy.CURRENT_WINDOW_IS_ACTIVE)

        with self._window.frame:
            with omni.ui.VStack(height=0, spacing=8):
                with omni.ui.HStack():
                    omni.ui.Label("Scope to display:")
                    self._scope_combo_model = Extension.ComboBoxModel()
                    self._scope_combo = omni.ui.ComboBox(self._scope_combo_model)

                with omni.ui.HStack():
                    omni.ui.Label("Scope description:")
                    self._scope_description = omni.ui.Label("", word_wrap=True)

                omni.ui.Line()
                # green color for header
                style_header = {"color": 0xFF00B976}
                with omni.ui.HStack(style=style_header):
                    if self._show_names:
                        omni.ui.Label("Name", alignment=omni.ui.Alignment.LEFT)
                    omni.ui.Label("Description", alignment=omni.ui.Alignment.LEFT)
                    omni.ui.Label("Amount", alignment=omni.ui.Alignment.RIGHT)
                omni.ui.Line()

                # For performance, draw with two labels (per-frame update)
                with omni.ui.HStack(style=style_header):
                    if self._show_names:
                        self._stats_names = omni.ui.Label("", alignment=omni.ui.Alignment.LEFT)
                    self._stats_desc = omni.ui.Label("", alignment=omni.ui.Alignment.LEFT)
                    self._stats_values = omni.ui.Label("", alignment=omni.ui.Alignment.RIGHT)

        self.menu_startup(WINDOW_NAME, WINDOW_NAME, MENU_GROUP, header="")

        self._sub_event = self._ed.observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_UPDATE,
            on_event=self._on_update,
            observer_name="omni.stats frame statistics"
        )
        self._window.set_visibility_changed_fn(self._visiblity_changed_fn)

    def on_shutdown(self):
        self.menu_shutdown()
        self._window = None
        self._sub_event = None

    def _visiblity_changed_fn(self, visible):
        self.menu_refresh()
        carb.settings.get_settings().set("/profiler/enableDeviceUtilizationQuery", visible)

    def _update_stats(self, scope_node):
        if scope_node is None:
            self._scope_description.text = ""
            self._stats_values.text = ""
            self._stats_desc.text = ""
            if self._show_names:
                self._stats_names.text = ""
            return

        self._scope_description.text = scope_node["description"]
        stat_nodes = self._stats.get_stats(scope_node["scopeId"])
        stats_names = ""
        stats_values = ""
        stats_descs = ""
        # Sort nodes in descending order based on the alphabet
        stat_nodes = sorted(stat_nodes, key=lambda node: node["description"].lower(), reverse=False)
        for node in stat_nodes:
            if self._show_names:
                stats_names += node["name"] + "\n"
            stats_descs += node["description"] + "\n"
            if node["type"] == 0:
                stats_values += "{:,}".format(node["value"]) + "\n"
            elif node["type"] == 1:
                stats_values += "{:.3f}".format(node["value"]) + "\n"
        if self._show_names:
            self._stats_names.text = stats_names
        self._stats_values.text = stats_values
        self._stats_desc.text = stats_descs

    def _on_update(self, _):
        if not self._window.visible:
            return
        # scope_node of None will clear everything
        scope_node = self._scope_combo_model._update_scopes(self._stats)
        self._update_stats(scope_node)
