"""
This is the implementation of the OGN node defined in OgnPrintText.ogn
"""

import time

import carb
import omni.graph.core as og
from omni.kit.viewport.utility import get_viewport_from_window_name, post_viewport_message


class OgnOnCustomEventInternalState:
    """Convenience class for maintaining per-node state information"""

    def __init__(self):
        self.display_time: float = 0


class OgnPrintText:
    """
    Prints text to the log and optionally the viewport
    """

    @staticmethod
    def internal_state():
        """Returns an object that will contain per-node state information"""
        return OgnOnCustomEventInternalState()

    @staticmethod
    def compute(db) -> bool:
        """Compute the outputs from the current input"""

        def ok():
            db.outputs.execOut = og.ExecutionAttributeState.ENABLED
            return True

        try:
            toast_min_period_s = 5.0
            to_screen = db.inputs.toScreen
            log_level = db.inputs.logLevel.lower()
            text = db.inputs.text

            if not text:
                return ok()

            if log_level:
                if log_level not in ("error", "warning", "warn", "info"):
                    db.log_error("Log Level must be one of error, warning or info")
                    return False
            else:
                log_level = "info"

            if to_screen:
                toast_time = db.per_instance_state.display_time

                viewport_name = db.inputs.viewport
                viewport_api = get_viewport_from_window_name(viewport_name)
                if viewport_api is None:
                    # Preserve legacy behavior of erroring when a name was provided
                    if viewport_name:
                        db.log_error(f"Could not get viewport window {viewport_name}")
                        return False
                    return ok()

                now_s = time.time()
                toast_age = now_s - toast_time
                if toast_age > toast_min_period_s:
                    toast_time = 0
                if toast_time == 0:
                    post_viewport_message(viewport_api, text)
                    db.state.displayTime = now_s
            else:
                # FIXME: Toast also prints to log so we only do one or the other
                if log_level == "info":
                    carb.log_info(text)
                elif log_level.startswith("warn"):
                    carb.log_warn(text)
                else:
                    carb.log_error(text)

            return ok()

        except Exception as error:  # pylint: disable=broad-except
            db.log_error(str(error))
            return False
