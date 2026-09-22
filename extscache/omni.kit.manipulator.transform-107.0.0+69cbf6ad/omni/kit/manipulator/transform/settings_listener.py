# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import weakref
from enum import Enum, auto
from typing import Callable

import carb.dictionary
import carb.settings

from .settings_constants import c
from .subscription import Subscription


class Listener:
    """A class that manages a collection of callback functions.

    This class provides methods to add, remove, and invoke callbacks. It is used for listening to
    settings changes and executing the registered callbacks when those settings change."""

    def __init__(self):
        """Initializes the Listener with an empty dictionary to store callbacks."""
        self._callback_id = 0
        self._callbacks = {}

    def add_listener(self, callback: Callable) -> int:
        """Adds a callback to the Listener.

        Args:
            callback (Callable): The function to be called when the listener is triggered.

        Returns:
            int: A unique identifier for the newly added callback."""
        self._callback_id += 1
        self._callbacks[self._callback_id] = callback
        return self._callback_id

    def remove_listener(self, id: int):
        """Removes a callback from the Listener by its identifier.

        Args:
            id (int): The unique identifier of the callback to be removed."""
        self._callbacks.pop(id)

    def subscribe_listener(self, callback: Callable) -> Subscription:
        """Subscribes a callback to the Listener and returns a Subscription object.

        The Subscription object, when deleted, will remove the callback from the Listener.

        Args:
            callback (Callable): The function to be called when the listener is triggered.

        Returns:
            Subscription: An object representing the subscription, which can be used to unsubscribe the callback."""
        id = self.add_listener(callback)
        return Subscription(
            lambda listener=weakref.ref(self), id=id: listener().remove_listener(id) if listener() else None
        )

    def _invoke_callbacks(self, *args, **kwargs):
        """Invokes all registered callbacks with the given arguments and keyword arguments."""
        for cb in self._callbacks.values():
            cb(*args, **kwargs)


class OpSettingsListener(Listener):
    """A listener for operation settings in a transformation manipulator.

    This class extends the base `Listener` to specifically listen to changes in operation,
    translation mode, and rotation mode settings. When a change is detected, registered callbacks
    are invoked with the appropriate `CallbackType`.

    Attributes:
        selected_op: The currently selected operation mode.
        translation_mode: The current translation mode setting.
        rotation_mode: The current rotation mode setting.
    """

    class CallbackType(Enum):
        """An enumeration of callback types for the OpSettingsListener.

        This enum defines the types of changes that the OpSettingsListener can be notified about."""

        OP_CHANGED = auto()
        """Indicates the operation mode setting has changed."""
        TRANSLATION_MODE_CHANGED = auto()
        """Indicates the translation mode setting has changed."""
        ROTATION_MODE_CHANGED = auto()
        """Indicates the rotation mode setting has changed."""

    def __init__(self) -> None:
        super().__init__()

        self._dict = carb.dictionary.get_dictionary()
        self._settings = carb.settings.get_settings()

        self._op_sub = self._settings.subscribe_to_node_change_events(c.TRANSFORM_OP_SETTING, self._on_op_changed)
        self.selected_op = self._settings.get(c.TRANSFORM_OP_SETTING)

        self._translation_mode_sub = self._settings.subscribe_to_node_change_events(
            c.TRANSFORM_MOVE_MODE_SETTING, self._on_translate_mode_changed
        )
        self.translation_mode = self._settings.get(c.TRANSFORM_MOVE_MODE_SETTING)

        self._rotation_mode_sub = self._settings.subscribe_to_node_change_events(
            c.TRANSFORM_ROTATE_MODE_SETTING, self._on_rotation_mode_changed
        )
        self.rotation_mode = self._settings.get(c.TRANSFORM_ROTATE_MODE_SETTING)

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self._op_sub:
            self._settings.unsubscribe_to_change_events(self._op_sub)
            self._op_sub = None
        if self._translation_mode_sub:
            self._settings.unsubscribe_to_change_events(self._translation_mode_sub)
            self._translation_mode_sub = None
        if self._rotation_mode_sub:
            self._settings.unsubscribe_to_change_events(self._rotation_mode_sub)
            self._rotation_mode_sub = None

    def _on_op_changed(self, item, event_type):
        selected_op = self._dict.get(item)
        if selected_op != self.selected_op:
            self.selected_op = selected_op
            self._invoke_callbacks(OpSettingsListener.CallbackType.OP_CHANGED, self.selected_op)

    def _on_translate_mode_changed(self, item, event_type):
        translation_mode = self._dict.get(item)
        if self.translation_mode != translation_mode:
            self.translation_mode = translation_mode
            self._invoke_callbacks(OpSettingsListener.CallbackType.TRANSLATION_MODE_CHANGED, self.translation_mode)

    def _on_rotation_mode_changed(self, item, event_type):
        rotation_mode = self._dict.get(item)
        if self.rotation_mode != rotation_mode:
            self.rotation_mode = rotation_mode
            self._invoke_callbacks(OpSettingsListener.CallbackType.ROTATION_MODE_CHANGED, self.rotation_mode)


class SnapSettingsListener(Listener):
    """A class that listens for changes in snap settings and triggers callbacks.

    This class extends the base `Listener` class to monitor various snap settings such as snap enable toggle, snap movement along axes, snap rotation, snap scaling, and snap to surface provider. It subscribes to the settings and updates its attributes accordingly when a change is detected.

    Args:
        enabled_setting_path (str, optional): The setting path for snap enable toggle. Defaults to '/app/viewport/snapEnabled'.
        move_x_setting_path (str, optional): The setting path for snap movement along the x-axis. Defaults to '/persistent/app/viewport/stepMove/x'.
        move_y_setting_path (str, optional): The setting path for snap movement along the y-axis. Defaults to '/persistent/app/viewport/stepMove/y'.
        move_z_setting_path (str, optional): The setting path for snap movement along the z-axis. Defaults to '/persistent/app/viewport/stepMove/z'.
        rotate_setting_path (str, optional): The setting path for snap rotation. Defaults to '/persistent/app/viewport/stepRotate'.
        scale_setting_path (str, optional): The setting path for snap scaling. Defaults to '/persistent/app/viewport/stepScale'.
        provider_setting_path (str, optional): The setting path for snap to surface provider. Defaults to '/persistent/app/viewport/snapToSurface'."""

    def __init__(
        self,
        enabled_setting_path: str = None,
        move_x_setting_path: str = None,
        move_y_setting_path: str = None,
        move_z_setting_path: str = None,
        rotate_setting_path: str = None,
        scale_setting_path: str = None,
        provider_setting_path: str = None,
    ) -> None:
        """Initializes a SnapSettingsListener to listen for changes in snap settings."""
        super().__init__()

        self._dict = carb.dictionary.get_dictionary()
        self._settings = carb.settings.get_settings()

        # keep around for backward compatibility
        SNAP_ENABLED_SETTING = "/app/viewport/snapEnabled"
        SNAP_MOVE_X_SETTING = "/persistent/app/viewport/stepMove/x"
        SNAP_MOVE_Y_SETTING = "/persistent/app/viewport/stepMove/y"
        SNAP_MOVE_Z_SETTING = "/persistent/app/viewport/stepMove/z"
        SNAP_ROTATE_SETTING = "/persistent/app/viewport/stepRotate"
        SNAP_SCALE_SETTING = "/persistent/app/viewport/stepScale"
        SNAP_TO_SURFACE_SETTING = "/persistent/app/viewport/snapToSurface"

        if not enabled_setting_path:
            enabled_setting_path = SNAP_ENABLED_SETTING
        if not move_x_setting_path:
            move_x_setting_path = SNAP_MOVE_X_SETTING
        if not move_y_setting_path:
            move_y_setting_path = SNAP_MOVE_Y_SETTING
        if not move_z_setting_path:
            move_z_setting_path = SNAP_MOVE_Z_SETTING
        if not rotate_setting_path:
            rotate_setting_path = SNAP_ROTATE_SETTING
        if not scale_setting_path:
            scale_setting_path = SNAP_SCALE_SETTING
        if not provider_setting_path:
            provider_setting_path = SNAP_TO_SURFACE_SETTING

        # subscribe to snap events
        def subscribe_to_value_and_get_current(setting_val_name: str, setting_path: str):
            def on_settings_changed(tree_item, changed_item, type):
                # do not use `value = self._dict.get(tree_item)`, Dict does not work well with array setting
                value = self._settings.get(setting_path)
                setattr(self, setting_val_name, value)
                self._invoke_callbacks(setting_val_name, value)

            sub = self._settings.subscribe_to_tree_change_events(setting_path, on_settings_changed)
            value = self._settings.get(setting_path)
            setattr(self, setting_val_name, value)
            return sub

        self._snap_enabled_sub = subscribe_to_value_and_get_current("snap_enabled", enabled_setting_path)
        self._snap_move_x_sub = subscribe_to_value_and_get_current("snap_move_x", move_x_setting_path)
        self._snap_move_y_sub = subscribe_to_value_and_get_current("snap_move_y", move_y_setting_path)
        self._snap_move_z_sub = subscribe_to_value_and_get_current("snap_move_z", move_z_setting_path)
        self._snap_rotate_sub = subscribe_to_value_and_get_current("snap_rotate", rotate_setting_path)
        self._snap_scale_sub = subscribe_to_value_and_get_current("snap_scale", scale_setting_path)
        self._snap_to_surface_sub = subscribe_to_value_and_get_current("snap_to_surface", provider_setting_path)
        self._snap_provider_sub = subscribe_to_value_and_get_current("snap_provider", provider_setting_path)

    def __del__(self):
        self.destroy()

    def destroy(self):
        """Cleans up the subscriptions made by the SnapSettingsListener instance.

        This method unsubscribes from all the setting change events to which this listener has previously subscribed."""
        if self._snap_enabled_sub:
            self._settings.unsubscribe_to_change_events(self._snap_enabled_sub)
            self._snap_enabled_sub = None

        if self._snap_move_x_sub:
            self._settings.unsubscribe_to_change_events(self._snap_move_x_sub)
            self._snap_move_x_sub = None

        if self._snap_move_y_sub:
            self._settings.unsubscribe_to_change_events(self._snap_move_y_sub)
            self._snap_move_y_sub = None

        if self._snap_move_z_sub:
            self._settings.unsubscribe_to_change_events(self._snap_move_z_sub)
            self._snap_move_z_sub = None

        if self._snap_rotate_sub:
            self._settings.unsubscribe_to_change_events(self._snap_rotate_sub)
            self._snap_rotate_sub = None

        if self._snap_scale_sub:
            self._settings.unsubscribe_to_change_events(self._snap_scale_sub)
            self._snap_scale_sub = None

        if self._snap_to_surface_sub:
            self._settings.unsubscribe_to_change_events(self._snap_to_surface_sub)
            self._snap_to_surface_sub = None

        if self._snap_provider_sub:
            self._settings.unsubscribe_to_change_events(self._snap_provider_sub)
            self._snap_provider_sub = None
