"""This module provides the ComboListBoxWidget class, which integrates a search field with a list box for item selection, and a function to create a searchable combo box widget."""

__all__ = ["ComboListBoxWidget"]

import asyncio
import carb.input
import omni.kit.app
import omni.appwindow
import omni.ui as ui
from typing import List
from .combo_model import ComboBoxListModel, ComboBoxListDelegate
from .search_widget import SearchWidget


class ComboListBoxWidget:
    """A widget that combines a search field with a list box for item selection.

    This widget facilitates the selection of items from a list that can be filtered
    through a search interface. Users can type in the search widget to filter the
    items displayed in the list box below it. It supports customization through themes
    and delegates for item display.

    Args:
        search_widget: SearchWidget
            An instance of SearchWidget to handle search input.
        item_list: list
            A list of items to be displayed and filtered in the list box.
        theme: str
            The visual theme for the widget's appearance.
        window_id: str
            The identifier for the window; default is 'SearchableComboBoxWindow'.
        delegate: ui.AbstractItemDelegate
            Delegate for custom item rendering; defaults to ComboBoxListDelegate."""

    def __init__(
        self,
        search_widget: SearchWidget,
        item_list: list,
        theme: str,
        window_id: str = "SearchableComboBoxWindow",
        delegate: ui.AbstractItemDelegate = ComboBoxListDelegate(),
    ):
        """A widget that combines a search field with a list box for item selection.

        This widget facilitates the selection of items from a list that can be filtered
        through a search interface. Users can type in the search widget to filter the
        items displayed in the list box below it. It supports customization through themes
        and delegates for item display.

        Args:
            search_widget: SearchWidget
                An instance of SearchWidget to handle search input.
            item_list: list
                A list of items to be displayed and filtered in the list box.
            theme: str
                The visual theme for the widget's appearance.
            window_id: str
                The identifier for the window; default is 'SearchableComboBoxWindow'.
            delegate: ui.AbstractItemDelegate
                Delegate for custom item rendering; defaults to ComboBoxListDelegate."""

        icon_path = (
            f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/data/icons"
        )
        self._height = 32
        self._theme = theme
        self.__parent = None
        self._window = None
        self.__frame = None
        self._placeholder_search_widget = search_widget
        self._search_widget = SearchWidget(theme=theme, icon_path=icon_path, modified_fn=self._search_updated)
        self._search_size = 22
        self._window_id = window_id

        self._name_value_model = ComboBoxListModel(item_list)
        self._name_value_delegate = delegate

        if theme == "NvidiaDark":
            BACKGROUND_COLOR = 0xFF3D3B38
            FIELD_TEXT_COLOR = 0xFFD5D5D5
            FIELD_BORDER_COLOR = 0
            FIELD_HOVER_COLOR = 0xFF383838
        else:
            BACKGROUND_COLOR = 0xFF545454
            FIELD_TEXT_COLOR = 0xFFD5D5D5
            FIELD_BORDER_COLOR = 0
            FIELD_HOVER_COLOR = 0xFFACACAF

        self._window_style = {
            "Window": {
                "background_color": BACKGROUND_COLOR,
                "border_radius": 6,
                "border_width": 1,
                "border_color": FIELD_BORDER_COLOR,
            },
            "ScrollingFrame": {"background_color": BACKGROUND_COLOR},
            "Field": {
                "background_color": BACKGROUND_COLOR,
                "color": FIELD_TEXT_COLOR,
                "border_color": FIELD_BORDER_COLOR,
                "border_radius": 1,
                "border_width": 0.5,
                "font_size": 16.0,
            },
            "Field:hovered": {"background_color": FIELD_HOVER_COLOR},
            "Field:pressed": {"background_color": FIELD_HOVER_COLOR},
            "Field::text_field": {"border_width": 0, "font_size": 14.0},
            # search
            "TreeView.Item::search_view": {"margin": 4},
            "TreeView:selected": {"background_color": 0xFF333333},
        }

    def set_parent(self, parent):
        """Set the parent widget

        Args:
            parent: prent widget."""
        self.__parent = parent

    def clean(self):
        """Cleans up the ComboListBoxWidget and destroys models."""
        if self._name_value_model:
            self._name_value_model.clean()
        if self._name_value_delegate:
            self._name_value_delegate.clean()
        if self._search_widget:
            self._search_widget.clean()

        del self._name_value_model
        del self._name_value_delegate

        self._placeholder_search_widget = None
        self._scrolling_frame = None
        self._combo_view = None
        del self._window

    def _search_updated(self, string):
        self._search_widget.update(string)
        self._name_value_model.filter_by_text(string)
        self._combo_view.scroll_here_y(0.0)

    def _select_next(self, comboview: ui.TreeView, model: ui.AbstractItemModel, after=True):
        full_list = model.get_item_children(None)
        selection = comboview.selection
        if not selection:
            comboview.selection = [full_list[0]]
        else:
            index = full_list.index(selection[0])
            index += 1 if after else -1
            if index < 0 or index >= len(full_list):
                return
            comboview.selection = [full_list[index]]

    def _select_index(self, comboview: ui.TreeView, model: ui.AbstractItemModel, index: int):
        full_list = model.get_item_children(None)
        selection = comboview.selection
        if index >= 0 and index < len(full_list):
            comboview.selection = [full_list[index]]

    def _get_view_height(self):
        item_count = len(self._name_value_model.get_item_children(None))
        view_height = (min(10, item_count) * self._height + 1.5) + 4
        view_height_min = (3 * self._height + 1.5) + 4

        try:
            appwindow = omni.appwindow.get_default_app_window()
            window_height = appwindow.get_height()
            window_height = (window_height / ui.Workspace.get_dpi_scale()) - 8

            if self._window.position_y + view_height > window_height:
                adj = ((self._window.position_y + view_height) - window_height) + self._search_size
                view_height -= adj
                if view_height < view_height_min:
                    view_height = view_height_min
        except:
            pass

        return view_height

    def destroy_ui(self, visible):
        """destroys the ComboListBoxWidget UI."""
        if not visible:
            self.set_parent(None)
            self.clean()

    def build_ui(self):
        """builds UI for the ComboListBoxWidget UI."""
        if self._window and self._window.visible:
            return
        # Create and show the window
        self._window = ui.Window(
            self._window_id,
            flags=ui.WINDOW_FLAGS_POPUP
            | ui.WINDOW_FLAGS_NO_TITLE_BAR
            | ui.WINDOW_FLAGS_NO_RESIZE
            | ui.WINDOW_FLAGS_NO_MOVE,
            auto_resize=True,
            padding_x=0,
            padding_y=0,
        )
        self._window.frame.set_style(self._window_style)
        self._window.set_visibility_changed_fn(self.destroy_ui)

        def view_clicked(view):
            async def get_selection():
                await omni.kit.app.get_app().next_update_async()
                selection = view.selection
                model = selection[0].name_model
                self._placeholder_search_widget.set_text(model.get_value_as_string())
                self._window.visible = False

            asyncio.ensure_future(get_selection())

        self._window.position_x = self.__parent.screen_position_x
        self._window.position_y = self.__parent.screen_position_y + 20

        with self._window.frame:
            with ui.VStack(width=0, height=0):
                self._search_widget.build_ui(self.__parent.computed_content_width + 40, self._search_size)
                self._scrolling_frame = ui.ScrollingFrame(
                    height=self._get_view_height(),
                    horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                    vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                )
                with self._scrolling_frame:
                    self._combo_view = ui.TreeView(
                        self._name_value_model,
                        delegate=self._name_value_delegate,
                        root_visible=False,
                        header_visible=False,
                        name="search_view",
                    )

                self._combo_view.set_mouse_released_fn(lambda x, y, b, c: view_clicked(self._combo_view))

                async def scroll_to_item():
                    await omni.kit.app.get_app().next_update_async()
                    await omni.kit.app.get_app().next_update_async()
                    item_index = self._name_value_model.get_index_for_item(self._placeholder_search_widget.get_text())
                    self._select_index(self._combo_view, self._name_value_model, item_index)

                asyncio.ensure_future(scroll_to_item())

    def destroy(self):
        """Destroys the ComboListBoxWidget widget."""
        self.__parent = None
        self.__frame = None
        self._scrolling_frame = None
        self._combo_view = None
        del self._window


def build_searchable_combo_widget(
    combo_list: List[str],
    combo_index: int,
    combo_click_fn: callable,
    widget_height: int,
    default_value: str,
    window_id: str = "SearchableComboBoxWindow",
    delegate: ui.AbstractItemDelegate = ComboBoxListDelegate(),
) -> SearchWidget:
    """Creates a searchable combo box widget with a specified list of options.

    Args:
        combo_list (List[str]): List of string options to be included in the combo box.
        combo_index (int): Index of the currently selected item in the combo list.
        combo_click_fn (callable): Function to be called when an item in the combo box is clicked.
        widget_height (int): The height of the widget.
        default_value (str): The default value to be displayed when no item is selected.
        window_id (str, optional): The identifier for the window; default is 'SearchableComboBoxWindow'.
        delegate (ui.AbstractItemDelegate, optional): Delegate for custom item rendering; defaults to ComboBoxListDelegate().

    Returns:
        SearchWidget: An instance of the SearchWidget with an attached searchable combo box."""
    theme = carb.settings.get_settings().get_as_string("/persistent/app/window/uiStyle") or "NvidiaDark"

    def show_combo_popup(
        search_widget: SearchWidget, name_field: ui.StringField, combo_index: int, combo_click_fn: callable
    ):
        window = ui.Workspace.get_window(window_id)
        if window:
            window.visible = False
            return

        listbox_widget = ComboListBoxWidget(
            search_widget=search_widget, item_list=combo_list, window_id=window_id, delegate=delegate, theme=theme
        )
        listbox_widget.set_parent(name_field)
        listbox_widget.build_ui()

    search_widget = SearchWidget(theme=theme, icon_path=None)
    name_field, listbox_button = search_widget.build_ui_popup(
        search_size=widget_height,
        default_value=default_value,
        popup_text=combo_list[combo_index] if combo_index >= 0 else default_value,
        index=combo_index,
        update_fn=combo_click_fn,
    )

    name_field.set_mouse_pressed_fn(
        lambda x, y, b, m, s=search_widget, f=name_field: show_combo_popup(s, f, combo_index, combo_click_fn)
    )
    listbox_button.set_mouse_pressed_fn(
        lambda x, y, b, m, s=search_widget, f=name_field: show_combo_popup(s, f, combo_index, combo_click_fn)
    )

    return search_widget
