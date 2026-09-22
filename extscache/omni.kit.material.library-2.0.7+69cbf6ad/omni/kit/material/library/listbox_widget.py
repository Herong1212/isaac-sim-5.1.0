"""Simulated combobox widget with drop-down list of materials from stage class."""

__all__ = ["MaterialListBoxWidget"]

import asyncio
import copy
import carb.input
import omni.usd
import omni.ui as ui
from typing import List
from .treeview_model import MaterialListModel, MaterialListDelegate
from .search_widget import SearchWidget


class MaterialListBoxWidget():
    """Simulated combobox widget with drop-down list of materials from stage class."""
    def __init__(self, icon_path:str, index: int, on_click_fn: callable, theme: str, filter_fn: callable=None, get_materials_async_fn: callable=None):
        """Initialize class function.

        Args:
            icon_path (str): path to icons, if None then omni.kit.material.library/data/icons will be used.
            index (int): default item in combobox.
            on_click_fn (callable): function called when combobox item changed.
            theme (str): theme name, should be "NvidiaDark" or "NvidiaLight". Not wildly supported.
            filter_fn (callable): filter function passed to MaterialListModel.
            get_materials_async_fn (callable): override for default omni.kit.material.library.get_materials_from_stage_async callback.
        """
        if not icon_path:
            icon_path = f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/data/icons"
        self._icon_path = icon_path
        self._height = 32
        self._index = index
        self._on_click_fn = on_click_fn
        self._theme = theme
        self.__parent = None
        self._window = None
        self.__frame = None
        self._search_widget = SearchWidget(theme=theme, icon_path=icon_path, modified_fn=self._search_updated)
        self._search_size = 22
        self._selection_on_loading_complete = None
        self._filter_fn = filter_fn
        self._get_materials_async_fn = get_materials_async_fn

        if theme == "NvidiaDark":
            BACKGROUND_COLOR = 0xFF555555
            FIELD_TEXT_COLOR = 0xFFD5D5D5
            FIELD_BORDER_COLOR = 0
            FIELD_HOVER_COLOR = 0xFF333333
        else: # pragma: no cover
            BACKGROUND_COLOR = 0xFF545454
            FIELD_TEXT_COLOR = 0xFFD5D5D5
            FIELD_BORDER_COLOR = 0
            FIELD_HOVER_COLOR = 0xFFACACAF

        self._window_style = {
            "Window": {
                "background_color": BACKGROUND_COLOR,
                "border_radius": 6,
                "border_width": 1,
                "border_color": FIELD_BORDER_COLOR
            },
            "ScrollingFrame":
            {
                "background_color": BACKGROUND_COLOR
            },
            "Field": {
                "background_color":  BACKGROUND_COLOR,
                "color": FIELD_TEXT_COLOR,
                "border_color": FIELD_BORDER_COLOR,
                "border_radius": 1,
                "border_width": 0.5,
                "font_size": 16.0,
            },
            "Field:hovered": {"background_color": FIELD_HOVER_COLOR},
            "Field:pressed": {"background_color": FIELD_HOVER_COLOR},

            "Field::text_field": {
                "border_width": 0,
                "font_size": 14.0
            },

            # search treeview
            "TreeView.Item::search_treeview": {
                "margin": 4
            },
        }

    def set_parent(self, parent: ui.Widget):
        """Set widget parent

        Args:
            parent (ui.Widget): parent widget to pin widget to.
        """
        self.__parent = parent

    def clean(self):
        """Clean up widget."""
        if self._name_value_model:
            self._name_value_model.clean()
        if self._name_value_delegate:
            self._name_value_delegate.clean()
        if self._search_widget:
            self._search_widget.clean()

        del self._name_value_model
        del self._name_value_delegate

        self._scrolling_frame = None
        self._tree_view = None
        del self._window

    def _search_updated(self, string):
        self._search_widget.update(string)
        self._name_value_model.filter_by_text(string)
        self._tree_view.scroll_here_y(0.0)

    def __on_key_pressed(self, key, mod, pressed):
        """Called when the user presses a key"""
        if not pressed:
            return
        if key == int(carb.input.KeyboardInput.ESCAPE):
            self._window.visible = False
        elif mod == 0 and key == int(carb.input.KeyboardInput.ENTER):
            self._execute(self._tree_view)
        elif mod == 0 and key == int(carb.input.KeyboardInput.DOWN):
            self._select_next(self._tree_view, self._name_value_model, after=True)
        elif mod == 0 and key == int(carb.input.KeyboardInput.UP):
            self._select_next(self._tree_view, self._name_value_model, after=False)

    def _select_next(self, treeview: ui.TreeView, model: ui.AbstractItemModel, after=True):
        full_list = model.get_item_children(None)
        selection = treeview.selection
        if not selection:
            treeview.selection = [full_list[0]]
        else:
            index = full_list.index(selection[0])
            index += 1 if after else -1
            if index < 0 or index >= len(full_list):
                return
            treeview.selection = [full_list[index]]

    def _select_index(self, treeview: ui.TreeView, model: ui.AbstractItemModel, index :int):
        full_list = model.get_item_children(None)
        selection = treeview.selection
        if index >= 0 and index < len(full_list):
            treeview.selection = [full_list[index]]

    def _get_treeview_height(self):
        item_count = len(self._name_value_model.get_item_children(None))
        treeview_height = ((min(10, item_count) * self._height+1.5) + 4)
        treeview_height_min = ((3 * self._height+1.5) + 4)

        try:
            appwindow = omni.appwindow.get_default_app_window()
            window_height = appwindow.get_height()
            window_height = (window_height / ui.Workspace.get_dpi_scale()) - 8

            if self._window.position_y + treeview_height > window_height:
                adj = ((self._window.position_y + treeview_height) - window_height) + self._search_size
                treeview_height -= adj
                if treeview_height < treeview_height_min:
                    treeview_height = treeview_height_min
        except:
            pass

        return treeview_height

    async def _update_list_model(self, new_list, percent, state):
        from omni.kit.material.library import UpdateState

        self._scrolling_frame.height = ui.Pixel(self._get_treeview_height())

        # select item now material list is now fully loaded
        if self._selection_on_loading_complete is not None and state == UpdateState.COMPLETE_LIST or state == UpdateState.UPDATE_COMPLETE:
            new_selection = self._selection_on_loading_complete
            full_list = self._tree_view.model.get_item_children(None)

            if new_selection == "None":
                await omni.kit.app.get_app().next_update_async()
                await omni.kit.app.get_app().next_update_async()
                self._tree_view.selection = [full_list[0]]
            else:
                for item in full_list:
                    if item.name_model.get_value_as_string() == new_selection:
                        self._tree_view.clear_selection()
                        await omni.kit.app.get_app().next_update_async()
                        await omni.kit.app.get_app().next_update_async()
                        self._tree_view.selection = [item]
                        break
            self._selection_on_loading_complete = None

    def _execute(self, treeview):
        selection = treeview.selection
        if selection:
            self._on_click_fn(selection[0].name_model, None)
            self._window.visible = False

    def set_selection_on_loading_complete(self, selection: str):
        """
        When loading material list is complete, select these materials in the list.
        """
        self._selection_on_loading_complete = selection

    def build_ui(self):
        """
        Build UI for list box widget.
        """
        if self._window and self._window.visible:  # pragma: no cover
            return                                 # pragma: no cover

        # Create and show the window
        self._window = ui.Window("MaterialPropertyPopupWindow",
                                  flags=ui.WINDOW_FLAGS_POPUP | ui.WINDOW_FLAGS_NO_TITLE_BAR | ui.WINDOW_FLAGS_NO_RESIZE | ui.WINDOW_FLAGS_NO_MOVE,
                                  auto_resize=True,
                                  padding_x=0,
                                  padding_y=0)
        self._window.frame.set_style(self._window_style)
        self._window.set_key_pressed_fn(self.__on_key_pressed)

        def tree_view_clicked(treeview):
            async def get_selection():
                await omni.kit.app.get_app().next_update_async()
                selection = treeview.selection
                if selection:
                    self._on_click_fn(selection[-1].name_model, None)
                    self._window.visible = False
            asyncio.ensure_future(get_selection())

        self._window.position_x = self.__parent.screen_position_x
        self._window.position_y = self.__parent.screen_position_y + 20

        with self._window.frame:
            with ui.VStack(width=0, height=0):
                self._search_widget.build_ui(self.__parent.computed_content_width + 40, self._search_size)

                self._name_value_model = MaterialListModel(self._search_widget.set_placeholder_text, self._update_list_model, self._filter_fn, self._get_materials_async_fn)
                self._name_value_delegate = MaterialListDelegate()

                self._scrolling_frame = ui.ScrollingFrame(
                    height=self._get_treeview_height(),
                    horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                    vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                )
                with self._scrolling_frame:
                    self._tree_view = ui.TreeView(
                        self._name_value_model,
                        delegate=self._name_value_delegate,
                        root_visible=False,
                        header_visible=False,
                        name="search_treeview",
                    )
                    self._select_index(self._tree_view, self._name_value_model, self._index)
                    self._tree_view.set_mouse_released_fn(lambda x, y, b, c, t=self._tree_view: tree_view_clicked(t))


    def destroy(self):
        """Destroy class and cleanup."""
        self.__parent = None
        self.__frame = None
        self._scrolling_frame = None
        self._tree_view = None
        del self._window
