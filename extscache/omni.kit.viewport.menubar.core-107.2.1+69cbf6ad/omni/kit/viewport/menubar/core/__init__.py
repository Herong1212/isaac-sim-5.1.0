# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This extension provides a comprehensive system for creating and managing custom menu bars and items within the viewport UI in Omniverse Kit applications."""

'''
### WIP TBD ###

PROBLEM:
    David has a very good menu::

        self._edit_menu_list = [
            MenuItemDescription(
                name="Undo",
                glyph="none.svg",
                enable_fn=lambda: omni.kit.undo.can_undo(),
                onclick_fn=omni.kit.undo.undo,
                hotkey=(carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL, carb.input.KeyboardInput.Z),
            )
        ]

        omni.kit.menu.utils.add_menu_items(self._edit_menu_list, "Edit", -9)

# Also: set_default_menu_priority
# Also: remove_menu_items
# Also: add_hook
# Also: remove_hook
# Also: add_layout
# Also: remove_layout

# Pros:
# - Lots of features
# - Lots of callbacks
# - Easy to read

# Cons:
# - Limited with ImGui Menu
# - No support of widgets
# - MenuItemDescription per menu item

### GOAL ###

# https://confluence.nvidia.com/pages/viewpage.action?spaceKey=OMNIVERSE&title=Viewport+Toolbar

# - Reuse the MenuItemDescription experience
# - Leverage new menu
# - Flexibility
# - Decentralization
# - MVP: Viewport menu
# - Ability to evolve to the universal menu framework

### SIMPLE CASE EXAMPLE ###

Example::

    class SliderMenuDelegate(ui.MenuDelegate):
        """A menu delegate that draws the Label and the Slider"""

        def __init__(self, model):
            self._model = model

        def build_item(self, item):
            ui.Label(item.text, width=200)
            ui.FloatSlider(self._model)


    # Put the menu item to the "Camera" menu
    with omni.kit.viewport.menubar.get_menu_item("Camera"):
        # Just declare, ViewportMenuItem will be stored in the model
        ViewportMenuItem(name="Camera Speed", parent="Camera", delegate=SliderMenuDelegate(self._speed_model))
        ViewportMenuItem(
            name="Camera Speed Scaller", parent="Camera", delegate=SliderMenuDelegate(self._speed_scale_model)
        )

ADVANCED CASE EXAMPLE::

    class HudMenu(ViewportMenuItem):
        def build_fn(self):
            # Not limited with one item per class
            with ui.Menu("Hud Status"):
                ui.MenuItem("FPS", checkable=True, checked=fps_checked)
                ui.MenuItem("GPU Memory", checkable=True, checked=gpu_checked)
                ui.MenuItem("Host Memory", checkable=True, checked=host_checked)
                ui.MenuItem("Resolution", checkable=True, checked=res_checked)

API::

    class ViewportMenu:
        def __init__(self,
            name: str = "",
            icon: str = "",
            appear_after: Union[list, str] = "",
            hotkey: Tuple[int, int] = None,
            onclick_fn: Callable = None,
            delegate: ui.MenuDelegate = None
            #
        ):
            # Adds self to the registry
            ...

        def build_fn(self):
            """
            Called by the parent. Everything that is here is added to the parent
            ui.Menu.
            """
            # Ability to reimplement
            # By default it creates a single ui.MenuItem only
            ...

        def invalidate(self):
            ...
'''

__all__ = [
    "get_instance",
    "ViewportMenuBarExtension",
    "AbstractViewportMenubarItem",
    "AbstractViewportMenuItem",
    "DEFAULT_MENUBAR_NAME",
    "VIEWPORT_MENUBAR_STYLE",
    "MenuDisplayStatus",

    "CategoryStatus",
    "AbstractWidgetMenuDelegate",
    "ViewportMenuDelegate",
    "CategoryMenuDelegate",
    "CheckboxMenuDelegate",
    "ColorMenuDelegate",
    "ComboBoxMenuDelegate",
    "IconMenuDelegate",
    "LabelMenuDelegate",
    "SeparatorDelegate",
    "SliderMenuDelegate",
    "SpinnerMenuDelegate",

    "CategoryMenuCollection",
    "CategoryMenuContainer",
    "AbstractColorMenuItem",
    "FloatArraySettingColorMenuItem",
    "RadioMenuCollection",
    "SelectableMenuItem",
    "ViewportButtonItem",
    "ViewportMenuContainer",
    "ViewportMenuItem",
    "ViewportMenuSeparator",
    "ViewportMenuSpacer",
    "ViewportMenubar",

    "BaseCategoryItem",
    "CategoryCollectionItem",
    "CategoryCustomItem",
    "CategoryStateItem",
    "SimpleCategoryModel",
    "ComboBoxItem",
    "ComboBoxModel",
    "SettingComboBoxModel",
    "SimpleListItem",
    "SimpleListModel",
    "SettingModel",
    "SettingModelWithDefaultValue",
    "USDAttributeModel",
    "USDBoolAttributeModel",
    "USDFloatAttributeModel",
    "USDIntAttributeModel",
    "USDStringAttributeModel",
    "USDMetadataModel",

    "ResetButton",
    "ResetHelper",
    "ViewportMenuModel",
]

from .delegate.abstract_widget_menu_delegate import AbstractWidgetMenuDelegate
from .delegate.category_menu_delegate import CategoryMenuDelegate
from .delegate.checkbox_menu_delegate import CheckboxMenuDelegate
from .delegate.color_menu_delegate import ColorMenuDelegate
from .delegate.combobox_menu_delegate import ComboBoxMenuDelegate
from .delegate.icon_menu_delegate import IconMenuDelegate
from .delegate.label_menu_delegate import LabelMenuDelegate
from .delegate.separator_menu_delegate import SeparatorDelegate
from .delegate.slider_menu_delegate import SliderMenuDelegate
from .delegate.spinner_menu_delegate import SpinnerMenuDelegate
from .delegate.viewport_menu_delegate import ViewportMenuDelegate
from .extension import ViewportMenuBarExtension, get_instance
from .menu_item.category_menu_collection import CategoryMenuCollection, CategoryStatus
from .menu_item.category_menu_container import CategoryMenuContainer
from .menu_item.color_menu_item import AbstractColorMenuItem, FloatArraySettingColorMenuItem
from .menu_item.radio_menu_collection import RadioMenuCollection
from .menu_item.selectable_menu_item import SelectableMenuItem
from .menu_item.viewport_button_item import ViewportButtonItem
from .menu_item.viewport_menu_container import ViewportMenuContainer
from .menu_item.viewport_menu_item import ViewportMenuItem
from .menu_item.viewport_menu_separator import ViewportMenuSeparator
from .menu_item.viewport_menu_spacer import ViewportMenuSpacer
from .menu_item.viewport_menubar_item import ViewportMenubar
from .model.category_model import (
    BaseCategoryItem,
    CategoryCollectionItem,
    CategoryCustomItem,
    CategoryStateItem,
    SimpleCategoryModel,
)
from .model.combobox_model import ComboBoxItem, ComboBoxModel, SettingComboBoxModel
from .model.list_model import SimpleListItem, SimpleListModel
from .model.reset_button import ResetButton, ResetHelper
from .model.setting_model import SettingModel, SettingModelWithDefaultValue
from .model.usd_attribute_model import (
    USDAttributeModel,
    USDBoolAttributeModel,
    USDFloatAttributeModel,
    USDIntAttributeModel,
    USDStringAttributeModel,
)
from .model.usd_metadata_model import USDMetadataModel
from .style import DEFAULT_MENUBAR_NAME, VIEWPORT_MENUBAR_STYLE
from .utils import menu_is_tearable
from .viewport_menu_model import AbstractViewportMenubarItem, AbstractViewportMenuItem, MenuDisplayStatus
from .viewport_menu_model import get_item as get_menu_item, ViewportMenuModel
