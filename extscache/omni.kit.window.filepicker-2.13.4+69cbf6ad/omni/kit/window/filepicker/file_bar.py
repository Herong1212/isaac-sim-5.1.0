# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ComboBoxMenu", "ComboBox", "FileBar"]
import omni.ui as ui
import omni.kit.app

from typing import List, Tuple, Callable, Union, Optional
from functools import partial
from .style import get_style, ICON_PATH
from omni.kit.async_engine import run_coroutine


class ComboBoxMenu:
    def __init__(self, menu_options: List, **kwargs):
        """
         Initialize the menu.

         Args:
              menu_options(List): List of menu options to be used
        """
        self._window: ui.Window = None
        self._parent: ui.Widget = kwargs.get("parent", None)
        self._width: int = kwargs.get("width", 210)
        self._height: int = kwargs.get("height", 140)
        self._max_items_per_menu = kwargs.get("max_items_per_menu", 8)
        self._selection_changed_fn: Callable = kwargs.get("selection_changed_fn", None)
        self._build_ui(menu_options)

    def _build_ui(self, menu_options: List):
        window_flags = (
            ui.WINDOW_FLAGS_NO_RESIZE
            | ui.WINDOW_FLAGS_POPUP
            | ui.WINDOW_FLAGS_NO_TITLE_BAR
            | ui.WINDOW_FLAGS_NO_BACKGROUND
            | ui.WINDOW_FLAGS_NO_MOVE
            | ui.WINDOW_FLAGS_NO_SCROLLBAR
        )
        self._window = ui.Window("ComboBoxMenu", flags=window_flags, auto_resize=True)
        with self._window.frame:
            with ui.ZStack(style=get_style()):
                ui.Rectangle(style_type_name_override="ComboBox.Menu.Background")
                with ui.HStack():
                    ui.Spacer(width=4)
                    if len(menu_options) <= self._max_items_per_menu:
                        ui.Frame(
                            width=self._width,
                            style_type_name_override="ComboBox.Menu.Frame",
                            build_fn=partial(self._frame_build_fn, menu_options),
                        )
                    else:
                        ui.ScrollingFrame(
                            width=self._width,
                            height=self._height,
                            horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                            vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                            style_type_name_override="ComboBox.Menu.Frame",
                            build_fn=partial(self._frame_build_fn, menu_options),
                        )

    def _frame_build_fn(self, menu_options: List):
        def on_select_menu(menu: int):
            self.hide()
            if self._selection_changed_fn:
                self._selection_changed_fn(menu)

        with ui.ZStack(height=0, style=get_style()):
            with ui.VStack(style_type_name_override="ComboBox.Menu"):
                for index, menu_option in enumerate(menu_options):
                    with ui.ZStack():
                        button = ui.Button(" ", clicked_fn=self.hide, style_type_name_override="ComboBox.Menu.Item")
                        with ui.HStack():
                            if type(menu_option) is tuple:
                                name, label = menu_option
                                ui.Label(name, width=0, style_type_name_override="ComboBox.Menu.Item", name="left")
                                ui.Spacer()
                                ui.Label(label[:40], width=0, style_type_name_override="ComboBox.Menu.Item", name="right")
                            else:
                                name = menu_option
                                ui.Label(name or "none", width=0, style_type_name_override="ComboBox.Menu.Item")
                                ui.Spacer()
                            button.set_clicked_fn(lambda menu=index: on_select_menu(menu))

    def show(self, offset_x: int = 0, offset_y: int =0):
        """
        Show the window. It will be positioned relative to the parent window.

        Keyword Args:
            offset_x(int): Offset in x direction. Default is 0.
            offset_y(int): Offset in y direction. Default is 0
        """
        if self._parent:
            self._window.position_x = self._parent.screen_position_x + offset_x
            self._window.position_y = self._parent.screen_position_y + offset_y
        elif offset_x != 0 or offset_y != 0:
            self._window.position_x = offset_x
            self._window.position_y = offset_y
        self._window.visible = True

    def hide(self):
        """
        Hides the window.
        """
        self._window.visible = False


class ComboBox:
    def __init__(self, options: List, **kwargs):
        """
        Initialize the menu.

        Args:
            options(List): List of options to show in combo box
        """
        import carb.settings
        settings = carb.settings.get_settings()
        self._width = kwargs.get("width", 200)
        self._selection = kwargs.get("selection", 0)
        self._selection_changed_fn: Callable = kwargs.get("selection_changed_fn", None)
        self._menu_options = options
        self._button = None
        self._label = None
        self._build_ui(options)

    def _build_ui(self, menu_options: List):
        if not menu_options:
            return None

        with ui.ZStack(width=self._width):
            self._button = ui.Button(" ", clicked_fn=self.show_menu, style_type_name_override="ComboBox.Button")
            with ui.HStack():
                ui.Spacer(width=8)
                self._label = ui.Label("", style_type_name_override="ComboBox.Button")
                ui.Spacer()
                ui.ImageWithProvider(f"{ICON_PATH}/dropdown.svg", width=20,
                    style_type_name_override="ComboBox.Button.Glyph")

        self._label.text = self.get_selection_as_string(self._selection)

    @property
    def selection(self) -> int:
        """
        Gets the selection of this combobox.

        Returns:
            int: Index of the currently selected menu option
        """
        return self._selection

    def get_selection_as_string(self, selection: int) -> str:
        """
        Returns the string corresponding to the selection.

        Args:
            selection(int): Index of the currently selected menu option

        Returns:
            str: String representation of the selected menu option or none
        """
        s = ""
        if selection < len(self._menu_options):
            menu_option = self._menu_options[selection]
            if type(menu_option) is tuple:
                s = menu_option[0]
            else:
                s = menu_option
            s = "" + (s or "none")
        return s

    def show_menu(self):
        """ Show the menu for the combobox. """
        menu = ComboBoxMenu(self._menu_options, parent=self._button, width=self._width,
            selection_changed_fn=self._on_selection_changed
        )
        menu.show(offset_x=0, offset_y=20)

    def _on_selection_changed(self, option: int):
        self._selection = option
        self._label.text = self.get_selection_as_string(self._selection)
        if self._selection_changed_fn:
            self._selection_changed_fn()


class FileBar:
    def __init__(self, **kwargs):
        """
        Initialize the FileBar.
        """
        self._field = None
        self._field_label = None
        self._hint_text_label = None
        self._sub_field_edit = None
        self._enable_filename_input = kwargs.get("enable_filename_input", True)
        self._focus_filename_input = kwargs.get("focus_filename_input", False)
        self._filename_changed_handler = kwargs.get("filename_changed_handler", None)

        # OBSOLETE item_filter_options. Prefer to use file_postfix_options + file_extension_options instead.
        self._item_filter_options: List[str] = kwargs.get("item_filter_options", None)
        self._item_filter_menu: ui.ComboBox = None
        self._current_filter_option: int = 0

        self._file_postfix_options: List[str] = kwargs.get("file_postfix_options", None)
        self._file_postfix: str = kwargs.get("file_postfix", None)
        self._file_postfix_menu: ComboBox = None
        self._file_extension_options: List[Tuple[str, str]] = kwargs.get("file_extension_options", None)
        self._file_extension: str = kwargs.get("file_extension", None)
        self._file_extension_menu: ComboBox = None
        self._filter_option_changed_handler = kwargs.get("filter_option_changed_handler", None)
        self._current_directory_provider = kwargs.get("current_directory_provider", None)
        self._apply_button_label = kwargs.get("apply_button_label", "Okay")
        self._cancel_button_label = kwargs.get("cancel_button_label", "Cancel")
        self._apply_button: ui.Button = None
        self._cancel_button: ui.Button = None
        self._click_apply_handler = kwargs.get("click_apply_handler", None)
        self._click_cancel_handler = kwargs.get("click_cancel_handler", None)
        self._file_name_model = None

        self._build_ui()

    def destroy(self):
        """ Destroy the widget. """
        self._file_name_model = None
        self._current_directory_provider = None
        self._filter_option_changed_handler = None
        self._file_extension_menu = None
        self._file_postfix_menu = None
        self._filename_changed_handler = None
        self._field_label = None
        self._hint_text_label = None
        self._item_filter_menu = None
        self._field = None
        self._sub_field_edit = None
        self._click_apply_handler = None
        self._click_cancel_handler = None
        self._apply_button = None
        self._cancel_button = None

    @property
    def current_filter_option(self) -> int:
        """
        Get the current filter option.

        Returns:
            int: The current filter option ( - 1 if none )
        """
        return self._current_filter_option

    @property
    def label_name(self) -> str:
        """
        Get the label name.

        Returns:
            str: The field label text.
        """
        if self._field_label:
            return self._field_label.text

        return None

    @label_name.setter
    def label_name(self, name: str):
        """
        Label the field with the name.

        Args:
            name (str): value set to the field.
        """
        if name and self._field_label:
            self._field_label.text = (f"{name}:")

    @property
    def filename(self) -> str:
        """
        Returns the filename to use for the file.

        Returns:
            str: The filename to use for the file.
        """
        if self._enable_filename_input:
            return self._file_name_model.get_value_as_string()
        return self._hint_text_label.text

    @property
    def directory(self) -> str:
        """
        Directory to store files in.

        Returns:
            str: Directory to store files in.
        """
        return self._current_directory_provider() if self._current_directory_provider else "."

    @filename.setter
    def filename(self, filename):
        """  Set the filename to use for this file. """
        if filename and self._file_name_model:
            self._file_name_model.set_value(filename)
            if not self._enable_filename_input:
                self._hint_text_label.text = filename

    @property
    def selected_postfix(self) -> str:
        """
        Return the selected postfix.

        Returns:
            str: Selected postfix.
        """
        postfix = None
        if self._file_postfix_options and self._file_postfix_menu:
            postfix = self._file_postfix_options[self._file_postfix_menu.selection]
        return postfix

    @property
    def postfix_options(self) -> List[str]:
        """
        Gets all the postfix_options.

        Returns:
            List[str]: All postfix options.
        """
        return self._file_postfix_options

    @property
    def selected_extension(self) -> str:
        """
        Return the currently selected file extension.

        Returns:
            str: File extension.
        """
        extension = None
        if self._file_extension_options and self._file_extension_menu:
            extension, _ = self._file_extension_options[self._file_extension_menu.selection]
        return extension

    @property
    def extension_options(self) -> List[Tuple[str, str]]:
        """
        Gets the extension_options.

        Returns:
            List[Tuple[str, str]]: Pair value of file extension and options
        """
        return self._file_extension_options

    def set_postfix(self, postfix: str):
        """
        Set the postfix to be used for the menu.

        Args:
            postfix(str): postfix of the file to be select.
        """
        if not postfix:
            return
        if self._file_postfix_options and self._file_postfix_menu:
            if postfix in self._file_postfix_options:
                index = self._file_postfix_options.index(postfix)
                self._file_postfix_menu._selection = index
                self._file_postfix_menu._on_selection_changed(index)

    def set_extension(self, extension: str):
        """
        Set the extension to be used for the file selection.

        Args:
            extension(str): extension of the file to be select.
        """
        if not extension:
            return
        if self._file_extension_options and self._file_extension_menu:
            extension_names = [name for name, _ in self._file_extension_options]
            if extension in extension_names:
                index = extension_names.index(extension)
                self._file_extension_menu._selection = index
                self._file_extension_menu._on_selection_changed(index)

    def set_click_apply_handler(self, click_apply_handler: Callable[[str, str], None]):
        """
        Sets the function to execute upon clicking apply.

        Args:
            click_apply_handler (Callable): Callback with filename being the name of the file, and dirname being the containing directory path with an ending slash.
                Signature is fn(filename: str, dirname: str) -> None

        """
        self._click_apply_handler = click_apply_handler

    def enable_apply_button(self, enable: bool =True):
        """
        Enable/disable the apply button for FileBar.

        Args:
            enable (bool): enable or disable the apply button.
        """
        self._apply_button.enabled = enable

    def focus_filename_input(self):
        """Utility to help focusing the filename input field."""
        if self._field:
            self._field.focus_keyboard()

    def _build_ui(self):
        with ui.HStack(height=24, spacing=2, style=get_style()):
            if self._enable_filename_input:
                with ui.ZStack():
                    ui.Rectangle(style_type_name_override="FileBar")
                    with ui.HStack():
                        self._field_label = ui.Label(f"File name:  ", width=0, style_type_name_override="FileBar.Label")
                        with ui.Placer(stable_size=True, offset_y=1.5):
                            self._field = ui.StringField(style_type_name_override="Field")
                            self._file_name_model = self._field.model
                            self._sub_field_edit = self._field.model.subscribe_value_changed_fn(self._on_filename_changed)

                if self._file_postfix_options:
                    try:
                        selection = self._file_postfix_options.index(self._file_postfix)
                    except Exception:
                        selection = 0
                    self._file_postfix_menu = ComboBox(
                        self._file_postfix_options, selection=selection, selection_changed_fn=self._on_menu_selection_changed, width=117)

                if self._file_extension_options:
                    selection = 0
                    if self._file_extension:
                        for index, option in enumerate(self._file_extension_options):
                            if self._file_extension == option[0]:
                                selection = index

                    self._file_extension_menu = ComboBox(
                        self._file_extension_options, selection=selection, selection_changed_fn=self._on_menu_selection_changed, width=300)

                if self._item_filter_options:
                    # OBSOLETE item_filter_options.  This code block is left her for backwards compatibility.
                    self._item_filter_menu = self._build_filter_combo_box()
            else:
                # OM-99158: Add hint text display if filename input is disabled
                with ui.ZStack():
                    ui.Rectangle(style_type_name_override="FileBar")
                    with ui.HStack():
                        self._field_label = ui.Label(
                            f"File name:  ", width=0, style_type_name_override="FileBar.Label", enabled=False)
                        self._hint_text_label = ui.Label(
                            "", width=0, style_type_name_override="FileBar.Label", enabled=False)

            self._apply_button = ui.Button(self._apply_button_label, width=117, clicked_fn=lambda: self._on_apply(),
                style_type_name_override="Button")
            self._cancel_button = ui.Button(self._cancel_button_label, width=117, clicked_fn=lambda: self._on_cancel(),
                style_type_name_override="Button")

    def _build_filter_combo_box(self) -> ui.ComboBox:
        # OBSOLETE This function is left here for backwards compatibility.
        args = [self._current_filter_option]
        args.extend(self._item_filter_options or [])
        with ui.ZStack(width=0):
            ui.Rectangle(style_type_name_override="FileBar")
            combo_box = ui.ComboBox(*args, width=300, style_type_name_override="ComboBox")
            combo_box.model.add_item_changed_fn(lambda m, _: self._on_menu_selection_changed(model=m))
        return combo_box

    def _on_filename_changed(self, search_words) -> bool:
        if self._filename_changed_handler is not None:
            self._filename_changed_handler(self.filename)

    def _on_menu_selection_changed(self, model: Optional[ui.AbstractItemModel] = None):
        if self._file_extension_menu:
            postfix_option = 0
            if self._file_postfix_menu:
                postfix_option = self._file_postfix_menu.selection
            extension_option = self._file_extension_menu.selection
            if self._filter_option_changed_handler:
                self._filter_option_changed_handler()
        elif self._item_filter_menu:
            # OBSOLETE This case is left here for backwards compatibility.
            index = model.get_item_value_model(None, 0)
            self._current_filter_option = index.get_value_as_int()
            if self._filter_option_changed_handler:
                self._filter_option_changed_handler()

    def _on_apply(self):
        if self._click_apply_handler:
            self._click_apply_handler(self.filename, self.directory.replace("\\", "/") if self.directory else None)

    def _on_cancel(self):
        if self._click_cancel_handler:
            self._click_cancel_handler(self.filename, self.directory.replace("\\", "/") if self.directory else None)
