# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.kit.app
import omni.ui as ui
import omni.usd
import omni.anim.navigation.core as nav
from .utils import refresh_property_window

DEFAULT_COLOR_OPACITY = 1.0
MAX_AREAS = 64

EXT_PATH = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
ICON_PATH = f"{EXT_PATH}/icons"


class NavMeshAreaItem(ui.AbstractItem):
    """Class that represents a NavMesh area item in the tree view model."""
    def __init__(self, name: str, color: int, default_cost: float):
        super().__init__()
        self.name_model = ui.SimpleStringModel(name)
        self.color_model = ui.SimpleIntModel(color)
        self.default_cost_model = ui.SimpleFloatModel(default_cost)


class NavMeshAreaItemModel(ui.AbstractItemModel):
    """Class that contains a list of area items for use with a tree view."""
    def __init__(self, *args):
        super().__init__()
        self._load_items()
        self._usd_context = omni.usd.get_context()
        self._usd_stage_event_sub = self._usd_context.get_stage_event_stream().create_subscription_to_pop(
            self._on_usd_stage_event, name="NavMeshAreasDelegate"
        )

    def _load_items(self):
        self._items = []
        inav = nav.acquire_interface()
        area_count = inav.get_area_count()
        for area_index in range(area_count):
            name = inav.get_area_name(area_index)
            if area_index == 0:
                self._default_area_name = name
            color = inav.get_area_color(area_index)
            default_cost = inav.get_area_default_cost(area_index)
            self._items.append(NavMeshAreaItem(name, color, default_cost))

    def _on_usd_stage_event(self, event):
        if event.type == int(omni.usd.StageEventType.OPENED):
            self._load_items()
            self._item_changed(None)

    def get_item_children(self, parentItem: ui.AbstractItem):
        """
        Returns the of children for a given item.
        @param item: The item for which to get the children.
        """
        if parentItem is not None:
            return []
        return self._items

    def get_item_value_model(self, item, column_id):
        """
        Returns the of model for a given item.
        @param item: The item for which to get the model.
        """
        if column_id == 3:
            return item.name_model
        elif column_id == 2:
            return item.default_cost_model
        elif column_id == 1:
            return item.name_model
        else:
            return item.color_model

    def get_item_value_model_count(self, *_):
        """Returns the number of columns in this model."""
        return 4

    def get_default_name(self):
        return self._default_area_name

    def create_area(self):
        inav = nav.acquire_interface()
        inav.create_area()
        new_index = inav.get_area_count() - 1
        name = inav.get_area_name(new_index)
        color = inav.get_area_color(new_index)
        default_cost = inav.get_area_default_cost(new_index)
        self._items.append(NavMeshAreaItem(name, color, default_cost))
        self._item_changed(None)
        refresh_property_window()

    def destroy_area(self, area_name):
        inav = nav.acquire_interface()
        index = inav.find_area(area_name)
        if index > -1:
            inav.destroy_area(index)
        for item in self._items:
            name = item.name_model.get_value_as_string()
            if name == area_name:
                self._items.remove(item)
                self._item_changed(None)
                refresh_property_window()

    def reload(self):
        self._load_items()
        self._item_changed(None)


class NavMeshAreasDelegate(ui.AbstractItemDelegate):
    def __init__(self, model):
        super().__init__()
        self._model = model
        self._field_begin_edit_subs = {}
        self._field_end_edit_subs = {}
        self._area_renames = {}

    def build_branch(self, model, item, column_id, level, expanded):
        """Create a branch widget that opens or closes subtree"""
        pass

    def build_header(self, column_id: int = 0):
        if column_id == 3:
            with ui.HStack(height=20):
                ui.Spacer()
        elif column_id == 2:
            with ui.HStack(height=20):
                ui.Spacer(width=8)
                ui.Label("Default Cost")
        elif column_id == 1:
            with ui.HStack(height=20):
                ui.Spacer(width=8)
                ui.Label("Name")
        else:
            with ui.HStack(height=20):
                ui.Spacer()

    def _on_begin_edit_area_name(self, value_model):
        self._area_renames[value_model] = value_model.get_value_as_string()

    def _on_end_edit_area_name(self, value_model):
        prev_name = self._area_renames[value_model]
        new_name = value_model.get_value_as_string()
        if new_name == "":
            value_model.set_value(prev_name)
            self._area_renames.pop(value_model)
        elif prev_name != new_name:
            value_model.set_value(new_name)
            self._area_renames.pop(value_model)
            inav = nav.acquire_interface()
            index = inav.find_area(prev_name)
            if index > -1:
                inav.set_area_name(index, new_name)

    def _on_end_edit_area_color(self, value_model, name_model):
        area_name = name_model.get_value_as_string()
        child_items = value_model.get_item_children()
        red = value_model.get_item_value_model(child_items[0]).get_value_as_float()
        green = value_model.get_item_value_model(child_items[1]).get_value_as_float()
        blue = value_model.get_item_value_model(child_items[2]).get_value_as_float()
        color_value = (int(red * 255) << 16) + (int(green * 255) << 8) + int(blue * 255)
        inav = nav.acquire_interface()
        index = inav.find_area(area_name)
        if index > -1:
            inav.set_area_color(index, color_value)

    def _on_end_edit_area_default_cost(self, value_model, name_model):
        area_name = name_model.get_value_as_string()
        default_cost = value_model.get_value_as_float()
        inav = nav.acquire_interface()
        index = inav.find_area(area_name)
        if index > -1:
            inav.set_area_default_cost(index, default_cost)

    def _on_destroy_area(self, name_model):
        area_name = name_model.get_value_as_string()
        self._model.destroy_area(area_name)

    def build_widget(self, model, item, column_id, level, expanded):
        """Create a widget per column per item"""
        value_model = model.get_item_value_model(item, column_id)
        name_model = model.get_item_value_model(item, 1)
        if column_id == 3:
            with ui.HStack():
                enabled = name_model.get_value_as_string() != model.get_default_name()
                if enabled:
                    field = ui.Button(
                        image_url=f"{ICON_PATH}/remove.svg",
                        image_height=14,
                        image_width=16,
                        width=25,
                        height=16,
                        margin=0,
                        padding=0,
                        identifier="remove_area"
                    ).set_mouse_pressed_fn(lambda x, y, b, m, n=name_model: self._on_destroy_area(n))
        elif column_id == 2:
            field = ui.FloatField(value_model, visible=True)
            self._field_end_edit_subs[field] = field.model.subscribe_end_edit_fn(lambda m=value_model, n=name_model: self._on_end_edit_area_default_cost(m, n))
        elif column_id == 1:
            field = ui.StringField(value_model, visible=True)
            self._field_begin_edit_subs[field] = field.model.subscribe_begin_edit_fn(lambda m=value_model: self._on_begin_edit_area_name(m))
            self._field_end_edit_subs[field] = field.model.subscribe_end_edit_fn(lambda m=value_model: self._on_end_edit_area_name(m))
        else:
            color_value = value_model.get_value_as_int()
            red = (((color_value >> 16) & 255) / 255.0) * DEFAULT_COLOR_OPACITY
            green = (((color_value >> 8) & 255) / 255.0) * DEFAULT_COLOR_OPACITY
            blue = ((color_value & 255) / 255.0) * DEFAULT_COLOR_OPACITY
            field = ui.ColorWidget(red, green, blue, visible=True)
            self._field_end_edit_subs[field] = field.model.subscribe_end_edit_fn(lambda m=value_model, i=item, n=name_model: self._on_end_edit_area_color(m, n))


class NavMeshAreasWidget:
    def __init__(self):
        self.model = NavMeshAreaItemModel()
        self._delegate = NavMeshAreasDelegate(self.model)
        with ui.VStack(height=0):
            self._tree_view = ui.TreeView(
                self.model,
                delegate=self._delegate,
                root_visible=False,
                header_visible=True,
                columns_resizable=False,
                column_widths=[40, ui.Percent(60), ui.Percent(25), ui.Percent(5)],
            )
            ui.Spacer(height=40)
            ui.Button("Add Area", height=30, width=100, clicked_fn=self._on_clicked_add_area, identifier="add_area")
            ui.Spacer(height=20)

    def _on_clicked_add_area(self):
        self.model.create_area()
        refresh_property_window()
