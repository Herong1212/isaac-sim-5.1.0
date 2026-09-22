# pylint: disable=relative-beyond-top-level

__all__ = ["OptionsMenu"]
from typing import Optional, Callable
import carb
import omni.ui as ui
import omni.client
from omni.kit.notification_manager import post_notification, NotificationStatus
from omni.kit.hotkeys.core import get_hotkey_registry, KeyboardLayoutDelegate
from .warning_window import WarningWindow
from ..model.hotkeys_model import HotkeysModel


class LayoutMenu(ui.MenuItemCollection):
    def __init__(self, model: HotkeysModel):
        self.__model = model
        super().__init__("Keyboard Layouts")
        self.__build_layout_items()

    def __build_layout_items(self):
        current_layout = get_hotkey_registry().keyboard_layout

        with self:
            for layout in KeyboardLayoutDelegate.get_instances():
                name = layout.get_name()
                checked = current_layout == layout
                menu_item = ui.MenuItem(
                    name,
                    checkable=True,
                    checked=checked,
                )
                menu_item.set_triggered_fn(lambda m=menu_item, n=name: self.__switch_keyboard_layput(m, n))

    def __switch_keyboard_layput(self, menu_item: ui.MenuItem, name: str) -> None:
        get_hotkey_registry().switch_layout(name)
        menu_item.checked = True
        self.__model._item_changed(None)  # pylint: disable=protected-access


class OptionsMenu:
    def __init__(self, model: HotkeysModel, widget: ui.Widget):
        self.__model = model
        self.__widget = widget
        self.__context_menu: Optional[ui.Menu] = None
        self.__last_dir: Optional[str] = None
        self.__export_dialog = None
        self.__import_dialog = None

    def show(self):
        if self.__context_menu is None:
            self.__context_menu = ui.Menu(f"Hotkeys window Context Menu##{hash(self)}")
            with self.__context_menu:
                ui.MenuItem("Import Preset", triggered_fn=self.__import_preset)
                ui.MenuItem("Export Preset", triggered_fn=self.__export_preset)
                ui.MenuItem("Restore Defaults", triggered_fn=self.__restore_defaults)
                LayoutMenu(self.__model)

        # Right-bottom allign to the widget
        # 120 is the menu width
        position_x = self.__widget.screen_position_x + self.__widget.computed_width - 120
        position_y = self.__widget.screen_position_y + self.__widget.computed_height

        self.__context_menu.show_at(position_x, position_y)

    def __import_preset(self):
        try:
            import omni.kit.window.filepicker  # pylint: disable=redefined-outer-name

            self.__import_dialog = omni.kit.window.filepicker.FilePickerDialog(
                "Import",
                apply_button_label="import",
                current_directory=self.__last_dir,
                click_apply_handler=self.__on_import,
                item_filter_options=["Hotkey preset file (*.json)", "All Files (*)"],
                # item_filter_fn=self.__on_filter_item,
            )
        except ImportError:
            carb.log_info("Failed to import omni.kit.window.filepicker")

    def __export_preset(self):
        try:
            import omni.kit.window.filepicker  # pylint: disable=redefined-outer-name

            self.__export_dialog = omni.kit.window.filepicker.FilePickerDialog(
                "Export As",
                apply_button_label="Export",
                current_directory=self.__last_dir,
                click_apply_handler=self.__on_export,
                item_filter_options=["Hotkey preset file (*.json)", "All Files (*)"],
                # item_filter_fn=self.__on_filter_item,
            )
        except ImportError:
            carb.log_info("Failed to import omni.kit.window.filepicker")

    def __on_export(self, filename: str, path: str, callback: Callable[[str], None] = None):
        """Called when the user presses the Save button in the dialog"""
        if path:
            self.__last_dir = path
        if not filename:
            return

        # Get the file extension from the filter
        if not filename.lower().endswith(".json") and self.__export_dialog.current_filter_option < 1:
            filename += ".json"

        if path:
            path = omni.client.combine_urls(path + "/", filename)
        else:
            path = filename
        self.__export_dialog.hide()

        # check dest file
        (result, list_entry) = omni.client.stat(path)
        if result == omni.client.Result.OK and not list_entry.access & omni.client.AccessFlags.WRITE:
            post_notification(
                f"Hotkey preset '{path}' is readonly, save to another one!",
                hide_after_timeout=True,
                status=NotificationStatus.WARNING,
            )
            return

        self.__export(path)

    def __export(self, url: str) -> None:
        get_hotkey_registry().export_storage(url)

    def __on_import(self, filename: str, path: str, callback: Callable[[str], None] = None):
        """Called when the user presses the Save button in the dialog"""
        self.__last_dir = path
        if not filename:
            return

        # Get the file extension from the filter
        if not filename.lower().endswith(".json") and self.__import_dialog.current_filter_option < 1:
            filename += ".json"

        url = omni.client.combine_urls(path + "/", filename)
        self.__import_dialog.hide()

        # check dest file
        (result, _) = omni.client.stat(url)
        if result != omni.client.Result.OK:
            post_notification(
                f"Hotkey preset '{url}' does not exists!",
                hide_after_timeout=True,
                status=NotificationStatus.WARNING,
            )
            return

        self.__import(url)

    def __import(self, url: str) -> None:
        get_hotkey_registry().import_storage(url)
        self.__model._item_changed(None)  # pylint: disable=protected-access

    def __restore_defaults(self) -> None:

        def __restore():
            get_hotkey_registry().restore_defaults()
            self.__model._item_changed(None)  # pylint: disable=protected-access

        warn_window = WarningWindow(
            "Restore Defaults",
            messages=[
                "Are you sure you want to restore all hotkeys to their defaults?",
                "\n",
                "This will also remove any user added hotkeys.",
            ],
            buttons=[
                ("Yes", __restore),
                ("No", None)
            ]
        )

        warn_window.position_x = self.__widget.screen_position_x + self.__widget.computed_width - warn_window.width
        warn_window.position_y = self.__widget.screen_position_y + self.__widget.computed_height
