from typing import Optional

from omni.kit.window.preferences import PreferenceBuilder
import omni.ui as ui

from .menubar_treeview_delegate import MenubarTreeViewDelegate
from .model import PreferenceModel
from ..viewport_menu_model import ViewportMenuModel
from ..style import VIEWPORT_PREFERENCE_STYLE

__all__ = ["ViewportMenubarPage"]


class ViewportMenubarPage(PreferenceBuilder):
    """
    Represent a preference page to show and edit viewport menubar settings.
    """

    def __init__(self, model: ViewportMenuModel):
        super().__init__("Viewport")
        self._model = PreferenceModel(model)
        self._tree_view: Optional[ui.TreeView] = None
        self._delegate: Optional[ui.AbstractItemDelegate] = None

    def destroy(self):
        if self._tree_view:
            self._delegate.destroy()
            self._tree_view.destroy()
            self._tree_view = None
        self._model.destroy()

    def build(self):
        self._delegate = MenubarTreeViewDelegate()
        with self.add_frame("Viewport Toolbar"):
            with ui.ScrollingFrame(style_type_name_override="TreeView.Frame", style=VIEWPORT_PREFERENCE_STYLE):
                self._tree_view = ui.TreeView(self._model, delegate=self._delegate, root_visible=False)
