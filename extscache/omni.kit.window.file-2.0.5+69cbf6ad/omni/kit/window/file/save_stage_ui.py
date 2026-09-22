# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
""" Dialog class for saving stage. """
__all__ = ["StageSaveDialog"]
import asyncio
import weakref
import urllib
from typing import Callable, Optional, List
import carb.settings
import omni.client
import omni.ui

try:
    from omni.kit.widget.versioning import CheckpointHelper
    have_versioning = True
except ModuleNotFoundError:
    have_versioning = False


class _CheckBoxStatus:
    def __init__(self, checkbox, layer_identifier, layer_is_writable):
        self.checkbox = checkbox
        self.layer_identifier = layer_identifier
        self.layer_is_writable = layer_is_writable
        self.is_checking = False


class StageSaveDialog:
    """
    Dialog class for saving stage.

    Keyword Args:
        on_save_fn (Callable): function to call when clicking 'Save Selected' button.
        on_dont_save_fn (Callable): function to call when clicking 'Don't Save' button.
        on_cancel_fn (Callable): function to call when clicking cancel button.
        enable_dont_save (bool): Disable 'Don't Save' button.
    """
    _WINDOW_WIDTH = 580
    _MAX_VISIBLE_LAYER_COUNT = 10

    def __init__(self,
            on_save_fn: Optional[Callable[[], None]]=None,
            on_dont_save_fn: Optional[Callable[[], None]]=None,
            on_cancel_fn: Optional[Callable[[], None]]=None,
            enable_dont_save=False
        ):
        self._usd_context = omni.usd.get_context()
        self._save_fn = on_save_fn
        self._dont_save_fn = on_dont_save_fn
        self._cancel_fn = on_cancel_fn
        self._checkboxes_status = []
        self._select_all_checkbox_is_checking = False
        self._selected_layers = []
        self._checkpoint_marks = {}

        flags = (
            omni.ui.WINDOW_FLAGS_NO_COLLAPSE
            | omni.ui.WINDOW_FLAGS_NO_SCROLLBAR
            | omni.ui.WINDOW_FLAGS_MODAL
        )
        self._window = omni.ui.Window(
            "Select Files to Save##file.py",
            visible=False,
            width=0,
            height=0,
            flags=flags,
            auto_resize=True,
            padding_x=10,
            dockPreference=omni.ui.DockPreference.DISABLED,
        )

        with self._window.frame:
            with omni.ui.VStack(height=0, width=StageSaveDialog._WINDOW_WIDTH):
                self._layers_scroll_frame = omni.ui.ScrollingFrame(height=160)
                omni.ui.Spacer(width=0, height=10)
                self._checkpoint_comment_frame = omni.ui.Frame()
                with self._checkpoint_comment_frame:
                    with omni.ui.VStack(height=0, spacing=5):
                        omni.ui.Label("*) File(s) that will be Checkpointed with a comment.")
                        with omni.ui.ZStack():
                            self._description_field = omni.ui.StringField(multiline=True, height=60)
                            self._description_field_hint_label = omni.ui.Label(
                                " Description", alignment=omni.ui.Alignment.LEFT_TOP, style={"color": 0xFF3F3F3F}
                            )
                            self._description_begin_edit_sub = self._description_field.model.subscribe_begin_edit_fn(
                                self._on_description_begin_edit
                            )
                            self._description_end_edit_sub = self._description_field.model.subscribe_end_edit_fn(
                                self._on_description_end_edit
                            )
                self._checkpoint_comment_spacer = omni.ui.Spacer(width=0, height=10)
                with omni.ui.HStack(height=0):
                    omni.ui.Spacer(height=0)
                    self._save_selected_button = omni.ui.Button("Save Selected", width=0, height=0)
                    self._save_selected_button.set_clicked_fn(self._on_save_fn)
                    omni.ui.Spacer(width=5, height=0)
                    if enable_dont_save:
                        self._dont_save_button = omni.ui.Button("Don't Save", width=0, height=0)
                        self._dont_save_button.set_clicked_fn(self._on_dont_save_fn)
                        omni.ui.Spacer(width=5, height=0)
                    self._cancel_button = omni.ui.Button("Cancel", width=0, height=0)
                    self._cancel_button.set_clicked_fn(self._on_cancel_fn)
                    omni.ui.Spacer(height=0)
                omni.ui.Spacer(height=5)

    def destroy(self):
        """ Destructor. """
        self._usd_context = None
        self._save_fn = None
        self._dont_save_fn = None
        self._cancel_fn = None
        self._checkboxes_status = None
        self._selected_layers = None
        self._checkpoint_marks = None
        if self._window:
            del self._window
        self._window = None

    def __del__(self):
        self.destroy()

    def _on_save_fn(self):
        if self._save_fn:
            self._save_fn(
                self._selected_layers,
                comment=self._description_field.model.get_value_as_string()
                if self._checkpoint_comment_frame.visible
                else "",
            )
        self._window.visible = False
        self._selected_layers = []

    def _on_dont_save_fn(self):
        if self._dont_save_fn:
            self._dont_save_fn(self._description_field.model.get_value_as_string())
        self._window.visible = False
        self._selected_layers = []

    def _on_cancel_fn(self):
        if self._cancel_fn:
            self._cancel_fn(self._description_field.model.get_value_as_string())
        self._window.visible = False
        self._selected_layers = []

    def _on_select_all_fn(self, model):
        if self._select_all_checkbox_is_checking:
            return

        self._select_all_checkbox_is_checking = True
        if model.get_value_as_bool():
            for checkbox_status in self._checkboxes_status:
                checkbox_status.checkbox.model.set_value(True)
        else:
            for checkbox_status in self._checkboxes_status:
                checkbox_status.checkbox.model.set_value(False)
        self._select_all_checkbox_is_checking = False

    def _check_and_select_all(self, select_all_check_box):
        select_all = True
        for checkbox_status in self._checkboxes_status:
            if checkbox_status.layer_is_writable and not checkbox_status.checkbox.model.get_value_as_bool():
                select_all = False
                break

        if select_all:
            self._select_all_checkbox_is_checking = True
            select_all_check_box.model.set_value(True)
            self._select_all_checkbox_is_checking = False

    def _on_checkbox_fn(self, model, check_box_index, select_all_check_box):
        check_box_status = self._checkboxes_status[check_box_index]
        if check_box_status.is_checking:
            return

        check_box_status.is_checking = True
        if not check_box_status.layer_is_writable:
            model.set_value(False)
        elif model.get_value_as_bool():
            self._selected_layers.append(check_box_status.layer_identifier)
            self._check_and_select_all(select_all_check_box)
        else:
            self._selected_layers.remove(check_box_status.layer_identifier)
            self._select_all_checkbox_is_checking = True
            select_all_check_box.model.set_value(False)
            self._select_all_checkbox_is_checking = False
        check_box_status.is_checking = False

    def show(self, layer_identifiers: List[str]=[]):
        """
        Show the dialog.
        Keyword Args:
            layer_identifiers(List[str]): list of layer identifier URLs.
        """
        self._layers_scroll_frame.clear()
        self._checkpoint_marks.clear()
        self._checkpoint_comment_frame.visible = False
        self._checkpoint_comment_spacer.visible = False

        settings = carb.settings.get_settings()
        enable_versioning = have_versioning and settings.get_as_bool("exts/omni.kit.window.file/enable_versioning") or False

        # make a copy
        self._selected_layers.extend(layer_identifiers)
        self._checkboxes_status = []

        #build layers_scroll_frame
        self._first_item_stack = None
        with self._layers_scroll_frame:
            with omni.ui.VStack(height=0):
                omni.ui.Spacer(width=0, height=10)
                with omni.ui.HStack(height=0):
                    omni.ui.Spacer(width=20, height=0)
                    self._select_all_checkbox = omni.ui.CheckBox(width=20, style={"font_size": 16})
                    self._select_all_checkbox.model.set_value(True)
                    omni.ui.Label("File Name", alignment=omni.ui.Alignment.LEFT)
                    omni.ui.Spacer(width=20, height=0)
                omni.ui.Spacer(width=0, height=10)
                with omni.ui.HStack(height=0):
                    omni.ui.Spacer(width=20, height=0)
                    omni.ui.Separator(height=0, style={"color": 0xFF808080})
                    omni.ui.Spacer(width=20, height=0)
                omni.ui.Spacer(width=0, height=5)

                for i in range(len(layer_identifiers)):
                    layer_identifier = layer_identifiers[i]
                    # TODO Move version related code
                    if enable_versioning:
                        # Check if the server support checkpoint
                        self._check_checkpoint_enabled(layer_identifier)
                    style = {}
                    layer_is_writable = omni.usd.is_layer_writable(layer_identifier)
                    layer_is_locked = omni.usd.is_layer_locked(self._usd_context, layer_identifier)
                    if not layer_is_writable or layer_is_locked:
                        self._selected_layers.remove(layer_identifier)
                        style = {"background_color": 0xFF808080, "color": 0xFF808080}
                    label_text = urllib.parse.unquote(layer_identifier).replace("\\", "/")
                    if not layer_is_writable or layer_is_locked:
                        label_text += " (Read-Only)"
                    omni.ui.Spacer(width=0, height=5)
                    stack = omni.ui.HStack(height=0, style=style)
                    if self._first_item_stack is None:
                        self._first_item_stack = stack
                    with stack:
                        omni.ui.Spacer(width=20, height=0)
                        checkbox = omni.ui.CheckBox(width=20, style={"font_size": 16})
                        checkbox.model.set_value(True)
                        omni.ui.Label(label_text, word_wrap=False, elided_text=True, alignment=omni.ui.Alignment.LEFT)
                        check_point_label = omni.ui.Label("*", width=3, alignment=omni.ui.Alignment.LEFT, visible=False)
                        omni.ui.Spacer(width=20, height=0)
                        self._checkpoint_marks[layer_identifier] = check_point_label
                        checkbox.model.add_value_changed_fn(
                            lambda a, b=i, c=self._select_all_checkbox: self._on_checkbox_fn(a, b, c)
                        )
                        self._checkboxes_status.append(_CheckBoxStatus(checkbox, layer_identifier, layer_is_writable))

            self._select_all_checkbox.model.add_value_changed_fn(lambda a: self._on_select_all_fn(a))
        self._window.visible = True

        async def __delay_adjust_window_size(weak_self):
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()
            __self = weak_self()
            if not __self:
                return

            y0 = __self._layers_scroll_frame.screen_position_y
            y1 = __self._first_item_stack.screen_position_y
            fixed_height = y1 - y0 + 5
            item_height = __self._first_item_stack.computed_content_height + 5
            count = min(StageSaveDialog._MAX_VISIBLE_LAYER_COUNT, len(__self._checkpoint_marks))

            scroll_frame_new_height = fixed_height + count * item_height
            __self._layers_scroll_frame.height = omni.ui.Pixel(scroll_frame_new_height)

        if len(layer_identifiers) > 0:
            asyncio.ensure_future(__delay_adjust_window_size(weakref.ref(self)))

    def is_visible(self):
        """
        Return:
            Return True if dialog is visible.
        """
        return self._window.visible

    def _on_description_begin_edit(self, model):
        self._description_field_hint_label.visible = False

    def _on_description_end_edit(self, model):
        if len(model.get_value_as_string()) == 0:
            self._description_field_hint_label.visible = True

    def _check_checkpoint_enabled(self, url):
        async def check_server_support(weak_self, url):
            _self = weak_self()
            if not _self:
                return

            if await CheckpointHelper.is_checkpoint_enabled_async(url):
                _self._checkpoint_comment_frame.visible = True
                _self._checkpoint_comment_spacer.visible = True
                label = _self._checkpoint_marks.get(url, None)
                if label:
                    label.visible = True

        asyncio.ensure_future(check_server_support(weakref.ref(self), url))
