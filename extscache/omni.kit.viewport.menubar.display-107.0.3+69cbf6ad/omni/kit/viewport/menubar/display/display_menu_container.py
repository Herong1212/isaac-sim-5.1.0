# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["DisplayMenuContainer"]

from functools import partial
from typing import Dict, List, Optional

import carb
import carb.settings
from omni.kit.viewport.menubar.core import (
    IconMenuDelegate,
    SettingModel,
    ViewportMenuContainer,
    CategoryMenuContainer,
    SelectableMenuItem,
    SimpleCategoryModel,
    CategoryStateItem,
    BaseCategoryItem,
    CategoryCustomItem,
    CategoryCollectionItem,
    ViewportMenuDelegate,
)
import omni.ui as ui

from .style import UI_STYLE

SHOW_BY_TYPE_EXCLUDE_LIST = "/exts/omni.kit.viewport.menubar.display/showByType/exclude_list"
HEADS_UP_CATEGORY_NAME = "Heads Up Display"
SHOW_BY_TYPE_CATEGORY_NAME = "Show By Type"
SHOW_BY_PURPOSE_CATEGORY_NAME = "Show By Purpose"
DEFAULT_CATEGORIES = [HEADS_UP_CATEGORY_NAME, SHOW_BY_TYPE_CATEGORY_NAME, SHOW_BY_PURPOSE_CATEGORY_NAME]
DEFAULT_SECTION = "default"
DISPLAY_ACTIONS_MAP = {
    "omni.kit.viewport.actions::toggle_bounding_box_visibility": "Bounding Box",
    "omni.kit.viewport.actions::toggle_grid_visibility": "Grid",
    "omni.kit.viewport.actions::toggle_camera_visibility": "Cameras" ,
    "omni.kit.viewport.actions::toggle_light_visibility": "Lights",
    "omni.kit.viewport.actions::toggle_skeleton_visibility": "Skeletons",
    "omni.kit.viewport.actions::toggle_audio_visibility": "Audio",
    "omni.kit.viewport.actions::toggle_mesh_visibility": "Meshes",
    "omni.kit.viewport.actions::toggle_selection_hilight_visibility": "Selection Outline",
    "omni.kit.viewport.actions::toggle_axis_visibility": "Axis",
    "omni.kit.viewport.actions::toggle_show_by_purpose_render": "Render",
    "omni.kit.viewport.actions::toggle_show_by_purpose_proxy": "Proxy",
    "omni.kit.viewport.actions::toggle_show_by_purpose_guide": "Guide",
}


def _make_viewport_setting(viewport_api_id: str, setting: str):
    return f"/persistent/app/viewport/{viewport_api_id}/{setting}/visible"


class DisplayMenuContainer(ViewportMenuContainer):
    """The menu with the visibility settings"""

    def __init__(self):
        super().__init__(
            name="Display",
            delegate=IconMenuDelegate("Display"),
            visible_setting_path="/exts/omni.kit.viewport.menubar.display/visible",
            order_setting_path="/exts/omni.kit.viewport.menubar.display/order",
            style=UI_STYLE,
            actions_map=DISPLAY_ACTIONS_MAP,
        )

        self._root_menu: Optional[ui.Menu] = None
        self._category_models: Dict[str, SimpleCategoryModel] = {}
        self._custom_settings: List[List[str, str]] = []
        self._custom_category_items: Dict[str, List[BaseCategoryItem]] = {}
        self._section_categories: Dict[str, List[str]] = {}
        self._section_categories[DEFAULT_SECTION] = DEFAULT_CATEGORIES[:]  # Copy the default categories list
        self.__mem_type_sub = carb.settings.get_settings().subscribe_to_node_change_events(
            "/exts/omni.kit.viewport.window/hud/memoryTypes",
            self.__mem_type_changed
        )
        self.__excludes_sub = None

    def destroy(self):
        setting_sub, self.__mem_type_sub = self.__mem_type_sub, None
        if setting_sub:
            carb.settings.get_settings().unsubscribe_to_change_events(setting_sub)
        excludes_sub, self.__excludes_sub = self.__excludes_sub, None
        if excludes_sub:
            carb.settings.get_settings().unsubscribe_to_change_events(excludes_sub)
        menu, self._root_menu = self._root_menu, None
        if menu:
            menu.destroy()
        super().destroy()

    def register_custom_setting(self, text: str, setting_path: str):
        self._custom_settings.append((text, setting_path))
        if self._root_menu:
            self._root_menu.invalidate()

    def deregister_custom_setting(self, text: str):
        found = [item for item in self._custom_settings if item[0] == text]
        if found:
            for item in found:
                self._custom_settings.remove(item)
            if self._root_menu:
                self._root_menu.invalidate()

    def register_custom_category_item(self, category: str, item: BaseCategoryItem, section: str):
        is_top_category = False
        if category not in DEFAULT_CATEGORIES and category not in self._category_models:
            if item.text == category and isinstance(item, CategoryCollectionItem):
                self._category_models[category] = SimpleCategoryModel(category, root=item)
                is_top_category = True
            else:
                self._category_models[category] = SimpleCategoryModel(category)

        if category not in self._custom_category_items:
            self._custom_category_items[category] = []
        if section not in self._section_categories:
            self._section_categories[section] = []

        if not is_top_category:
            self._custom_category_items[category].append(item)

        if category not in self._section_categories[section]:
            self._section_categories[section].append(category)
        if self._root_menu:
            self._root_menu.invalidate()

    def deregister_custom_category_item(self, category: str, item: BaseCategoryItem):
        if category in self._custom_category_items and item in self._custom_category_items[category]:
            self._custom_category_items[category].remove(item)

        if category not in DEFAULT_CATEGORIES and ((item.text == category and isinstance(item, CategoryCollectionItem)) or len(self._custom_category_items[category]) == 0):
            del self._category_models[category]
            # Now clean up section
            sections = list(self._section_categories.keys())
            for section in sections:
                if category in self._section_categories[section]:
                    self._section_categories[section].remove(category)
                    if len(self._section_categories[section]) == 0:
                        del self._section_categories[section]

        if self._root_menu:
            self._root_menu.invalidate()

    def build_fn(self, viewport_context: dict):
        self._root_menu = ui.Menu(self.name, delegate=self._delegate,
                                  on_build_fn=partial(self._build_menu_items, viewport_context),
                                  style=self._style)

    def _build_menu_items(self, viewport_context: dict, *args, **kwargs):
        viewport = viewport_context.get("viewport_api")
        viewport_api_id: str = str(viewport.id)
        settings = carb.settings.get_settings()

        show_by_type_items: list[BaseCategoryItem] = [
            CategoryStateItem("Cameras", setting_path=_make_viewport_setting(viewport_api_id, "scene/cameras"), hotkey_text=self._get_menu_item_hotkey_text("Cameras")),
            CategoryStateItem("Lights", setting_path=_make_viewport_setting(viewport_api_id, "scene/lights"), hotkey_text=self._get_menu_item_hotkey_text("Lights")),
            CategoryStateItem("Skeletons", setting_path=_make_viewport_setting(viewport_api_id, "scene/skeletons"), hotkey_text=self._get_menu_item_hotkey_text("Skeletons")),
            CategoryStateItem("Audio", setting_path=_make_viewport_setting(viewport_api_id, "scene/audio"), hotkey_text=self._get_menu_item_hotkey_text("Audio")),
        ]
        if (exclude_list := settings.get(SHOW_BY_TYPE_EXCLUDE_LIST)):
            show_by_type_items = [item for item in show_by_type_items if item.text not in exclude_list]
        if self.__excludes_sub is None:
            self.__excludes_sub = carb.settings.get_settings().subscribe_to_node_change_events(
                SHOW_BY_TYPE_EXCLUDE_LIST,
                self.__excludes_changed
            )

        hud_items = [CategoryStateItem("FPS", setting_path=_make_viewport_setting(viewport_api_id, "hud/renderFPS"))]

        memory_types = settings.get("/exts/omni.kit.viewport.window/hud/memoryTypes") or ()
        for mem_type in memory_types:
            hud_items.append(CategoryStateItem(f"{mem_type.capitalize()} Memory", setting_path=_make_viewport_setting(viewport_api_id, f"hud/{mem_type}Memory")))

        hud_items += [
            CategoryStateItem("Resolution", setting_path=_make_viewport_setting(viewport_api_id, "hud/renderResolution")),
            CategoryStateItem("Progress", setting_path=_make_viewport_setting(viewport_api_id, "hud/renderProgress")),
        ]

        default_category_models = {
            HEADS_UP_CATEGORY_NAME: SimpleCategoryModel(
                HEADS_UP_CATEGORY_NAME,
                hud_items
            ),

            SHOW_BY_TYPE_CATEGORY_NAME: SimpleCategoryModel(
                SHOW_BY_TYPE_CATEGORY_NAME,
                show_by_type_items
            ),

            SHOW_BY_PURPOSE_CATEGORY_NAME: SimpleCategoryModel(
                SHOW_BY_PURPOSE_CATEGORY_NAME,
                [
                    CategoryStateItem("Guide", setting_path="/persistent/app/hydra/displayPurpose/guide", hotkey_text=self._get_menu_item_hotkey_text("Guide")),
                    CategoryStateItem("Proxy", setting_path="/persistent/app/hydra/displayPurpose/proxy", hotkey_text=self._get_menu_item_hotkey_text("Proxy")),
                    CategoryStateItem("Render", setting_path="/persistent/app/hydra/displayPurpose/render", hotkey_text=self._get_menu_item_hotkey_text("Render")),
                ]
            )
        }

        for _, model in default_category_models.items():
            for item in model.get_item_children():
                children = model.get_item_children(item)
                show_hotkey_placeholder = any(child.hotkey_text for child in children)
                for child in children:
                    child.show_hotkey_placeholder = show_hotkey_placeholder

        self._category_models.update(default_category_models)

        # XXX: These add_item calls currently must occur to add the separator!
        self._category_models[SHOW_BY_TYPE_CATEGORY_NAME].add_item(CategoryCustomItem(
            "Meshes",
            lambda: SelectableMenuItem("Meshes",
                                       SettingModel(setting_path=_make_viewport_setting(viewport_api_id, "scene/meshes")),
                                       hotkey_text=self._get_menu_item_hotkey_text("Meshes"))
        ))
        self._category_models[HEADS_UP_CATEGORY_NAME].add_item(CategoryCustomItem(
            "Camera Speed",
            lambda: SelectableMenuItem("Camera Speed",
                                       SettingModel(_make_viewport_setting(viewport_api_id, "hud/cameraSpeed")))
        ))

        identifier = "omni.kit.viewport.menubar.display"

        # Create default section categories first
        for name in self._section_categories[DEFAULT_SECTION]:
            model = self._category_models[name]
            if name in self._custom_category_items:
                for item in self._custom_category_items[name]:
                    model.add_item(item)

            # XXX: Workaround nested creation of these items not being able to trigger an action!
            trigger_fns = None
            if name in (SHOW_BY_TYPE_CATEGORY_NAME, HEADS_UP_CATEGORY_NAME):
                icon_click_id = f"{identifier}.{name}.{name}"  # Left-most check/mixed icon was toggled
                if name == SHOW_BY_TYPE_CATEGORY_NAME:
                    trigger_fns = {
                        "Cameras": partial(self.__trigger_action, "toggle_camera_visibility", viewport_api=viewport),
                        "Lights": partial(self.__trigger_action, "toggle_light_visibility", viewport_api=viewport),
                        "Skeletons": partial(self.__trigger_action, "toggle_skeleton_visibility", viewport_api=viewport),
                        "Audio": partial(self.__trigger_action, "toggle_audio_visibility", viewport_api=viewport),
                        "Meshes": partial(self.__trigger_action, "toggle_mesh_visibility", viewport_api=viewport),
                        icon_click_id: partial(self.__trigger_action, "toggle_show_by_type_visibility", viewport_api=viewport),
                    }
                elif name == HEADS_UP_CATEGORY_NAME:
                    trigger_fns = {
                        "FPS": partial(self.__trigger_action, "toggle_hud_fps_visibility", viewport_api=viewport),
                        "Process Memory": partial(self.__trigger_action, "toggle_hud_memory_visibility", viewport_api=viewport, process=True, device=False, host=False),
                        "Device Memory": partial(self.__trigger_action, "toggle_hud_memory_visibility", viewport_api=viewport, process=False, device=True, host=False),
                        "Host Memory": partial(self.__trigger_action, "toggle_hud_memory_visibility", viewport_api=viewport, process=False, device=False, host=True),
                        "Resolution": partial(self.__trigger_action, "toggle_hud_resolution_visibility", viewport_api=viewport),
                        "Progress": partial(self.__trigger_action, "toggle_hud_progress_visibility", viewport_api=viewport),
                        "Camera Speed": partial(self.__trigger_action, "toggle_hud_camera_speed_visibility", viewport_api=viewport),
                        icon_click_id: partial(self.__trigger_action, "toggle_hud_visibility", viewport_api=viewport, use_setting=True),
                    }

            CategoryMenuContainer(model, identifier=f"{identifier}.{name}", trigger_fns=trigger_fns)

        # Now iterate named sections, with a separator for each.
        for section, categories in self._section_categories.items():
            if section is DEFAULT_SECTION:
                continue
            ui.Separator(text=section)
            for name in categories:
                model = self._category_models[name]
                if name in self._custom_category_items:
                    for item in self._custom_category_items[name]:
                        model.add_item(item)
                CategoryMenuContainer(model, identifier=f"{identifier}.{name}")

        ui.Separator()

        # This currently is just easier tied to legacy global setting
        show_hotkey_placeholder = False
        for item in ["Selection Outline", "Axis", "Grid", "Bounding Box"]:
            if self._get_menu_item_hotkey_text(item):
                show_hotkey_placeholder = True
                break
        SelectableMenuItem(
            "Selection Outline",
            SettingModel(_make_viewport_setting(viewport_api_id, "guide/selection")),
            triggered_fn=partial(self.__trigger_action, "toggle_selection_hilight_visibility", viewport_api=viewport),
            trigger_will_set_model=True,
            hotkey_text=self._get_menu_item_hotkey_text("Selection Outline"),
            delegate=ViewportMenuDelegate(show_hotkey_placeholder=show_hotkey_placeholder)
        )
        SelectableMenuItem(
            "Axis",
            SettingModel(_make_viewport_setting(viewport_api_id, "guide/axis")),
            triggered_fn=partial(self.__trigger_action, "toggle_axis_visibility", viewport_api=viewport),
            trigger_will_set_model=True,
            hotkey_text=self._get_menu_item_hotkey_text("Axis"),
            delegate=ViewportMenuDelegate(show_hotkey_placeholder=show_hotkey_placeholder)
        )
        SelectableMenuItem(
            "Grid",
            SettingModel(_make_viewport_setting(viewport_api_id, "guide/grid")),
            triggered_fn=partial(self.__trigger_action, "toggle_grid_visibility", viewport_api=viewport),
            trigger_will_set_model=True,
            hotkey_text=self._get_menu_item_hotkey_text("Grid"),
            delegate=ViewportMenuDelegate(show_hotkey_placeholder=show_hotkey_placeholder)
        )
        SelectableMenuItem(
            "Bounding Box",
            SettingModel(_make_viewport_setting(viewport_api_id, "guide/boundingBox")),
            triggered_fn=partial(self.__trigger_action, "toggle_bounding_box_visibility", viewport_api=viewport),
            trigger_will_set_model=True,
            hotkey_text=self._get_menu_item_hotkey_text("Bounding Box"),
            delegate=ViewportMenuDelegate(show_hotkey_placeholder=show_hotkey_placeholder)
        )

        # Custom display settings
        if self._custom_settings:
            ui.Separator()
            for (text, setting_path) in self._custom_settings:
                SelectableMenuItem(text, SettingModel(setting_path))

    def __mem_type_changed(self, *args, **kwargs):
        if self._root_menu:
            self._root_menu.invalidate()

    def __trigger_action(self, action: str, *args, **kwargs):
        import omni.kit.actions.core  # noqa: PLW0621
        action_registry = omni.kit.actions.core.get_action_registry()
        if action_registry:
            exc_action = action_registry.get_action("omni.kit.viewport.actions", action)
            if exc_action:
                exc_action.execute(*args, **kwargs)
            else:
                carb.log_error(f"Could not find action to run: '{action}'")
        else:
            carb.log_error(f"Could not get action_registry to run '{action}")

    def __excludes_changed(self, *args, **kwargs) -> None:
        if self._root_menu:
            self._root_menu.invalidate()
