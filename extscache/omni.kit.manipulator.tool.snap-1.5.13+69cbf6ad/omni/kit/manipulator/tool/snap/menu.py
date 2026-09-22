# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from __future__ import annotations

import asyncio
import math
from typing import Dict, Optional, Type

import carb.settings
import omni.kit.app
import omni.kit.context_menu
import omni.ui as ui
from omni.kit.manipulator.transform import Constants as transform_c
from .provider import SnapProvider
from omni.kit.widget.options_menu import OptionItem, OptionSeparator, OptionsModel, OptionsMenu, OptionRadios

from .models import SettingModel
from .registry import SnapProviderRegistry
from .settings_constants import (
    CONFORM_TO_TARGET_SETTING_PATH,
    CONFORM_UP_AXIS_SETTING_PATH,
    KEEP_SPACING_SETTING_PATH,
    SNAP_ENABLED_SETTING,
    SNAP_PROVIDER_NAME_SETTING_PATH,
    SNAP_ROTATE_SETTING_PATH,
    SNAP_SCALE_SETTING_PATH,
    SNAP_SETTING_PREFIX,
    SNAP_TRANSLATE_SETTING_PATH,
)

TRANSFORM_OP_SETTING = "/app/transform/operation"
OP_TO_NAME = {transform_c.TRANSFORM_OP_MOVE: "translate", transform_c.TRANSFORM_OP_ROTATE: "rotate", transform_c.TRANSFORM_OP_SCALE: "scale"}
MENU_SUFFIX_TRANSLATE = "translate"
MENU_SUFFIX_ROTATE = "rotate"
MENU_SUFFIX_SCALE = "scale"


class ProviderItem(OptionItem):
    """A menu item representing a snap provider in a snap options menu.

    This class extends OptionItem to create an interactive menu entry for enabling or
     disabling a snap provider within the application.

    Args:
        name: str
            The name of the snap provider.
        provider_class: Type[SnapProvider]
            The class type of the snap provider.
        enabled: bool
            Indicates whether the provider is initially enabled."""

    def __init__(self, name: str, provider_class: Type[SnapProvider], enabled: bool):
        """Initializes a menu item for a snap provider.

        Args:
            name (str): The name of the snap provider.
            provider_class (Type[SnapProvider]): The class of the snap provider.
            enabled (bool): A flag indicating if the provider is enabled."""
        self._name = name
        self._provider_class = provider_class
        self._settings = carb.settings.get_settings()
        super().__init__(
            f"{provider_class.get_display_name()}##{name}",  # append ##{name} for unique menu entry,
            default=False,
            on_value_changed_fn=self._enable_provider,
            enabled=enabled,
        )
        self.model.set_value(self.is_checked())

    def _enable_provider(self, enabled: bool) -> None:
        """Enables or disables the snap provider based on the provided boolean value.

        Args:
            enabled (bool): A boolean indicating whether to enable or disable the provider."""
        enabled_providers = list(self._settings.get(SNAP_PROVIDER_NAME_SETTING_PATH) or [])
        if enabled and self._name not in enabled_providers:
            enabled_providers.append(self._name)
        elif not enabled and self._name in enabled_providers:
            enabled_providers.remove(self._name)
        self._settings.set(SNAP_PROVIDER_NAME_SETTING_PATH, enabled_providers)

    def is_checked(self) -> bool:
        """Checks if the provider is enabled in the settings.

        Returns:
            bool: True if the provider is enabled, False otherwise."""
        enabled_providers = list(self._settings.get(SNAP_PROVIDER_NAME_SETTING_PATH) or [])
        return self._name in enabled_providers


class ExplicitTransformItem(OptionItem):
    """A menu item for explicitly setting transform values in a snap options menu.

    This class extends OptionItem to provide a UI component that allows users to enter specific transform values (like translation, rotation, and scale) when snapping objects in the scene. The behavior and default value are adjusted depending on the type of transformation.

    Args:
        suffix: str
            A string that represents the suffix for the transform operation (e.g., 'translate', 'rotate', 'scale').

    """

    def __init__(self, suffix: str):
        """Initializes an ExplicitTransformItem with a specific suffix.

        Args:
            suffix (str): A string that represents the suffix for the transform operation (e.g., 'translate', 'rotate', 'scale').
        """
        self._suffix = suffix
        self._explicit_transform_model = SettingModel(SNAP_SETTING_PREFIX + self._suffix)
        self._explicit_transform_default = 1.0

        def __on_explicit_transform_changed(_):
            # Notification item model changed to update dirty
            self.model._value_changed()

        self.__sub_explicit_transform_model = self._explicit_transform_model.subscribe_value_changed_fn(
            __on_explicit_transform_changed
        )
        if suffix == MENU_SUFFIX_TRANSLATE:
            super().__init__("Explicit Transform", default=True, hide_on_click=True)
        else:
            super().__init__("Explicit Transform", setting_path=SNAP_ENABLED_SETTING, default=False)

    def destroy(self):
        """Cleans up the resources and subscriptions associated with this item."""
        self.__sub_explicit_transform_model = None
        super().destroy()

    def build_custom_widget(self, item: ui.MenuItem):
        """Builds the custom widget for the menu item.

        Args:
            item (ui.MenuItem): The UI menu item that this custom widget is associated with."""
        ui.Spacer()
        with ui.HStack(
            content_clipping=True
        ):  # need content_clipping so that input into the drag field doesn't click through into menu
            ui.FloatDrag(model=self._explicit_transform_model, width=50)

    def on_triggered(self):
        """Handles the action when the menu item is triggered.

        This method performs specific actions based on the suffix of the transform operation."""
        if self._suffix == MENU_SUFFIX_TRANSLATE:
            if not self.model.as_bool:
                carb.settings.get_settings().set(SNAP_PROVIDER_NAME_SETTING_PATH, [])
        else:
            super().on_triggered()

    @property
    def dirty(self) -> bool:
        """Indicates whether the item's value has changed from its default.

        Returns:
            bool: True if the value has changed, False otherwise."""
        return self.model.as_bool != self.default or not math.isclose(
            self._explicit_transform_model.as_float, self._explicit_transform_default
        )

    def reset(self) -> None:
        """Resets the item to its default state, both the check status and the explicit transform value."""
        # Reset both check status and explicit transform value
        self.model.set_value(self.default)
        self._explicit_transform_model.set_value(self._explicit_transform_default)


class SnapMenu:
    """A class responsible for creating and managing the snap options menu in the application.

    This class provides functionality to build and display menus for translating, rotating, and scaling objects using snap providers. It also handles the creation of menu items related to snapping such as 'Align to Target' and 'Keep Spacing'.
    """

    def __init__(self):
        self._settings = carb.settings.get_settings()
        self._options_models: Dict[str, OptionsModel] = {}
        self._options_menus: Dict[str, OptionsMenu] = {}
        self._align_to_target_item: Optional[OptionItem] = None
        self._align_by_axis_item: Optional[OptionRadios] = None

        self._registry = SnapProviderRegistry.get_instance()
        self._sub = self._registry.subscribe_to_registry_change(self._build_translate_menu)
        self._snap_target_sub = self._settings.subscribe_to_tree_change_events(
            SNAP_PROVIDER_NAME_SETTING_PATH, self._on_snap_targets_changed
        )
        self._transform_op_sub = self._settings.subscribe_to_node_change_events(
            TRANSFORM_OP_SETTING, self._on_transform_op_changed
        )

    def destroy(self, menu_only: bool = False):
        """Destroys the snap menu, cleaning up resources.

        Args:
            menu_only (bool): If True, only destroy the menu components, not the subscriptions."""
        for _, menu in self._options_menus.items():
            menu.destroy()
        self._options_menus = {}
        self._options_models = {}
        self._align_to_target_item = None
        self._align_by_axis_item = None

        if menu_only:
            return

        if self._transform_op_sub:
            self._settings.unsubscribe_to_change_events(self._transform_op_sub)
            self._transform_op_sub = None

        if self._snap_target_sub:
            self._settings.unsubscribe_to_change_events(self._snap_target_sub)
            self._snap_target_sub = None

        if self._sub:
            self._registry.unsubscribe_to_registry_change(self._sub)
            self._sub = None

    def __del__(self):
        self.destroy()

    def get_options_menu(self, suffix: Optional[str] = None) -> Optional[OptionsMenu]:
        """Retrieves the options menu corresponding to the provided suffix.

        Args:
            suffix (Optional[str]): A string representing the suffix for the options menu to retrieve.

        Returns:
            Optional[OptionsMenu]: The requested options menu or None if not found."""
        if suffix is None:
            current_op = self._settings.get(TRANSFORM_OP_SETTING)
            suffix = OP_TO_NAME.get(current_op, "translate")

        menu = self._options_menus.get(suffix, None)
        if menu is None:
            if suffix == MENU_SUFFIX_TRANSLATE:
                return self._build_translate_menu()
            elif suffix == MENU_SUFFIX_ROTATE:
                return self._build_rotate_menu()
            elif suffix == MENU_SUFFIX_SCALE:
                return self._build_scale_menu()
        return menu

    def _can_conform(self) -> bool:
        """Determines if any of the snap providers can orient.

        Returns:
            bool: True if at least one provider can orient, otherwise False."""
        provider_names = self._settings.get(SNAP_PROVIDER_NAME_SETTING_PATH)
        if not provider_names:
            return False

        for provider_name in provider_names:
            provider = self._registry.get_provider_class_by_name(provider_name)
            if provider and provider.can_orient():
                # return True as long as one of the providers can orient
                return True

        return False

    def _on_align_by_target_changed(self, value: bool) -> None:
        """Handles changes to the 'Align to Target' setting, enabling or disabling the 'Align by Axis' item.

        Args:
            value (bool): The new value of the 'Align to Target' setting."""
        if self._align_by_axis_item:
            self._align_by_axis_item.enabled = self._can_conform() and value

    def _build_translate_menu(self) -> OptionsMenu:
        """Builds the translate options menu with relevant items.

        Returns:
            OptionsMenu: The constructed translate options menu."""
        suffix = MENU_SUFFIX_TRANSLATE
        providers = self._registry.providers

        items = []

        # Provider items
        sorted_providers = dict(sorted(providers.items(), key=lambda item: item[1].get_display_name()))
        for name, provider_class in sorted_providers.items():
            objects = {"main_toolbar": True}
            if provider_class.can_show_menu(objects):
                items.append(ProviderItem(name, provider_class, enabled=provider_class.can_enable_menu(objects)))

        # Other items
        self._align_to_target_item = OptionItem(
            "Align to Target",
            setting_path=CONFORM_TO_TARGET_SETTING_PATH,
            default=False,
            on_value_changed_fn=self._on_align_by_target_changed,
            enabled=self._can_conform(),
            hide_on_click=True,
        )
        self._align_by_axis_item = OptionRadios(
            ["X", "Y", "Z", "Stage"],
            setting_path=CONFORM_UP_AXIS_SETTING_PATH,
            default="Stage",
            menu_text="Align by Axis",
            hide_on_click=True,
        )
        self._on_align_by_target_changed(self._align_to_target_item.model.as_bool)
        self._explicit_transform_item = ExplicitTransformItem(suffix)
        items.extend(
            [
                OptionSeparator(),
                OptionItem("Keep Spacing", setting_path=KEEP_SPACING_SETTING_PATH, default=True, hide_on_click=True),
                OptionSeparator(),
                self._align_to_target_item,
                self._align_by_axis_item,
                OptionSeparator(),
                self._explicit_transform_item,
            ]
        )

        options_model = self._options_models.get(suffix, None)
        if options_model is None:
            options_model = OptionsModel("Snap Options", items)
            self._options_models[suffix] = options_model
        else:
            options_model.rebuild_items(items)

        options_menu = self._options_menus.get(suffix, None)
        if options_menu is None:
            options_menu = OptionsMenu(options_model)
            self._options_menus[suffix] = options_menu

        return options_menu

    def _build_rotate_menu(self) -> OptionsMenu:
        """Builds the rotate options menu with relevant items.

        Returns:
            OptionsMenu: The constructed rotate options menu."""
        suffix = MENU_SUFFIX_ROTATE

        options_model = OptionsModel("Snap Options", [ExplicitTransformItem(suffix)])
        self._options_models[suffix] = options_model

        options_menu = OptionsMenu(options_model)
        self._options_menus[suffix] = options_menu

        return options_menu

    def _build_scale_menu(self) -> OptionsMenu:
        """Builds the scale options menu with relevant items.

        Returns:
            OptionsMenu: The constructed scale options menu."""
        suffix = MENU_SUFFIX_SCALE

        options_model = OptionsModel("Snap Options", [ExplicitTransformItem(suffix)])
        self._options_models[suffix] = options_model

        options_menu = OptionsMenu(options_model)
        self._options_menus[suffix] = options_menu

        return options_menu

    def _on_snap_targets_changed(self, *args, **kwargs):
        """Callback to update the UI based on changes in the snap targets settings.

        This method is called asynchronously to ensure that it processes changes
        only after all other events have been handled."""
        # This is a tree setting which will trigger several create/changed/destroy with value changed at same time
        # Delay a frame to check final value only to avoid self loop

        async def ___on_snap_targets_changed_async():
            await omni.kit.app.get_app().next_update_async()
            if self._align_to_target_item:
                self._align_to_target_item.enabled = self._can_conform()
            if self._align_by_axis_item:
                self._on_align_by_target_changed(self._align_to_target_item.model.as_bool)

            translate_model = self._options_models.get("translate", None)
            if translate_model:
                for item in translate_model.get_item_children():
                    if isinstance(item, ProviderItem):
                        checked = item.is_checked()
                        if item.model.as_bool != checked:
                            item.model.set_value(checked)

            if self._explicit_transform_item:
                checked = not self._settings.get(SNAP_PROVIDER_NAME_SETTING_PATH)
                if self._explicit_transform_item.model != checked:
                    self._explicit_transform_item.model.set_value(checked)

        asyncio.ensure_future(___on_snap_targets_changed_async())

    def _on_transform_op_changed(self, item, event_type):
        """Callback to handle changes in the transform operation settings.

        This method updates the visibility of the snap options menu based on the current
        transform operation. If a different snap options menu is open, it will be closed.

        Args:
            item: The settings item that changed.
            event_type: The type of the event that triggered the change."""
        current_op = self._settings.get(TRANSFORM_OP_SETTING)
        current_suffix = OP_TO_NAME.get(current_op, "translate")
        # If different snap options menu opened, close it.
        # Since the snap menu for each transform operation is different.
        for suffix, options_menu in self._options_menus.items():
            if suffix != current_suffix and options_menu.shown:
                options_menu.hide()
