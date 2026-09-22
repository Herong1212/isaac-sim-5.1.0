# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["WidgetGroup"]

import asyncio
from abc import abstractmethod

import omni.kit.app
import omni.ui as ui

from .context_menu import ContextMenuEvent


class WidgetGroup:
    """
    Base class to create a group of widgets on Toolbar
    """

    def __init__(self):
        self._context = ""
        self._context_token = None
        self._show_menu_task = None
        self._toolbar_ext_path = (
            omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module("omni.kit.widget.toolbar")
        )

    @abstractmethod
    def clean(self):
        """
        Clean up function to be called before destroying the object.
        """
        if self._context_token:
            self._release_toolbar_context()
            self._context_token = None
        self._context = ""

        if self._show_menu_task:
            self._show_menu_task.cancel()
            self._show_menu_task = None

    @abstractmethod
    def get_style(self) -> dict:
        """
        Gets the style of all widgets defined in this Widgets group.
        """
        pass

    @abstractmethod
    def create(self, default_size) -> dict[str, ui.Widget]:
        """
        Main function to creates widget.
        If you want to export widgets and allow external code to fetch and manipulate them, return a Dict[str, Widget] mapping from name to instance at the end of the function.
        """
        pass

    def on_toolbar_context_changed(self, context: str):
        """
        Called when toolbar's effective context has changed.

        Args:
            context: new toolbar context.
        """
        pass

    def on_added(self, context):
        """
        Called when widget is added to toolbar when calling Toolbar.add_widget

        Args:
            context: the context used to add widget when calling Toolbar.add_widget.
        """
        self._context = context

    def on_removed(self):
        """
        Called when widget is removed from toolbar when calling Toolbar.remove_widget
        """
        pass

    def _acquire_toolbar_context(self):
        """
        Request toolbar to switch to current widget's context.
        """
        import omni.kit.widget.toolbar
        self._context_token = omni.kit.widget.toolbar.get_instance().acquire_toolbar_context(self._context)

    def _release_toolbar_context(self):
        """
        Release the ownership of toolbar context and reset to default. If the ownership was preemptively taken by other owner, release does nothing.
        """
        import omni.kit.widget.toolbar
        omni.kit.widget.toolbar.get_instance().release_toolbar_context(self._context_token)

    def _is_in_context(self):
        """
        Checks if the Toolbar is in default context or owned by current widget's context.

        Override this function if you want to customize the behavior.

        Returns:
            True if toolbar is either in default context or owned by current widget.
            False otherwise.
        """
        import omni.kit.widget.toolbar
        toolbar_context = omni.kit.widget.toolbar.get_instance().get_context()
        return toolbar_context == omni.kit.widget.toolbar.Toolbar.DEFAULT_CONTEXT or self._context == toolbar_context

    def _invoke_context_menu(self, button_id: str, min_menu_entries: int = 1):
        """
        Function to invoke context menu.

        Args:
            button_id: button_id of the context menu to be invoked.
            min_menu_entries: minimal number of menu entries required for menu to be visible (default 1).
        """
        import omni.kit.widget.toolbar

        event = ContextMenuEvent()
        event.payload["widget_name"] = button_id
        event.payload["min_menu_entries"] = min_menu_entries
        omni.kit.widget.toolbar.get_instance().context_menu.on_mouse_event(event)

    def _on_mouse_pressed(self, button, button_id: str, min_menu_entries: int = 2):
        """
        Function to handle flyout menu. Either with LMB long press or RMB click.

        Args:
            button_id: button_id of the context menu to be invoked.
            min_menu_entries: minimal number of menu entries required for menu to be visible (default 1).
        """
        self._acquire_toolbar_context()
        if button == 1:  # Right click, show immediately
            self._invoke_context_menu(button_id, min_menu_entries)
        elif button == 0:  # Schedule a task if hold LMB long enough
            self._show_menu_task = asyncio.ensure_future(self._schedule_show_menu(button_id))

    def _on_mouse_released(self, button):
        if button == 0:
            if self._show_menu_task:
                self._show_menu_task.cancel()

    async def _schedule_show_menu(self, button_id: str, min_menu_entries: int = 2):
        await asyncio.sleep(0.3)
        self._invoke_context_menu(button_id, min_menu_entries)
        self._show_menu_task = None

    def _build_flyout_indicator(
        self, width, height, index: str, extension_id: str = "omni.kit.widget.toolbar", padding=7, min_menu_count=2
    ):
        import carb
        import omni.kit.context_menu

        indicator_size = 3
        with ui.Placer(offset_x=width - indicator_size - padding, offset_y=height - indicator_size - padding):
            indicator = ui.Image(
                f"{self._toolbar_ext_path}/data/icon/flyout_indicator_dark.svg",
                width=indicator_size,
                height=indicator_size,
            )

        def on_menu_changed(evt: carb.events.IEvent):
            try:
                menu_list = omni.kit.context_menu.get_menu_dict(index, extension_id)
                # because we moved separated the widget from the window extension, we need to still grab the menu from
                # the window extension
                menu_list_backward_compatible = omni.kit.context_menu.get_menu_dict(index, "omni.kit.window.toolbar")
                if menu_list_backward_compatible and evt.payload.get("extension_id", None) == "omni.kit.window.toolbar":
                    omni.kit.app.log_deprecation(
                        'Adding menu using "add_menu(menu, index, "omni.kit.window.toolbar")" is deprecated. '
                        'Please use "add_menu(menu, index, "omni.kit.widget.toolbar")"'
                    )
                # TODO check the actual menu entry visibility with show_fn
                indicator.visible = len(menu_list + menu_list_backward_compatible) >= min_menu_count
            except AttributeError as exc:
                carb.log_warn(f"on_menu_changed error {exc}")

        # Check initial state
        on_menu_changed(None)

        event_stream = omni.kit.context_menu.get_menu_event_stream()
        return event_stream.create_subscription_to_pop(on_menu_changed)
