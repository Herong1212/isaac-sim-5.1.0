# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ViewportMenuContainer"]

from typing import Dict, List

from carb.eventdispatcher import get_eventdispatcher, Event
import omni.ui as ui

from ..viewport_menu_model import get_items
from ..viewport_menu_model import pop_from_scope
from ..viewport_menu_model import push_to_scope
from ..viewport_menu_model import AbstractViewportMenuItem, ViewportMenuModel
from .viewport_menu_item import ViewportMenuItem


class ViewportMenuContainer(ViewportMenuItem):
    """A menu container within a viewport menubar."""
    def __init__(self, *args, **kwargs):
        """
        Constructor.

        For args and keyword args, please refer to ViewportMenuItem.
        """
        # Map from action to menu item text
        self.__actions_map = kwargs.pop("actions_map", {})
        # Map from menu item text to action
        self.__texts_map = {v: k for k, v in self.__actions_map.items()} if self.__actions_map else {}
        # Watch for hotkey register/deregister/change to support hotkey text in menu item
        if self.__actions_map:
            self.__setup_hotkey_watching()

        self.__hotkey_change_event_sub = None
        self.__hotkey_register_event_sub = None
        self.__hotkey_deregister_event_sub = None

        super().__init__(*args, **kwargs)

        # When visible and order changed, trigger UI updates
        self._visible_sub = self.visible_model.subscribe_value_changed_fn(lambda m: self._invalidate())
        self._order_sub = self.order_model.subscribe_value_changed_fn(lambda m: self._invalidate())

    def destroy(self) -> None:
        """Release resources"""
        if self.__hotkey_change_event_sub:
            self.__hotkey_change_event_sub = None
        if self.__hotkey_register_event_sub:
            self.__hotkey_register_event_sub = None
        if self.__hotkey_deregister_event_sub:
            self.__hotkey_deregister_event_sub = None

        self._visible_sub = None
        self._order_sub = None

        # Clean children
        self._clean()

        super().destroy()

    def build_fn(self, factory_args: Dict):
        """
        Callback to build menu. Reimplement it to have own customized item.

        Args:
            factory_args (dict): Argument related to viewport.
        """
        children = self._children

        # TODO: Lazy menu
        with ui.Menu(self.name, delegate=self._delegate, style=self._style):
            for child in children:
                child.build_fn(factory_args)

    def __enter__(self):
        # Clean all existing child items
        # For multiple viewport window, menu contrainer may build multiple times
        # Make sure child items not duplicated
        self._clean()

        push_to_scope(self)

    def __exit__(self, exc_type, exc_value, traceback):
        pop_from_scope()

    @property
    def _children(self) -> List[AbstractViewportMenuItem]:
        """All child items"""
        # TODO: Sorting code
        return get_items(self.name)

    def _invalidate(self) -> None:
        ViewportMenuModel()._item_changed(None)  # noqa PLW0212

    def _clean(self):
        for child in self._children:
            child.destroy()

    def _get_menu_item_hotkey_text(self, text: str) -> str:
        # get hotkey text from menu item text
        action_id = self.__texts_map.get(text, "")
        if action_id and self.__hotkeys:
            hotkey = self.__hotkeys.get(action_id, None)
            return hotkey if hotkey else ""
        return ""

    def __setup_hotkey_watching(self) -> None:
        try:
            from omni.kit.hotkeys.core import get_hotkey_registry, HOTKEY_CHANGED_GLOBAL_EVENT, HOTKEY_REGISTER_GLOBAL_EVENT, HOTKEY_DEREGISTER_GLOBAL_EVENT
            self.__hotkeys: Dict[str, str] = {}
            # Find all hotkeys registered
            registry = get_hotkey_registry()
            hotkeys = registry.get_all_hotkeys()
            for hotkey in hotkeys:
                action_id = hotkey.action_ext_id + "::" + hotkey.action_id
                if action_id in self.__actions_map:
                    self.__hotkeys[action_id] = hotkey.key_text

            # Watch hotkey events
            self.__hotkey_register_event_sub = get_eventdispatcher().observe_event(
                event_name=HOTKEY_REGISTER_GLOBAL_EVENT, on_event=self._on_hotkey_changed)
            self.__hotkey_deregister_event_sub = get_eventdispatcher().observe_event(
                event_name=HOTKEY_DEREGISTER_GLOBAL_EVENT, on_event=self._on_hotkey_deregister)
            self.__hotkey_change_event_sub = get_eventdispatcher().observe_event(
                event_name=HOTKEY_CHANGED_GLOBAL_EVENT, on_event=self._on_hotkey_changed)
        except ImportError:
            self.__hotkeys = None
            self.__hotkey_change_event_sub = None
            self.__hotkey_register_event_sub = None
            self.__hotkey_deregister_event_sub = None

    def _on_hotkey_changed(self, event: Event) -> None:
        action_id = event["action_ext_id"] + "::" + event["action_id"]
        if action_id in self.__actions_map:
            self.__hotkeys[action_id] = event["key"]
            self._invalidate()

    def _on_hotkey_deregister(self, event: Event) -> None:
        action_id = event["action_ext_id"] + "::" + event["action_id"]
        if action_id in self.__actions_map:
            self.__hotkeys.pop(action_id)
            self._invalidate()
