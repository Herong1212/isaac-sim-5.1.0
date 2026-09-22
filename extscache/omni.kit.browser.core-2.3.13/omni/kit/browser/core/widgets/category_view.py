from omni import ui
from .category_delegate import CategoryDelegate
from ..models import CategoryItem

from typing import List


class CategoryView(ui.TreeView):
    """
    TreeView to represent categories.
    Keyword Args:
        delegate (CatetoryDelegate): delegate object to represent category item. Default using CategoryDelegate
        on_category_selected_fn (func): Function called when category item selected (None if nothing selected). Default is None.
            Function signature: void on_category_selected_fn(item: CategoryItem)
    """

    def __init__(self, model, delegate=CategoryDelegate(), on_category_selected_fn=None):
        self._delegate = delegate
        self._on_category_selected_fn = on_category_selected_fn
        self._multi_selections = False

        super().__init__(
            model, delegate=self._delegate, root_visible=False, header_visible=False, drop_between_items=False
        )
        self.set_selection_changed_fn(self._on_selection_changed)

    def _on_selection_changed(self, selections: List[CategoryItem]):
        if len(selections) > 1:
            if not self._multi_selections:
                # Diable multi selection
                selections = selections[-1:]
                self.selection = selections

        if len(selections) == 0:
            if self._on_category_selected_fn:
                self._on_category_selected_fn(None)
        else:
            for item in selections:
                if self._on_category_selected_fn:
                    self._on_category_selected_fn(item)
