# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from omni import ui
from carb import log_warn
from typing import Callable, List
from omni.kit.search_core import SearchEngineRegistry
from .delegate import SearchDelegate
from .model import SearchResultsModel
from .style import get_style, ICON_PATH


class SearchWordButton:
    """
    Represents a search word widget, combined with a label to show the word and a close button to remove it.
    Args:
        word (str): String of word.
    Keyword args:
        on_close_fn (callable): Function called when close button clicked. Function signure:
            void on_close_fn(widget: SearchWordButton)
    """

    def __init__(self, word: str, on_close_fn: callable = None):
        self._container = ui.ZStack(width=0)
        with self._container:
            with ui.VStack():
                ui.Spacer(height=5)
                ui.Rectangle(style_type_name_override="SearchField.Word")
                ui.Spacer(height=5)
            with ui.HStack():
                ui.Spacer(width=3)
                ui.Label(word, width=0, style_type_name_override="SearchField.Word.Label")
                ui.Spacer(width=3)
                ui.Button(
                    image_width=8,
                    style_type_name_override="SearchField.Word.Button",
                    clicked_fn=lambda: on_close_fn(self) if on_close_fn is not None else None,
                    identifier="search_word_button",
                )

    @property
    def visible(self) -> None:
        """Widget visibility"""
        return self._container.visible

    @visible.setter
    def visible(self, value: bool) -> None:
        self._container.visible = value


class SearchField(SearchDelegate):
    """A search field to input search words

    Args:
        callback (callable): Function called after search is done. Function signature: void callback(model: SearchResultsModel)

    Keyword Args:
        width (Optional[ui.Length]): Widget width. Default None means auto.
        height (Optional[ui.Length]): Widget height. Default ui.Pixel(26). Use None for auto.
        subscribe_edit_changed (bool): True to retrieve on_search_fn called when input changes. Default False only retrieve on_search_fn called when input ends.
        show_tokens (bool): Default True to show tokens if end editing. Do nothing if False.

    Properties:
        visible (bool): Widget visibility.
        enabled (bool): Enable/disable widget.
    """

    SEARCH_IMAGE_SIZE = 16
    CLOSE_IMAGE_SIZE = 12

    def __init__(self, callback: Callable, **kwargs):
        """Initializes the search field."""
        super().__init__(**kwargs)
        self._callback = callback

        self._container_args = {"style": get_style()}
        if kwargs.get("width") is not None:
            self._container_args["width"] = kwargs.get("width")
        self._container_args["height"] = kwargs.get("height", ui.Pixel(26))
        self._subscribe_edit_changed = kwargs.get("subscribe_edit_changed", False)
        self._show_tokens = kwargs.get("show_tokens", True)
        self._search_field: ui.StringField = None
        self._search_engine = None
        self._search_engine_menu = None
        self._search_words: List[str] = []
        self._in_searching = False
        self._search_label = None

        # OM-76011:subscribe to engine changed
        self.__search_engine_changed_sub = SearchEngineRegistry().subscribe_engines_changed(
            self._on_search_engines_changed
        )

    @property
    def visible(self):
        """Gets widget visibility.

        Returns:
            bool: The current visibility state of the widget.
        """
        return self._container.visible

    @visible.setter
    def visible(self, value):
        """Sets widget visibility.

        Args:
            value (bool): New visibility state.
        """
        self._container.visible = value

    @property
    def enabled(self):
        """Gets widget enabled state.

        Returns:
            bool: The current enabled state of the widget.
        """
        return self._container.enabled

    @enabled.setter
    def enabled(self, value):
        """Sets widget enabled state.

        Args:
            value (bool): New enabled state.
        """
        self._container.enabled = value
        if value:
            self._search_label.text = "Search"
        else:
            self._search_label.text = "Search disabled. Please install a search extension."

    @property
    def search_dir(self):
        """Gets the current search directory.

        Returns:
            str: The current search directory.
        """
        return self._search_dir

    @search_dir.setter
    def search_dir(self, search_dir: str):
        """Sets search directory value.

        Args:
            search_dir (str): New search directory.
        """
        dir_changed = search_dir != self._search_dir
        self._search_dir = search_dir
        if self._in_searching and dir_changed:
            self.search(self._search_words)

    def build_ui(self):
        """Builds the UI components for the search field."""
        self._container = ui.ZStack(**self._container_args)
        with self._container:
            # background
            self._background = ui.Rectangle(style_type_name_override="SearchField.Frame")
            with ui.HStack():
                with ui.VStack(width=0):
                    # Search "magnifying glass" button
                    search_button = ui.Button(
                        image_url=f"{ICON_PATH}/search.svg",
                        image_width=SearchField.SEARCH_IMAGE_SIZE,
                        image_height=SearchField.SEARCH_IMAGE_SIZE,
                        style_type_name_override="SearchField.Button",
                        identifier="show_engine_menu",
                    )
                    search_button.set_clicked_fn(
                        lambda b=search_button: self._show_engine_menu(
                            b.screen_position_x, b.screen_position_y + b.computed_height
                        )
                    )
                with ui.HStack():
                    with ui.ZStack():
                        with ui.HStack():
                            # Individual word widgets
                            if self._show_tokens:
                                self._words_container = ui.HStack()
                                self._build_search_words()
                            # String field to accept user input, here ui.Spacer for border of SearchField.Frame
                            with ui.VStack():
                                ui.Spacer()
                                with ui.HStack(height=0):
                                    self._search_field = ui.StringField(
                                        ui.SimpleStringModel(),
                                        mouse_double_clicked_fn=lambda x, y, btn, m: self._convert_words_to_string(),
                                        style_type_name_override="SearchField",
                                    )
                                ui.Spacer()

                        self._hint_container = ui.HStack(spacing=4)
                        with self._hint_container:
                            # Hint label
                            self._search_label = ui.Label(
                                "Search", width=275, style_type_name_override="SearchField.Hint"
                            )

                    # Close icon
                    with ui.VStack(width=20):
                        ui.Spacer(height=2)
                        self._clear_button = ui.Button(
                            image_width=SearchField.CLOSE_IMAGE_SIZE,
                            style_type_name_override="SearchField.Clear",
                            clicked_fn=self._on_clear_clicked,
                        )
                        ui.Spacer(height=2)
                    ui.Spacer(width=2)
                    self._clear_button.visible = False

        self._sub_begin_edit = self._search_field.model.subscribe_begin_edit_fn(self._on_begin_edit)
        self._sub_end_edit = self._search_field.model.subscribe_end_edit_fn(self._on_end_edit)
        if self._subscribe_edit_changed:
            self._sub_text_edit = self._search_field.model.subscribe_value_changed_fn(self._on_text_edit)
        else:
            self._sub_text_edit = None

        # check on init for if we have available search engines
        self._on_search_engines_changed()

    def destroy(self):
        """Destroys and cleans up search field resources."""
        self._callback = None
        self._search_field = None
        self._sub_begin_edit = None
        self._sub_end_edit = None
        self._sub_text_edit = None
        self._background = None
        self._hint_container = None
        self._clear_button = None
        self._search_label = None
        self._container = None
        self.__search_engine_changed_sub = None

    def _show_engine_menu(self, x, y):
        self._search_engine_menu = ui.Menu("Engines")
        search_names = SearchEngineRegistry().get_available_search_names(self._search_dir)
        if not search_names:
            return

        # TODO: We need to have predefined default search
        if self._search_engine is None or self._search_engine not in search_names:
            self._search_engine = search_names[0]

        def set_current_engine(engine_name):
            self._search_engine = engine_name

        with self._search_engine_menu:
            for name in search_names:
                ui.MenuItem(
                    name,
                    checkable=True,
                    checked=self._search_engine == name,
                    triggered_fn=lambda n=name: set_current_engine(n),
                )
        self._search_engine_menu.show_at(x, y)

    def _get_search_words(self) -> List[str]:
        # Split the input string to words and filter invalid
        search_string = self._search_field.model.get_value_as_string()
        search_words = [word for word in search_string.split(" ") if word]
        if len(search_words) == 0:
            return None
        elif len(search_words) == 1 and search_words[0] == "":
            # If empty input, regard as clear
            return None
        else:
            return search_words

    def _on_begin_edit(self, model):
        self._set_in_searching(True)

    def _on_end_edit(self, model: ui.AbstractValueModel) -> None:
        search_words = self._get_search_words()
        if search_words is None:
            # Filter empty(hidden) word
            filter_words = [word for word in self._search_words if word]
            if len(filter_words) == 0:
                self._set_in_searching(False)
        else:
            if self._show_tokens:
                self._search_words.extend(search_words)
                self._build_search_words()
                self._search_field.model.set_value("")
            else:
                self._search_words = search_words
        self.search(self._search_words)

    def _on_text_edit(self, model: ui.AbstractValueModel) -> None:
        new_search_words = self._get_search_words()
        if new_search_words is not None:
            # Add current input to search words
            search_words = []
            search_words.extend(self._search_words)
            search_words.extend(new_search_words)
            self._search_words = search_words
        self.search(self._search_words)

    def _convert_words_to_string(self) -> None:
        if self._show_tokens:
            # convert existing search words back to string
            filter_words = [word for word in self._search_words if word]
            seperator = " "
            self._search_words = []
            self._build_search_words()

            original_string = seperator.join(filter_words)
            # Append current input
            input_string = self._search_field.model.get_value_as_string()
            if input_string:
                original_string = original_string + seperator + input_string

            self._search_field.model.set_value(original_string)

    def _on_clear_clicked(self) -> None:
        # Update UI
        self._set_in_searching(False)
        self._search_field.model.set_value("")
        self._search_words.clear()
        self._build_search_words()

        # Notification
        self.search(None)

    def _set_in_searching(self, in_searching: bool) -> None:
        self._in_searching = in_searching
        # Background outline
        self._background.selected = in_searching
        # Show/Hide hint frame (search icon and hint lable)
        self._hint_container.visible = not in_searching
        # Show/Hide close image
        self._clear_button.visible = in_searching

    def _build_search_words(self):
        if self._show_tokens:
            self._words_container.clear()
        if len(self._search_words) == 0:
            return

        with self._words_container:
            ui.Spacer(width=4)
            for index, word in enumerate(self._search_words):
                if word:
                    SearchWordButton(word, on_close_fn=lambda widget, idx=index: self._hide_search_word(idx, widget))

    def _hide_search_word(self, index: int, widget: SearchWordButton) -> None:
        # Here cannot remove the widget since this function is called by the widget
        # So just set invisible and change to empty word
        # It will be removed later if clear or edit end.
        widget.visible = False
        if index >= 0 and index < len(self._search_words):
            self._search_words[index] = ""
            self.search(self._search_words)

    def search(self, search_words: List[str]):
        """Search using selected search engine.

        Args:
            search_words (List[str]): List of search terms.
        """
        # TODO: We need to have predefined default search
        if self._search_engine is None:
            search_names = SearchEngineRegistry().get_search_names()
            self._search_engine = search_names[0] if search_names else None

        if self._search_engine:
            SearchModel = SearchEngineRegistry().get_search_model(self._search_engine)
        else:
            log_warn("No search engines registered! Please import a search extension.")
            return

        if not SearchModel:
            log_warn(f"Search engine '{self._search_engine}' not found.")
            return

        search_words = [word for word in search_words or [] if word]  # Filter empty(hidden) word
        if len(search_words) > 0:
            search_results = SearchModel(search_text=" ".join(search_words), current_dir=self._search_dir)
            model = SearchResultsModel(search_results)
        else:
            model = None

        if self._callback:
            self._callback(model)

    def _on_search_engines_changed(self):
        search_names = SearchEngineRegistry().get_search_names()
        self.enabled = bool(search_names)
