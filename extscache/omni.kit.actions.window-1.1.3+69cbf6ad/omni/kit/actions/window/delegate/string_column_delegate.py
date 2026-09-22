__all__ = ["StringColumnDelegate"]
from .abstract_column_delegate import AbstractColumnDelegate
from ..model.actions_item import ActionExtItem, AbstractActionItem
from ..model.abstract_actions_model import AbstractActionsModel
from ..style import HIGHLIGHT_LABEL_STYLE
import omni.ui as ui
from omni.kit.widget.highlight_label import HighlightLabel
from typing import Callable


class StringColumnDelegate(AbstractColumnDelegate):
    """
    A simple delegate to display a string in column.

    Kwargs:
        get_value_fn (Callable[[ui.AbstractItem], str]): Callback function to get item display string. Default using item.id
        width (ui.Length): Column width. Default ui.Fraction(1).
    """
    def __init__(self, name: str, get_value_fn: Callable[[AbstractActionItem], str]=None, width: ui.Length=ui.Fraction(1)):
        self._get_value_fn = get_value_fn
        super().__init__(name, width=width)

    def build_widget(self, model: AbstractActionsModel, item: AbstractActionItem, level: int, expand: bool):
        if isinstance(item, ActionExtItem):
            container = ui.ZStack()
            with container:
                with ui.VStack():
                    ui.Spacer()
                    ui.Rectangle(height=26, style_type_name_override="ActionsView.Row.Background")
                    ui.Spacer()
                HighlightLabel(self.get_value(item), highlight=item.highlight, style=HIGHLIGHT_LABEL_STYLE, alignment=ui.Alignment.LEFT_TOP)
            return container
        if isinstance(item, ActionExtItem) or isinstance(item, AbstractActionItem):
            label = HighlightLabel(self.get_value(item), highlight=item.highlight, style=HIGHLIGHT_LABEL_STYLE)
            return label.widget
        else:
            return None

    def get_value(self, item: AbstractActionItem):
        if self._get_value_fn:
            return self._get_value_fn(item)
        else:
            return item.id
