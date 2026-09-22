__all__ = ["AbstractActionItem", "ActionExtItem", "ActionDetailItem"]
import omni.ui as ui
from omni.kit.actions.core import Action


class AbstractActionItem(ui.AbstractItem):
    """
    General action item.

    Args:
        id (str): Item id.
        highlight (str): Highlight string.
    """
    # Represent action detail
    def __init__(self, id: str, highlight: str = None):
        self.id = id
        self.highlight = highlight
        super().__init__()


class ActionExtItem(AbstractActionItem):
    """
    Represent extension actions belongs to.

    Args:
        ext_id (str): Extension id.
        highlight (str): Highlight string.
    """
    def __init__(self, ext_id: str, highlight: str = None):
        super().__init__(ext_id, highlight=highlight)


class ActionDetailItem(AbstractActionItem):
    def __init__(self, action: Action, highlight: str = None):
        super().__init__(action.id, highlight=highlight)
        self.action = action
