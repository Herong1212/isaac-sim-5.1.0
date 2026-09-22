from omni import ui
from ..models import CategoryItem


class CategoryDelegate(ui.AbstractItemDelegate):
    """
    Delegate to represent category item.
    Args:
        teee_mode: Show categories in tree mode. Default flat mode (no branches)
    """

    def __init__(self, tree_mode: bool = False):
        self._tree_mode = tree_mode
        super().__init__()

    def build_widget(
        self, model: ui.AbstractItemModel, item: CategoryItem, index: int = 0, level: int = 0, expanded: bool = False
    ):
        """
        Create a widget per catetory item
        Args:
            model (AbstractItemModel): Category data model
            item (CategoryItem): Category item
            index (int): ignore
            level (int): ignore
            expand (int): ignore
        """
        if self._tree_mode and len(item.children) > 0:
            # In tree mode, if have children, show as branch
            ui.Label(
                self.get_label(item), alignment=ui.Alignment.LEFT_CENTER, style_type_name_override="TreeView.Item.Name"
            )
            return

        count = self.get_count(item)

        with ui.HStack(height=20):
            if self._tree_mode:
                ui.Label("  " * level, width=0)
            ui.Spacer(width=6)
            if not self._tree_mode:
                with ui.VStack(width=6):
                    ui.Spacer()
                    ui.Line(height=10, alignment=ui.Alignment.LEFT, style_type_name_override="TreeView.Mark")
                    ui.Spacer()
            ui.Label(
                self.get_label(item), alignment=ui.Alignment.LEFT_CENTER, style_type_name_override="TreeView.Item.Name"
            )

            if not self._tree_mode:
                ui.Label(
                    str(count),
                    width=10,
                    alignment=ui.Alignment.RIGHT_CENTER,
                    style_type_name_override="TreeView.Item.Count",
                )

    def build_branch(
        self,
        model: ui.AbstractItemModel,
        item: CategoryItem,
        column_id: int = 0,
        level: int = 0,
        expanded: bool = False,
    ):
        """
        Create a branch widget that opens or closes subtree
        Args:
            model (AbstractItemModel): Category data model
            item (CategoryItem): Category item
            column_id (int): ignore
            level (int): ignore
            expand (int): ignore
        """
        if not self._tree_mode or len(item.children) == 0:
            # In tree mode, if have children, show as branch
            return

        with ui.HStack(height=20, spacing=5):
            ui.Label("  " * level, width=0)
            if expanded:
                ui.Label("- ", width=5)
            else:
                ui.Label("+ ", width=5)

    def get_label(self, item: CategoryItem) -> str:
        return item.name

    def get_count(self, item: CategoryItem) -> str:
        return item.count
