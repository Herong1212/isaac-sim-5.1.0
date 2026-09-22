"""
Core menu class. Used by omni.kit.menu.utils and omni.kit.context_menu to build menus.
"""

import collections
import copy
from pathlib import Path

import carb
import omni.kit.app
from omni import ui

__all__ = ["has_delegate_func", "DictReadOnly", "IconMenuBaseDelegate", "uiMenu", "uiMenuItem", "MenuEventType"]


class MenuEventType:
    """Enum for menu activation events

    This class represents different types of events that can trigger the activation of a menu.
    """

    ACTIVATE = 0
    """Menu was activated"""


def has_delegate_func(delegate, func_name):
    """Checks if delegate class has func_name function.

    Args:
        delegate (object): The delegate object to check.
        func_name (str): The name of the function to look for.

    Returns:
        bool: True if the delegate has a callable function with the given name, otherwise False.
    """
    return bool(delegate and hasattr(delegate, func_name) and callable(getattr(delegate, func_name)))


class DictReadOnly(collections.abc.Mapping):
    """Read-only dictionary. Prevents accidental write-backs to dictionary.

    Args:
        data (dict): The dictionary to be wrapped in a read-only interface.
    """

    def __readonly__(self, *args, **kwargs):
        raise RuntimeError("'DictReadOnly' object is read only")

    def __init__(self, data):
        """Initializes the DictReadOnly instance."""
        self.__data = data

    def __getitem__(self, key):
        return self.__data[key]

    def __len__(self):
        return len(self.__data)

    def __iter__(self):
        return iter(self.__data)

    def __or__(self, other):
        # for compatibility with python 3.7 don't use "|"
        return self.merge_dict(other)

    def copy(self):
        """Creates a shallow copy of the read-only dictionary.

        Returns:
            DictReadOnly: A new DictReadOnly instance with copied data.
        """
        return DictReadOnly(copy.copy(self.__data))

    def merge_dict(self, other):
        """Merges another dictionary into the current read-only dictionary.

        Args:
            other (dict): The dictionary to merge with the current dictionary.

        Returns:
            DictReadOnly: A new DictReadOnly instance with merged data.
        """
        new_dict = dict(copy.copy(self.__data))
        new_dict.update(other)
        return DictReadOnly(new_dict)

    def __str__(self) -> str:
        return str(self.__data)

    __ior__ = __readonly__


class uiMenu(ui.Menu):  # noqa # pylint: disable=invalid-class-name
    """ui.Menu subclass. Has glyph, menu_checkable, menu_hotkey_text, submenu and parent_menu properties

    Args:
        args: Arguments for the ui.Menu constructor.

    Keyword Args:
        glyph: The glyph associated with the menu.
        menu_checkable: If the menu is checkable.
        menu_hotkey_text: The hotkey text for the menu.
        submenu: If the menu is a submenu.
        parent_menu: The parent menu.
    """

    def __init__(self, *args, **kwargs):
        """Initializes the uiMenu instance."""
        self.glyph = None
        self.submenu = False
        self.menu_hotkey_text = None
        self.menu_checkable = False
        self.parent_menu = None
        self.radio_group = None

        if "glyph" in kwargs:
            self.glyph = kwargs.pop("glyph", None)

        if "menu_checkable" in kwargs:
            self.menu_checkable = kwargs.pop("menu_checkable", None)

        if "menu_hotkey_text" in kwargs:
            self.menu_hotkey_text = kwargs.pop("menu_hotkey_text", None)

        if "submenu" in kwargs:
            self.submenu = kwargs.pop("submenu", None)

        if "parent_menu" in kwargs:
            self.parent_menu = kwargs.pop("parent_menu", None)

        super().__init__(*args, **kwargs, menu_compatibility=False)


class uiMenuItem(ui.MenuItem):  # noqa # pylint: disable=invalid-class-name
    """ui.MenuItem subclass. Has glyph, menu_checkable, menu_hotkey_text, and parent_menu properties

    Args:
        args: Positional arguments passed to the parent class.

    Keyword Args:
        glyph: Custom glyph for the menu item.
        menu_checkable: Indicates if the menu item is checkable.
        menu_hotkey_text: Hotkey text for the menu item.
        parent_menu: Reference to the parent menu.
        radio_group: Radio group to which this menu item belongs.
    """

    def __init__(self, *args, **kwargs):
        """Initializes a new instance of the uiMenuItem class."""
        self.glyph = None
        self.submenu = False
        self.parent_menu = None
        self.menu_hotkey_text = None
        self.menu_checkable = False
        self.radio_group = None

        if "glyph" in kwargs:
            self.glyph = kwargs.pop("glyph", None)

        if "menu_checkable" in kwargs:
            self.menu_checkable = kwargs.pop("menu_checkable", None)

        if "menu_hotkey_text" in kwargs:
            self.menu_hotkey_text = kwargs.pop("menu_hotkey_text", None)

        if "parent_menu" in kwargs:
            self.parent_menu = kwargs.pop("parent_menu", None)

        if "radio_group" in kwargs:
            self.radio_group = kwargs.pop("radio_group", None)

        super().__init__(*args, **kwargs, menu_compatibility=False)


class IconMenuBaseDelegate(ui.MenuDelegate):
    """Icon Menu Delegate class.

    Keyword Args:
        background_color (int): Background color of the menu.
        background_selected_color (int): Background color when an item is selected.
        icon_size (float): Size of the icons.
        text_size (float): Size of the text.
        tick_size (float): Size of the tick marks.
        separator_size (list): Size of the separators.
        tick_spacing (list): Spacing of the tick marks.
        margin_size (list): Margin size.
        margin_size_posttick (list): Margin size after the tick mark.
        post_label_spaces (float): Space after the label.
        root_spacing (float): Spacing at the root level.
        submenu_pre_spacing (float): Pre-spacing for submenu items.
        submenu_spacing (float): Spacing for submenu items.
        submenu_icon_size (float): Size of the submenu icons.
        item_spacing (list): Spacing for menu items.
        icon_spacing (list): Spacing for icons.
        hotkey_spacing (list): Spacing for hotkeys.
        color_label_enabled (int): Color of the label when enabled.
        color_label_disabled (int): Color of the label when disabled.
        color_tick_enabled (int): Color of the tick mark when enabled.
        color_tick_disabled (int): Color of the tick mark when disabled.
        color_separator (int): Color of the separators.
        color_icon_enabled (int): Color of the icon when enabled.
        color_icon_disabled (int): Color of the icon when disabled.
        menu_title_text_color (int): Color of the menu title text.
        menu_title_color (int): Color of the menu title.
        menu_title_line_color (int): Color of the menu title line.
        menu_title_text_height (float): Height of the menu title text.
        menu_title_text_spacer (list): Spacer size for the menu title text.
        menu_title_close_icon_size (float): Size of the close icon in the menu title.
        menu_title_close_color (int): Color of the close icon in the menu title.
        menu_headfoot_spacing (float): Menu header & footer spacing.
        show_menu_titles (bool): Whether to show menu titles.
        indent_all_ticks (bool): Whether to indent all tick marks.
    """

    def __init__(self, **kwargs):
        """Initializes the IconMenuBaseDelegate."""
        super().__init__(**kwargs)

        # doc compiler breaks when `omni.kit.app.get_app()` is called
        try:
            extension_folder_path = Path(
                omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
            )
            self.ICON_PATH = extension_folder_path.joinpath("data/icons")
        except RuntimeError:
            self.ICON_PATH = Path()

        self.BACKGROUND_COLOR = 0xFF3D3B38
        self.BACKGROUND_SELECTED_COLOR = 0xFF333333
        self.ICON_SIZE = 14
        self.TEXT_SIZE = 14
        self.TICK_SIZE = 14
        self.SEPARATOR_SIZE = [0, 6]
        self.TICK_SPACING = [3, 6]
        self.MARGIN_SIZE = [4, 4]
        self.MARGIN_SIZE_POSTTICK = [4, 4]
        self.POST_LABEL_SPACES = 2
        self.ROOT_SPACING = 1
        self.SUBMENU_PRE_SPACING = 5
        self.SUBMENU_SPACING = 4
        self.SUBMENU_ICON_SIZE = 10
        self.ITEM_SPACING = 4
        self.ICON_SPACING = [4, 4]
        self.HOTKEY_SPACING = [8, 108]
        self.COLOR_LABEL_ENABLED = 0xFFCCCCCC
        self.COLOR_LABEL_DISABLED = 0xFF6F6F6F
        self.COLOR_TICK_ENABLED = 0xFFCCCCCC
        self.COLOR_TICK_DISABLED = 0xFF4F4F4F
        self.COLOR_SEPARATOR = 0xFF6F6F6F
        self.COLOR_ICON_ENABLED = 0xFFCCCCCC
        self.COLOR_ICON_DISABLED = 0xFF6F6F6F
        self.MENU_TITLE_TEXT_COLOR = 0xFFCCCCCC
        self.MENU_TITLE_COLOR = 0xFF2A2825
        self.MENU_TITLE_LINE_COLOR = 0xFF373635
        self.MENU_TITLE_TEXT_HEIGHT = 32
        self.MENU_TITLE_TEXT_SPACER = [8, 2]
        self.MENU_TITLE_CLOSE_ICON_SIZE = 18
        self.MENU_TITLE_CLOSE_COLOR = 0xFFC6C6C6
        self.MENU_HEADFOOT_SPACING = [0, 0]
        self.show_menu_titles = False
        self.indent_all_ticks = True

        self.__update_style()

    def __update_style(self):
        self.MENU_STYLE = DictReadOnly(
            {
                "Menu.Window": {"background_color": self.BACKGROUND_COLOR},
                "Menu.Title": {"background_color": self.MENU_TITLE_COLOR},
                "Menu.Title.Line": {"color": self.MENU_TITLE_LINE_COLOR},
                "Menu.Title.Text": {"color": self.MENU_TITLE_TEXT_COLOR},
                "Image::Icon": {"margin_width": 0, "margin_height": 0, "color": self.COLOR_ICON_ENABLED},
                "Image::Icon:disabled": {"margin_width": 0, "margin_height": 0, "color": self.COLOR_ICON_DISABLED},
                "Label::Enabled": {
                    "margin_width": self.MARGIN_SIZE[0],
                    "margin_height": self.MARGIN_SIZE[1],
                    "color": self.COLOR_LABEL_ENABLED,
                },
                "Label::Disabled": {
                    "margin_width": self.MARGIN_SIZE[0],
                    "margin_height": self.MARGIN_SIZE[1],
                    "color": self.COLOR_LABEL_DISABLED,
                },
                "Label::Enabled_PT": {
                    "margin_width": self.MARGIN_SIZE_POSTTICK[0],
                    "margin_height": self.MARGIN_SIZE_POSTTICK[1],
                    "color": self.COLOR_LABEL_ENABLED,
                },
                "Label::Disabled_PT": {
                    "margin_width": self.MARGIN_SIZE_POSTTICK[0],
                    "margin_height": self.MARGIN_SIZE_POSTTICK[1],
                    "color": self.COLOR_LABEL_DISABLED,
                },
                "Image::SubMenu": {
                    "image_url": f"{self.ICON_PATH}/subdir.svg",
                    "margin_width": 0,
                    "margin_height": 0,
                    "color": self.COLOR_LABEL_ENABLED,
                },
                "Image::TickEnabled": {
                    "image_url": f"{self.ICON_PATH}/checked.svg",
                    "margin_width": 0,
                    "margin_height": 0,
                    "color": self.COLOR_TICK_ENABLED,
                },
                "Image::TickDisabled": {
                    "image_url": f"{self.ICON_PATH}/checked.svg",
                    "margin_width": 0,
                    "margin_height": 0,
                    "color": self.COLOR_TICK_DISABLED,
                },
                "Image::RadioEnabled": {
                    "image_url": f"{self.ICON_PATH}/radiomark.svg",
                    "margin_width": 0,
                    "margin_height": 0,
                    "color": self.COLOR_TICK_ENABLED,
                },
                "Image::RadioDisabled": {
                    "image_url": f"{self.ICON_PATH}/radiomark.svg",
                    "margin_width": 0,
                    "margin_height": 0,
                    "color": self.COLOR_TICK_DISABLED,
                },
                "Menu.Separator": {"color": self.COLOR_SEPARATOR, "margin_width": self.SEPARATOR_SIZE[-1]},
            }
        )

    def get_style(self):
        """Get current style

        Returns:
            DictReadOnly: The current menu style.
        """
        return self.MENU_STYLE

    def load_settings(self, extension):
        """Loads settings from /exts/{extension}/* which control how menus are built.

        Args:
            extension (str): Extension identifier for settings.
        """
        try:
            settings = carb.settings.get_settings()
        except RuntimeError:
            carb.log_warn("load_settings: failed to get_settings")
            return

        def read_setting(setting_path, var):
            value = settings.get(setting_path)
            if value is not None:
                setattr(self, var, value)

        read_setting(f"exts/{extension}/background_color", "BACKGROUND_COLOR")
        read_setting(f"exts/{extension}/background_selected_color", "BACKGROUND_SELECTED_COLOR")
        read_setting(f"exts/{extension}/icon_size", "ICON_SIZE")
        read_setting(f"exts/{extension}/text_size", "TEXT_SIZE")
        read_setting(f"exts/{extension}/tick_size", "TICK_SIZE")
        read_setting(f"exts/{extension}/separator_size", "SEPARATOR_SIZE")
        read_setting(f"exts/{extension}/tick_spacing", "TICK_SPACING")
        read_setting(f"exts/{extension}/margin_size", "MARGIN_SIZE")
        read_setting(f"exts/{extension}/margin_size_posttick", "MARGIN_SIZE_POSTTICK")
        read_setting(f"exts/{extension}/post_label_spaces", "POST_LABEL_SPACES")
        read_setting(f"exts/{extension}/root_spacing", "ROOT_SPACING")
        read_setting(f"exts/{extension}/submenu_pre_spacing", "SUBMENU_PRE_SPACING")
        read_setting(f"exts/{extension}/submenu_spacing", "SUBMENU_SPACING")
        read_setting(f"exts/{extension}/submenu_icon_size", "SUBMENU_ICON_SIZE")
        read_setting(f"exts/{extension}/item_spacing", "ITEM_SPACING")
        read_setting(f"exts/{extension}/icon_spacing", "ICON_SPACING")
        read_setting(f"exts/{extension}/hotkey_spacing", "HOTKEY_SPACING")
        read_setting(f"exts/{extension}/color_label_enabled", "COLOR_LABEL_ENABLED")
        read_setting(f"exts/{extension}/color_label_disabled", "COLOR_LABEL_DISABLED")
        read_setting(f"exts/{extension}/color_tick_enabled", "COLOR_TICK_ENABLED")
        read_setting(f"exts/{extension}/color_tick_disabled", "COLOR_TICK_DISABLED")
        read_setting(f"exts/{extension}/color_separator", "COLOR_SEPARATOR")
        read_setting(f"exts/{extension}/color_icon_enabled", "COLOR_ICON_ENABLED")
        read_setting(f"exts/{extension}/color_icon_disabled", "COLOR_ICON_DISABLED")
        read_setting(f"exts/{extension}/menu_title_text_color", "MENU_TITLE_TEXT_COLOR")
        read_setting(f"exts/{extension}/menu_title_color", "MENU_TITLE_COLOR")
        read_setting(f"exts/{extension}/menu_title_line_color", "MENU_TITLE_LINE_COLOR")
        read_setting(f"exts/{extension}/menu_title_text_height", "MENU_TITLE_TEXT_HEIGHT")
        read_setting(f"exts/{extension}/menu_title_text_spacer", "MENU_TITLE_TEXT_SPACER")
        read_setting(f"exts/{extension}/menu_title_close_icon_size", "MENU_TITLE_CLOSE_ICON_SIZE")
        read_setting(f"exts/{extension}/menu_title_close_color", "MENU_TITLE_CLOSE_COLOR")
        read_setting(f"exts/{extension}/menu_headfoot_spacing", "MENU_HEADFOOT_SPACING")

        # bool settings
        read_setting(f"exts/{extension}/show_menu_titles", "show_menu_titles")
        read_setting(f"exts/{extension}/indent_all_ticks", "indent_all_ticks")

        # settings have updated, recreate style
        self.__update_style()

    def build_title(self, item):
        """Builds the header for a menu item.

        Args:
            item (ui.MenuItem): The menu item for which to build the header.

        Returns:
            None
        """
        with ui.VStack():
            if not self.show_menu_titles:
                super().build_title(item)
            else:
                self._build_item_title(item)

            # header
            ui.Spacer(height=self.MENU_HEADFOOT_SPACING[0])

    def build_status(self, item):
        """Builds the footer for a menu item.

        Args:
            item (ui.MenuItem): The menu item for which to build the footer.

        Returns:
            None
        """
        with ui.VStack():
            super().build_status(item)
            # footer
            ui.Spacer(height=self.MENU_HEADFOOT_SPACING[1])

    # overridable functions
    # get style
    def _build_item_get_style(self, item: ui.Menu) -> dict:
        style = self.get_style()
        if item.delegate and hasattr(item.delegate, "get_style"):
            style = style | item.delegate.get_style()
        return style

    # build title
    def _build_item_title(self, item):
        with ui.ZStack():
            ui.Rectangle(style={"background_color": self.MENU_TITLE_COLOR, "border_radius": 4.0})
            with ui.HStack(height=self.MENU_TITLE_TEXT_HEIGHT):
                ui.Spacer(width=self.MENU_TITLE_TEXT_SPACER[0])
                with ui.ZStack():
                    with ui.HStack():  # this is attached menu
                        ui.Spacer(width=self.MENU_TITLE_CLOSE_ICON_SIZE)
                        ui.Line(style={"Line": {"color": self.MENU_TITLE_LINE_COLOR}, "Line:checked": {"color": 0x0}})

                    with ui.HStack():  # this is detached menu
                        ui.Label(
                            item.text,
                            style={"Label": {"color": 0x0}, "Label:checked": {"color": self.MENU_TITLE_TEXT_COLOR}},
                            width=0,
                        )
                        ui.Spacer(width=self.MENU_TITLE_TEXT_SPACER[0])
                        ui.Line(style={"Line": {"color": 0x0}, "Line:checked": {"color": self.MENU_TITLE_LINE_COLOR}})

                # close button
                ui.Spacer(width=self.MENU_TITLE_TEXT_SPACER[1])
                with ui.VStack(width=self.MENU_TITLE_CLOSE_ICON_SIZE):
                    ui.Spacer()
                    ui.Image(
                        mouse_pressed_fn=lambda x, y, button, modifier: item.hide(),
                        width=self.MENU_TITLE_CLOSE_ICON_SIZE,
                        height=self.MENU_TITLE_CLOSE_ICON_SIZE,
                        style={
                            "image_url": f"{self.ICON_PATH}/close.svg",
                            "Image": {"background_color": 0x0, "color": 0x0},
                            "Image:checked": {
                                "background_color": self.MENU_TITLE_COLOR,
                                "color": self.MENU_TITLE_CLOSE_COLOR,
                            },
                        },
                    )
                    ui.Spacer()
                ui.Spacer(width=self.MENU_TITLE_TEXT_SPACER[0])

    # build header
    def _build_item_header(self, item: ui.Menu):
        if not (isinstance(item, uiMenu) and not item.submenu):
            ui.Spacer(width=self.ITEM_SPACING)
        else:
            ui.Spacer(width=self.ROOT_SPACING)

    # build tick
    def _build_item_tick(self, item: ui.Menu):
        if self.indent_all_ticks and item.menu_checkable:
            if item.checkable:
                style_name = "TickEnabled" if item.checked else "TickDisabled"
                if item.radio_group:
                    style_name = "RadioEnabled" if item.checked else "RadioDisabled"
                ui.Spacer(width=self.TICK_SPACING[0])
                ui.Image("", width=self.TICK_SIZE, name=style_name)
                ui.Spacer(width=self.TICK_SPACING[1])
            else:
                ui.Spacer(width=self.TICK_SIZE)
                ui.Spacer(width=self.TICK_SPACING[1])
        elif item.checkable:
            style_name = "TickEnabled" if item.checked else "TickDisabled"
            if item.radio_group:
                style_name = "RadioEnabled" if item.checked else "RadioDisabled"
            ui.Spacer(width=self.TICK_SPACING[0])
            ui.Image("", width=self.TICK_SIZE, name=style_name)
            ui.Spacer(width=self.TICK_SPACING[1])

    # build glyph
    def _build_item_glyph(self, item: ui.Menu):
        if item.glyph:
            glyph_path = (
                item.glyph
                if "/" in item.glyph.replace("\\", "/")
                else carb.tokens.get_tokens_interface().resolve("${glyphs}/" + item.glyph)
            )
            ui.Spacer(width=self.ICON_SPACING[0])
            with ui.VStack(width=self.ICON_SIZE):
                ui.Spacer()
                ui.Image(glyph_path, width=self.ICON_SIZE, height=self.ICON_SIZE, name="Icon")
                ui.Spacer()
            ui.Spacer(width=self.ICON_SPACING[1])

    # build label
    def _build_item_label(self, item: ui.Menu):
        if isinstance(item, uiMenu):
            if item.submenu:
                ui.Label(f"{item.text}", height=self.ICON_SIZE, name="Enabled" if item.enabled else "Disabled")
            else:
                ui.Label(f"{item.text}", height=self.ICON_SIZE, name="Enabled_PT" if item.enabled else "Disabled_PT")
            ui.Spacer(width=self.ROOT_SPACING)
        else:
            max_length = 0
            if has_delegate_func(self, "get_elided_length"):
                max_length = self.get_elided_length(item.parent_menu.name if item.parent_menu else None)

            label_text = item.text
            label_length = len(label_text)
            if max_length and label_length > max_length:
                # make text elided
                crop_length = int(max_length / 2)
                label_text = label_text[0:crop_length] + "..." + label_text[label_length - crop_length :]

            if item.checkable:
                ui.Label(
                    f"{label_text}{' '*self.POST_LABEL_SPACES}",
                    height=self.TEXT_SIZE,
                    name="Enabled_PT" if item.enabled else "Disabled_PT",
                )
            else:
                ui.Label(
                    f"{label_text}{' '*self.POST_LABEL_SPACES}",
                    height=self.TEXT_SIZE,
                    name="Enabled" if item.enabled else "Disabled",
                )

    # build hotkey text
    def _build_item_hotkey(self, item: ui.Menu):
        if item.hotkey_text:
            ui.Spacer(width=self.HOTKEY_SPACING[0])
            ui.Label(item.hotkey_text.title(), height=self.ICON_SIZE, name="Disabled", width=100)
        elif item.menu_hotkey_text:
            ui.Spacer(width=self.HOTKEY_SPACING[1])

    # build subdir marker
    def _build_item_subdir(self, item: ui.Menu):
        if item.submenu:
            ui.Spacer(width=self.SUBMENU_PRE_SPACING)
            ui.Image("", width=self.SUBMENU_ICON_SIZE, name="SubMenu")
            ui.Spacer(width=self.SUBMENU_SPACING)

    def build_item(self, item: ui.Widget):
        """Build menu omni.ui for item, only uiMenu or uiMenuItem are handled by this function, anything else is handled by the ui.MenuDelegate base-class. Can be overridden on subclass along with _build_item_header, _build_item_tick, _build_item_glyph, _build_item_label, _build_item_hotkey, _build_item_subdir.

        Args:
            item (ui.Widget): The menu item to build.

        Returns:
            None
        """
        if isinstance(item, ui.Separator):
            with ui.HStack(height=self.SEPARATOR_SIZE[0], style=self.MENU_STYLE):
                # when SEPARATOR_SIZE == 2 then SEPARATOR_SIZE[1] is pre-spacing & post text spacing
                # when SEPARATOR_SIZE == 3 then SEPARATOR_SIZE[1] is pre-spacing & SEPARATOR_SIZE[2] is post text spacing
                if len(self.SEPARATOR_SIZE) == 3:
                    ui.Spacer(width=self.SEPARATOR_SIZE[1])
                return super().build_item(item)
        elif not isinstance(item, uiMenu) and not isinstance(item, uiMenuItem):
            carb.log_warn(f"build_item: bad menu item {item.text} - Should be uiMenu/uiMenuItem")
            return super().build_item(item)

        with ui.VStack():
            with ui.HStack(height=0, style=self._build_item_get_style(item)):
                self._build_item_header(item)
                self._build_item_tick(item)
                self._build_item_glyph(item)
                self._build_item_label(item)
                self._build_item_hotkey(item)
                self._build_item_subdir(item)

        return None
