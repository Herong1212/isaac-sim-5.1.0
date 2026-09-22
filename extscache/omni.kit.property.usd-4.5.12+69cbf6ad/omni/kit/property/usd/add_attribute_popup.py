# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = []

import weakref

import carb
import omni.kit.commands
import omni.kit.undo
import omni.ui as ui
import omni.usd
from pxr import Sdf

from .prim_selection_payload import PrimSelectionPayload


class ValueTypeNameItem(ui.AbstractItem):
    """
    Item for the value type name combo box.
    """

    def __init__(self, value_type_name: Sdf.ValueTypeName, value_type_name_str: str):
        super().__init__()
        self.value_type_name = value_type_name
        self.model = ui.SimpleStringModel(value_type_name_str)


class VariabilityItem(ui.AbstractItem):
    """
    Item for the variability combo box.
    """

    def __init__(self, variability: Sdf.Variability, variability_str: str):
        super().__init__()
        self.variability = variability
        self.model = ui.SimpleStringModel(variability_str)


class ComboBoxModel(ui.AbstractItemModel):
    """
    Model for the combo box.
    """

    def __init__(self):
        super().__init__()

        self._current_index = ui.SimpleIntModel()
        self._current_index.add_value_changed_fn(lambda a: self._item_changed(None))

        self._items = []
        self._populate_items()

    def _populate_items(self):  # pragma: no cover
        pass

    def get_item_children(self, item):
        """
        Get the children of the item.

        Args:
            item (AbstractItem): The item to get the children of.
        """
        return self._items

    def get_item_value_model(self, item, column_id):
        """
        Get the value model of the item.

        Args:
            item (AbstractItem): The item to get the value model of.
            column_id (int): The column id of the item.
        """
        if item is None:
            return self._current_index
        return item.model

    def get_selected_item(self):
        """
        Get the selected item.

        Returns:
            AbstractItem: The selected item.
        """
        return self._items[self._current_index.get_value_as_int()]


class ValueTypeNameModel(ComboBoxModel):
    """
    Model for the value type name combo box.
    """

    def _populate_items(self):
        """
        Populate the items.
        """
        for prop in dir(Sdf.ValueTypeNames):
            type_name = getattr(Sdf.ValueTypeNames, prop)
            if isinstance(type_name, Sdf.ValueTypeName):
                self._items.append(ValueTypeNameItem(type_name, prop))


class VariabilityModel(ComboBoxModel):
    """
    Model for the variability combo box.
    """

    def _populate_items(self):
        self._items = [
            VariabilityItem(Sdf.VariabilityVarying, "Varying"),
            VariabilityItem(Sdf.VariabilityUniform, "Uniform"),
        ]


class AddAttributePopup:
    """
    Popup for adding an attribute to the selected prims.
    """

    def __init__(self):
        # pylint: disable=protected-access
        self._add_attribute_window_payload = None
        self._add_attribute_window = ui.Window(
            "Add Attribute...", visible=False, flags=ui.WINDOW_FLAGS_NO_RESIZE, auto_resize=True
        )
        with self._add_attribute_window.frame:
            with ui.VStack(height=0, spacing=5):
                label_width = 80
                widget_width = 300
                with ui.HStack(width=0):
                    ui.Label("Name", width=label_width)
                    self._add_attr_name_field = ui.StringField(width=widget_width)
                    self._add_attr_name_field.model.set_value("new_attr")

                with ui.HStack(width=0):
                    ui.Label("Type", width=label_width)

                    self._value_type_name_model = ValueTypeNameModel()
                    ui.ComboBox(self._value_type_name_model, width=widget_width)

                with ui.HStack(width=0):
                    ui.Label("Custom", width=label_width)
                    self._custom_checkbox = ui.CheckBox()
                    self._custom_checkbox.model.set_value(True)

                with ui.HStack(width=0):
                    ui.Label("Variability", width=label_width)

                    self._variability_model = VariabilityModel()
                    ui.ComboBox(self._variability_model, width=widget_width)

                self._error_msg_label = ui.Label(
                    "",
                    visible=False,
                    style={"color": 0xFF0000FF},
                )

                with ui.HStack():
                    ui.Spacer()

                    def on_add(weak_self):
                        ref_self = weak_self()
                        error_message = ""
                        if ref_self:
                            stage = ref_self._add_attribute_window_payload.get_stage()
                            if stage:
                                selected_item = ref_self._value_type_name_model.get_selected_item()
                                value_type_name = selected_item.value_type_name
                                attr_name = ref_self._add_attr_name_field.model.get_value_as_string()
                                custom = ref_self._custom_checkbox.model.get_value_as_bool()
                                variability = ref_self._variability_model.get_selected_item().variability
                                usd_context = omni.usd.get_context_from_stage(stage)

                                if usd_context is not None:
                                    if Sdf.Path.IsValidNamespacedIdentifier(attr_name):
                                        try:
                                            usd_context_name = usd_context.get_name()
                                            omni.kit.undo.begin_group()
                                            for path in ref_self._add_attribute_window_payload:
                                                path = Sdf.Path(path).AppendProperty(attr_name)

                                                prop = stage.GetPropertyAtPath(path)
                                                if prop:  # pragma: no cover
                                                    error_message = (
                                                        "One or more attribute to be created already exists."
                                                    )
                                                else:
                                                    omni.kit.commands.execute(
                                                        "CreateUsdAttributeOnPath",
                                                        attr_path=path,
                                                        attr_type=value_type_name,
                                                        custom=custom,
                                                        variability=variability,
                                                        usd_context_name=usd_context_name,
                                                    )
                                        finally:
                                            omni.kit.undo.end_group()
                                    else:  # pragma: no cover
                                        error_message = f'Invalid identifier "{attr_name}"'
                                else:  # pragma: no cover
                                    # No context means the stage is not attached to any context
                                    # and CreateUsdAttributeOnPath requires one
                                    error_message = f"Could not find USD context of stage {stage}"

                        if error_message:  # pragma: no cover
                            ref_self._error_msg_label.visible = True
                            ref_self._error_msg_label.text = error_message
                            carb.log_warn(error_message)
                        else:
                            ref_self._add_attribute_window.visible = False

                    ui.Button("Add", clicked_fn=lambda weak_self=weakref.ref(self): on_add(weak_self))

                    def on_cancel(weak_self):  # pragma: no cover
                        ref_self = weak_self()
                        if ref_self:
                            ref_self._add_attribute_window.visible = False

                    ui.Button("Cancel", clicked_fn=lambda weak_self=weakref.ref(self): on_cancel(weak_self))
                    ui.Spacer()

    def show_fn(self, objects: dict):
        """
        Show the popup.

        Args:
            objects (dict): The objects of the prim selection.
        """
        if "prim_list" not in objects or "stage" not in objects:  # pragma: no cover
            return False
        stage = objects["stage"]
        if not stage:  # pragma: no cover
            return False
        return len(objects["prim_list"]) >= 1

    def click_fn(self, payload: PrimSelectionPayload):
        """
        Click the popup.

        Args:
            payload (PrimSelectionPayload): The payload of the prim selection.
        """
        self._add_attribute_window.visible = True
        self._add_attribute_window_payload = payload
        self._error_msg_label.visible = False

    def __del__(self):
        """
        Delete the popup.
        """
        self.destroy()

    def hide(self):
        """
        Hide the popup.
        """
        self._add_attribute_window.visible = False
        self._add_attribute_window_payload = None
        self._error_msg_label.visible = False

    def destroy(self):
        """
        Destroy the popup.
        """
        self._add_attribute_window = None
        self._add_attribute_window_payload = None
        self._error_msg_label = None
        self._add_attr_name_field = None
        self._value_type_name_model = None
