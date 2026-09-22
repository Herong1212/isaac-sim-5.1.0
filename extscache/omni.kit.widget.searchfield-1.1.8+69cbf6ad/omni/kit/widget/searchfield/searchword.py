import carb
from omni import ui
from .style import UI_STYLE, ICON_PATH


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
        settings = carb.settings.get_settings()
        self._theme = settings.get_as_string("/persistent/app/window/uiStyle") or "NvidiaDark"

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
        """
        Widget visibility
        """
        return self._container.visible

    @visible.setter
    def visible(self, value: bool) -> None:
        self._container.visible = value
