__all__ = ["AbstractColumnDelegate"]
import omni.ui as ui
import abc


class AbstractColumnDelegate:
    """
    Represent a column delegate in actions Treeview.

    Args:
        name (str): Column name.
        width (ui.Length): Column width. Default ui.Fraction(1).
    """
    def __init__(self, name: str, width: ui.Length=ui.Fraction(1)):
        self._name = name
        if isinstance(width, int) or isinstance(width, float):
            width = ui.Pixel(width)
        self._width = width

    @property
    def width(self) -> ui.Length:
        """
        Column width.
        """
        return self._width

    def execute(self, item: ui.AbstractItem):
        """
        Execute model item.
        Args:
            item (ui.AbstractItem): Item to show.
        """
        pass

    @abc.abstractmethod
    def build_widget(self, model: ui.AbstractItemModel, item: ui.AbstractItem, level: int, expand: bool) -> ui.Widget:
        """
        Build a custom column widget in TreeView.
        Return created widget.

        Args:
            model (ui.AbstractItemModel): Actions model.
            item (ui.AbstractItem): Item to show.
            level (int): Level in treeview.
            expand (bool): Iten expand or not.
        """
        return None

    def build_header(self):
        """
        Build header widget in TreeView, default ui.Label(name)
        """
        with ui.ZStack():
            ui.Rectangle(style_type_name_override="ActionsView.Header.Background")
            ui.Label(self._name, style_type_name_override="ActionsView.Header.Text")


