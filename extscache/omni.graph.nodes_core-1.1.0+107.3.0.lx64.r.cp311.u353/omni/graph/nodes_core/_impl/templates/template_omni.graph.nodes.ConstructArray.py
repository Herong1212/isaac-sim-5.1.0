# Copyright (c) 2022-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from functools import partial

import omni.graph.core as og
from omni.graph.nodes_core.scripts.ui_utils import _build_add_remove_buttons, _retrieve_existing_numeric_dynamic_inputs
from omni.graph.ui import OmniGraphAttributeModel, OmniGraphPropertiesWidgetBuilder
from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutGroup, CustomLayoutProperty
from omni.kit.property.usd.usd_attribute_model import UsdAttributeModel
from omni.kit.property.usd.usd_attribute_widget import UsdPropertyUiEntry

MIN_INPUT_COUNT = 0


class CustomLayout:
    def __init__(self, compute_node_widget):
        self.enable = True
        self.compute_node_widget = compute_node_widget
        self.controller = og.Controller()
        self.array_size_model = None
        self.add_button = None
        self.remove_button = None
        self.node_prim_path = self.compute_node_widget._payload[-1]
        self.node = self.controller.node(self.node_prim_path)
        self._retrieve_existing_inputs = _retrieve_existing_numeric_dynamic_inputs

    def _on_click_add(self):
        (input_attribs, _) = self._retrieve_existing_inputs(self.node)

        # Increment the array size to trigger the creation of the new attribute at the end of the list
        array_size_attr = self.node.get_attribute("inputs:arraySize")
        array_size = array_size_attr.get()
        num_attribs = len(input_attribs) + 1
        if array_size != num_attribs:
            self.array_size_model.set_value(num_attribs)
            self._resize_input_array(num_attribs)

    def _on_click_remove(self):
        (input_attribs, _) = self._retrieve_existing_inputs(self.node)
        if not input_attribs:
            return

        # Decrement the array size to trigger the removal of the last attribute
        array_size_attr = self.node.get_attribute("inputs:arraySize")
        array_size = array_size_attr.get()
        num_attribs = len(input_attribs) - 1
        if array_size != num_attribs:
            (success, _) = self._resize_input_array(num_attribs)
            if success:
                self.array_size_model.set_value(num_attribs)

    def _get_input_type(self):
        """
        Returns a 2-tuple of the attribute type and extended type
        arguments required for og.Controller.create_attribute based on the first input

        Return:
            (attribute_type, extended_type) tuple. The type of attribute_type and extended_type
            depends on the extended type of the first attribute (input0)
        """

        input_0 = self.controller.node(self.node).get_attribute("inputs:input0")
        if not input_0:
            return ("any", og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY)

        if input_0.get_extended_type() == og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION:
            return (
                f"[{','.join(input_0.get_union_types())}]",
                (og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION, input_0.get_union_types()),
            )

        if input_0.get_extended_type() == og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_REGULAR:
            return (input_0.get_resolved_type(), og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_REGULAR)

        if input_0.get_extended_type() == og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY:
            return ("any", og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY)

        raise og.OmniGraphTypeError(f"Unexpected extended type {input_0.get_extended_type()} on attribute {input_0}")

    def _resize_input_array(self, new_count: int) -> tuple[bool, int]:
        """
        Resize the input array

        Args:
            new_count: The new array size

        Return:
            tuple[bool, int]: Returns a tuple with a success value and the new inputs count.
        """

        (input_attribs, largest_suffix) = self._retrieve_existing_inputs(self.node)
        current_attrib_count = len(input_attribs)

        # If the output type is resolved, store it when new attributes are added
        out_attr = self.node.get_attribute("outputs:array")
        elem_type = None
        if out_attr.get_resolved_type().base_type != og.BaseDataType.UNKNOWN:
            elem_type = out_attr.get_resolved_type()
            elem_type.array_depth = 0

        if new_count > current_attrib_count:
            create_count = new_count - current_attrib_count
            (attr_type, ext_type) = self._get_input_type()
            while create_count > 0:
                create_count = create_count - 1
                largest_suffix = largest_suffix + 1
                new_attrib = self.controller.create_attribute(
                    self.node,
                    f"inputs:input{largest_suffix}",
                    attr_type,
                    og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT,
                    None,
                    ext_type,
                )
                if elem_type:
                    new_attrib.set_resolved_type(elem_type)
        else:
            remove_count = current_attrib_count - new_count
            while remove_count > 0:
                attrib_to_remove = self.node.get_attribute(f"inputs:input{largest_suffix}")
                try:
                    self.controller.remove_attribute(attrib_to_remove)
                except og.OmniGraphError:
                    return False, largest_suffix + 1
                largest_suffix = largest_suffix - 1
                remove_count = remove_count - 1
        return True, largest_suffix + 1

    def _on_array_size_changed(self, model: UsdAttributeModel):
        """Callback when the arraySize attribute changes"""
        if model._is_prev_same():  # noqa: PLW0212
            return

        # negative values are not allowed
        new_attrib_count = max(model.get_value_as_int(), 0)

        (success, new_count) = self._resize_input_array(new_attrib_count)
        if not success:
            model.set_value(new_count)

    def _on_array_size_reset_to_default(self, model: UsdAttributeModel):
        default = 1
        if model._has_default_value:  # noqa: PLW0212
            default = model._default_value  # noqa: PLW0212

        (_, new_count) = self._resize_input_array(default)
        model.set_value(new_count)

    def _build_array_size_property(self, ui_prop: UsdPropertyUiEntry, *args) -> OmniGraphAttributeModel:
        stage = self.compute_node_widget.stage
        # Build arraySize property widget with the default builder
        self.array_size_model = OmniGraphPropertiesWidgetBuilder.build(
            stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            args[-3],  # prim_paths
            args[-2],  # additional_label_kwargs
            args[-1],  # additional_widget_kwargs
        )
        # register the value changed callback
        self.array_size_model.add_end_edit_fn(self._on_array_size_changed)
        self.array_size_model.set_on_set_default_fn(
            lambda m=self.array_size_model: self._on_array_size_reset_to_default(m)
        )
        return self.array_size_model

    def _controls_build_fn(self, *args):
        def _remove_button_enabled() -> bool:
            (input_attribs, _) = self._retrieve_existing_inputs(self.node)
            return len(input_attribs) > MIN_INPUT_COUNT

        _build_add_remove_buttons(self, self._on_click_add, self._on_click_remove, _remove_button_enabled)

    def apply(self, props):
        # Called by compute_node_widget to apply UI when selection changes
        def find_prop(name):
            return next((p for p in props if p.prop_name == name), None)

        frame = CustomLayoutFrame(hide_extra=True)
        (input_attribs, _) = self._retrieve_existing_inputs(self.node)
        with frame:
            with CustomLayoutGroup("Inputs"):
                prop = find_prop("inputs:arraySize")
                if prop is not None:
                    CustomLayoutProperty(prop.prop_name, None, build_fn=partial(self._build_array_size_property, prop))

                prop = find_prop("inputs:arrayType")
                if prop is not None:
                    CustomLayoutProperty(prop.prop_name)

                for attrib in input_attribs:
                    prop = find_prop(attrib.get_name())
                    if prop is not None:
                        CustomLayoutProperty(prop.prop_name)

                CustomLayoutProperty(None, None, build_fn=self._controls_build_fn)

            prop = find_prop("outputs:array")
            if prop is not None:
                with CustomLayoutGroup("Outputs"):
                    CustomLayoutProperty(prop.prop_name)

        return frame.apply(props)
