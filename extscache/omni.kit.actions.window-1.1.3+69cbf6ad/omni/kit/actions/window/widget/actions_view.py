__all__ = ["ActionsView"]
import omni.ui as ui
from ..model.abstract_actions_model import AbstractActionsModel
from ..delegate.actions_delegate import ActionsDelegate

class ActionsView(ui.TreeView):
    def __init__(self, model: AbstractActionsModel, delegate: ActionsDelegate):
        super().__init__(
            model,
            delegate=delegate,
            root_visible=False,
            header_visible=True,
            columns_resizable=True,
            style_type_name_override="ActionsView"
        )
        self.column_widths = delegate.column_widths

