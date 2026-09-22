# Public API for module omni.kit.widget.highlight_label:

## Classes

- class HighlightLabel
  - def __init__(self, text: str, highlight: Optional[str] = None, match_case: bool = False, width: ui.Length = ui.Fraction(1), height: ui.Length = ui.Fraction(1), label_width: int | ui.Length = 0, style: Dict = None, **kwargs)
  - [property] def widget(self) -> Optional[ui.HStack]
  - [property] def visible(self)
  - [visible.setter] def visible(self, value: bool)
  - [property] def text(self) -> str
  - [text.setter] def text(self, value: str)
  - [property] def hightlight(self) -> Optional[str]
  - [hightlight.setter] def highlight(self, value: Optional[str])
  - [property] def text(self) -> str
  - [text.setter] def text(self, value: str)
