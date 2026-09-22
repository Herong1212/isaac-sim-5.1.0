__all__ = ["ActionsWindow"]
from .model.actions_model import ActionsModel, ActionDetailItem
from .column_registry import ColumnRegistry
from .widget.actions_view import ActionsView
from .delegate.actions_delegate import ActionsDelegate
from .delegate.string_column_delegate import StringColumnDelegate
from .style import ACTIONS_WINDOW_STYLE
import omni.kit.app
import omni.ui as ui
from omni.kit.actions.core import Action

import asyncio
from typing import List, Optional


class ActionsWindow(ui.Window):
    """
    Window to show registered actions.
    """

    def __init__(self, title: str, width=1200, height=600):
        self._search_field = None

        super().__init__(title, width=width, height=height)
        self.frame.set_style(ACTIONS_WINDOW_STYLE)
        self.frame.set_build_fn(self._build_ui)

    def destroy(self):
        self.visible = False
        if self._search_field:
            self._search_field.destroy()
        self._actions_view = None

    def _register_column_delegates(self):
        self._column_registry.register_delegate(StringColumnDelegate("Action", width=200))
        self._column_registry.register_delegate(
            StringColumnDelegate(
                "Display Name",
                get_value_fn=lambda item: item.action.display_name if isinstance(item, ActionDetailItem) else "",
                width=300
            )
        )
        self._column_registry.register_delegate(
            StringColumnDelegate(
                "Tag",
                get_value_fn=lambda item: item.action.tag if isinstance(item, ActionDetailItem) else "",
                width=160,
            )
        )
        self._column_registry.register_delegate(
            StringColumnDelegate(
                "Icon Url",
                lambda item: item.action.icon_url if isinstance(item, ActionDetailItem) else "",
                width=120,
            )
        )
        self._column_registry.register_delegate(
            StringColumnDelegate(
                "Description",
                lambda item: item.action.description if isinstance(item, ActionDetailItem) else "",
                width=200,
            )
        )

    def _build_ui(self):
        self._column_registry = ColumnRegistry()
        self._register_column_delegates()
        
        self._actions_model = ActionsModel(self._column_registry, on_search_action_fn=self._on_search_action)
        self._actions_delegate = ActionsDelegate(self._actions_model, self._column_registry)

        with self.frame:
            with ui.VStack(spacing=4):
                try:
                    from omni.kit.widget.searchfield import SearchField 
                    self._search_field = SearchField(
                        on_search_fn=self._on_search,
                        subscribe_edit_changed=True,
                        style=ACTIONS_WINDOW_STYLE,
                        show_tokens=False,
                    )
                except ImportError:
                    self._search_field = None
                with ui.ScrollingFrame(
                    horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                    vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                    style_type_name_override="ActionsView",
                ):
                    self._actions_view = ActionsView(self._actions_model, self._actions_delegate)

    def _on_search(self, search_words: Optional[List[str]]) -> None:
        self._actions_model.search(search_words)
        self._actions_view.set_expanded(None, True, True)

    def _on_search_action(self, action: Action, word: str) -> bool:
        if word.lower() in action.extension_id.lower() \
            or word.lower() in action.id.lower() \
            or word.lower() in action.display_name.lower() \
            or word.lower() in action.description.lower() \
            or word.lower() in action.tag.lower() \
            or word.lower() in action.icon_url.lower():
                return True

        return False
