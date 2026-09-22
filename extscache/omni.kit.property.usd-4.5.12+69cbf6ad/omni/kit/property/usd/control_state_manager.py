# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ControlStateHandler", "ControlStateManager"]

import weakref
from typing import Callable

import omni.usd
from pxr import Usd


class ControlStateHandler:
    """
    Class that handles the control state of an attribute.
    """

    def __init__(self, on_refresh_state: Callable, on_build_state: Callable, icon_path: str):
        """
        Initializes a new instance of the ControlStateHandler.

        Args:
            on_refresh_state (Callable): function to be called when control state refreshes. Callable should returns a tuple(bool, bool).
                The first bool decides if the flag of this state should be set. The second bool decides if a force rebuild should be triggered.
            on_build_state (Callable): function to be called when build control state UI. Callable should returns a tuple(bool, Callable, str).
                If first bool is True, subsequent states with lower (larger value) priority will be skipped.
                Second Callable is the action to perform when click on the icon.
                Third str is tooltip when hovering over icon.
            icon_path (str): path to an SVG file to show next to attribute when this state is True.
        """
        self.on_refresh_state = on_refresh_state
        self.on_build_state = on_build_state
        self.icon_path = icon_path


class ControlStateManager:
    """
    Class that manages the control states of an attribute.
    """

    _instance = None

    @classmethod
    def get_instance(cls):
        """Get current instance for ControlStateManager."""
        return weakref.proxy(cls._instance)

    def __init__(self, icon_path):
        """Initializes a new instance of the ControlStateManager.

        Args:
            icon_path: Path for icons."""
        self._icon_path = icon_path
        self._next_flag = 1
        self._control_state_handlers = {}
        ControlStateManager._instance = self
        self._builtin_handles = []
        self._default_icon_path = f"{self._icon_path}/Default value.svg"
        self._register_builtin_handlers()

    def __del__(self):  # pragma: no cover
        self.destory()

    def destory(self):
        """Cleans up control states."""
        for handle_flag in self._builtin_handles:
            self.unregister_control_state(handle_flag)

        ControlStateManager.instance = None

    def register_control_state(
        self, on_refresh_state: Callable, on_build_state: Callable, icon_path: str, priority: float = 0.0
    ) -> int:
        """Registers a new control states.

        Args:
            on_refresh_state (Callable): function to be called when control state refreshes. Callable should returns a tuple(bool, bool).
                The first bool decides if the flag of this state should be set. The second bool decides if a force rebuild should be triggered.
            on_build_state (Callable): function to be called when build control state UI. Callable should returns a tuple(bool, Callable, str).
                If first bool is True, subsequent states with lower (larger value) priority will be skipped.
                Second Callable is the action to perform when click on the icon.
                Third str is tooltip when hovering over icon.
            icon_path (str): path to an SVG file to show next to attribute when this state is True.
            priority (float): priority override.
        """
        entry = ControlStateHandler(on_refresh_state, on_build_state, icon_path)
        flag = self._next_flag
        self._next_flag <<= 1
        self._add_entry(flag, priority, entry)
        return flag

    def unregister_control_state(self, flag):
        """Unregisters a existing control state."""
        self._control_state_handlers.pop(flag)

    def update_control_state(self, usd_model_base):
        """Updates control state."""
        control_state = 0
        force_refresh = False
        for flag, (_, handler) in self._control_state_handlers.items():
            set_flag, f_refresh = handler.on_refresh_state(usd_model_base)
            force_refresh |= f_refresh
            if set_flag:
                control_state |= flag

        return control_state, force_refresh

    def build_control_state(self, control_state, **kwargs):
        """Gets control state values for UI."""
        for flag, (_, handler) in self._control_state_handlers.items():
            handled, action, tooltip = handler.on_build_state(flag & control_state, **kwargs)
            if handled:
                return action, handler.icon_path, tooltip

        return None, self._default_icon_path, ""

    def _add_entry(self, flag: int, priority: float, entry: ControlStateHandler):
        self._control_state_handlers[flag] = (priority, entry)
        # sort by priority
        self._control_state_handlers = dict(sorted(self._control_state_handlers.items(), key=lambda item: item[1][0]))

    def _register_builtin_handlers(self):
        self._builtin_handles.append(self._register_mixed())
        self._builtin_handles.append(self._register_connected())
        self._builtin_handles.append(self._register_connected_error())
        self._builtin_handles.append(self._register_keyed())
        self._builtin_handles.append(self._register_sampled())
        self._builtin_handles.append(self._register_not_default())
        self._builtin_handles.append(self._register_locked())
        self._builtin_handles.append(self._register_readonly())

    def _register_mixed(self):
        def on_refresh(usd_model_base):
            return usd_model_base.is_ambiguous(), False

        def on_build(has_state_flag, **kwargs):
            model = kwargs.get("model")
            widget_comp_index = kwargs.get("widget_comp_index", -1)
            mixed_overlay = kwargs.get("mixed_overlay", None)
            if mixed_overlay and not isinstance(mixed_overlay, list):
                mixed_overlay = [mixed_overlay]
            no_mixed = kwargs.get("no_mixed", False)

            if not has_state_flag or no_mixed or not model.is_comp_ambiguous(widget_comp_index):
                if mixed_overlay:
                    for overlay in mixed_overlay:
                        overlay.visible = False

                return False, None, None

            if mixed_overlay:
                # for array only one mixed overlay
                if model.is_array_type() and len(mixed_overlay) == 1:
                    mixed_overlay[0].visible = model.is_ambiguous()
                else:
                    for i, overlay in enumerate(mixed_overlay):
                        comp_index = max(widget_comp_index, i)
                        overlay.visible = model.is_comp_ambiguous(comp_index)

            return True, None, "Mixed value among selected prims"

        icon_path = f"{self._icon_path}/mixed properties.svg"

        return self.register_control_state(on_refresh, on_build, icon_path, 0)

    def _register_connected(self):
        def on_refresh(usd_model_base):
            return any(usd_model_base.get_connections()), False

        def on_build(has_state_flag, **kwargs):
            if not has_state_flag:
                return False, None, None

            model = kwargs.get("model")
            value_widget = kwargs.get("value_widget", None)
            extra_widgets = kwargs.get("extra_widgets", [])

            action = None
            tooltip = ""

            connections = model.get_connections()
            # if its a bad connection, ignore as that is handled by _register_connected_error
            if connections and hasattr(model, "get_bad_connection"):
                bad_connection, _ = model.get_bad_connection()
                if bad_connection:
                    return False, None, None

            if not all(ele == connections[0] for ele in connections):
                tooltip = "Attribute have different connections among selected prims."

            last_prim_connections = connections[-1]
            if len(last_prim_connections) > 0:
                if value_widget:
                    value_widget.enabled = False
                for widget in extra_widgets:
                    widget.enabled = False

                if not tooltip:
                    for path in last_prim_connections:
                        tooltip += f"{path}\n"

                def on_click_connection(*arg, path=last_prim_connections[-1]):
                    # Get connection on last selected prim
                    last_prim_connections = model.get_connections()[-1]
                    if len(last_prim_connections) > 0:
                        # TODO multi-context, pass context name in payload??
                        selection = omni.usd.get_context().get_selection()
                        selection.set_selected_prim_paths([path.GetPrimPath().pathString], True)

                action = on_click_connection
            return True, action, tooltip

        icon_path = f"{self._icon_path}/Expression.svg"

        return self.register_control_state(on_refresh, on_build, icon_path, 10)

    def _register_connected_error(self):
        def on_refresh(usd_model_base):
            return any(usd_model_base.get_connections()), False

        def on_build(has_state_flag, **kwargs):
            if not has_state_flag:
                return False, None, None

            model = kwargs.get("model")
            # verify model has _bad_connection as not everything inherits from UsdBase
            if not hasattr(model, "get_bad_connection"):
                return False, None, None

            value_widget = kwargs.get("value_widget", None)
            extra_widgets = kwargs.get("extra_widgets", [])

            action = None
            _, tooltip = model.get_bad_connection()

            connections = model.get_connections()
            # if its a bad connection, ignore as that is handled by _register_connected_bad
            bad_connection, _ = model.get_bad_connection()
            if connections and not bad_connection:
                return False, None, None

            last_prim_connections = connections[-1]
            if len(last_prim_connections) > 0:
                if value_widget:
                    value_widget.enabled = False
                for widget in extra_widgets:
                    widget.enabled = False

                def on_click_connection(*arg, path=last_prim_connections[-1]):
                    # Get connection on last selected prim
                    last_prim_connections = model.get_connections()[-1]
                    if len(last_prim_connections) > 0:
                        # TODO multi-context, pass context name in payload??
                        selection = omni.usd.get_context().get_selection()
                        selection.set_selected_prim_paths([path.GetPrimPath().pathString], True)

                action = on_click_connection
            return True, action, tooltip

        icon_path = f"{self._icon_path}/Expression-bad.svg"

        return self.register_control_state(on_refresh, on_build, icon_path, 10)

    def _register_locked(self):
        def on_refresh(usd_model_base):
            return usd_model_base.is_locked(), False

        def on_build(has_state_flag, **kwargs):
            if not has_state_flag:
                return False, None, None

            return True, None, "Value is locked"

        icon_path = f"{self._icon_path}/Locked Value.svg"

        return self.register_control_state(on_refresh, on_build, icon_path, 20)

    def _register_readonly(self):
        def on_refresh(usd_model_base):
            return usd_model_base.is_readonly() if hasattr(usd_model_base, "is_readonly") else False, False

        def on_build(has_state_flag, **kwargs):
            if not has_state_flag:
                return False, None, None

            return True, None, "Value is locked"

        icon_path = f"{self._icon_path}/Locked Value.svg"

        return self.register_control_state(on_refresh, on_build, icon_path, 20)

    def _register_keyed(self):
        def on_refresh(usd_model_base):
            # pylint: disable=protected-access
            current_time_code = usd_model_base.get_current_time_code()
            for attribute in usd_model_base._get_attributes():
                if isinstance(attribute, Usd.Attribute) and omni.usd.attr_has_timesample_on_key(
                    attribute, current_time_code
                ):
                    return True, False  # pragma: no cover
            return False, False

        def on_build(has_state_flag, **kwargs):
            if not has_state_flag:
                return False, None, None

            return True, None, "Timesampled keyframe"  # pragma: no cover

        icon_path = f"{self._icon_path}/TimeSamples.svg"

        return self.register_control_state(on_refresh, on_build, icon_path, 20)

    def _register_sampled(self):
        def on_refresh(usd_model_base):
            # pylint: disable=protected-access
            return usd_model_base._might_be_time_varying, False

        def on_build(has_state_flag, **kwargs):
            if not has_state_flag:
                return False, None, None

            return True, None, "Timesampled value"  # pragma: no cover

        icon_path = f"{self._icon_path}/TimeVarying.svg"

        return self.register_control_state(on_refresh, on_build, icon_path, 30)

    def _register_not_default(self):
        def on_refresh(usd_model_base):
            return usd_model_base.is_different_from_default(), False

        def on_build(has_state_flag, **kwargs):
            if not has_state_flag:
                return False, None, None

            model = kwargs.get("model")
            widget_comp_index = kwargs.get("widget_comp_index", -1)
            return True, lambda *_: model.set_default(widget_comp_index), "Value different from default"

        icon_path = f"{self._icon_path}/Changed value.svg"

        return self.register_control_state(on_refresh, on_build, icon_path, 40)
