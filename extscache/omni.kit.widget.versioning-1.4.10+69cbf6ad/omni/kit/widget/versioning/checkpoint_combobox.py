# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import asyncio
from functools import lru_cache
from typing import Optional

import omni.client
import omni.kit.app
import omni.ui as ui
import carb

from .widget import CheckpointWidget
from .style import get_style
from .checkpoints_model import CheckpointItem


@lru_cache()
def _get_down_arrow_icon_path(theme: str) -> str:
    ext_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
    return f"{ext_path}/data/icons/{theme}/down_arrow.svg"


class CheckpointCombobox:
    """A combobox widget for selecting checkpoints in Omni UI.

    This class creates and manages a combobox element that displays the current checkpoint retrieved from an absolute asset path. When the widget is activated, a popup window appears presenting a list of available checkpoints for selection. The chosen checkpoint is reflected through a callback function that is executed upon selection change.

    Args:
        absolute_asset_path (str): The absolute asset URL used to retrieve checkpoint information.
        on_selection_changed_fn (callable): A callback function invoked when the checkpoint selection is changed.
        width (ui.Length): The width of the combobox widget. Defaults to ui.Pixel(100).
        has_pre_spacer (bool): Indicates whether a spacer is inserted before the combobox for layout purposes.
        popup_width (int): The width of the dropdown popup displaying the list of checkpoints.
        visible (bool): Specifies if the combobox is visible upon initialization.
        modal (bool): Determines whether the popup window behaves as a modal window.
    """

    def __init__(
        self,
        absolute_asset_path,
        on_selection_changed_fn,
        width: ui.Length = ui.Pixel(100),
        has_pre_spacer: bool = True,
        popup_width: int = 450,
        visible: bool = True,
        modal: bool = False,
    ):
        """Initializes the CheckpointCombobox instance."""
        self._get_comment_task = None
        self._theme = carb.settings.get_settings().get("/persistent/app/window/uiStyle") or "NvidiaDark"
        self._url = absolute_asset_path
        self._width = width
        self._has_pre_spacer = has_pre_spacer
        self._popup_width = popup_width
        self._visible = visible
        self._modal = modal
        self.__on_selection_changed_fn = on_selection_changed_fn

        self.__container: Optional[ui.ZStack] = None
        self.__checkpoint_field: Optional[ui.StringField] = None

        self._build_checkpoint_combobox()

    def destroy(self):
        """Destroys the CheckpointCombobox and cleans up internal resources."""
        self._checkpoint_list_popup = None
        self._search_field_value_change_sub = None
        self._search_field_begin_edit_sub = None
        self._search_field_end_edit_sub = None
        if self._get_comment_task:
            self._get_comment_task.cancel()
            self._get_comment_task = None

    @property
    def visible(self) -> bool:
        """Gets the visible property of the CheckpointCombobox.

        Returns:
            bool: Current visible status.
        """
        return self._visible

    @visible.setter
    def visible(self, value: bool) -> None:
        """Sets the visible property of the CheckpointCombobox.

        Args:
            value (bool): New visible value to set.
        """
        self._visible = value
        if self.__container:
            self.__container.visible = value

    @property
    def url(self) -> str:
        """Gets the url property of the CheckpointCombobox.

        Returns:
            str: Current url value.
        """
        return self._url

    @url.setter
    def url(self, value: str) -> None:
        """Sets the url property of the CheckpointCombobox.

        Args:
            value (str): New url value to set.
        """
        self._url = value
        if self.__checkpoint_field:
            self.__config_field()

    def _build_checkpoint_combobox(self):
        self.__container = ui.ZStack(visible=self._visible, style=get_style())
        with self.__container:
            with ui.HStack():
                if self._has_pre_spacer:
                    ui.Spacer()
                with ui.ZStack(width=self._width):
                    self.__checkpoint_field = ui.StringField(
                        read_only=True, enabled=False, style_type_name_override="ComboBox"
                    )
                    self.__config_field()

                    arrow_outer_size = 14
                    arrow_size = 10
                    with ui.HStack():
                        ui.Spacer()
                        with ui.VStack(width=arrow_outer_size):
                            ui.Spacer(height=6)
                            ui.Image(_get_down_arrow_icon_path(self._theme), width=arrow_size, height=arrow_size)

                    def on_mouse_pressed(field):
                        popup_width = self._popup_width if self._popup_width > 0 else field.computed_width
                        popup_height = 200
                        self._show_checkpoint_widget(
                            self._url,
                            field.screen_position_x - popup_width + field.computed_content_width,
                            field.screen_position_y,
                            field.computed_content_height,
                            popup_width,
                            popup_height,
                        )

                    self.__checkpoint_field.set_mouse_pressed_fn(
                        lambda x, y, b, m, field=self.__checkpoint_field: on_mouse_pressed(field)
                    )
        return None

    def __config_field(self):
        (client_url, checkpoint) = self.__get_current_checkpoint()
        self.__checkpoint_field.model.set_value(str(checkpoint) if checkpoint else "<head>")
        if checkpoint:

            async def get_comment():
                result, entries = await omni.client.list_checkpoints_async(self._url)
                if result:
                    for entry in entries:
                        if entry.relative_path == client_url.query:
                            self.__checkpoint_field.set_tooltip(entry.comment)
                            break

            self._get_comment_task = asyncio.ensure_future(get_comment())
        else:
            self.__checkpoint_field.set_tooltip("<Not using Checkpoint>")

    def __get_current_checkpoint(self):
        checkpoint = 0
        client_url = omni.client.break_url(self._url)
        if client_url.query:
            _, checkpoint = omni.client.get_branch_and_checkpoint_from_query(client_url.query)
        return (client_url, checkpoint)

    def __on_checkpoint_selection_changed(self, item: CheckpointItem):
        if item:
            self.url = item.get_full_url()
            self._checkpoint_list_popup.visible = False
        if self.__on_selection_changed_fn:
            self.__on_selection_changed_fn(item)

    def _build_list_popup(self, url):
        with ui.VStack():
            with ui.ZStack(height=0):
                search_field = ui.StringField(style_type_name_override="ComboBox.Field")
                search_label = ui.Label(
                    " Search", name="hint", enabled=False, style_type_name_override="ComboBox.Field"
                )
            checkpoint_widget = CheckpointWidget(url, show_none_entry=True)

            self._search_field_value_change_sub = search_field.model.subscribe_value_changed_fn(
                lambda model: checkpoint_widget.set_search(model.get_value_as_string())
            )

            def begin_search(model):
                search_label.visible = False

            self._search_field_begin_edit_sub = search_field.model.subscribe_begin_edit_fn(begin_search)

            def end_search(model):
                if model.get_value_as_string() != "":
                    search_label.visible = True

            self._search_field_end_edit_sub = search_field.model.subscribe_end_edit_fn(end_search)
            checkpoint_widget.add_on_selection_changed_fn(self.__on_checkpoint_selection_changed)

        def on_visibility_changed(visible):
            checkpoint_widget.destroy()

        self._checkpoint_list_popup.set_visibility_changed_fn(on_visibility_changed)

    def _show_checkpoint_widget(self, url, pos_x, pos_y, pos_y_offset, width, height):
        # If there is not enough space to expand the list downward, expand it upward instead
        # TODO multi OS window?
        window_height = ui.Workspace.get_main_window_height()
        window_width = ui.Workspace.get_main_window_width()
        if pos_y + height > window_height:
            pos_y -= height
        else:
            pos_y += pos_y_offset

        if self._modal:
            flags = ui.WINDOW_FLAGS_MODAL | ui.WINDOW_FLAGS_NO_BACKGROUND
        else:
            flags = ui.WINDOW_FLAGS_POPUP
        flags = flags | ui.WINDOW_FLAGS_NO_TITLE_BAR | ui.WINDOW_FLAGS_NO_RESIZE | ui.WINDOW_FLAGS_NO_MOVE
        self._checkpoint_list_popup = ui.Window(
            "Checkpoint Widget Window",
            flags=flags,
            padding_x=1,
            padding_y=1,
            width=window_width if self._modal else width,
            height=window_height if self._modal else height,
        )

        self._checkpoint_list_popup.frame.set_style(get_style())
        if self._modal:
            # Modal window, simulate a popup window
            # - background transparent
            # - mouse press outside list will hide window
            def __hide_list_popup():
                self._checkpoint_list_popup.visible = False

            with self._checkpoint_list_popup.frame:
                with ui.HStack():
                    ui.Spacer(width=pos_x, mouse_pressed_fn=lambda x, y, b, a: __hide_list_popup())
                    with ui.VStack():
                        ui.Spacer(height=pos_y, mouse_pressed_fn=lambda x, y, b, a: __hide_list_popup())
                        self._build_list_popup(url)
                        ui.Spacer(
                            height=window_height - pos_y - height,
                            mouse_pressed_fn=lambda x, y, b, a: __hide_list_popup(),
                        )
                    ui.Spacer(
                        width=window_width - pos_x - width, mouse_pressed_fn=lambda x, y, b, a: __hide_list_popup()
                    )
        else:
            self._checkpoint_list_popup.position_x = pos_x
            self._checkpoint_list_popup.position_y = pos_y

            with self._checkpoint_list_popup.frame:
                self._build_list_popup(url)
