__all__ = ["HelpExtension"]

import webbrowser

import carb
import carb.input
import carb.settings
import omni.kit.app
import omni.kit.menu.utils
from carb.input import KeyboardInput as Key
from omni.kit.menu.utils import MenuItemDescription


class HelpExtension:
    """A class to manage help menu actions and items.

    This class is responsible for registering and managing help-related
    menu items and their associated actions within the application.
    It dynamically configures menu items based on application settings
    and provides functionalities to open various documentation URLs.

    """

    def __init__(self):
        """Initializes the HelpExtension and sets up help menu items."""

        def get_discover_kit_sdk_path(settings):
            if omni.kit.app.get_app().is_app_external():
                return settings.get("/exts/omni.kit.menu.common/external_kit_sdk_url")
            return settings.get("/exts/omni.kit.menu.common/internal_kit_sdk_url")

        def get_manual_url_path(settings):
            if omni.kit.app.get_app().is_app_external():
                return settings.get("/exts/omni.kit.menu.common/external_kit_manual_url")
            return settings.get("/exts/omni.kit.menu.common/internal_kit_manual_url")

        def get_discover_reference_guide_path(settings):
            if omni.kit.app.get_app().is_app_external():
                return settings.get("/exts/omni.kit.menu.common/external_reference_guide_url")
            return settings.get("/exts/omni.kit.menu.common/internal_reference_guide_url")

        settings = carb.settings.get_settings()
        discover_reference_guide_path = get_discover_reference_guide_path(settings)
        discover_kit_sdk_path = get_discover_kit_sdk_path(settings)
        manual_url_path = get_manual_url_path(settings)

        self._register_actions(
            "omni.kit.menu.common", discover_reference_guide_path, discover_kit_sdk_path, manual_url_path
        )

        reference_guide_name = settings.get("/exts/omni.kit.menu.common/reference_guide_name")
        kit_sdk_name = settings.get("/exts/omni.kit.menu.common/kit_sdk_name")
        kit_manual_name = settings.get("/exts/omni.kit.menu.common/kit_manual_name")

        self._help_menu = []

        if reference_guide_name and discover_reference_guide_path:
            self._help_menu.append(
                MenuItemDescription(
                    name=reference_guide_name,
                    onclick_action=("omni.kit.menu.common", "OpenRefGuide"),
                    hotkey=(0, Key.F1),
                    enabled=reference_guide_name is not None,
                )
            )

        if kit_sdk_name and discover_kit_sdk_path:
            self._help_menu.append(
                MenuItemDescription(
                    name=kit_sdk_name,
                    onclick_action=("omni.kit.menu.common", "OpenDevKitSDK"),
                    enabled=discover_kit_sdk_path is not None,
                )
            )

        if kit_manual_name and manual_url_path:
            self._help_menu.append(
                MenuItemDescription(
                    name=kit_manual_name,
                    onclick_action=("omni.kit.menu.common", "OpenDevManual"),
                    enabled=manual_url_path is not None,
                )
            )

        if self._help_menu:
            omni.kit.menu.utils.add_menu_items(self._help_menu, "Help", 99)

    def __del__(self):
        omni.kit.menu.utils.remove_menu_items(self._help_menu, "Help")
        self._deregister_actions("omni.kit.menu.common")

    def _register_actions(self, extension_id, discover_reference_guide_path, discover_kit_sdk_path, manual_url_path):
        action_registry = omni.kit.actions.core.get_action_registry()
        actions_tag = "Help Menu Actions"

        # actions
        action_registry.register_action(
            extension_id,
            "OpenRefGuide",
            lambda: webbrowser.open(discover_reference_guide_path),
            display_name="Help->Reference Guide",
            description="Reference Guide",
            tag=actions_tag,
        )

        action_registry.register_action(
            extension_id,
            "OpenDevKitSDK",
            lambda: webbrowser.open(discover_kit_sdk_path),
            display_name="Help->Discover Kit SDK",
            description="Discover Kit SDK",
            tag=actions_tag,
        )

        action_registry.register_action(
            extension_id,
            "OpenDevManual",
            lambda: webbrowser.open(manual_url_path),
            display_name="Help->Developers Manual",
            description="Developers Manual",
            tag=actions_tag,
        )

    def _deregister_actions(self, extension_id):
        action_registry = omni.kit.actions.core.get_action_registry()
        if action_registry:
            action_registry.deregister_all_actions_for_extension(extension_id)
