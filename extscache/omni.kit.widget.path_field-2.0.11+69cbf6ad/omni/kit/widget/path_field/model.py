# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import asyncio
import omni.kit.app
import omni.ui as ui

from typing import List
from .style import UI_STYLES
from carb.input import KeyboardInput as Key
from carb.input import KEYBOARD_MODIFIER_FLAG_CONTROL
from functools import partial
import omni.appwindow


class DelayedFocus:
    """A helper to run focus_keyboard the next frame"""

    def __init__(self, field: ui.StringField):
        self.__task = None
        self.__field = field

    def destroy(self):
        if self.__task and not self.__task.done():
            self.__task.cancel()

        self.__task = None
        self.__field = None

    def focus_keyboard(self):
        """Execute frame.focus_keyboard in the next frame"""
        # Update in the next frame.
        if self.__task is None or self.__task.done():
            self.__task = asyncio.ensure_future(self.__delayed_do())

    async def __delayed_do(self):
        # Wait one frame
        await omni.kit.app.get_app().next_update_async()
        self.__field.focus_keyboard()


class PathFieldModel(ui.AbstractValueModel):
    def __init__(self, parent: ui.Widget, theme: str, **kwargs):
        super().__init__()
        self._parent = parent
        self._window = None
        self._field = None
        self._tooltips_frame = None
        self._tooltips = None
        self._tooltip_items = []
        self._num_tooltips = 0
        self._path = None  # Always ends with separator character!
        self._branches = []
        self._focus = None

        self._style = UI_STYLES[theme]
        self._apply_path_handler = kwargs.get("apply_path_handler", None)
        self._apply_path_on_branch_changed = False
        self._current_path_provider = kwargs.get("current_path_provider", None)
        self._branching_options_provider = kwargs.get("branching_options_provider", None)  # OBSOLETE
        self._branching_options_handler = kwargs.get("branching_options_handler", None)
        self._tooltips_max_visible = kwargs.get("tooltips_max_visible", 10)
        self._separator = kwargs.get("separator", "/")
        self._modal = kwargs.get("modal", False)
        self._win_resize_event_sub = None
        self._is_paste = False
        self._delay_update_tooltip_to_enter = False

    def set_value(self, value: str):
        print("Warning: Method 'set_value' is provided for compatibility only and should not be used.")

    def get_value_as_string(self) -> str:
        # Return empty string to parent widget
        return ""

    def set_path(self, path: str):
        self._path = path

    def set_branches(self, branches: [str]):
        self._branches = branches or []

    def begin_edit(self):
        if not (self._window and self._window.visible):
            self._build_ui()

        # Reset path in case we inadvertently deleted it
        if self._current_path_provider:
            input_str = self._current_path_provider()
        else:
            input_str = ""

        self._field.model.set_value(input_str)

    def _build_ui(self):
        # Create and show the window with field and list of tips
        if self._modal:
            flags = ui.WINDOW_FLAGS_MODAL
        else:
            flags = ui.WINDOW_FLAGS_POPUP
        flags = (
            flags
            | ui.WINDOW_FLAGS_NO_TITLE_BAR
            | ui.WINDOW_FLAGS_NO_BACKGROUND
            | ui.WINDOW_FLAGS_NO_MOVE
        )
        window_args = {
            "flags": flags,
            "auto_resize": True,
            "padding_x": 0,
            "padding_y": 0,
            "spacing": 0,
        }
        window_height = ui.Workspace.get_main_window_height()
        window_width = ui.Workspace.get_main_window_width()
        if self._modal:
            window_args["width"] = window_width
            window_args["height"] = window_height
        self._window = ui.Window("0", **window_args)
        self._window.frame.set_style(self._style)

        if self._win_resize_event_sub is None:
            event_stream = omni.appwindow.get_default_app_window().get_window_resize_event_stream()
            if event_stream:
                self._win_resize_event_sub = event_stream.create_subscription_to_pop(
                    lambda *_: self._hide_window(), name="path_field popup window")

        width = self._parent.computed_content_width
        height = 20
        if self._modal:
            # Modal window, simulate a popup window
            # - background transparent
            # - mouse press outside list will hide window
            pos_x = self._parent.screen_position_x - 1 if self._parent else 0
            pos_y = self._parent.screen_position_y + 1 if self._parent else 0
            with self._window.frame:
                with ui.HStack():
                    ui.Spacer(width=pos_x, mouse_pressed_fn=lambda x, y, b, a: self._hide_window())
                    with ui.VStack():
                        ui.Spacer(height=pos_y, mouse_pressed_fn=lambda x, y, b, a: self._hide_window())
                        self.__build_input(width, height)
                        ui.Spacer(height=window_height-pos_y-height, mouse_pressed_fn=lambda x, y, b, a: self._hide_window())
                    ui.Spacer(width=window_width-pos_x-width, mouse_pressed_fn=lambda x, y, b, a: self._hide_window())
        else:
            with self._window.frame:
                self.__build_input(width, height)
                self._place_window()

        # Process pre-defined set of key presses
        self._window.set_key_pressed_fn(self._on_key_pressed)

    def _on_main_window_resized(self, *_):
        if self._window and self._window.visible:
            self._hide_window()

    def __build_input(self, width, height):
        with ui.VStack(height=0):
            with ui.ZStack():
                ui.Rectangle()
                # Use scrolling frame to confine width in case of long inputs
                with ui.ScrollingFrame(
                    width=width,
                    height=height,
                    horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                    vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                    style={"background_color": 0x0},
                ):
                    with ui.HStack(spacing=0):
                        ui.Spacer(width=3)
                        input = ui.SimpleStringModel()
                        input.add_value_changed_fn(lambda m: self._update_tooltips())
                        with ui.Placer(stable_size=True, offset_x=6, offset_y=3):
                            self._field = ui.StringField(input, style_type_name_override="InputField")
                            # TODO: It's a workaround. We need to find out
                            # why we need delayed focus here and why
                            # self._field.focus_keyboard doesn't work.
                            self._focus = DelayedFocus(self._field)
                            self._focus.focus_keyboard()

            # Reserve for tooltips
            self._tooltips_frame = ui.Frame()

    def _on_key_pressed(self, key: int, key_mod: int, key_down: bool):
        """
        Process keys on release.
        """
        key = Key(key)  # Convert to enumerated type

        if key_down:
            if key == Key.V and key_mod & KEYBOARD_MODIFIER_FLAG_CONTROL:
                # We need it to avoid the connection to the server if the
                # string is pasted
                self._is_paste = True
            return

        if self._is_paste:
            self._is_paste = False

        do_apply_path = False

        if key == Key.ESCAPE:
            do_apply_path = True
            self._hide_window()

        elif key in [Key.TAB, Key.RIGHT, Key.ENTER]:
            if self._tooltips and self._tooltip_items:
                index = self._tooltips.model.get_value_as_int()
                self._extend_path_by_selected_branch(index)
            if key == Key.ENTER:
                do_apply_path = True
                self._hide_window()
                if self._delay_update_tooltip_to_enter:
                    self._update_tooltips(force_update=True)
                    self._delay_update_tooltip_to_enter = False
            elif self._apply_path_on_branch_changed:
                do_apply_path = True

        elif key == Key.LEFT:
            self._shrink_path_by_tail_branch()
            if self._apply_path_on_branch_changed:
                do_apply_path = True

        elif key == Key.DOWN:
            if self._tooltips and self._num_tooltips > 0:
                value = self._tooltips.model.get_value_as_int()
                self._tooltips.model.set_value((value + 1) % self._num_tooltips)

        elif key == Key.UP:
            if self._tooltips and self._num_tooltips > 0:
                value = self._tooltips.model.get_value_as_int()
                self._tooltips.model.set_value(value - 1 if value >= 1 else self._num_tooltips - 1)

        else:
            # Skip all other keys
            pass

        if do_apply_path and self._apply_path_handler:
            try:
                self._apply_path_handler(self._field.model.get_value_as_string())
            except Exception:
                pass

    def _update_tooltips(self, force_update=False):
        """Generates list of tips"""
        if not self._field:
            return

        cur_path = self._path or ""
        input_str = self._field.model.get_value_as_string()

        # TODO: This is a hack to avoid the connection to the server if the
        # string is pasted. When we paste full path, we don't want to wait for
        # the server connection.
        if self._is_paste:
            self.set_path(input_str)
            # OM-75838 Don't auto-suggest subdirs when filepath is pasted into toolbar
            self._update_tooltips_menu(None, True, None)
            self._delay_update_tooltip_to_enter = True
            return

        splits = input_str.rsplit(self._separator, 1)
        match_str = splits[1] if len(splits) > 1 else splits[0]
        # Alternatively: match_str = input_str.replace(cur_path, "").lower().rstrip(self._separator)

        if not input_str.startswith(cur_path) or self._separator in input_str[len(cur_path) :] or force_update:
            # Off the current path, need to update both path and branches before continuing.
            if self._branching_options_handler:
                new_path = splits[0]
                new_path += self._separator if new_path else ""
                self.set_path(new_path)
                return self._branching_options_handler(new_path, partial(self._update_tooltips_menu, match_str, True))
        else:
            self._update_tooltips_menu(match_str, False, None)

    def _update_tooltips_menu(self, match_str: str, update_branches: bool, branches: List[str]):
        if update_branches:
            self.set_branches(branches)

        self._num_tooltips = 0
        self._tooltip_items.clear()
        if self._branches:
            with self._tooltips_frame:
                with ui.HStack():
                    with ui.HStack(mouse_pressed_fn=lambda x, y, b, _: self._hide_window()):
                        ui.Spacer(width=6)
                        ui.Label(self._path or "", width=0, style_type_name_override="Tooltips.Spacer")
                    with ui.ZStack():
                        ui.Rectangle(style_type_name_override="Tooltips.Menu")
                        with ui.VStack():
                            self._tooltips = ui.RadioCollection()
                            self._tooltip_items.clear()
                            # Pre-pend an empty branch to pick none
                            for branch in [" "] + self._branches:
                                if self._num_tooltips >= self._tooltips_max_visible:
                                    break
                                if not match_str or (branch and branch.lower().startswith(match_str.lower())):
                                    item = ui.RadioButton(
                                        text=branch,
                                        height=20,
                                        radio_collection=self._tooltips,
                                        style_type_name_override="Tooltips.Item",
                                    )
                                    item.set_clicked_fn(partial(self._extend_path_by_selected_branch, self._num_tooltips))
                                    self._tooltip_items.append(item)
                                    self._num_tooltips += 1
                            self._tooltips.model.set_value(0)
                    with ui.HStack(mouse_pressed_fn=lambda x, y, b, _: self._hide_window()):
                        ui.Spacer(style_type_name_override="Tooltips.Spacer")
        else:
            # OM-75838 When there are no subdirs to auto-suggest, hide tooltips menu.
            self._tooltips_frame.clear()

        if not self._modal:
            self._place_window()

    def _extend_path_by_selected_branch(self, index: int):
        index = min(index, len(self._tooltip_items) - 1)
        if not self._tooltip_items[index].visible:
            return
        branch = self._tooltip_items[index].text.strip()
        if branch:
            # Skip empty strings, incl. one we introduced. Don't allow ending with 2 copies of separator.
            new_path = self._path + (branch + self._separator if not branch.endswith(self._separator) else branch)
        else:
            new_path = self._path
        if self._field:
            self._field.model.set_value(new_path)

    def _shrink_path_by_tail_branch(self):
        input_str = self._field.model.get_value_as_string()
        splits = input_str.rstrip(self._separator).rsplit(self._separator, 1)
        if len(splits) > 1 and splits[1]:
            new_path = splits[0] + self._separator
        else:
            new_path = ""
        if self._field:
            self._field.model.set_value(new_path)

    def _place_window(self):
        if self._parent:
            self._window.position_x = self._parent.screen_position_x - 1
            self._window.position_y = self._parent.screen_position_y + 1

    def _hide_window(self):
        if self._window:
            self._window.visible = False

    def destroy(self):
        self._field = None
        self._tootip_items = None
        self._tooltips = None
        self._tooltips_frame = None
        self._parent = None
        self._window = None
        if self._focus:
            self._focus.destroy()
        self._focus = None
        self._win_resize_event_sub = None
