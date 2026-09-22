# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["LayerExtension", "get_current_focused_layer_item", "set_current_focused_layer_item", "remove_layer_selection_changed_fn", "add_layer_selection_changed_fn", "get_layer_model", "get_selected_items"]

from typing import Callable
import carb
from carb.eventdispatcher import get_eventdispatcher
import os
import asyncio
from pathlib import Path
import omni.ext
import omni.usd
import omni.kit.app
import omni.ui as ui
import omni.kit.notification_manager as nm
import omni.kit.usd.layers as layers
from omni.kit.menu.utils import MenuHelperExtension
import omni.kit.app

from omni.kit.usd.layers import LayerUtils
from typing import List
from pxr import Sdf

from .window import LayerWindow
from .layer_item import LayerItem
from .layer_model import LayerModel
from .layer_link_window import LayerLinkWindow
from .layer_model_utils import LayerModelUtils
from .actions import ActionManager

ICON_PATH = Path(__file__).parent.absolute().parent.parent.parent.parent.joinpath("icons")
_extension_instance = None


class LayerExtension(omni.ext.IExt, MenuHelperExtension):
    """The entry point for Layer 2"""

    CONTEXT_MENU_ITEM_INSERT_SUBLAYER = "Insert As Sublayer"
    """ context menu item to insert sublayer """
    WINDOW_NAME = "Layer"
    """ Layer extension window's name"""
    MENU_GROUP = "Window"
    """ Menu shows in 'Window' group """

    def on_startup(self, ext_id):
        """
        Called on extension startup.

        Args:
            ext_id (int): The ID of the extension.

        """
        global _extension_instance
        _extension_instance = self

        # Register command related actions
        self._ext_name = omni.ext.get_extension_name(ext_id)
        self._action_manager = ActionManager()
        self._action_manager.on_startup(self)

        ui.Workspace.set_show_window_fn(LayerExtension.WINDOW_NAME, self.show_window)

        self._usd_context = omni.usd.get_context()
        self._layers = layers.get_layers(self._usd_context)
        self._selection_listeners = set([])
        self._window = None
        self.menu_startup(LayerExtension.WINDOW_NAME, LayerExtension.WINDOW_NAME, LayerExtension.MENU_GROUP)
        ui.Workspace.show_window(LayerExtension.WINDOW_NAME)

        self._link_window = None

        app = omni.kit.app.get_app()
        self._context_icon_menu_items = []
        self._extensions_subscription = [
            get_eventdispatcher().observe_event(observer_name="omni.kit.widget.layers", on_event=self._on_event, event_name=omni.ext.GLOBAL_EVENT_SCRIPT_CHANGED),
            get_eventdispatcher().observe_event(observer_name="omni.kit.widget.layers", on_event=self._on_event, event_name=omni.ext.GLOBAL_EVENT_FOLDER_CHANGED),
        ]
        self._menu_registered = False

        self._on_layer_edit_mode_update(self._layers.get_edit_mode())
        self._layer_edit_mode_subscription = self._layers.get_event_stream().create_subscription_to_pop_by_type(
            int(layers.LayerEventType.EDIT_MODE_CHANGED),
            self._on_layer_events, name="Layers Extension"
        )

    def _on_layer_events(self, event: carb.events.IEvent):
        payload = layers.get_layer_event_payload(event)
        if payload and payload.event_type == layers.LayerEventType.EDIT_MODE_CHANGED:
            edit_mode = self._layers.get_edit_mode()
            self._on_layer_edit_mode_update(edit_mode)

    def _on_layer_edit_mode_update(self, edit_mode):
        if edit_mode == layers.LayerEditMode.SPECS_LINKING:
            if not self._link_window:
                self._link_window = LayerLinkWindow()
        elif self._link_window:
            self._link_window.destroy()
            self._link_window = None

    def _on_event(self, _):
        if not self._menu_registered:
            self._register_menus()
            self._menu_registered = True

    def on_shutdown(self):
        """Called on extension shutdown."""
        self._action_manager.on_shutdown()

        global _extension_instance
        _extension_instance = None
        if self._link_window:
            self._link_window.destroy()
            self._link_window = None

        # remove menu
        self.menu_shutdown()
        if self._window:
            self._window.destroy()
            self._window = None

        for fn in self._selection_listeners:
            fn(None)
        self._selection_listeners.clear()

        self._menu_registered = False
        self._extensions_subscription = None
        self._unregister_menus()
        self._layers = None

        ui.Workspace.set_show_window_fn(LayerExtension.WINDOW_NAME, None)

    def _get_content_window(self):
        try:
            import omni.kit.window.content_browser as content

            return content.get_content_window()
        except ImportError:
            pass

        return None

    def _unregister_menus(self):
        self._context_icon_menu_items.clear()
        extension_manager = omni.kit.app.get_app_interface().get_extension_manager()

        content_window = self._get_content_window()
        if content_window and extension_manager.is_extension_enabled("omni.kit.window.content_browser"):
            content_window.delete_context_menu(self.CONTEXT_MENU_ITEM_INSERT_SUBLAYER)

    def _register_menus(self):
        content_window = self._get_content_window()

        if content_window:
            content_window.add_context_menu(
                self.CONTEXT_MENU_ITEM_INSERT_SUBLAYER,
                f"{ICON_PATH}/icoExternalLink.svg",
                lambda b, c: self._on_icon_menu_click(b, c),
                LayerExtension._is_show_insert_visible,
                separator_name=None,
                index=3  # Index
            )

    @staticmethod
    def _is_show_insert_visible(content_url):
        return omni.usd.is_usd_writable_filetype(content_url)

    def _on_icon_menu_click(self, menu, value):
        file_path = value
        stage = self._usd_context.get_stage()
        if not stage:
            return

        root_layer = stage.GetRootLayer()
        if root_layer.identifier != file_path:
            found = False
            for sublayer_path in root_layer.subLayerPaths:
                absolute_path = root_layer.ComputeAbsolutePath(sublayer_path)
                if os.path.normpath(value) == os.path.normpath(absolute_path):
                    found = True

            if found:
                nm.post_notification(
                    f"Duplicate sublayer found in the Root Layer.",
                    status=nm.NotificationStatus.WARNING,
                    duration=4
                )
            else:
                LayerUtils.insert_sublayer(root_layer, 0, file_path)
        else:
            nm.post_notification(
                f"Cannot insert Root Layer as sublayer.",
                status=nm.NotificationStatus.WARNING,
                duration=4
            )

    async def _destroy_window_async(self):
        # wait one frame, this is due to the one frame defer
        # in Window::_moveToMainOSWindow()
        await omni.kit.app.get_app().next_update_async()
        if self._window:
            self._window.destroy()
            self._window = None

    def _visibility_changed_fn(self, visible):
        self.menu_refresh()
        if not visible:
            # Destroy the window, since we are creating new window
            # in show_window
            asyncio.ensure_future(self._destroy_window_async())

    def show_window(self, value):
        """
        Show or hide the Layer Window.

        Args:
            value (bool): True to show the window, False to hide it.

        """
        if value and not self._window:
            self._window = LayerWindow(LayerExtension.WINDOW_NAME, self._usd_context)
            self._window.set_visibility_changed_listener(self._visibility_changed_fn)
            # Register selection listeners again

            for fn in self._selection_listeners:
                self._window.add_layer_selection_changed_fn(fn)

        elif self._window:
            self._window.set_visible(value)
            for fn in self._selection_listeners:
                fn(None)

    @omni.kit.app.deprecated("omni.kit.widget.layers.LayerExtension.get_current_focused_layer_item is deprecated. Use omni.kit.widget.layers.get_current_focused_layer_item instead.")
    def get_current_focused_layer_item(self) -> LayerItem:
        """
        Get the current focused layer item in the Layer Window.

        Returns:
            LayerItem or None: The current focused layer item, or None if the window is not available.

        """
        if not self._window:
            return None

        return self._window.get_current_focused_layer_item()

    @omni.kit.app.deprecated("omni.kit.widget.layers.LayerExtension.set_current_focused_layer_item is deprecated. Use omni.kit.widget.layers.set_current_focused_layer_item instead.")
    def set_current_focused_layer_item(self, layer_identifier: str):
        """
        Set the focused layer item in the Layer Window.

        Args:
            layer_identifier (str): The identifier of the layer item to set as focused.

        """
        if not self._window:
            return

        return self._window.set_current_focused_layer_item(layer_identifier)

    @omni.kit.app.deprecated("omni.kit.widget.layers.LayerExtension.remove_layer_selection_changed_fn is deprecated. Use omni.kit.widget.layers.remove_layer_selection_changed_fn instead.")
    def remove_layer_selection_changed_fn(self, fn: Callable[[LayerItem], None]):
        """
        Remove a selection listener.

        Args:
            fn (Callable[[LayerItem], None]): The selection listener function to remove.

        """
        if not fn:
            return

        self._selection_listeners.discard(fn)

        if not self._window:
            return

        return self._window.remove_layer_selection_changed_fn(fn)

    @omni.kit.app.deprecated("omni.kit.widget.layers.LayerExtension.add_layer_selection_changed_fn is deprecated. Use omni.kit.widget.layers.add_layer_selection_changed_fn instead.")
    def add_layer_selection_changed_fn(self, fn: Callable[[LayerItem], None]):
        """
        Add a layer selection changed function to the selection listeners.

        Args:
            fn (Callable[[LayerItem], None]): The function to add.

        Returns:
            Any: The result of the window's `add_layer_selection_changed_fn` method.

        """
        if not fn:
            return

        self._selection_listeners.add(fn)

        if not self._window:
            return

        return self._window.add_layer_selection_changed_fn(fn)

    @omni.kit.app.deprecated("omni.kit.widget.layers.LayerExtension.get_layer_model is deprecated. Use omni.kit.widget.layers.get_layer_model instead.")
    def get_layer_model(self) -> LayerModel:
        """
        Get the layer model from the window.

        Returns:
            LayerModel or None: The layer model from the window, or None if the window is not available.

        """
        if not self._window:
            return None

        return self._window.get_layer_model()

    @omni.kit.app.deprecated("omni.kit.widget.layers.LayerExtension.get_selected_items is deprecated. Use omni.kit.widget.layers.get_selected_items instead.")
    def get_selected_items(self) -> List[ui.AbstractItem]:
        """
        Get the selected items from the layer view in the window.

        Returns:
            List[ui.AbstractItem]: The selected items, or an empty list if the window is not available.

        """
        if not self._window:
            return []

        return list(self._window.layer_view.selection)

    @omni.kit.app.deprecated("omni.kit.widget.layers.LayerExtension.get_instance is deprecated, please use the public API for specific functionality instead of accessing the extension instance.")
    @staticmethod
    def get_instance():
        """
        Returns the instance of the extension.

        Returns:
            The instance of the extension.
        """
        return _extension_instance


def _get_instance():
    return _extension_instance


def get_current_focused_layer_item() -> LayerItem:
    """
    Get the current focused layer item in the Layer Window.

    Returns:
        LayerItem or None: The current focused layer item, or None if the window is not available.

    """
    ext_inst = _get_instance()
    if not ext_inst._window:
        return None

    return ext_inst._window.get_current_focused_layer_item()

def set_current_focused_layer_item(layer_identifier: str):
    """
    Set the focused layer item in the Layer Window.

    Args:
        layer_identifier (str): The identifier of the layer item to set as focused.

    """
    ext_inst = _get_instance()
    if not ext_inst._window:
        return

    return ext_inst._window.set_current_focused_layer_item(layer_identifier)

def remove_layer_selection_changed_fn(fn: Callable[[LayerItem], None]):
    """
    Remove a selection listener.

    Args:
        fn (Callable[[LayerItem], None]): The selection listener function to remove.

    """
    if not fn:
        return

    ext_inst = _get_instance()
    ext_inst._selection_listeners.discard(fn)

    if not ext_inst._window:
        return

    return ext_inst._window.remove_layer_selection_changed_fn(fn)

def add_layer_selection_changed_fn(fn: Callable[[LayerItem], None]):
    """
    Add a layer selection changed function to the selection listeners.

    Args:
        fn (Callable[[LayerItem], None]): The function to add.

    Returns:
        Any: The result of the window's `add_layer_selection_changed_fn` method.

    """
    if not fn:
        return

    ext_inst = _get_instance()
    ext_inst._selection_listeners.add(fn)

    if not ext_inst._window:
        return

    return ext_inst._window.add_layer_selection_changed_fn(fn)

def get_layer_model() -> LayerModel:
    """
    Get the layer model from the window.

    Returns:
        LayerModel or None: The layer model from the window, or None if the window is not available.

    """
    ext_inst = _get_instance()
    if not ext_inst._window:
        return None

    return ext_inst._window.get_layer_model()

def get_selected_items() -> List[ui.AbstractItem]:
    """
    Get the selected items from the layer view in the window.

    Returns:
        List[ui.AbstractItem]: The selected items, or an empty list if the window is not available.

    """
    ext_inst = _get_instance()
    if not ext_inst._window:
        return []

    return list(ext_inst._window.layer_view.selection)
