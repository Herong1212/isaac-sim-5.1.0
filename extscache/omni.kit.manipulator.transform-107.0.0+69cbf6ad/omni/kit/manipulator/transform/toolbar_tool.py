# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from __future__ import annotations

import asyncio
import weakref
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Dict
from weakref import ProxyType

import carb
import omni.kit.app
import omni.kit.context_menu
import omni.ui as ui

from .manipulator import TransformManipulator
from .types import Operation


class ToolbarTool(ABC):
    """An abstract base class for creating toolbar tools that interact with TransformManipulators.

    This class provides foundational structure and common functionality for specialized toolbar tools. It is not intended to be instantiated directly but subclassed by concrete tool implementations.

    Args:
        manipulator (ProxyType[TransformManipulator]): A weak reference proxy to the TransformManipulator.
        operation (Operation): The operation type that the toolbar tool is associated with.
        toolbar_height (int): The height of the toolbar to which the tool belongs.
        toolbar_payload (Dict[str, Any]): Optional; A dictionary of payload items for the toolbar.
        tooltip_update_fn (Callable[[str, bool, float], None]): Optional; Function to call for updating tooltips."""

    def __init__(
        self,
        manipulator: ProxyType[TransformManipulator],
        operation: Operation,
        toolbar_height: int,
        toolbar_payload: Dict[str, Any] = {},
        tooltip_update_fn: Callable[[str, bool, float], None] = None,
    ):
        """Initializes a new instance of a toolbar tool."""
        self._manipulator = manipulator
        self._operation = operation
        self._model = manipulator.model
        self._toolbar_height = toolbar_height
        self._toolbar_payload = toolbar_payload
        self._tooltip_update_fn = tooltip_update_fn

    def destroy(self):
        """Cleans up resources and references held by the toolbar tool."""
        self._manipulator = None
        self._model = None
        self._toolbar_payload = None
        self._tooltip_update_fn = None

    def __del__(self):
        self.destroy()

    @classmethod
    @abstractmethod
    def can_build(cls, manipulator: TransformManipulator, operation: Operation) -> bool:
        """
        Called right before a tool instance is to be instantiated to determine if this tool can be built on current toolbar.

        Args:
            manipulator (TransformManipulator): manipulator that hosts the toolbar
            operation (Operation): The transform Operation the tool will be built for.

        Return:
            bool: True if the tool can be built, its constructor will be called. False if not, the tool will be skipped and not placed on toolbar.
        """
        raise NotImplementedError("You must override `can_build` in your derived class!")
        return False


class DefaultMenuDelegate(ui.MenuDelegate):
    """A delegate for default menu that handles the style of the context menu.

    This delegate provides a default style configuration for context menus used within the application."""

    def get_style(self):
        """Gets the style configuration for the context menu.

        Returns:
            The style configuration dictionary for the menu."""
        from omni.kit.context_menu import style

        return style.MENU_STYLE


class SimpleToolButton(ToolbarTool):
    """A toolbar button with optional context menu for transform manipulators.

    This class provides a button for the toolbar that can interact with transform manipulators and optionally display a context menu.

    Args:
        menu_delegate (ui.MenuDelegate, optional): Delegate for styling the context menu associated with the button.
        *args: Variable length argument list for parent class initialization.
        **kwargs: Arbitrary keyword arguments for parent class initialization."""

    def __init__(self, menu_delegate: ui.MenuDelegate = None, *args, **kwargs):
        """Initializes a new instance of a simple tool button with an optional context menu."""
        super().__init__(*args, **kwargs)
        self._show_menu_task = None
        self._cancel_next_value_changed = False  # workaround context menu triggering button state change
        self._ignore_model_change = False
        self._button = None
        self._stack = None
        self._menu_delegate = menu_delegate if menu_delegate else DefaultMenuDelegate()

    def destroy(self):
        """Cleans up resources and references held by the simple tool button."""
        self._menu_delegate = None

        if self._show_menu_task is not None:
            self._show_menu_task.cancel()
            self._show_menu_task = None

        if self._button:
            self._button.set_mouse_hovered_fn(None)

        self._sub = None
        self._button = None
        self._stack = None

        super().destroy()

    def _get_style(self) -> Dict:
        """Gets the style configuration for the button.

        Returns:
            Dict: The style configuration dictionary for the button."""
        return {
            "Button": {"background_color": 0x0},
            "Button:checked": {"background_color": 0x8FD1912E},
            "Button:hovered": {"background_color": 0x0},
            "Button:pressed": {"background_color": 0x0},
        }

    def _build_widget(
        self,
        button_name: str,
        model: ui.AbstractValueModel,
        enabled_img_url: str,
        disabled_img_url: str = None,
        menu_index: str = None,
        menu_extension_id: str = None,
        no_toggle: bool = False,
        menu_on_left_click: bool = False,
        menu_payload: Dict[str, Any] = {},
        tooltip: str = "",
        disabled_tooltip: str = "",
    ):
        """Builds the button widget with an optional context menu.

        Args:
            button_name (str): The name of the button.
            model (ui.AbstractValueModel): The model that holds the button state.
            enabled_img_url (str): The URL to the image displayed when the button is enabled.
            disabled_img_url (str, optional): The URL to the image displayed when the button is disabled.
            menu_index (str, optional): Identifier for the context menu.
            menu_extension_id (str, optional): Extension ID related to the context menu.
            no_toggle (bool, optional): If True, the button doesn't toggle state on click.
            menu_on_left_click (bool, optional): If True, displays the context menu on left click.
            menu_payload (Dict[str, Any], optional): Additional payload for the context menu.
            tooltip (str, optional): The tooltip text when the button is enabled.
            disabled_tooltip (str, optional): The tooltip text when the button is disabled."""
        self._button_name = button_name
        self._model = model
        self._enabled_img_url = enabled_img_url
        self._disabled_img_url = disabled_img_url
        self._menu_index = menu_index
        self._menu_extension_id = menu_extension_id
        self._no_toggle = no_toggle
        self._menu_on_left_click = menu_on_left_click
        self._menu_payload = menu_payload
        self._tooltip = tooltip
        self._disabled_tooltip = disabled_tooltip
        self._button_hovered = False

        style = {}
        if self._disabled_img_url:
            style[f"Button.Image::{self._button_name}_enabled"] = {"image_url": f"{self._enabled_img_url}"}
            style[f"Button.Image::{self._button_name}_disabled"] = {"image_url": f"{self._disabled_img_url}"}
        else:
            style[f"Button.Image::{self._button_name}"] = {"image_url": f"{self._enabled_img_url}"}

        style.update(self._get_style())

        self._stack = ui.ZStack(width=0, height=0, style=style)
        with self._stack:
            dimension = self._toolbar_height
            self._button = ui.ToolButton(
                name=self._button_name,
                model=self._model,
                image_width=dimension,
                image_height=dimension,
            )
            self._button.set_mouse_hovered_fn(self._on_hovered)
            if self._menu_index is not None and self._menu_extension_id is not None:
                self._button.set_mouse_pressed_fn(lambda x, y, b, _: self._on_mouse_pressed(b, self._menu_index))
                self._button.set_mouse_released_fn(lambda x, y, b, _: self._on_mouse_released(b))
                self._build_flyout_indicator(dimension, dimension, self._menu_index, self._menu_extension_id)

        # only update name if enabled and disabled imgs are different
        if self._disabled_img_url or self._tooltip != self._disabled_tooltip:
            self._update_name(self._button, self._button.model.as_bool)

        self._sub = self._button.model.subscribe_value_changed_fn(self._on_model_changed)

    def _on_hovered(self, state: bool):
        """Callback function that is called when the button is hovered.

        Args:
            state (bool): The hover state of the button."""
        self._button_hovered = state
        if self._tooltip and self._tooltip_update_fn:
            tooltip = (
                self._disabled_tooltip if not self._button.model.as_bool and self._disabled_tooltip else self._tooltip
            )
            self._tooltip_update_fn(tooltip, state, self._button.screen_position_x)

    def _on_model_changed(self, model):
        """Callback function that is called when the button's model value changes.

        Args:
            model: The model associated with the button."""
        if self._ignore_model_change:
            return

        if self._no_toggle:
            self._ignore_model_change = True
            model.set_value(not model.as_bool)
            self._ignore_model_change = False
            return

        if self._cancel_next_value_changed:
            self._cancel_next_value_changed = False
            model.set_value(not model.as_bool)

        if self._disabled_img_url or self._tooltip != self._disabled_tooltip:
            self._update_name(self._button, model.as_bool)

    def _update_name(self, button: ui.ToolButton, enabled: bool):
        """Updates the button's name based on its enabled state.

        Args:
            button (ui.ToolButton): The button to update.
            enabled (bool): The enabled state of the button."""
        if self._disabled_img_url:
            button.name = f"{self._button_name}_{'enabled' if enabled else 'disabled'}"
        self._on_hovered(self._button_hovered)
        self._manipulator.refresh_toolbar()

    def _invoke_context_menu(self, button_id: str, right_click: bool, min_menu_entries: int = 1):
        """Invokes the context menu for the button.

        Args:
            button_id (str): The identifier of the button.
            right_click (bool): Indicates whether the menu is invoked by a right click.
            min_menu_entries (int, optional): The minimum number of entries required for the menu to be visible."""
        context_menu = omni.kit.context_menu.get_instance()

        objects = {"widget_name": button_id, "manipulator": self._manipulator, "model": self._model}
        objects.update(self._toolbar_payload)
        objects.update(self._menu_payload)

        menu_list = omni.kit.context_menu.get_menu_dict(self._menu_index, self._menu_extension_id)
        context_menu.show_context_menu(
            self._menu_index, objects, menu_list, min_menu_entries, delegate=self._menu_delegate
        )

        # if from long LMB hold
        if not right_click:
            self._cancel_next_value_changed = True

    def _on_mouse_pressed(self, button, button_id: str, min_menu_entries: int = 1):
        """Function to handle flyout menu. Either with LMB long press or RMB click.

        Args:
            button: Mouse button that was pressed.
            button_id (str): The identifier of the button.
            min_menu_entries (int, optional): The minimum number of entries required for the menu to be visible."""
        if button == 1 or button == 0 and self._menu_on_left_click:  # show immediately
            # We cannot call self._invoke_context_menu directly inside of sc.Widget's context, otherwise it will be draw
            # on the auxiliary window. Schedule a async task so the menu is still in main window
            self._show_menu_task = asyncio.ensure_future(
                self._schedule_show_menu(button_id, wait_seconds=0.0, min_menu_entries=min_menu_entries)
            )
        elif button == 0:  # Schedule a task if hold LMB long enough
            self._show_menu_task = asyncio.ensure_future(
                self._schedule_show_menu(button_id, min_menu_entries=min_menu_entries)
            )

    def _on_mouse_released(self, button):
        """Handler for button release events, potentially canceling the display of the context menu.

        Args:
            button: Mouse button that was released."""
        if button == 0:
            if self._show_menu_task:
                self._show_menu_task.cancel()

    async def _schedule_show_menu(self, button_id: str, min_menu_entries: int = 1, wait_seconds: float = 0.3):
        """Schedules the display of the context menu after a delay.

        Args:
            button_id (str): The identifier of the button for the context menu.
            min_menu_entries (int, optional): The minimum number of entries required for the menu to be visible.
            wait_seconds (float, optional): The time to wait before showing the menu."""
        if wait_seconds > 0.0:
            await asyncio.sleep(wait_seconds)
        try:
            self._invoke_context_menu(button_id, False, min_menu_entries)
        except Exception:
            import traceback

            carb.log_error(traceback.format_exc())
        self._show_menu_task = None

    def _build_flyout_indicator(self, width, height, index: str, extension_id: str, padding=-8, min_menu_count=1):
        """Builds an indicator for the flyout menu.

        Args:
            width: The width of the area where the indicator will be placed.
            height: The height of the area where the indicator will be placed.
            index (str): The index used for context menu retrieval.
            extension_id (str): The extension ID related to the context menu.
            padding (int, optional): The padding offset for the indicator's position.
            min_menu_count (int, optional): The minimum number of menu entries required for the indicator to be visible.

        Returns:
            Subscription: A subscription to the menu event stream to update the indicator visibility."""
        indicator_size = 4
        ICON_FOLDER_PATH = Path(f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/data/icons")
        with ui.Placer(offset_x=width - indicator_size - padding, offset_y=height - indicator_size - padding):
            indicator = ui.Image(
                f"{ICON_FOLDER_PATH}/flyout_indicator_dark.svg",
                width=indicator_size,
                height=indicator_size,
            )

        def on_menu_changed(evt: carb.events.IEvent):
            try:
                menu_list = omni.kit.context_menu.get_menu_dict(index, extension_id)
                # TODO check the actual menu entry visibility with show_fn
                indicator.visible = len(menu_list) >= min_menu_count
            except AttributeError as exc:
                carb.log_warn(f"on_menu_changed error {exc}")

        # Check initial state
        on_menu_changed(None)

        event_stream = omni.kit.context_menu.get_menu_event_stream()
        return event_stream.create_subscription_to_pop(on_menu_changed)
