"""This module provides the HighlightLabel widget class for creating labels with highlighted text selections."""


import carb
import math
from omni import ui
from typing import Optional, Dict
from .style import UI_STYLE


def split_selection(text, selection, match_case: bool = False):
    """
    Splits the provided text into a list of substrings to facilitate drawing segments of selected text.

    The resulting list alternates between unselected and selected text, starting with an unselected portion. If the entire text is selected, it returns a list starting with an empty string followed by the entire text.

    Args:
        text (str): The text to split based on the selection.
        selection (str): The substring to search for within `text`.
        match_case (bool, optional): If True, the search is case-sensitive; otherwise, it's case-insensitive. Defaults to False.

    Returns:
        list of str: A list containing the split parts of the text with the selection highlighted.

    Examples:
        - split_selection("helloworld", "o") -> ["hell", "o", "w", "o", "rld"]
        - split_selection("helloworld", "helloworld") -> ["", "helloworld"]"""
    if not selection:
        return [text, ""]
    else:
        origin_text = text
        if not match_case:
            selection = selection.lower()
            text = text.lower()
        elif text == selection:
            return ["", text]

    selection_len = len(selection)
    result = []
    while True:
        found = text.find(selection)

        result.append(origin_text if found < 0 else origin_text[:found])

        if found < 0:
            break
        else:
            result.append(origin_text[found : found + selection_len])
            text = text[found + selection_len :]
            origin_text = origin_text[found + selection_len :]

    return result


class HighlightLabel:
    """Represents a label widget that can show highlighted words.

    Args:
        text (str): The text content of the label.
        highlight (Optional[str]): The word within `text` to be highlighted.
        match_case (bool): If `True`, matching is case-sensitive. Defaults to `False`.
        width (ui.Length): The width of the widget. Defaults to `ui.Fraction(1)`.
        height (ui.Length): The height of the widget. Defaults to `ui.Fraction(1)`.
        label_width (int): The width used for ui.Label.
        style (Dict): Custom styling for the widget.

    Keyword Args:
        alignment (Optional[ui.Alignment]): Aligns the content within the label. Default is `ui.Alignment.LEFT_CENTER`.
        name (Optional[str]): The name of the widget. Used for identifying widgets.
        style_type_name_override (Optional[str]): Overrides the default style type name for customization."""

    def __init__(
        self,
        text: str,
        highlight: Optional[str] = None,
        match_case: bool = False,
        width: ui.Length = ui.Fraction(1),
        height: ui.Length = ui.Fraction(1),
        label_width: int|ui.Length = 0,
        style: Dict = None,
        **kwargs,
    ):
        """Initializes the highlight label widget."""
        self._container: Optional[ui.HStack] = None
        self.__text = text
        self.__hightlight = highlight
        self.__match_case = match_case
        self.__width = width
        self.__height = height
        self.__style = UI_STYLE.copy()
        self.__label_width = label_width
        if style:
            self.__style.update(style)
        self.__label_kwargs = kwargs
        self._build_ui()

    def _build_ui(self):
        if not self._container:
            self._container = ui.HStack(
                width=self.__width, height=self.__height, style=self.__style, **self.__label_kwargs
            )
        else:
            self._container.clear()

        kwargs = self.__label_kwargs.copy()
        if "alignment" in self.__style:
            alignment = self.__style.get("alignment")
        elif "alignment" in kwargs:
            alignment = kwargs.get("alignment")
        else:
            alignment = ui.Alignment.LEFT_CENTER
        left_aligned = alignment.name.startswith("LEFT")

        if not self.__hightlight:
            with self._container:
                if not left_aligned:
                    ui.Spacer()
                ui.Label(
                    self.__text,
                    width=self.__label_width,
                    style=self.__style,
                    **kwargs,
                )
                if left_aligned:
                    ui.Spacer()
        else:
            selection_chain = split_selection(self.__text, self.__hightlight, match_case=self.__match_case)
            labelnames_chain = [kwargs.pop("name", ""), "highlight"]
            # Extend the label names depending on the size of the selection chain. Example, if it was [a, b]
            # and selection_chain is [z,y,x,w], it will become [a, b, a, b].
            labelnames_chain *= int(math.ceil(len(selection_chain) / len(labelnames_chain)))

            with self._container:
                if not left_aligned:
                    ui.Spacer()
                for current_text, current_name in zip(selection_chain, labelnames_chain):
                    if not current_text:
                        continue

                    # Only override highlight style, so we are otherwise compatible with Label
                    style_type = "HighlightLabel" if current_name == "highlight" else "Label"
                    style_type = kwargs.pop("style_type_name_override", style_type)

                    ui.Label(
                        current_text,
                        width=self.__label_width,
                        name=current_name,
                        style_type_name_override=style_type,
                        style=self.__style,
                        **kwargs,
                    )
                if left_aligned:
                    ui.Spacer()

    @property
    def widget(self) -> Optional[ui.HStack]:
        """Gets the widget's container."""
        return self._container

    @property
    def visible(self) -> None:
        """Gets the visibility of the widget."""
        return self._container.visible

    @visible.setter
    def visible(self, value: bool) -> None:
        """Sets the visibility of the widget.

        Args:
            value (bool): The visibility state to set."""
        self._container.visible = value

    @property
    def text(self) -> str:
        """Gets the text of the label.

        Returns:
            str: The current text of the label."""
        return self.__text

    @text.setter
    def text(self, value: str) -> None:
        """Sets the text of the label and rebuilds the UI.

        Args:
            value (str): The text to set."""
        self.__text = value
        self._build_ui()

    @property
    def hightlight(self) -> Optional[str]:
        """Gets the highlight text of the label.

        Returns:
            Optional[str]: The current highlight text of the label."""
        return self.__hightlight

    @hightlight.setter
    def highlight(self, value: Optional[str]) -> None:
        """Sets the highlight text of the label and rebuilds the UI.

        Args:
            value (Optional[str]): The highlight text to set."""
        self.__hightlight = value
        self._build_ui()

    @property
    def text(self) -> str:
        """Gets the text of the label.

        Returns:
            str: The current text of the label."""
        return self.__text

    @text.setter
    def text(self, value: str) -> None:
        """Sets the text of the label and rebuilds the UI.

        Args:
            value (str): The text to set."""
        self.__text = value

    def __getattr__(self, attr):
        return getattr(self._container, attr)
