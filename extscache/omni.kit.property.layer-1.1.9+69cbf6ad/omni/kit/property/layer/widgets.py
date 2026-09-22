# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides the LayerPropertyWidgets class for managing layer property widgets in NVIDIA Omniverse extensions, including registration, unregistration, and update mechanisms based on layer selection changes."""


__all__ = ["LayerPropertyWidgets", "SelectionNotifier", "get_instance"]

import weakref
from pathlib import Path

import carb
import omni.ext
import omni.kit.app
import omni.usd

ICON_PATH = ""


_instance = None


def get_instance():
    """Returns the singleton instance of the class.

    Returns:
        The singleton instance of the class if it has been instantiated,
        otherwise returns None."""
    return _instance


class LayerPropertyWidgets(omni.ext.IExt):
    """A class responsible for managing layer property widgets in an extension.

    This class handles the registration and unregistration of custom property widgets
    related to layers within an NVIDIA Omniverse extension. It also manages a selection notifier
    that updates the widgets based on the current layer selection. Upon startup, this class registers
    the necessary widgets and subscribes to extension enable events to maintain the registration
    state. On shutdown, the class ensures that resources are properly released and widgets are
    unregistered. The class is designed to be used as a singleton within the scope of the extension.

    Typically, this class is not instantiated directly by the user but is managed by the Omniverse
    extension framework."""

    def __init__(self):
        """Initializes the LayerPropertyWidgets extension."""
        self._registered = False
        self._examples = None
        self._selection_notifiers = []
        self._meta_widget = None
        self._layer_path_widget = None
        self._hooks = []
        super().__init__()

    def on_startup(self, ext_id):
        """Called when the extension starts up.

        Args:
            ext_id (str): The ID of the started extension."""
        global _instance
        _instance = self

        manager = omni.kit.app.get_app().get_extension_manager()
        extension_path = manager.get_extension_path(ext_id)
        global ICON_PATH
        ICON_PATH = Path(extension_path).joinpath("data").joinpath("icons")
        self._selection_notifiers.append(SelectionNotifier())  # default context
        self._hooks = manager.subscribe_to_extension_enable(
            lambda _: self._register_widget(),
            lambda _: self._unregister_widget(),
            ext_name="omni.kit.window.property",
            hook_name="omni.kit.property.layer listener",
        )

    def on_shutdown(self):
        """Called when the extension is shutting down."""
        global _instance
        if _instance:
            _instance = None

        for notifier in self._selection_notifiers:
            notifier.stop()
        self._selection_notifiers.clear()
        self._hooks = None

        if self._registered:
            self._unregister_widget()

    def _register_widget(self):
        try:
            import omni.kit.window.property as p

            from .layer_property_widgets import LayerMetaWiget, LayerPathWidget

            w = p.get_window()
            self._layer_path_widget = LayerPathWidget(ICON_PATH)
            self._meta_widget = LayerMetaWiget(ICON_PATH)
            if w:
                w.register_widget("layers", "path", self._layer_path_widget)
                w.register_widget("layers", "metadata", self._meta_widget)

                for notifier in self._selection_notifiers:
                    notifier.start()
                    # notifier._notify_layer_selection_changed(None)  # force a refresh
                self._registered = True
        except ModuleNotFoundError as exc:
            carb.log_warn(f"error {exc}")

    def _unregister_widget(self):
        try:
            import omni.kit.window.property as p

            w = p.get_window()
            if w:
                for notifier in self._selection_notifiers:
                    notifier.stop()
                w.unregister_widget("layers", "metadata")
                w.unregister_widget("layers", "path")
                self._registered = False
            if self._layer_path_widget:
                self._layer_path_widget.destroy()
            self._layer_path_widget = None
            self._meta_widget = None
        except ModuleNotFoundError as exc:
            carb.log_warn(f"Unable to unregister omni.kit.property.layer.widgets: {exc}")


class SelectionNotifier:
    """A class responsible for notifying about layer selection changes in a property window context.

    This class subscribes to layer selection events and triggers notifications to update the property window when a layer's selection state changes. It is capable of starting and stopping the notification process and is meant to be used with a specific property window context, which could be specified during initialization.

    Args:
        property_window_context_id (str): An identifier for the property window context to which the notifier is bound. Defaults to an empty string.
    """

    def __init__(self, property_window_context_id=""):
        """Constructor for SelectionNotifier."""
        self._property_window_context_id = property_window_context_id

    def start(self):
        """Starts the notification process for layer selection changes."""
        try:
            import omni.kit.widget.layers

            omni.kit.widget.layers.add_layer_selection_changed_fn(self._notify_layer_selection_changed)
        except ImportError:
            pass

    def stop(self):
        """Stops the notification process and cleans up."""
        try:
            import omni.kit.widget.layers

            omni.kit.widget.layers.remove_layer_selection_changed_fn(self._notify_layer_selection_changed)
        except ImportError:
            pass

    def _notify_layer_selection_changed(self, item):
        import omni.kit.window.property as p

        # TODO _property_window_context_id
        w = p.get_window()
        try:
            import omni.kit.widget.layers
        except ImportError:
            pass
        else:
            if w:
                layer_item = omni.kit.widget.layers.get_current_focused_layer_item()
                if layer_item:
                    w.notify("layers", weakref.ref(layer_item))
                else:
                    w.notify("layers", None)
