import carb
import carb.eventdispatcher
import omni.ui as ui
from omni.metropolis.utils.config_file.core import ConfigFile
from omni.metropolis.utils.config_file.property import ListPropertyGroup
from omni.metropolis.utils.triggers.core import TriggersManager
from omni.metropolis.utils.triggers.ui_util import UITriggerHelper
from omni.metropolis.utils.ui_util import MinimalStringListModel, UIStyleUtil, UIUtil

from ..config_file_defines import EventPropertyBase, IncidentEventSection


class EventPanel:
    """
    UI class responsible for displaying IncidentEventSection.
    Config file is accessed from the carb event for modularity.
    """

    def __init__(self, config_file_changed_event: str, config_file_saved_event: str):
        self._config_changed_event = config_file_changed_event
        self._config_saved_event = config_file_saved_event
        self._config_changed_sub = None
        self._config_saved_sub = None
        self._frame = None
        self._model = None
        self._delegate = None
        self._treeview = None
        self._add_btn = None
        self._del_btn = None

        self._config_file: ConfigFile = None

    def destroy(self):
        if self._config_changed_sub:
            self._config_changed_sub.reset()
            self._config_changed_sub = None
        if self._config_saved_sub:
            self._config_saved_sub.reset()
            self._config_saved_sub = None

    def build_ui_frame(self):
        if not self._frame:
            self._frame = ui.CollapsableFrame(
                title="Events",
                height=0,
                collapsed=True,
                style=UIStyleUtil.get_collapsable_frame_style(),
                name="subFrame",
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                build_header_fn=lambda collapsed, title: UIUtil.build_collapsable_frame_header_with_image(
                    collapsed, title, "${omni.metropolis.utils}/data/ui_icons/Stage/icoPrim.svg"
                ),
            )
        self.build_ui()

    def build_ui(self):
        with self._frame:
            with ui.VStack(height=0):
                self._model = EventPanel.UIEventListModel(None)
                self._delegate = EventPanel.UIResponseListDelegate()
                self._treeview = ui.TreeView(
                    self._model,
                    delegate=self._delegate,
                    root_visible=False,
                    header_visible=True,
                )
                ui.Spacer(height=10)
                with ui.HStack(spacing=60):
                    self._add_btn = ui.Button(text=f"{UIUtil.get_plus_glyph()} Add", width=55, height=10, spacing=3)
                    self._add_btn.set_clicked_fn(self.on_add_btn)
                    self._del_btn = ui.Button(text=f"{UIUtil.get_minus_glyph()} Del", width=55, height=10, spacing=3)
                    self._del_btn.set_clicked_fn(self.on_del_btn)
        # Register config file related callbacks
        self._config_changed_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
            event_name=self._config_changed_event,
            on_event=lambda e: self._on_config_file_changed(e["Payload"]["config_file"]),
        )
        self._config_saved_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
            event_name=self._config_saved_event,
            on_event=lambda e: self._on_config_file_saved(e["Payload"]["config_file"]),
        )
        self.update_ui()

    def update_ui(self):
        list_data = (
            self._config_file.get_property_group(IncidentEventSection.name, "event_list")
            if self._config_file is not None
            else None
        )

        self._add_btn.enabled = self._config_file is not None and list_data is not None
        self._del_btn.enabled = self._config_file is not None and list_data is not None
        self._model.update_list_data(list_data)

    def on_add_btn(self):
        if not self._config_file:
            return
        incident_list = self._config_file.get_property_group(IncidentEventSection.name, "event_list")
        if not incident_list:
            return
        # Use the first implemented event type as the new event
        new_event_cls = EventPropertyBase.get_all_implemented_event_cls()[0]
        new_event_prop = new_event_cls()
        new_event_prop.setup_by_default()
        incident_list.add_to_list(new_event_prop)
        self.update_ui()

    def on_del_btn(self):
        if not self._config_file:
            return
        incident_list = self._config_file.get_property_group(IncidentEventSection.name, "event_list")
        if not incident_list:
            return
        if len(self._treeview.selection) == 0:
            carb.log_warn("No events selected to delete.")
            return
        for select in self._treeview.selection:
            incident_list.remove_from_list(select.event_prop)
        self.update_ui()

    def _on_config_file_changed(self, config_file: ConfigFile):
        self._config_file = config_file
        self.update_ui()

    def _on_config_file_saved(self, config_file: ConfigFile):
        self._config_file = config_file
        self.update_ui()

    class UIEventItem(ui.AbstractItem):
        """Manage UI models for each EventProperty"""

        def __init__(self, item: EventPropertyBase):
            super().__init__()
            self._model_changed_fn_list: callable = []  # Notify if ui models are changed (need UI refresh)
            self._property_changed_fn_list: callable = []  # Notify if event property is changed
            # Save the property
            self.event_prop = item
            # Event type model
            event_options = EventPropertyBase.get_all_implemented_event_type_names()
            self.type_model = MinimalStringListModel(event_options, event_options.index(self.event_prop.name))
            self.type_model.add_item_changed_fn(lambda m, i: self._on_event_type_changed(m.get_selection()))
            # Set up item models by loaded property
            self.setup_event_item_models()

        def setup_event_item_models(self):
            value_dict = self.event_prop.get_resolved_value()
            # Name model
            self.name_model = ui.SimpleStringModel(value_dict["name"])
            self.name_model.add_end_edit_fn(lambda m: self._on_name_value_changed())
            # Sub item models
            self.sub_item_models = {}  # (sub item name str, dict of models to represent each sub item value)
            for item_name, item_dict in self.event_prop.default_items.items():
                self.sub_item_models[item_name] = {}
                for sub_item_name, sub_item_value in item_dict.items():
                    value = value_dict[item_name][sub_item_name]
                    model = UIUtil.create_model_for_value(sub_item_value)  # Use default value as type hint to create UI
                    model.set_value(value)  # Set UI with current loaded value
                    model.add_value_changed_fn(
                        lambda m=model, n1=item_name, n2=sub_item_name: self._on_sub_item_value_changed(
                            n1, n2, UIUtil.get_value_from_model(m)
                        )
                    )
                    self.sub_item_models[item_name][sub_item_name] = model
            self.setup_trigger_models()

        def setup_trigger_models(self):
            value_dict = self.event_prop.get_resolved_value().copy()
            self.trigger_helper = UITriggerHelper(value_dict["trigger"])
            self.trigger_helper.create_ui_models()
            self.trigger_helper.add_trigger_type_changed_fn(self._on_trigger_type_changed)
            self.trigger_helper.add_trigger_value_changed_fn(self._on_trigger_value_changed)

        def _on_trigger_type_changed(self, trigger_value_dict: dict):
            # Update to value property
            self._on_trigger_value_changed(trigger_value_dict)
            # Notify models are updated
            self._notify_model_changed()

        def _on_trigger_value_changed(self, trigger_value_dict: dict):
            value_dict = self.event_prop.get_resolved_value().copy()
            value_dict["trigger"] = trigger_value_dict
            self.event_prop.set_value(value_dict)

        def _on_event_type_changed(self, new_event_name: str):
            if new_event_name == self.event_prop.name:
                return
            # Craete new EventProperty
            new_event_cls = EventPropertyBase.get_implemented_event_cls_by_name(new_event_name)
            new_event_prop = new_event_cls()
            new_event_prop.setup_by_default()
            self.event_prop = new_event_prop
            # Update models
            self.setup_event_item_models()
            # Notify
            self._notify_property_changed()

        def _on_name_value_changed(self):
            value_dict = self.event_prop.get_resolved_value().copy()
            value_dict["name"] = self.name_model.get_value_as_string()
            self.event_prop.set_value(value_dict)

        def _on_sub_item_value_changed(self, item_name, sub_item_name, new_value):
            value_dict = self.event_prop.get_resolved_value().copy()
            value_dict[item_name][sub_item_name] = new_value
            self.event_prop.set_value(value_dict)

        def add_model_changed_fn(self, fn: callable):
            self._model_changed_fn_list.append(fn)

        def _notify_model_changed(self):
            for fn in self._model_changed_fn_list:
                fn(self)

        def add_event_type_changed_fn(self, fn: callable):
            self._property_changed_fn_list.append(fn)

        def _notify_property_changed(self):
            for fn in self._property_changed_fn_list:
                fn(self)

    class UIEventListModel(ui.AbstractItemModel):
        def __init__(self, event_list_prop_group: ListPropertyGroup):
            super().__init__()
            self._children = []
            self._event_list_prop_group = event_list_prop_group

        def update_list_data(self, event_list_prop_group):
            self._event_list_prop_group = event_list_prop_group
            self._children.clear()
            if event_list_prop_group:
                self._children = [EventPanel.UIEventItem(e) for e in event_list_prop_group.data_group]
                for event_item in self._children:
                    event_item.add_model_changed_fn(lambda m: self._item_changed(m))
                    event_item.add_event_type_changed_fn(self._on_event_type_changed)
            self._item_changed(None)

        def _on_event_type_changed(self, event_item):
            if not self._event_list_prop_group:
                return
            # Fetch new EventProperty from item
            idx = self._children.index(event_item)
            self._event_list_prop_group.replace_from_list(idx, event_item.event_prop)
            # Refresh UI
            self._item_changed(event_item)

        def get_item_children(self, item):
            if item is not None:
                # Since we are doing a flat list, we return the children of root only.
                # If it's not root we return.
                return []
            return self._children

        def get_item_value_model_count(self, item):
            return 1  # Column count

    class UIResponseListDelegate(ui.AbstractItemDelegate):
        def __init__(self):
            super().__init__()

        def build_header(self, column_id):
            ui.Label("Event List", height=30)

        def build_widget(self, model, item, column_id, level, expanded):
            with ui.VStack(spacing=5):
                ui_item: EventPanel.UIEventItem = item
                ui.ComboBox(ui_item.type_model)
                with ui.HStack(spacing=5):
                    ui.Label("\tName", width=120)
                    ui.StringField(ui_item.name_model)
                for item_name, sub_item_dict in ui_item.sub_item_models.items():
                    ui.Label(f"\t{item_name}", width=120)
                    for sub_item_name, sub_item_model in sub_item_dict.items():
                        with ui.HStack(spacing=5):
                            ui.Label(f"\t\t{sub_item_name}", width=120)
                            UIUtil.create_field_for_model(sub_item_model)
                ui_item.trigger_helper.create_ui()
