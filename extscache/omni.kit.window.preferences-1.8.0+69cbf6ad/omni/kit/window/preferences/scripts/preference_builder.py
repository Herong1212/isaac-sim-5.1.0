"""
Page building class.
"""
__all__ = ['create_setting_widget', 'create_setting_widget_combo', 'get_style', 'get_ui_style_name', 'PreferenceBuilder', 'PageItem', 'PageModel', 'PreferenceBuilderUI']

import asyncio
import os
import enum
from typing import List, Callable, Union
import carb
import omni.kit.menu.utils
import omni.ui as ui
from omni.ui import color as cl
from omni.kit.widget.settings import create_setting_widget, create_setting_widget_combo, SettingType
from omni.kit.widget.settings import get_style, get_ui_style_name

# Base class for a preference builder
class PreferenceBuilder:
    """
    Page building class
    """
    WINDOW_NAME = "Preferences"

    def __init__(self, title):
        self._title = title
        carb.settings.get_settings().set_default_string("/placeholder", "missing setting")

    def __del__(self):
        pass

    def show_page(self) ->bool:
        """
        Page is visible. Function can be overridden in subclasses to hide pages.

        Returns:
            True or False
        """
        return True

    def label(self, name: str, tooltip: str=None):
        """
        Create a UI widget label.

        Args:
            name: Name to be in label
            tooltip: The Tooltip string to be displayed when mouse hovers on the label

        Returns:
            :class:`ui.Widget` connected with the setting on the path specified.
        """
        if tooltip:
            ui.Label(name, word_wrap=True, name="title", width=ui.Percent(50), tooltip=tooltip)
        else:
            ui.Label(name, word_wrap=True, name="title", width=ui.Percent(50))

    def create_setting_widget_combo(self, name: str, setting_path: str, list: List[str],
        setting_is_index : bool | None = None,
        **kwargs) -> ui.Widget:
        """
        Creating a Combo Setting widget.


        This function creates a combo box that shows a provided list of names and it is connected with setting by path
        specified. Underlying setting values are used from values of `items` dict.

        Args:
            setting_path: Path to the setting to show and edit.
            items: Can be either :py:obj:`dict` or :py:obj:`list`. For :py:obj:`dict` keys are UI displayed names, values are
                actual values set into settings. If it is a :py:obj:`list` UI displayed names are equal to setting values.
            setting_is_index:
                None - Detect type from setting_path value. If the type is int, set to True.
                True - setting_path value is index into items list
                False - setting_path value is string in items list (default)
        """
        with ui.HStack(height=24):
            self.label(name)
            widget, model = create_setting_widget_combo(setting_path, list, setting_is_index=setting_is_index, **kwargs)
        return widget

    def create_setting_widget(
        self, label_name: str, setting_path: str, setting_type: SettingType, **kwargs
    ) -> ui.Widget:
        """
        Create a UI widget connected with a setting.

        If ``range_from`` >= ``range_to`` there is no limit. Undo/redo operations are also supported, because changing setting
        goes through the :mod:`omni.kit.commands` module, using :class:`.ChangeSettingCommand`.

        Args:
            setting_path: Path to the setting to show and edit.
            setting_type: Type of the setting to expect.
            range_from: Limit setting value lower bound.
            range_to: Limit setting value upper bound.

        Returns:
            :class:`ui.Widget` connected with the setting on the path specified.
        """
        if carb.settings.get_settings().get(setting_path) is None:
            return self.create_setting_widget(label_name, "/placeholder", SettingType.STRING)

        clicked_fn = None
        if "clicked_fn" in kwargs:
            clicked_fn = kwargs["clicked_fn"]
            del kwargs["clicked_fn"]

        # omni.kit.widget.settings.create_drag_or_slider won't use min/max unless hard_range is set to True
        if 'range_from' in kwargs and 'range_to' in kwargs:
            kwargs['hard_range'] = True

        vheight = 24
        vpadding = 0
        if setting_type == SettingType.FLOAT or setting_type == SettingType.INT or setting_type == SettingType.STRING:
            vheight = 20
            vpadding = 3

        with ui.HStack(height=vheight):
            tooltip = kwargs.pop('tooltip', '')
            self.label(label_name, tooltip)
            widget, model = create_setting_widget(setting_path, setting_type, **kwargs)
            if clicked_fn:
                from functools import partial

                ui.Button(
                    style={"image_url": "resources/icons/folder.png"}, clicked_fn=partial(clicked_fn, widget), width=24
                )

        ui.Spacer(height=vpadding)

        return widget

    def add_frame(self, name: str) -> ui.CollapsableFrame:
        """
        Create a UI collapsable frame.

        Args:
            name: Name to be in frame

        Returns:
            :class:`ui.Widget` connected with the setting on the path specified.
        """
        return ui.CollapsableFrame(title=name, identifier=f"preferences_builder_{name}")

    def spacer(self) -> ui.Spacer:
        """
        Create a UI spacer.

        Args:
            None

        Returns:
            :class:`ui.Widget` connected with the setting on the path specified.
        """
        return ui.Spacer(height=10)

    def get_title(self) -> str:
        """
        Gets the page title

        Args:
            None

        Returns:
            str name of the page
        """
        return self._title

    def cleanup_slashes(self, path: str, is_directory: bool = False) -> str:
        """
        Makes path/slashes uniform

        Args:
            path: path
            is_directory is path a directory, so final slash can be added

        Returns:
            path
        """
        path = os.path.normpath(path)
        if is_directory:
            if path[-1] != "/":
                path += "/"
        return path.replace("\\", "/")


class PageItem(ui.AbstractItem):
    """Single item of the model"""

    def __init__(self, pages):
        super().__init__()
        self.name = pages[0].get_title()
        self.name_model = ui.SimpleStringModel(self.name)
        self.pages = pages


class PageModel(ui.AbstractItemModel):
    def __init__(self, page_list: List[str]):
        super().__init__()
        self._page_list = page_list.copy()
        self._pages = []
        for key in self._page_list:
            page = self._page_list[key]
            self._pages.append(PageItem(page))
        self._item_changed(None)

    def get_item_children(self, item: PageItem) -> List[PageItem]:
        if item is not None:
            # Since we are doing a flat list, we return the children of root only.
            # If it's not root we return.
            return []

        show_pages = []
        for page in self._pages:
            if any(p.show_page() for p in page.pages):
                show_pages.append(page)

        return show_pages

    def get_item_value_model_count(self, item: PageItem) -> int:
        """The number of columns"""
        return 1

    def get_item_value_model(self, item: PageItem, column_id: int) -> ui.SimpleStringModel:
        if item and isinstance(item, PageItem):
            return item.name_model


class PreferenceBuilderUI:
    """
    Preferences "page" display functions.

    """
    def __init__(self, visibility_changed_fn: Callable):
        self._visibility_changed_fn = visibility_changed_fn
        self._active_page = ""
        self._treeview = None

    def destroy(self): # pragma: no cover
        """
        Destroy class and cleanup.
        """
        ui.Workspace.set_show_window_fn(PreferenceBuilder.WINDOW_NAME, None)
        self._page_list = None
        self._pages_model = None
        self._visibility_changed_fn = None
        self._treeview = None
        del self._window

    def __del__(self): # pragma: no cover
        ui.Workspace.set_show_window_fn(PreferenceBuilder.WINDOW_NAME, None)
        pass

    def update_page_list(self, page_list: List) -> None:
        """
        Updates page list

        Args:
            page_list: list of pages

        Returns:
            None
        """
        self._page_list = {}
        self._page_header = []
        for page in page_list:
            if isinstance(page, PreferenceBuilder):
                if not page._title:
                    self._page_header.append(page)
                elif not page._title in self._page_list:
                    self._page_list[page.get_title()] = [page]
                else:
                    self._page_list[page.get_title()].append(page)

    def create_window(self):
        """
        Create omni.ui.window

        Args:
            None

        Returns:
            None
        """
        def set_window_state(v):
            self._show_window(None, v)
            if v:
                self.rebuild_pages()

        self._treeview = None
        self._window = None
        ui.Workspace.set_show_window_fn(PreferenceBuilder.WINDOW_NAME, set_window_state)

    def _show_window(self, menu, value):
        if value:
            self._window = ui.Window(PreferenceBuilder.WINDOW_NAME, width=1000, height=600, dockPreference=ui.DockPreference.LEFT_BOTTOM)
            self._window.set_visibility_changed_fn(self._on_visibility_changed_fn)
            self._window.frame.set_style(get_style())
            self._window.deferred_dock_in("Content")
        elif self._window:
            self._treeview = None
            self._window.destroy()
            self._window = None

    def rebuild_pages(self) -> None:
        """
        Rebuilds window pages using current page list

        Args:
            None

        Returns:
            None
        """
        self._pages_model = PageModel(self._page_list)
        full_list = self._pages_model.get_item_children(None)
        if not full_list or not self._window:
            return
        elif not self._active_page in self._page_list:
            self._active_page = next(iter(self._page_list))

        def treeview_clicked(treeview):
            async def get_selection():
                await omni.kit.app.get_app().next_update_async()
                if treeview.selection:
                    selection = treeview.selection[0]
                    self.set_active_page(selection.name)

            asyncio.ensure_future(get_selection())

        with self._window.frame:
            prefs_style = {"ScrollingFrame::header": {"background_color": 0xFF444444},
                           "ScrollingFrame::header:hovered": {"background_color": 0xFF444444},
                           "ScrollingFrame::header:pressed": {"background_color": 0xFF444444},
                           "Button::global": {"color": cl("#34C7FF"), "margin": 0, "margin_width": 0, "padding": 5},
                           "Button.Label::global": {"color": cl("#34C7FF")},
                           "Button::global:hovered": {"background_color": 0xFF545454},
                           "Button::global:pressed": {"background_color": 0xFF555555},
                           }

            with ui.VStack(style=prefs_style, name="header"):
                if self._page_header:
                    with ui.HStack(width=0, height=10):
                        for page in self._page_header:
                            page.build()
                    ui.Spacer(height=3)

                with ui.HStack():
                    with ui.ScrollingFrame(
                        width=175, horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF
                    ):
                        if get_ui_style_name() == "NvidiaLight":
                            FIELD_BACKGROUND = 0xFF545454
                            FIELD_TEXT_COLOR = 0xFFD6D6D6
                        else:
                            FIELD_BACKGROUND = 0xFF23211F
                            FIELD_TEXT_COLOR = 0xFFD5D5D5

                        self._treeview = ui.TreeView(
                            self._pages_model,
                            root_visible=False,
                            header_visible=False,
                            style={
                                "TreeView.Item": {"margin": 4},
                                "margin_width": 0.5,
                                "margin_height": 0.5,
                                "background_color": FIELD_BACKGROUND,
                                "color": FIELD_TEXT_COLOR,
                            },
                        )
                        if not self._treeview.selection and len(full_list) > 0:
                            for page in full_list:
                                if page.name == self._active_page:
                                    self._treeview.selection = [page]
                                    break
                        selection = self._treeview.selection

                        self._treeview.set_mouse_released_fn(lambda x, y, b, c, tv=self._treeview: treeview_clicked(tv))

                    with ui.VStack():
                        ui.Spacer(height=7)
                        self._page_frame = ui.ScrollingFrame(
                            horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED
                        )
                    if selection:
                        self._build_page(selection[0].pages)

    def set_active_page(self, page_index: Union[int, str]) -> None:
        """
        Set the given page index as the active one.

        Args:
            page_index: Index of page of the page list to set as the active one.

        Returns:
            None
        """
        if isinstance(page_index, str):
            self._active_page = page_index
        else:
            for index, key in enumerate(self._page_list):
                if index == page_index:
                    self._active_page = self._page_list[key].get_title()
                    break

        # Build and display the list of preference widgets on the right-hand column of the panel:
        async def rebuild():
            await omni.kit.app.get_app().next_update_async()
            self._build_page(self._page_list[self._active_page])

        asyncio.ensure_future(rebuild())

        # Select the title of the page on the left-hand column of the panel, acting as navigation tabs between the
        # Preference pages:
        if self._pages_model and self._treeview:
            for page in self._pages_model.get_item_children(None):
                if page.name == self._active_page:
                    self._treeview.selection = [page]
                    break

    def select_page(self, page: PreferenceBuilder) -> bool:
        """
        If found, display the given Preference page and select its title in the TreeView.

        Args:
            page: One of the page from the list of pages.

        Returns:
            bool: A flag indicating if the given page was successfully selected.
        """
        for key in self._page_list:
            items = self._page_list[key]
            for item in items:
                if item == page:
                    self.set_active_page(item.get_title())
                    return True
        return False

    def _build_page(self, pages: List[PreferenceBuilder]) -> None:
        with self._page_frame:
            with ui.VStack():
                for page in pages:
                    if page.show_page():
                        page.build()
                        if len(pages) > 1:
                            ui.Spacer(height=7)

    def show_window(self) -> None:
        """
        Shows window

        Args:
            None

        Returns:
            None
        """
        if not self._window:
            self._show_window(None, True)
            self.rebuild_pages()

    def hide_window(self) -> None:
        """
        Hides window

        Args:
            None

        Returns:
            None
        """
        if self._window:
            self._show_window(None, False)

    def _on_visibility_changed_fn(self, visible) -> None:
        self._visibility_changed_fn(visible)
        omni.kit.menu.utils.refresh_menu_items("Edit")
