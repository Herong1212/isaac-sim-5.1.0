import asyncio
from typing import Optional, List, Callable
from functools import partial

import omni.kit.app
import omni.ui as ui
from .style import UI_STYLE

MAX_SUGGESTIONS = 10

class SuggestItem(ui.AbstractItem):
    """Item for suggest model"""
    def __init__(self, text: str):
        super().__init__()
        self.text = text
        self.model = ui.SimpleStringModel(self.text)


class SuggestModel(ui.AbstractItemModel):
    """Item model to show in suggest treeview"""
    def __init__(self, suggestions: List[str] = [], max_suggestions=MAX_SUGGESTIONS):
        super().__init__()
        self._suggestions = suggestions
        self.max_suggestions = max_suggestions
        self.input: str = ""

    @property
    def suggestions(self) -> List[str]:
        return self._suggestions

    @suggestions.setter
    def suggestions(self, texts: List[str]) -> None:
        self._suggestions = texts
        self._item_changed(None)

    def get_item_children(self, item: Optional[ui.AbstractItem] = None) -> List[SuggestItem]:
        """Returns all the children when the widget asks it."""
        if item is not None:
            return []

        self._items = []
        for text in self._suggestions:
            if len(self._items) > self.max_suggestions:
                break
            if text.lower().startswith(self.input.lower()):
                self._items.append(SuggestItem(text))

        return self._items

    def get_item_value_model_count(self, item: SuggestItem) -> int:
        """The number of columns"""
        return 1

    def get_item_value_model(self, item: SuggestItem, column_id: int) -> ui.SimpleStringModel:
        return item.model if item else None

class SuggestWindow(ui.Window):
    """
    A suggest window to show a input field (instead of search field) and a treeview (show suggestions)
    """
    def __init__(self, search_field: ui.StringField, suggestions: List[str] = [], max_suggestions=MAX_SUGGESTIONS, on_end_edit_fn: Callable=None, on_double_clicked_fn: Callable=None):
        flags = (
            ui.WINDOW_FLAGS_NO_COLLAPSE
            | ui.WINDOW_FLAGS_NO_TITLE_BAR
            | ui.WINDOW_FLAGS_NO_SCROLLBAR
            | ui.WINDOW_FLAGS_NO_RESIZE
            | ui.WINDOW_FLAGS_NO_CLOSE
            | ui.WINDOW_FLAGS_NO_DOCKING
            | ui.WINDOW_FLAGS_NO_BACKGROUND
        )
        super().__init__(
            "##Suggest window for search field",
            width=0,
            height=0,
            flags=flags,
            visible=False,
            padding_y=0,
            padding_x=0,
            auto_resize=True,
        )
        self._suggestions = suggestions
        self._suggest_model = SuggestModel(suggestions=suggestions, max_suggestions=max_suggestions)
        self.__input_field: Optional[ui.StringField] = None
        self.__search_field = search_field
        self._on_end_edit_fn = on_end_edit_fn
        self._on_double_click_fn = on_double_clicked_fn
        self.frame.set_build_fn(self._build_ui)
        self.frame.set_style(UI_STYLE)
        self.set_visibility_changed_fn(self._on_visibility_changed)

    def destroy(self):
        self._sub_suggestion = None
        self.visible = False
        self.set_visibility_changed_fn(None)

    @property
    def suggestions(self) -> List[str]:
        return self._suggest_model.suggestions

    @suggestions.setter
    def suggestions(self, texts: List[str]) -> None:
        self._suggest_model.suggestions = texts

    @property
    def max_suggestions(self) -> int:
        return self._suggest_model.max_suggestions

    @max_suggestions.setter
    def max_suggestions(self, count: int) -> None:
        self._suggest_model.max_suggestions = count

    def _build_ui(self):
        with self.frame:
            with ui.VStack(width=0):
                # Input field, to be same as search field
                self.__input_field = ui.StringField(
                    style_type_name_override="SearchField",
                    width = self.__search_field.computed_width,
                    height=self.__search_field.computed_height,
                    mouse_double_clicked_fn=lambda x, y, btn, m: self._on_double_click(),
                )
                ui.Spacer(height=3)

                # OM-81777: Buttons to show suggestions instead of Treeview
                # Because suggestion window does not show Treeview while its height not set if HDR enabled in Windows display settings
                with ui.HStack():
                    with ui.ZStack(height=0):
                        ui.Rectangle(style_type_name_override="TreeView.Frame")
                        with ui.HStack():
                            ui.Spacer(width=1)
                            self._suggestion_container = ui.VStack()
                            self.__build_suggestions()

                            def __refresh_suggestions(model, item):
                                async def __delay_refresh():
                                    await omni.kit.app.get_app().next_update_async()

                                    self._suggestion_container.clear()
                                    self.__build_suggestions()

                                asyncio.ensure_future(__delay_refresh())

                            self._sub_suggestion = self._suggest_model.subscribe_item_changed_fn(__refresh_suggestions)
                            ui.Spacer(width=1)

                    with ui.HStack():
                       ui.Spacer(style_type_name_override="Tooltips.Spacer")

        self._sub_end_edit = self.__input_field.model.subscribe_end_edit_fn(self._on_end_edit)
        self._sub_text_edit = self.__input_field.model.subscribe_value_changed_fn(self._on_text_edit)

    def __build_suggestions(self):
        with self._suggestion_container:
            for item in self._suggest_model.get_item_children(None):
                ui.Button(
                    item.text if item.text else " ",
                    height=20,
                    style_type_name_override="Tooltips.Item",
                    mouse_pressed_fn=lambda x, y, b, a, t=item.text: self._on_suggestion_pressed(t),
                )

    def _build_suggest_list(self):
        self._suggest_model.input = self.__input_field.model.as_string
        self._suggest_model._item_changed(None)

    def _on_end_edit(self, model: ui.AbstractValueModel) -> None:
        self.visible = False
        if self._on_end_edit_fn:
            self._on_end_edit_fn()

        # Clean input
        self.__input_field.model.set_value("")
        self._build_suggest_list()

    def _on_text_edit(self, model: ui.AbstractValueModel) -> None:
        # Input string changed, update search field and suggestion list
        self.__search_field.model.set_value(self.__input_field.model.as_string)
        self._build_suggest_list()

    def _on_suggestion_pressed(self, text: str) -> None:
        self.__input_field.model.set_value(text)

    def _on_visibility_changed(self, visible: bool) -> None:
        if visible:
            self.__search_field.visible = False

            async def __delay_init():
                while self.__input_field is None:
                    await omni.kit.app.get_app().next_update_async()
                self.position_x = self.__search_field.screen_position_x
                self.position_y = self.__search_field.screen_position_y
                self.width = self.__search_field.computed_content_width
                for _ in range(2):
                    await omni.kit.app.get_app().next_update_async()
                self.__input_field.model.set_value(self.__search_field.model.as_string)
                self.__input_field.focus_keyboard()
                self._sub_end_edit = self.__input_field.model.subscribe_end_edit_fn(self._on_end_edit)
                self._sub_text_edit = self.__input_field.model.subscribe_value_changed_fn(self._on_text_edit)

            asyncio.ensure_future(__delay_init())
        else:
            self.__search_field.visible = True
            self._sub_text_edit = None
            self._sub_end_edit = None

    def _on_double_click(self):
        # OM-107724: double click to edit all words
        if self._on_double_click_fn:
            self._on_double_click_fn()

        # Hide to refresh search field then show again to show at correct position with string
        async def __delay_set_position():
            self.visible = False
            await omni.kit.app.get_app().next_update_async()
            self.visible = True

        asyncio.ensure_future(__delay_set_position())