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
from omni.graph.ui_nodes.ogn.OgnOnWidgetClickedDatabase import OgnOnWidgetClickedDatabase

from . import UINodeCommon


class OgnOnWidgetClicked:
    @staticmethod
    def internal_state():
        return UINodeCommon.OgnUIEventNodeInternalState()

    @staticmethod
    def compute(db) -> bool:

        widget_identifier = db.inputs.widgetIdentifier
        if not widget_identifier:
            return True

        event_name = "clicked_" + widget_identifier
        if db.per_instance_state.first_time_subscribe(db.node, event_name):
            return True

        payload = db.per_instance_state.try_pop_event()

        if payload is None:
            return True

        # Currently payload is an empty dictionary

        db.outputs.clicked = og.ExecutionAttributeState.ENABLED
        return True

    # ----------------------------------------------------------------------------
    @staticmethod
    def release(node):
        # Unsubscribe right away instead of waiting for GC cleanup, we don't want our callback firing
        # after the node has been released.
        with suppress(og.OmniGraphError):
            state = OgnOnWidgetClickedDatabase.shared_internal_state(node)
            state.release()
