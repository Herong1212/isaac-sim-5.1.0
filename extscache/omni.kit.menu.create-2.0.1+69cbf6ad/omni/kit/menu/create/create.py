"""This module defines the CreateMenuExtension class to enhance the 'Create' menu in Omniverse Kit, adding menu items for creating various types of primitives and handling their associated actions."""

__all__ = [
    "CreateMenuExtension",
    "rebuild_menus",
]

# pylint: disable=redefined-outer-name, protected-access
import os

import carb.input
import omni.ext
import omni.kit.menu.utils
from omni.kit.menu.utils import MenuItemDescription, MenuItemOrder

from .create_actions import _get_action_name, deregister_actions, register_actions

_extension_instance = None
_extension_path = None

PERSISTENT_SETTINGS_PREFIX = "/persistent"


class CreateMenuExtension(omni.ext.IExt):
    """A class designed to extend Omniverse Kit's menu capabilities, specifically for creating various types of primitives.

    This class manages the creation and organization of menu items related to creating different types of primitives, such as shapes, lights, audio sources, cameras, and more. It dynamically builds a 'Create' menu based on settings and available options, allowing users to quickly access tools for adding new elements into their scene. The class also handles custom actions for creating these items with specific attributes or settings.
    """

    def __init__(self):
        """Initializes the CreateMenuExtension and sets the default menu priority for the 'Create' menu."""
        super().__init__()
        omni.kit.menu.utils.set_default_menu_priority("Create", -8)
        self._ext_name = None
        self._settings = None
        self._create_menu_list = None

    def on_startup(self, ext_id):
        """Called when the extension starts up. Registers actions and builds the create menu.

        Args:
            ext_id (str): The ID of the extension that is starting up."""
        global _extension_instance
        _extension_instance = self

        global _extension_path
        _extension_path = omni.kit.app.get_app_interface().get_extension_manager().get_extension_path(ext_id)

        self._settings = carb.settings.get_settings()
        self._create_menu_list = None
        self._build_create_menu()

        self._ext_name = omni.ext.get_extension_name(ext_id)
        register_actions(self._ext_name, CreateMenuExtension, lambda: _extension_instance)

    def on_shutdown(self):
        """Called when the extension shuts down. Deregisters actions and removes the 'Create' menu items."""
        global _extension_instance

        deregister_actions(self._ext_name)
        _extension_instance = None
        omni.kit.menu.utils.remove_menu_items(self._create_menu_list, "Create")

    def _rebuild_menus(self):
        omni.kit.menu.utils.remove_menu_items(self._create_menu_list, "Create")
        self._build_create_menu()

    def _high_quality_option_toggle(self):
        enabled = self._settings.get(PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/highQuality")
        self._settings.set(PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/highQuality", not enabled)

    def _build_create_menu(self):
        from omni.usd import get_geometry_standard_prim_list, get_light_prim_list

        def is_create_type_enabled(type_name: str):
            settings = carb.settings.get_settings()
            if type_name == "Shape":
                if (
                    settings.get("/app/primCreation/hideShapes") is True
                    or settings.get("/app/primCreation/enableMenuShape") is False
                ):
                    return False
                return True
            enabled = settings.get(f"/app/primCreation/enableMenu{type_name}")
            if enabled is True or enabled is False:
                return enabled
            return True

        # setup menus
        self._create_menu_list = []

        # Shapes
        if is_create_type_enabled("Shape"):
            sub_menu = []
            for prim in get_geometry_standard_prim_list().keys():
                sub_menu.append(
                    MenuItemDescription(
                        name=prim, onclick_action=("omni.kit.menu.create", f"create_prim_{prim.lower()}")
                    )
                )

            def on_high_quality_option_checked():
                enabled = self._settings.get(PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/highQuality")
                return enabled

            sub_menu.append(MenuItemDescription())
            sub_menu.append(
                MenuItemDescription(
                    name="High Quality",
                    onclick_action=("omni.kit.menu.create", "high_quality_option_toggle"),
                    ticked_fn=on_high_quality_option_checked,
                )
            )

            self._create_menu_list.append(
                MenuItemDescription(
                    name="Shape", glyph="menu_prim.svg", appear_after=["Mesh", MenuItemOrder.FIRST], sub_menu=sub_menu
                )
            )

        # Lights
        if is_create_type_enabled("Light"):
            sub_menu = []
            for name, _prim, _attrs in get_light_prim_list():
                sub_menu.append(
                    MenuItemDescription(
                        name=name, onclick_action=("omni.kit.menu.create", f"create_prim_{_get_action_name(name)}")
                    )
                )
            self._create_menu_list.append(
                MenuItemDescription(name="Light", glyph="menu_light.svg", appear_after="Shape", sub_menu=sub_menu)
            )

        # Audio
        try:
            import usd.schema.audio

            audio_prim_list = usd.schema.audio.get_audio_prim_list()  # pylint: disable=c-extension-no-member
            if is_create_type_enabled("Audio") and audio_prim_list:
                sub_menu = []
                for name, _prim, _attrs in audio_prim_list:
                    sub_menu.append(
                        MenuItemDescription(
                            name=name, onclick_action=("omni.kit.menu.create", f"create_prim_{_get_action_name(name)}")
                        )
                    )
                self._create_menu_list.append(
                    MenuItemDescription(name="Audio", glyph="menu_audio.svg", appear_after="Light", sub_menu=sub_menu)
                )
        except ModuleNotFoundError:
            pass

        # Camera
        if is_create_type_enabled("Camera"):
            self._create_menu_list.append(
                MenuItemDescription(
                    name="Camera",
                    glyph="menu_camera.svg",
                    appear_after="Audio",
                    onclick_action=("omni.kit.menu.create", "create_prim_camera"),
                )
            )

        # Scope
        if is_create_type_enabled("Scope"):
            self._create_menu_list.append(
                MenuItemDescription(
                    name="Scope",
                    glyph="menu_scope.svg",
                    appear_after="Camera",
                    onclick_action=("omni.kit.menu.create", "create_prim_scope"),
                )
            )

        # Xform
        if is_create_type_enabled("Xform"):
            self._create_menu_list.append(
                MenuItemDescription(
                    name="Xform",
                    glyph="menu_xform.svg",
                    appear_after="Scope",
                    onclick_action=("omni.kit.menu.create", "create_prim_xform"),
                )
            )

        if self._create_menu_list:
            import omni.kit.menu.utils

            omni.kit.menu.utils.add_menu_items(self._create_menu_list, "Create", -8)

    @staticmethod
    def on_create_prim(prim_type, attributes, use_settings: bool = False):
        """Executes the command to create a primitive with the specified type and attributes.

        Args:
            prim_type (str): The type of the primitive to create.
            attributes (dict): The attributes to apply to the primitive.
            use_settings (bool, optional): Whether to use the settings for the primitive creation. Defaults to False."""
        usd_context = omni.usd.get_context()
        with omni.kit.usd.layers.active_authoring_layer_context(usd_context):
            omni.kit.commands.execute("CreatePrimWithDefaultXform", prim_type=prim_type, attributes=attributes)

    @staticmethod
    def on_create_light(light_type, attributes):
        """Executes the command to create a light with the specified type and attributes.

        Args:
            light_type (str): The type of the light to create.
            attributes (dict): The attributes to apply to the light."""
        usd_context = omni.usd.get_context()
        with omni.kit.usd.layers.active_authoring_layer_context(usd_context):
            omni.kit.commands.execute("CreatePrim", prim_type=light_type, attributes=attributes)

    @staticmethod
    def on_create_prims():
        """Executes the command to create a set of predefined primitives."""
        usd_context = omni.usd.get_context()
        with omni.kit.usd.layers.active_authoring_layer_context(usd_context):
            omni.kit.commands.execute("CreatePrims", prim_types=["Cone", "Cylinder", "Cone"])


def get_extension_path(sub_directory):
    """Retrieves the full path to a specified subdirectory within the extension's directory.

    Args:
        sub_directory (str): The name of the subdirectory within the extension's directory. If empty, returns the path to the extension's root directory.

    Returns:
        str: The normalized full path to the specified subdirectory within the extension's directory."""
    path = _extension_path
    if sub_directory:
        path = os.path.normpath(os.path.join(path, sub_directory))
    return path


def rebuild_menus():
    """Rebuilds the 'Create' menu in the extension.

    This function will trigger a rebuild of the 'Create' menu, ensuring that any
    changes in menu items or settings are reflected in the user interface. It is
    called when external changes necessitate a refresh of the menu structure.
    """
    if _extension_instance:
        _extension_instance._rebuild_menus()
