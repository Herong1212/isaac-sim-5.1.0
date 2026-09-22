# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ButtonMenuEntry", "PrimPathWidget"]

import asyncio
import unicodedata
import weakref
from functools import lru_cache
from typing import Callable

import carb
import omni.kit.clipboard
import omni.ui as ui
import omni.usd
from omni.kit.widget.highlight_label import HighlightLabel
from omni.kit.window.property.templates import HORIZONTAL_SPACING, LABEL_HEIGHT, SimplePropertyWidget
from pxr import Sdf, Tf, Trace, Usd

from .add_attribute_popup import AddAttributePopup
from .context_menu import ContextMenu, ContextMenuEvent
from .prim_selection_payload import PrimSelectionPayload

g_singleton = None


@lru_cache()
def _get_plus_glyph():
    return ui.get_custom_glyph_code("${glyphs}/menu_context.svg")


def post_notification(
    message: str, info: bool = False, duration: int = 3, hide_after_timeout: bool = True
):  # pragma: no cover
    """Posts a notification.

    Args:
        message (str): The message to post.
        info (bool): Whether the message is an info message.
        duration (int): The duration of the message.
        hide_after_timeout (bool): Whether to hide the message after the timeout.
    """
    try:
        import omni.kit.notification_manager as nm

        nm.post_notification(
            message,
            status=nm.NotificationStatus.INFO if info else nm.NotificationStatus.WARNING,
            duration=duration,
            hide_after_timeout=hide_after_timeout,
        )
    except ModuleNotFoundError:
        pass


class Constant:
    """A class for constants.

    This class is used to store constants that are used throughout the application.
    """

    def __setattr__(self, name, value):  # pragma: no cover
        """Raises a ValueError if an attempt is made to change a constant.

        Args:
            name (str): The name of the constant.
            value (any): The value to set the constant to.
        """
        raise ValueError(f"Can't change Constant.{name}")

    MIXED = "Mixed"
    """A constant for mixed values."""
    MIXED_COLOR = 0xFFCC9E61
    """A constant for the mixed color."""
    LABEL_COLOR = 0xFF9E9E9E
    """A constant for the label color."""
    LABEL_FONT_SIZE = 14
    """A constant for the label font size."""
    LABEL_WIDTH = 80
    """A constant for the label width."""
    ADD_BUTTON_SIZE = 52
    """A constant for the add button size."""


class ButtonMenuEntry:
    """A class for a button menu entry.

    This class is used to store a button menu entry.
    """

    def __init__(
        self,
        path: str,
        glyph: str = None,
        name_fn: Callable = None,
        show_fn: Callable = None,
        enabled_fn: Callable = None,
        onclick_fn: Callable = None,
        add_to_context_menu: bool = False,
    ):
        self.path = path
        self.glyph = glyph
        self.name_fn = name_fn
        self.show_fn = show_fn
        self.enabled_fn = enabled_fn
        self.onclick_fn = onclick_fn
        if add_to_context_menu:
            self.context_menu = omni.kit.widget.context_menu.add_menu(self.get_context_menu(), "ADD", "")
        else:  # pragma: no cover
            self.context_menu = None

    def clean(self):
        """Cleans up the context menu."""
        self.context_menu = None

    def get_dict(self, payload, name=None):
        """Gets the dictionary representation of the button menu entry.

        Args:
            payload (any): The payload to be passed to the onclick function.
            name (str): The name of the button menu entry.

        Returns:
            dict: The dictionary representation of the button menu entry.
        """
        data = {}
        if name:
            data = {"name": name}
        else:
            data = {"name": self.path}

        data["glyph"] = self.glyph
        if self.name_fn:
            data["name_fn"] = self.name_fn
        if self.show_fn:
            data["show_fn"] = self.show_fn
        if self.enabled_fn:
            data["enabled_fn"] = self.enabled_fn
        if self.onclick_fn:
            data["onclick_fn"] = lambda o, p=payload: self.onclick_fn(payload=p)

        return data

    def get_context_menu(self):
        """Gets the context menu for the button menu entry.

        Returns:
            dict: The context menu for the button menu entry.
        """
        parts = self.path.split("/")
        if len(parts) > 1:
            last_name = parts.pop()
            first_name = parts.pop(0)
            context_root = {"name": {first_name: []}}
            context_item = context_root["name"][first_name]

            while parts:
                name = parts.pop(0)
                context_item.append({"name": {name: []}})
                context_item = context_item[0]["name"][name]

            context_item.append(
                {
                    "name": last_name,
                    "glyph": self.glyph,
                    "name_fn": self.name_fn,
                    "show_fn": self.show_fn,
                    "enabled_fn": self.enabled_fn,
                    "onclick_fn": lambda o, f=(
                        weakref.ref(self.onclick_fn) if self.onclick_fn else None
                    ): PrimPathWidget.payload_wrapper(objects=o, onclick_fn_weak=f),
                }
            )
            return context_root

        context_item = {
            "name": self.path,
            "glyph": self.glyph,
            "name_fn": self.name_fn,
            "show_fn": self.show_fn,
            "enabled_fn": self.enabled_fn,
            "onclick_fn": lambda o, f=(
                weakref.ref(self.onclick_fn) if self.onclick_fn else None
            ): PrimPathWidget.payload_wrapper(objects=o, onclick_fn_weak=f),
        }

        return context_item


class MenuDelegate(ui.MenuDelegate):
    """A delegate for the menu.

    This class is used to handle the menu delegate.
    """

    def get_parameters(self, name, kwargs):
        """Gets the parameters for the menu.

        Args:
            name (str): The name of the parameter.
            kwargs (dict): The keyword arguments.

        Returns:
            dict: The parameters for the menu.
        """
        if name == "tearable":
            kwargs[name] = False
        return kwargs


class PrimPathWidget(SimplePropertyWidget):
    """A widget for displaying and interacting with USD Prim paths in Omniverse Kit applications.

    This widget extends the SimplePropertyWidget to provide a comprehensive interface for USD Prim path manipulation and visualization. It includes features such as renaming Prims, adding attributes, and displaying various Prim properties like instanceability and path. It supports large selection handling and integrates with the application's notification system for feedback. The widget also incorporates a context menu for additional actions and utilizes a caching mechanism for performance optimization.
    """

    def __init__(self):
        """Initializes the PrimPathWidget."""
        super().__init__(title="Path", collapsable=False)
        self._context_menu = ContextMenu()
        self._path_draw_items = []
        self._button_menu_items = []
        self._hooks = []
        self._path_item_padding = 0.0
        self._listener = None
        self._add_attribute_popup = None
        self._anchor_prim = None
        self._show_instance = None
        self._any_item_visible = False
        self._menu_delegate = MenuDelegate()
        self._hooks.append(
            omni.kit.app.SettingChangeSubscription(
                "exts/omni.kit.property.usd/allow_rename_prims", self._on_rename_setting_changed
            )
        )
        self._on_rename_setting_changed(None, carb.settings.ChangeEventType.CHANGED)

        global g_singleton
        g_singleton = self

        self.add_path_item(self._build_prim_name_widget)
        self.add_path_item(self._build_prim_path_widget)
        # self.add_path_item(self._build_prim_stage_widget)
        self.add_path_item(self._build_prim_instanceable_widget)
        self.add_path_item(self._build_prim_large_selection_widget)
        self._add_menus()

    def __del__(self):  # pragma: no cover
        """Destroy the PrimPathWidget."""
        self.clean()
        self.reset()
        global g_singleton
        g_singleton = None

    def clean(self):
        """Cleans up resources managed by the widget."""
        self._path_draw_items = []
        if self._add_attribute_popup:
            self._add_attribute_popup.destroy()
            self._add_attribute_popup = None
        super().clean()

    def reset(self):
        """Resets the widget to its initial state."""
        if self._listener:
            self._listener.Revoke()
        self._listener = None

    def on_new_payload(self, payload):  # pylint: disable=arguments-differ
        """Handles a new payload for the widget.

        Args:
            payload (dict): The new payload to be handled by the widget.

        Returns:
            bool: True if the payload is handled successfully, otherwise False."""
        if self._payload != payload and self._add_attribute_popup:
            self._add_attribute_popup.hide()

        if not super().on_new_payload(payload, ignore_large_selection=True):
            return False  # pragma: no cover

        self._anchor_prim = None
        stage = payload.get_stage()
        instance = []
        if stage:
            for prim_path in payload:
                prim = stage.GetPrimAtPath(prim_path)
                if prim:
                    self._anchor_prim = prim
                    instance.append(prim.IsInstanceable())

        self._show_instance = len(set(instance)) == 1
        return payload and len(payload) > 0

    @staticmethod
    def payload_wrapper(objects, onclick_fn_weak):
        """Wraps the payload for onclick events.

        Args:
            objects (dict): Objects associated with the onclick event.
            onclick_fn_weak (Callable): Weakref to the onclick function to be executed."""
        onclick_fn = onclick_fn_weak()
        if onclick_fn:
            prim_paths = []
            if "prim_list" in objects:
                prim_paths = [prim.GetPath() for prim in objects["prim_list"]]
            payload = PrimSelectionPayload(weakref.ref(objects["stage"]), prim_paths)
            onclick_fn(payload=payload)

    def build_items(self):
        """Builds the items for the widget based on the current payload."""
        self.reset()
        if self._anchor_prim:
            self._listener = Tf.Notice.Register(
                Usd.Notice.ObjectsChanged, self._on_usd_changed, self._anchor_prim.GetStage()
            )

        for item in self._path_draw_items:
            item()
        # we always show prim name regardless of filter
        self._any_item_visible = True

    def _build_prim_name_widget(self):
        from omni.kit.property.usd.usd_property_widget import get_ui_style

        def get_names_as_string(prim_paths):
            paths = ""
            for path in prim_paths:
                paths += f"{path.name}\n"
            return paths

        prim_paths = self._payload
        selected_info_name = "(nothing selected)"
        is_editable = False
        tooltip = ""
        if len(prim_paths) > 1:
            selected_info_name = f"({len(prim_paths)} models selected) common attributes shown"
            for index, path in enumerate(prim_paths):
                tooltip += f"{path.name}\n"
                if index > 9:
                    tooltip += "...."
                    break
        elif len(prim_paths) == 1:
            selected_info_name = f"{prim_paths[0].name}"
            is_editable = self._allow_rename_prims

        with ui.HStack(height=0):
            weakref_menu = weakref.ref(self._context_menu)
            ui.Spacer(width=8)
            button_width = Constant.ADD_BUTTON_SIZE
            if get_ui_style() == "NvidiaLight":
                button_width = Constant.ADD_BUTTON_SIZE + 25
            add_button = ui.Button(f"{_get_plus_glyph()} Add", width=button_width, height=LABEL_HEIGHT, name="add")
            add_button.set_mouse_pressed_fn(
                lambda x, y, b, m, widget=add_button: self._on_mouse_pressed(b, weakref_menu, widget)
            )
            ui.Spacer(width=(Constant.LABEL_WIDTH + self._path_item_padding) - button_width)
            ui.Spacer(width=8)
            if get_ui_style() == "NvidiaLight":
                ui.Spacer(width=10)

            frame = ui.Frame()
            with frame:
                widget = ui.StringField(
                    name="prims_name",
                    height=LABEL_HEIGHT,
                    tooltip=tooltip,
                    tooltip_offset_y=22,
                    enabled=False,
                    identifier="prim_name",
                )
            widget.model.set_value(selected_info_name)

            copy_func = lambda _: self._copy_to_clipboard(
                to_copy=get_names_as_string(prim_paths=prim_paths)
            )  # pylint: disable=unnecessary-lambda-assignment
            if is_editable:

                async def editf(b, m, w, f, tt):
                    self._edit_field(model=w.model, frame=f, tooltip=tt, buttons=b)
                    self._build_copy_menu(buttons=b, context_menu=weakref_menu, copy_fn=copy_func)

                widget.set_mouse_pressed_fn(
                    lambda x, y, b, m, w=widget, f=frame, tt=tooltip: asyncio.ensure_future(editf(b, m, w, f, tt))
                )
            else:
                widget.set_mouse_pressed_fn(
                    lambda x, y, b, m: self._build_copy_menu(buttons=b, context_menu=weakref_menu, copy_fn=copy_func)
                )

            ui.Spacer(width=5)

    def _on_rename_setting_changed(self, item, event_type):
        if event_type == carb.settings.ChangeEventType.CHANGED:
            self._allow_rename_prims = carb.settings.get_settings().get_as_bool(
                "/exts/omni.kit.property.usd/allow_rename_prims"
            )

    def _build_prim_path_widget(self):
        from omni.kit.property.usd.usd_property_widget import get_ui_style

        def get_paths_as_string(prim_paths):
            paths = ""
            for path in prim_paths:
                paths += f"{path.pathString}\n"

            return paths

        if not self._filter.matches("Prim Path"):
            return

        highlight = self._filter.name

        prim_paths = self._payload
        weakref_menu = weakref.ref(self._context_menu)
        selected_info_name = ""
        tooltip = ""
        style = {}
        if len(prim_paths) == 1:
            selected_info_name = f"{prim_paths[0]}"
        elif len(prim_paths) > 1:
            selected_info_name = Constant.MIXED
            style = {"Field": {"color": Constant.MIXED_COLOR}, "Tooltip": {"color": 0xFF333333}}

            for index, path in enumerate(prim_paths):
                tooltip += f"{path}\n"
                if index > 9:
                    tooltip += "...."
                    break

        with ui.HStack(height=0):
            ui.Spacer(width=8)
            HighlightLabel(
                "Prim Path",
                name="path_label",
                width=Constant.LABEL_WIDTH + self._path_item_padding,
                height=LABEL_HEIGHT,
                style={"font_size": Constant.LABEL_FONT_SIZE},
                highlight=highlight,
            )
            ui.Spacer(width=8)
            if get_ui_style() == "NvidiaLight":
                ui.Spacer(width=10)
            widget = ui.StringField(
                name="prims_path",
                height=LABEL_HEIGHT,
                enabled=False,
                tooltip=tooltip,
                tooltip_offset_y=22,
                style=style,
                identifier="prim_path",
            )
            widget.model.set_value(selected_info_name)
            widget.set_mouse_pressed_fn(
                lambda x, y, b, m: self._build_copy_menu(
                    buttons=b,
                    context_menu=weakref_menu,
                    copy_fn=lambda _: self._copy_to_clipboard(to_copy=get_paths_as_string(prim_paths=prim_paths)),
                )
            )
            ui.Spacer(width=5)

    def _build_prim_stage_widget(self):
        stage_path = "unsaved"
        stage = self._payload.get_stage()
        weakref_menu = weakref.ref(self._context_menu)
        if stage and stage.GetRootLayer() and stage.GetRootLayer().realPath:
            stage_path = stage.GetRootLayer().realPath

        with ui.HStack(height=0):
            ui.Spacer(width=8)
            ui.Label(
                "Stage Path",
                name="stage_label",
                width=Constant.LABEL_WIDTH + self._path_item_padding,
                height=LABEL_HEIGHT,
                style={"font_size": Constant.LABEL_FONT_SIZE},
            )
            ui.Spacer(width=8)
            widget = ui.StringField(name="prims_stage", height=LABEL_HEIGHT, enabled=False)
            widget.model.set_value(stage_path)
            widget.set_mouse_pressed_fn(
                lambda x, y, b, m, model=widget.model: self._build_copy_menu(
                    buttons=b,
                    context_menu=weakref_menu,
                    copy_fn=lambda _: self._copy_to_clipboard(to_copy=model.as_string),
                )
            )
            ui.Spacer(width=5)

    def _build_prim_instanceable_widget(self):
        from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidgetBuilder, get_ui_style

        if not self._anchor_prim or not self._show_instance:
            return

        def on_instanceable_changed(model):
            omni.kit.commands.execute("ToggleInstanceableCommand", prim_path=self._payload.get_paths())

        if not self._filter.matches("Instanceable"):
            return

        highlight = self._filter.name

        additional_label_kwargs = {"highlight": highlight}
        with ui.HStack(spacing=HORIZONTAL_SPACING):
            settings = carb.settings.get_settings()
            left_aligned = settings.get("ext/omni.kit.window.property/checkboxAlignment") == "left"

            if not left_aligned:
                additional_label_kwargs["width"] = 0
            else:
                additional_label_kwargs["width"] = (Constant.LABEL_WIDTH + self._path_item_padding) - 8
            if get_ui_style() == "NvidiaLight":
                additional_label_kwargs["word_wrap"] = False
            ui.Spacer(width=3)
            UsdPropertiesWidgetBuilder.create_label("Instanceable", {}, additional_label_kwargs)
            if not left_aligned:
                ui.Spacer(width=15)
            else:
                ui.Spacer(width=0)
            with ui.VStack(width=10):
                ui.Spacer()
                check_box = ui.CheckBox(width=10, height=0, name="greenCheck")
                check_box.model.set_value(self._anchor_prim.IsInstanceable())
                check_box.model.add_value_changed_fn(on_instanceable_changed)
                ui.Spacer()
            if left_aligned:
                ui.Spacer(width=5)
            ui.Spacer(width=5)

    def _build_prim_large_selection_widget(self):
        def show_all():
            if self._payload:
                self._payload.set_large_selection_override(True)
                property_window = omni.kit.window.property.get_window()
                if property_window:
                    property_window.request_rebuild()

        if self._payload.is_large_selection():
            ui.Separator()
            ui.Label(
                f"You have selected {len(self._payload)} Prims, to preserve fast performance the Property Widget is not showing above the current limit of {self._payload.get_large_selection_count()} Prims. Press the button below to show it anyway but expect it to take some time",
                alignment=ui.Alignment.CENTER,
                word_wrap=True,
            )
            ui.Button(
                "Skip Large Selection Protection", clicked_fn=lambda: show_all(), identifier="large_payload_show_all"
            )  # pylint: disable=unnecessary-lambda-assignment

    def _add_menus(self):
        # pylint: disable=protected-access
        self._add_attribute_popup = AddAttributePopup()

        self.add_button_menu_entry(
            "Attribute",
            show_fn=lambda objects, weak_self=weakref.ref(self): (
                weak_self()._add_attribute_popup.show_fn(objects) if weak_self() else None
            ),
            onclick_fn=lambda payload, weak_self=weakref.ref(self): (
                weak_self()._add_attribute_popup.click_fn(payload) if weak_self() else None
            ),
        )

    def _on_mouse_pressed(self, button, context_menu, widget):
        """Called when the user press the mouse button on the item"""
        if button != 0:  # pragma: no cover
            # It's for LMB menu only
            return

        if not context_menu():  # pragma: no cover
            return

        # Show the menu
        xpos = (int)(widget.screen_position_x)
        ypos = (int)(widget.screen_position_y + widget.computed_content_height)
        context_menu().on_mouse_event(
            ContextMenuEvent(self._payload, self._button_menu_items, xpos, ypos, delegate=self._menu_delegate)
        )

    def _build_copy_menu(self, buttons, context_menu, copy_fn):
        if buttons != 1:
            # It's for right mouse button for menu only
            return

        if not context_menu():  # pragma: no cover
            return

        # setup menu
        menu_list = [{"name": "Copy to clipboard", "glyph": "menu_link.svg", "onclick_fn": copy_fn}]

        # show menu
        context_menu().show_context_menu(menu_list=menu_list)

    def _edit_field(self, model, frame, tooltip, buttons):
        if buttons != 0:
            # It's for left mouse button only
            return

        with frame:
            widget = ui.StringField(
                name="prims_name",
                height=LABEL_HEIGHT,
                tooltip=tooltip,
                tooltip_offset_y=22,
                identifier="prim_name_rename",
            )
            widget.model.set_value(model.as_string)
            widget.focus_keyboard()

        widget.model.add_begin_edit_fn(lambda m, w=widget: self._prim_name_begin_edit(model=m))
        widget.model.add_end_edit_fn(lambda m, w=widget: self._prim_name_end_edit(model=m))

    def _prim_name_begin_edit(self, model):
        # OMPE-31959: Check and convert current label if Unicode normalization is enabled
        from omni.kit.widget.stage import UnicodeNormalizationMethod, get_unicode_normalization_method

        normalize_method = get_unicode_normalization_method()
        if normalize_method != UnicodeNormalizationMethod.DISABLED:
            normalized_name = unicodedata.normalize(normalize_method, model.as_string)
            if normalized_name != model.as_string:
                msg = f"Unicode {normalize_method} normalization has altered the prim name from '{model.as_string}' to '{normalized_name}'."
                carb.log_warn(msg)
                post_notification(msg)

            model.set_value(normalized_name)

    def _prim_name_end_edit(self, model):
        def select_new_prim(old_prim_name: Sdf.Path, new_prim_name: Sdf.Path):
            omni.usd.get_context().get_selection().set_selected_prim_paths([new_prim_name.pathString], True)

        def rename_viewport_active_camera(old_prim_name: Sdf.Path, new_prim_name: Sdf.Path):
            try:
                from omni.kit.viewport.utility import get_active_viewport

                viewport = get_active_viewport()
                if viewport and viewport.camera_path == old_prim_name:
                    viewport.camera_path = new_prim_name or "/OmniverseKit_Persp"
            except ImportError:
                pass

        def get_normalized_name(name, method):
            return unicodedata.normalize(method, name)

        def get_new_prim_path(stage, parent_path, new_prim_name, prim):
            new_prim_path = parent_path.AppendChild(new_prim_name)
            return omni.usd.get_stage_next_free_path(stage, new_prim_path, False, source_prim=prim)

        stage = self._payload.get_stage()
        prim = stage.GetPrimAtPath(self._payload[0])

        if not prim:
            PrimPathWidget.rebuild()
            return

        from omni.kit.widget.stage import UnicodeNormalizationMethod, get_unicode_normalization_method

        normalize_method = get_unicode_normalization_method()
        if (
            prim.GetPath().name == model.get_value_as_string()
            and normalize_method == UnicodeNormalizationMethod.DISABLED
        ):
            PrimPathWidget.rebuild()
            return

        old_prim_path = prim.GetPath().pathString
        new_prim_name = omni.usd.make_valid_identifier(model.get_value_as_string())
        parent_path = prim.GetPath().GetParentPath()

        if normalize_method != UnicodeNormalizationMethod.DISABLED:
            normalized_new_prim_name = get_normalized_name(new_prim_name, normalize_method)
            # Notify user if normalization changes the prim name
            if normalized_new_prim_name != new_prim_name:
                msg = f"Unicode {normalize_method} normalization has altered the prim name from '{new_prim_name}' to '{normalized_new_prim_name}'."
                carb.log_warn(msg)
                post_notification(msg)

            normalized_child_names = {
                get_normalized_name(child.GetName(), normalize_method)
                for child in prim.GetParent().GetChildren()
                if child != prim
            }
            new_prim_name = normalized_new_prim_name
            if new_prim_name in normalized_child_names:
                new_prim_name = Sdf.Path(get_new_prim_path(stage, parent_path, new_prim_name, prim)).name
        else:
            new_prim_name = Sdf.Path(get_new_prim_path(stage, parent_path, new_prim_name, prim)).name

        new_prim_path = parent_path.AppendChild(new_prim_name).pathString
        if new_prim_path == old_prim_path:
            PrimPathWidget.rebuild()
            return

        if Sdf.Path.IsValidPathString(new_prim_path):
            rename_viewport_active_camera(old_prim_path, new_prim_path)
            move_dict = {old_prim_path: new_prim_path}
            omni.kit.commands.execute(
                "MovePrims", paths_to_move=move_dict, on_move_fn=select_new_prim, destructive=False
            )
        else:
            post_notification(f"Cannot rename {old_prim_path} to {new_prim_path} as its not a valid USD path")

    def _copy_to_clipboard(self, to_copy):
        omni.kit.clipboard.copy(to_copy)

    @staticmethod
    def add_button_menu_entry(
        path: str,
        glyph: str = None,
        name_fn=None,
        show_fn: Callable = None,
        enabled_fn: Callable = None,
        onclick_fn: Callable = None,
        add_to_context_menu: bool = True,
    ):
        """Adds a new button menu entry.

        Args:
            path (str): The path where the menu entry will be added.
            glyph (str, optional): The icon glyph for the menu entry.
            name_fn (Callable, optional): Function to generate the name of the menu entry.
            show_fn (Callable, optional): Function to determine if the menu entry should be shown.
            enabled_fn (Callable, optional): Function to determine if the menu entry should be enabled.
            onclick_fn (Callable, optional): Function to be executed when the menu entry is clicked.
            add_to_context_menu (bool, optional): Indicates if the entry should be added to the context menu."""
        # pylint: disable=protected-access

        item = None
        if g_singleton:
            item = ButtonMenuEntry(path, glyph, name_fn, show_fn, enabled_fn, onclick_fn, add_to_context_menu)
            g_singleton._button_menu_items.append(item)
        else:  # pragma: no cover
            carb.log_error("PrimPathWidget not initialized")
        return item

    @staticmethod
    def remove_button_menu_entry(item: ButtonMenuEntry):
        """Removes a button menu entry.

        Args:
            item (:obj:`ButtonMenuEntry`): The menu entry to be removed."""
        # pylint: disable=protected-access

        if g_singleton:
            g_singleton._button_menu_items.remove(item)
            item.clean()
        else:  # pragma: no cover
            carb.log_error("PrimPathWidget not initialized")

    @staticmethod
    def get_button_menu_entries():
        """Retrieves all button menu entries.

        Returns:
            list: A list of button menu entries."""
        # pylint: disable=protected-access

        if g_singleton:
            return g_singleton._button_menu_items

        carb.log_error("PrimPathWidget not initialized")  # pragma: no cover
        return None

    @staticmethod
    def add_path_item(draw_fn: Callable):
        """Adds a new path item.

        Args:
            draw_fn (Callable): The function used to draw the path item."""
        # pylint: disable=protected-access

        if g_singleton:
            g_singleton._path_draw_items.append(draw_fn)
        else:  # pragma: no cover
            carb.log_error("PrimPathWidget not initialized")

    @staticmethod
    def remove_path_item(draw_fn: Callable):
        """Removes a path item.

        Args:
            draw_fn (Callable): The function used to draw the path item that will be removed."""
        # pylint: disable=protected-access

        if g_singleton:
            g_singleton._path_draw_items.remove(draw_fn)
        else:  # pragma: no cover
            carb.log_error("PrimPathWidget not initialized")

    @staticmethod
    def get_path_items():
        """Retrieves all path items.

        Returns:
            list: A list of path items."""
        # pylint: disable=protected-access

        if g_singleton:
            return g_singleton._path_draw_items

        carb.log_error("PrimPathWidget not initialized")  # pragma: no cover
        return None

    @staticmethod
    def rebuild():
        """Requests a rebuild of the widget."""
        if g_singleton:
            g_singleton.request_rebuild()
        else:  # pragma: no cover
            carb.log_error("PrimPathWidget not initialized")

    @staticmethod
    def set_path_item_padding(padding: float):
        """Sets the padding for path items.

        Args:
            padding (float): The padding value to be set."""
        # pylint: disable=protected-access

        if g_singleton:
            g_singleton._path_item_padding = padding
        else:  # pragma: no cover
            carb.log_error("PrimPathWidget not initialized")

    @staticmethod
    def get_path_item_padding(padding=None):
        """Gets the padding for path items.

        Args:
            padding (any): Not used."""
        # pylint: disable=protected-access
        if g_singleton:
            return g_singleton._path_item_padding

        carb.log_error("PrimPathWidget not initialized")  # pragma: no cover
        return 0.0

    @Trace.TraceFunction
    def _on_usd_changed(self, notice, stage):
        for path in notice.GetResyncedPaths():
            if path in self._payload:
                self.request_rebuild()
                return

            # layer was deleted
            if path == Sdf.Path.absoluteRootPath:
                payload = self._payload.cleanup_payload()
                # where prims removed from payload as they were part of the layer that was deleted?
                if payload != self._payload:
                    import omni.kit.window.property as p

                    p.get_window().notify("prim", payload)
                else:
                    self.request_rebuild()
                return
