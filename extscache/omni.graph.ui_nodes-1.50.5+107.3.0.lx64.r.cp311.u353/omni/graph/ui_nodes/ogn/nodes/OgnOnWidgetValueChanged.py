# Copyright (c) 2022, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from contextlib import suppress

import omni.graph.core as og
from omni.graph.ui_nodes.ogn.OgnOnWidgetValueChangedDatabase import OgnOnWidgetValueChangedDatabase

from . import UINodeCommon


class OgnOnWidgetValueChanged:
    @staticmethod
    def try_resolve_output_attribute(node, attr_name, attr_type):
        out_attr = node.get_attribute(attr_name)
        attr_type_valid = attr_type.base_type != og.BaseDataType.UNKNOWN

        if out_attr.get_resolved_type().base_type != og.BaseDataType.UNKNOWN and (
            not attr_type_valid or attr_type != out_attr.get_resolved_type()
        ):
            out_attr.set_resolved_type(og.Type(og.BaseDataType.UNKNOWN))

        if attr_type_valid and out_attr.get_resolved_type().base_type == og.BaseDataType.UNKNOWN:
            out_attr.set_resolved_type(attr_type)

    @staticmethod
    def internal_state():
        return UINodeCommon.OgnUIEventNodeInternalState()

    @staticmethod
    def compute(db) -> bool:

        widget_identifier = db.inputs.widgetIdentifier
        if not widget_identifier:
            return True

        event_name = "value_changed_" + widget_identifier
        if db.per_instance_state.first_time_subscribe(db.node, event_name):
            return True

        payload = db.per_instance_state.try_pop_event()

        if payload is None:
            return True

        if "valueType" in payload.get_keys():
            value_type = payload["valueType"]
            OgnOnWidgetValueChanged.try_resolve_output_attribute(
                db.node, "outputs:newValue", og.AttributeType.type_from_ogn_type_name(value_type)
            )

        if "newValue" in payload.get_keys():
            new_value = payload["newValue"]
            db.outputs.newValue = new_value

        db.outputs.valueChanged = og.ExecutionAttributeState.ENABLED
        return True

    # ----------------------------------------------------------------------------
    @staticmethod
    def release(node):
        # Unsubscribe right away instead of waiting for GC cleanup, we don't want our callback firing
        # after the node has been released.
        with suppress(og.OmniGraphError):
            state = OgnOnWidgetValueChangedDatabase.per_instance_internal_state(node)
            state.release()
