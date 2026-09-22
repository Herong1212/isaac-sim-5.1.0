# Copyright (c) 2022, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.graph.core as og
import omni.kit.app
import omni.ui as ui

from . import UINodeCommon


class OgnSlider:
    @staticmethod
    def internal_state():
        return UINodeCommon.OgnUINodeInternalState()

    @staticmethod
    def compute(db) -> bool:
        # OM-97733: This node hasn't been converted to use the widget registry yet. Let's discourage
        # its use.
        db.log_warning("The Slider node is unsupported and may not behave as expected.")

        if db.inputs.create != og.ExecutionAttributeState.DISABLED:
            min_value = db.inputs.min
            max_value = db.inputs.max

            step = db.inputs.step
            if step <= 0:
                db.log_error("The step size of the slider must be positive!")
                return False

            width = db.inputs.width
            if width <= 0:
                db.log_error("The width of the slider must be positive!")
                return False

            widget_identifier = UINodeCommon.get_unique_widget_identifier(db)

            parent_widget = UINodeCommon.get_parent_widget(db)
            if parent_widget is None:
                return False

            # Tear down previously created widget
            if db.per_instance_state.created_widget is not None:
                UINodeCommon.tear_down_widget(db)

            def on_slider_finished_dragging(model):
                if not db.per_instance_state.created_widget.enabled:
                    return
                message_bus = omni.kit.app.get_app().get_message_bus_event_stream()
                event_name = "value_changed_" + widget_identifier
                reg_event_name = UINodeCommon.registered_event_name(event_name)
                payload = {"newValue": model.get_value_as_float(), "valueType": "float"}
                message_bus.push(reg_event_name, payload=payload)

            # Now create the button widget and register callbacks
            with parent_widget:
                db.per_instance_state.created_frame = ui.Frame()
                with db.per_instance_state.created_frame:
                    with ui.HStack(content_clipping=1):
                        db.per_instance_state.created_widget = ui.FloatSlider(
                            identifier=widget_identifier,
                            width=width,
                            min=min_value,
                            max=max_value,
                            step=step,
                        )
                        db.per_instance_state.created_widget.model.set_value((min_value + max_value) / 2)
                        db.per_instance_state.created_widget.model.add_end_edit_fn(on_slider_finished_dragging)

            db.outputs.created = og.ExecutionAttributeState.ENABLED
            db.outputs.widgetPath = UINodeCommon.find_widget_path(db.per_instance_state.created_widget)
            return True

        if db.inputs.tearDown != og.ExecutionAttributeState.DISABLED:
            return UINodeCommon.tear_down_widget(db)

        if db.inputs.show != og.ExecutionAttributeState.DISABLED:
            return UINodeCommon.show_widget(db)

        if db.inputs.hide != og.ExecutionAttributeState.DISABLED:
            return UINodeCommon.hide_widget(db)

        if db.inputs.enable != og.ExecutionAttributeState.DISABLED:
            return UINodeCommon.enable_widget(db)

        if db.inputs.disable != og.ExecutionAttributeState.DISABLED:
            return UINodeCommon.disable_widget(db)

        db.log_warning("Unexpected execution with no execution input enabled")
        return False
