"""
SimplePropertyWidget class.
"""

# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = [
    "LABEL_WIDTH",
    "LABEL_WIDTH_LIGHT",
    "LABEL_HEIGHT",
    "HORIZONTAL_SPACING",
    "build_frame_header",
    "SimplePropertyWidget",
    "GroupHeaderContextMenu",
    "GroupHeaderContextMenuEvent",
    "PropertyWidget",  # omni.kit.property.environment tries to import this from here
    "ButtonItem",
]

import asyncio
import functools
import traceback
from dataclasses import dataclass

import carb
import omni.kit.app
import omni.kit.window.property.managed_frame
import omni.ui as ui
from omni.kit.async_engine import run_coroutine
from omni.kit.widget.highlight_label import HighlightLabel
from omni.kit.window.property.property_widget import PropertyWidget
from omni.kit.window.property.style import get_style

from .header_context_menu import GroupHeaderContextMenu, GroupHeaderContextMenuEvent

LABEL_WIDTH = 160
LABEL_WIDTH_LIGHT = 235
LABEL_HEIGHT = 18
HORIZONTAL_SPACING = 4


@dataclass
class ButtonItem:
    """
    A dataclass for a button item.
    """

    text: str = ""
    """The text of the button."""
    icon: str = ""
    """The icon of the button."""
    width: int = 0
    """The width of the button."""
    height: int = 0
    """The height of the button."""
    enabled: bool = True
    """Whether the button is enabled."""
    callback_fn: callable = None
    """The callback function of the button."""
    identifier: str = ""
    """The identifier of the button."""


def handle_exception(func):
    """
    Decorator to print exception in async functions.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except asyncio.CancelledError:
            # We always cancel the task. It's not a problem.
            pass
        except Exception as e:  # pylint: disable=broad-exception-caught # noqa: PLW0718
            carb.log_error(f"Exception when async '{func}'")
            carb.log_error(f"{e}")
            carb.log_error(f"{traceback.format_exc()}")

    return wrapper


def build_frame_header(collapsed, text: str, group_id: str = None):
    """Custom header for CollapsibleFrame

    Args:
        collapsed (bool): Default collapsed state.
        text (str): Name of CollapsibleFrame.
        group_id (str): Group identifier, which is passed to GroupHeaderContextMenuEvent.
    """
    group_id = group_id if group_id else text

    if collapsed:
        alignment = ui.Alignment.RIGHT_CENTER
        width = 5
        height = 7
    else:
        alignment = ui.Alignment.CENTER_BOTTOM
        width = 7
        height = 5

    header_stack = ui.HStack(spacing=8)
    with header_stack:
        with ui.VStack(width=0):
            ui.Spacer()
            ui.Triangle(
                style_type_name_override="CollapsableFrame.Header", width=width, height=height, alignment=alignment
            )
            ui.Spacer()
        ui.Label(text, style_type_name_override="CollapsableFrame.Header")

    def show_attribute_context_menu(b):
        if b != 1:
            return

        event = GroupHeaderContextMenuEvent(group_id=group_id, payload=[])
        GroupHeaderContextMenu.on_mouse_event(event)

    header_stack.set_mouse_pressed_fn(lambda x, y, b, _: show_attribute_context_menu(b))


def build_frame_header_with_buttons(collapsed, text: str, group_id: str, button_list: list):
    """Custom header for CollapsibleFrame

    Args:
        collapsed (bool): Default collapsed state.
        text (str): Name of CollapsibleFrame.
        group_id (str): Group identifier, which is passed to GroupHeaderContextMenuEvent.
    """
    group_id = group_id if group_id else text

    if collapsed:
        alignment = ui.Alignment.RIGHT_CENTER
        width = 5
        height = 7
    else:
        alignment = ui.Alignment.CENTER_BOTTOM
        width = 7
        height = 5

    header_stack = ui.HStack(spacing=8)
    with header_stack:
        with ui.VStack(width=0):
            ui.Spacer()
            ui.Triangle(
                style_type_name_override="CollapsableFrame.Header", width=width, height=height, alignment=alignment
            )
            ui.Spacer()
        ui.Label(text, style_type_name_override="CollapsableFrame.Header")
        ui.Spacer()
        with ui.HStack(content_clipping=True, width=0):
            for button in button_list:
                ui.Spacer(width=8)
                if button.icon:
                    ui.Button(
                        width=button.width,
                        height=button.height,
                        clicked_fn=button.callback_fn,
                        style={"image_url": button.icon},
                        enabled=button.enabled,
                        identifier=button.identifier,
                    )
                else:
                    ui.Button(
                        button.text,
                        width=button.width,
                        height=button.height,
                        clicked_fn=button.callback_fn,
                        identifier=button.identifier,
                    )

    def show_attribute_context_menu(b):
        if b != 1:
            return

        event = GroupHeaderContextMenuEvent(group_id=group_id, payload=[])
        GroupHeaderContextMenu.on_mouse_event(event)

    header_stack.set_mouse_pressed_fn(lambda x, y, b, _: show_attribute_context_menu(b))


class SimplePropertyWidget(PropertyWidget):
    """
    SimplePropertyWidget provides a simple vertical list of "Label" -> "Value widget" pair layout.
    """

    def __init__(self, title: str, collapsed: bool = False, collapsable: bool = True):
        """Initialize class function

        Args:
            collapsed (bool): Default Collapsed state of frame.
            collapsable (collapsable): Created frame is CollapsibleFrame/Frame.
        """
        super().__init__(title)
        self._collapsed_default = collapsed
        self._collapsed = collapsed
        self._collapsable = collapsable
        self._collapsable_frame = None
        self._payload = None
        self._pending_rebuild_task = None
        self._filter_changed_sub = None
        self.__style = get_style()
        self._any_item_visible = False

    def clean(self):
        """
        See PropertyWidget.clean
        """
        self.reset()

        if self._pending_rebuild_task is not None:
            self._pending_rebuild_task.cancel()
        self._pending_rebuild_task = None

        if self._collapsable_frame is not None:
            self._collapsable_frame.set_build_fn(None)
            if self._collapsable:
                self._collapsable_frame.set_collapsed_changed_fn(None)
            self._collapsable_frame = None

    def reset(self):
        """
        See PropertyWidget.reset
        """
        # Do not cancel rebuild task here as we are called from that task through derived build_items()

    def request_rebuild(self):
        """
        Request the widget to rebuild.
        It will be rebuilt on next frame.
        """
        if self._pending_rebuild_task:
            return
        self._pending_rebuild_task = run_coroutine(self._delayed_rebuild())

    def add_label(self, label: str):
        """
        Add a Label with a highlight text based on current filter

        Args:
            label (str): Name of label.
        """
        filter_text = self._filter.name
        HighlightLabel(
            label, highlight=filter_text, name="label", width=LABEL_WIDTH, height=LABEL_HEIGHT, style=self.__style
        )

    def add_item(self, label: str, value):
        """
        This function is supposed to be called inside of build_items function.
        Adds a "Label" -> "Value widget" pair item to the widget. "value" will be an uneditable string in a StringField.

        Args:
            label (str): The label text of the entry.
            value: The value to be stringified and displayed in a StringField.
        """
        if not self._filter.matches(label):
            return

        with ui.HStack(spacing=HORIZONTAL_SPACING):
            self.add_label(label)
            ui.StringField(name="models").model.set_value(str(value))
        self._any_item_visible = True

    def add_item_with_model(self, label: str, model, editable: bool = False, identifier: str = None):
        """
        This function is supposed to be called inside of build_items function.
        Adds a "Label" -> "Value widget with model" pair item to the widget. "value" will be an editable string in a
        StringField backed by supplied model.

        Args:
            label (str): The label text of the entry.
            model: The model to be used by the string field.
            editable: If the StringField generated from model should be editable. Default is False.
        """
        if not self._filter.matches(label):
            return

        with ui.HStack(spacing=HORIZONTAL_SPACING):
            self.add_label(label)
            sf = ui.StringField(name="models", model=model, enabled=editable)
            if identifier and sf:
                sf.identifier = identifier
        self._any_item_visible = True

    def on_new_payload(self, payload, ignore_large_selection=False) -> bool:
        """
        See PropertyWidget.on_new_payload
        """
        self._payload = payload

        if (
            not ignore_large_selection
            and payload
            and hasattr(payload, "is_large_selection")
            and payload.is_large_selection()
        ):
            return False

        return True

    def build_items(self):
        """
        When derived from SimplePropertyWidget, override this function to build your items.
        """
        self.add_item("Hello", "World")

    def on_collapsed_changed(self, collapsed):
        """Update collapsed state.

        Args:
            collapsed (bool): New state of collapsed frame.
        """
        self._collapsed = collapsed

    def build_impl(self):
        """See PropertyWidget.build_impl."""
        if self._filter_changed_sub is None:
            self._filter_changed_sub = self._filter.name_model.add_value_changed_fn(self._on_filter_changed)

        if self._collapsable:
            self._collapsable_frame = ui.CollapsableFrame(
                self._title, build_header_fn=self._build_frame_header, collapsed=self._collapsed_default
            )

            self._collapsable_frame.set_collapsed_changed_fn(self.on_collapsed_changed)
            omni.kit.window.property.managed_frame.prep(self._collapsable_frame, group_name="Property")

        else:
            self._collapsable_frame = ui.Frame(height=0, style={"Frame": {"padding": 0}})
        # We cannot use build_fn because rebuild() won't trigger on invisible frames and toggling visible
        # first causes flicker during property search. So we build explicitly here.
        # request_rebuild() is still deferred to support batching of changes.
        self.request_rebuild()

    def _build_frame_header(self, collapsed, text: str, group_id: str = None):
        build_frame_header(collapsed, text, group_id)

    def _build_frame_header_with_buttons(self, collapsed, text: str, group_id: str, button_list: list):
        build_frame_header_with_buttons(collapsed, text, group_id, button_list)

    def _build_frame(self):
        import time

        start = time.monotonic()
        with ui.VStack(height=0, spacing=5, name="frame_v_stack"):
            # ui.Spacer(height=0)
            self._any_item_visible = False
            self.build_items()
            if self._filter.name:
                self._collapsable_frame.visible = self._any_item_visible
            else:
                # for compatibility with widgets which don't support filtering
                self._collapsable_frame.visible = True
            ui.Spacer(height=0)
        took = time.monotonic() - start
        if took > 0.2:
            carb.log_warn(f"{self.__class__.__name__}.build_items took {took} seconds")

    @handle_exception
    async def _delayed_rebuild(self):
        if self._pending_rebuild_task is not None:
            try:
                if self._collapsable_frame:
                    with self._collapsable_frame:
                        self._build_frame()
                    self._collapsable_frame.rebuild()  # force rebuild of frame header too
            finally:
                self._pending_rebuild_task = None

    def _on_filter_changed(self, model: ui.AbstractValueModel):
        """
        Called when filter changes. Default calls request_rebuild().
        Derived classes can override to optimize by selectively changing property visibility.

        Args:
            model (ui.AbstractValueModel): model.
        """
        self.request_rebuild()
