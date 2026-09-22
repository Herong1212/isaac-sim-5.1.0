from functools import partial
from typing import Callable, Dict, List, Optional

import carb.settings
from omni import ui

from .searchword import SearchWordButton
from .style import UI_STYLE
from .suggest_window import SuggestWindow


class SearchField:
    """
    Represents a search field where users can input search words and receive suggestions.
    """

    SEARCH_IMAGE_SIZE = 16
    """Size of search image"""

    CLOSE_IMAGE_SIZE = 12
    """Size of close image"""

    def __init__(
        self,
        width: Optional[ui.Length] = None,
        height: Optional[ui.Length] = ui.Pixel(26),
        on_search_fn: Callable[[Optional[List[str]]], None] = None,
        subscribe_edit_changed: bool = False,
        show_tokens: bool = True,
        style: Dict = None,
        suggestions: Optional[List[str]] = None,
        max_suggestions: int = 10,
        separator=" ",
    ):
        """
        Construct a search field.

        Keyword Args:
            width (Optional[ui.Length]): Widget width. Default None, means auto.
            height (Optional[ui.Length]): Widget height. Default ui.Pixel(26). Use None for auto.
            on_search_fn (Callable[[Optional[List[str]]], None]): Function called to do searching.
            subscribe_edit_changed (bool): True to retrieve on_search_fn called when input changed. Default False only retrieve on_search_fn called when input ended.
            show_tokens (bool): Default True to show tokens if end edit. Do nothing if False.
            style (Dict): Widget additional style. Default None, means using default style.
            suggestions (Optional[List[str]]): Show suggestion list when input search words. Default None means not supported.
            max_suggestions (int): Max number of suggestions to show at same time.
            separator (Optional[str]): Separator to break the search string into multiple words. None means no separate. Defaults to " ".

        Properties:
            visible (bool): Widget visibility.
            enabled (bool): Enable/Disable widget.
            search_words (Optional[List[str]]): Search words.
            suggestions (Optional[List[str]]): Suggestions.
            max_suggestions (int): Maximum number of suggestions.
            text (str): Text in the search field.
        """
        ui_style = UI_STYLE.copy()
        if style is not None:
            ui_style.update(style)
        self._container_args = {"style": ui_style}
        if height is not None:
            self._container_args["height"] = height
        if width is not None:
            self._container_args["width"] = width
        self._on_search_fn = on_search_fn
        self._subscribe_edit_changed = subscribe_edit_changed
        self._show_tokens = show_tokens

        self._search_words: List[str] = []
        self._suggestions: Optional[List[str]] = suggestions
        self._max_suggestions = max_suggestions
        self._separator = separator
        self._suggest_window: Optional[SuggestWindow] = None
        self._search_label = None

        settings = carb.settings.get_settings()
        self._theme = settings.get_as_string("/persistent/app/window/uiStyle") or "NvidiaDark"

        self._build_ui()

    def destroy(self):
        """
        Clean resources.
        """
        self._search_label = None
        self._on_search_fn = None
        self._sub_begin_edit = None
        self._sub_end_edit = None
        self._sub_text_edit = None
        self._background = None
        self._hint_container = None
        self._clear_button = None
        self._container = None
        if self._suggest_window:
            self._suggest_window.visible = False
            self._suggest_window.destroy()
            self._suggest_window = None

    @property
    def visible(self) -> bool:
        """
        Widget visibility
        """
        return self._container.visible

    @visible.setter
    def visible(self, value):
        self._container.visible = value

    @property
    def enabled(self) -> bool:
        """
        Widget enabled/disabled
        """
        return self._container.enabled

    @enabled.setter
    def enabled(self, value):
        self._container.enabled = value

    @property
    def search_words(self) -> Optional[List[str]]:
        """
        Current words appeared in the search field.
        """
        return self._search_words if self._show_tokens else None

    @search_words.setter
    def search_words(self, words: List[str]) -> None:
        if self._show_tokens:
            self._search_words = words
            self._build_search_words()
            self._hint_container.visible = not bool(words)
            self._notify(self._search_words)

    @property
    def suggestions(self) -> Optional[List[str]]:
        """
        Suggestion words to show when input in search field
        """
        return self._suggestions

    @suggestions.setter
    def suggestions(self, words: List[str]) -> None:
        self._suggestions = words
        if self._suggest_window:
            self._suggest_window.suggestions = words

    @property
    def max_suggestions(self) -> int:
        """Max number of suggestion words appeared"""
        return self._max_suggestions

    @max_suggestions.setter
    def max_suggestions(self, count: int) -> None:
        self._max_suggestions = count
        if self._suggest_window:
            self._suggest_window.max_suggestions = count

    def set_filter(self, filter_cls):
        """
        Set filter.

        :meta private:
        """
        self._filter = filter_cls
        self._set_in_searching(True)

    @property
    def text(self) -> str:
        """
        Text currently in search field
        """
        return self._search_field.model.get_value_as_string()

    @text.setter
    def text(self, text: str) -> None:
        self._search_field.model.set_value(text)
        self._hint_container.visible = not bool(text)
        search_words = self._get_search_words()
        self._notify(search_words)

    def clear(self):
        """clear search words"""
        self._on_clear_clicked()

    def _build_ui(self):
        self._container = ui.ZStack(**self._container_args)
        with self._container:
            # background
            self._background = ui.Rectangle(style_type_name_override="SearchField.Frame")

            with ui.HStack():
                with ui.ZStack():
                    with ui.HStack():
                        # Individual word widgets
                        if self._show_tokens:
                            self._words_container = ui.HStack(spacing=5)
                            self._build_search_words()
                        # string field to accept user input, here ui.Spacer for border of SearchField.Frame
                        with ui.VStack():
                            ui.Spacer()
                            with ui.HStack(height=0):
                                ui.Spacer(width=2)
                                self._search_field = ui.StringField(
                                    ui.SimpleStringModel(),
                                    mouse_double_clicked_fn=lambda x, y, btn, m: self._on_double_click(),
                                    style_type_name_override="SearchField",
                                )
                            ui.Spacer()

                    self._hint_container = ui.HStack(spacing=5)
                    with self._hint_container:
                        ui.Spacer(width=4)
                        # Search icon
                        with ui.VStack(width=0):
                            ui.Spacer()
                            ui.Image(
                                width=SearchField.SEARCH_IMAGE_SIZE,
                                height=SearchField.SEARCH_IMAGE_SIZE,
                                style_type_name_override="SearchField.Search",
                            )
                            ui.Spacer()
                        # Hint label
                        self._search_label = ui.Label("Search", style_type_name_override="SearchField.Hint")

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
            self._ignore_text_update = False
        else:
            self._sub_text_edit = None

    def _get_search_words(self) -> List[str]:
        # Split the input string to words and filter invalid
        search_string = self._search_field.model.get_value_as_string()
        if self._separator:
            search_words = [word for word in search_string.split(self._separator) if word]
        else:
            search_words = [search_string] if len(search_string) > 0 else []
        if len(search_words) == 0:
            return None
        elif len(search_words) == 1 and search_words[0] == "":
            # If empty input, regard as clear
            return None
        else:
            return search_words

    def _on_begin_edit(self, model):
        self._set_in_searching(True)
        if self._suggestions is not None:
            self._show_suggest_window()

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
                if self._subscribe_edit_changed:
                    self._ignore_text_update = True
                self._search_field.model.set_value("")
                if self._subscribe_edit_changed:
                    self._ignore_text_update = False
            else:
                self._search_words = search_words
        if not self._subscribe_edit_changed:
            self._notify(self._search_words)

        if self._show_tokens:
            self._words_container.visible = True

    def _on_text_edit(self, model: ui.AbstractValueModel) -> None:
        if self._ignore_text_update:
            return
        new_search_words = self._get_search_words()
        if self._show_tokens:
            if new_search_words is not None:
                # Add current input to search words
                search_words = []
                search_words.extend(self._search_words)
                search_words.extend(new_search_words)
                self._notify(search_words)
            else:
                self._notify(self._search_words)
        else:
            self._notify(new_search_words)

    def _on_double_click(self):
        self._convert_words_to_string()

        # OM-107704: It is strange that although words container cleared but sometimes there still be blank area left
        # Here force to hide words container and show it again when end edit
        if self._show_tokens:
            self._words_container.visible = False

    def _convert_words_to_string(self) -> None:
        if self._show_tokens:
            # convert existing search words back to string
            filter_words = [word for word in self._search_words if word]
            self._search_words = []
            self._build_search_words()

            original_string = self._separator.join(filter_words) if self._separator else "".join(filter_words)
            # Append current input
            input_string = self._search_field.model.get_value_as_string()
            if input_string:
                if self._separator:
                    original_string += self._separator + input_string
                else:
                    original_string += input_string

            self._search_field.model.set_value(original_string)

    def _on_clear_clicked(self) -> None:
        # Update UI
        self._set_in_searching(False)
        self._search_field.model.set_value("")
        self._search_words = []
        self._build_search_words()

        # Notification
        if self._on_search_fn is not None:
            self._on_search_fn(None)

    def _set_in_searching(self, in_searching: bool) -> None:
        # Background outline
        self._background.selected = in_searching
        # Show/Hide hint frame (search icon and hint lable)
        self._hint_container.visible = not in_searching
        # Show/Hide close image
        self._clear_button.visible = in_searching

    def _show_suggest_window(self) -> None:
        # In suggest mode, use input field in suggest window instead
        self._sub_end_edit = None
        if self._suggest_window is None:
            self._suggest_window = SuggestWindow(
                self._search_field,
                self._suggestions,
                max_suggestions=self._max_suggestions,
                on_end_edit_fn=partial(self._on_end_edit, self._search_field.model),
                on_double_clicked_fn=self._on_double_click,
            )

        self._sub_end_edit = None
        self._suggest_window.visible = True

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
            self._notify(self._search_words)

        # OM-70923: Focus keyboard back to search field if all search words cleared
        # Then it losts focus, the field could be in normal state instead of "searching"
        valid_search_words = [word for word in self._search_words if word]
        if not valid_search_words:
            self._search_field.focus_keyboard()

    def _notify(self, search_words) -> bool:
        if self._on_search_fn is not None:
            if search_words is None:
                self._on_search_fn(None)
            else:
                # Filter empty(hidden) word
                filter_words = [word for word in search_words if word]
                if len(filter_words) == 0:
                    self._on_search_fn(None)
                else:
                    self._on_search_fn(filter_words)
