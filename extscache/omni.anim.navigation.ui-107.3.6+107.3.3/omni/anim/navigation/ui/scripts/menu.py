# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from functools import partial

from .utils import refresh_property_window
import carb
import carb.settings
import omni.kit.commands
import omni.kit.context_menu
import omni.kit.menu.utils
import omni.kit.undo
import omni.usd
from omni.kit.menu.utils import MenuItemDescription
from omni.kit.property.usd import PrimPathWidget
from omni.kit.property.usd.prim_selection_payload import PrimSelectionPayload
from pxr import Sdf, Usd, UsdGeom, UsdShade
import NavSchema
import weakref

MENU_NAME = "Navigation"
MENU_GLYPH = "menu_navigation.svg"
MENU_NAVMESH_INCLUDE_VOLUME = "NavMesh Include Volume"
MENU_NAVMESH_EXCLUDE_VOLUME = "NavMesh Exclude Volume"

DEFAULT_USDGEOM_BASISCURVE_PURPOSE_SETTING = "/persistent/exts/omni.curve.manipulator/creation/purpose"


class Menu:
    def __init__(self, navmesh_menu, ext_id):
        self._ext_id = ext_id
        self._settings = carb.settings.get_settings()
        self._add_button_menu_entries = []
        self._register_actions()
        self._navmesh_menu = weakref.ref(navmesh_menu)
        self.on_startup()

    def _build_context_menu(self, objects):
        from omni.kit.context_menu import ContextMenuExtension
        # keep copy objects to prevent python GC
        objects['n_menu'] = ContextMenuExtension.uiMenu(
            MENU_NAME,
            glyph=MENU_GLYPH,
            submenu=True,
            tearable=True,
            style={"secondary_color": 0xFFFFFFFF}
        )
        objects['n_menuitems'] = []
        with objects['n_menu']:
            objects['n_menuitems'].append(
                ContextMenuExtension.uiMenuItem(
                    MENU_NAVMESH_INCLUDE_VOLUME,
                    triggered_fn=partial(self._on_menu_click, MENU_NAVMESH_INCLUDE_VOLUME, objects))
            )
            objects['n_menuitems'].append(
                ContextMenuExtension.uiMenuItem(
                    MENU_NAVMESH_EXCLUDE_VOLUME,
                    triggered_fn=partial(self._on_menu_click, MENU_NAVMESH_EXCLUDE_VOLUME, objects))
            )

    def on_startup(self) -> None:
        # add navigation main menu
        create_original_svg_color = carb.settings.get_settings().get("/exts/omni.kit.menu.create/original_svg_color")
        main_sub_menu = []
        main_sub_menu.append(
            MenuItemDescription(name=MENU_NAVMESH_INCLUDE_VOLUME, onclick_action=(self._ext_id, "create_navmesh_include_volume"))
        )
        main_sub_menu.append(
            MenuItemDescription(name=MENU_NAVMESH_EXCLUDE_VOLUME, onclick_action=(self._ext_id, "create_navmesh_exclude_volume"))
        )
        self._main_menu_items = []
        self._main_menu_items.append(
            MenuItemDescription(
                name=MENU_NAME,
                glyph=MENU_GLYPH,
                appear_after=["Xform", "Material"],
                sub_menu=main_sub_menu,
                original_svg_color=create_original_svg_color,
            )
        )
        omni.kit.menu.utils.add_menu_items(self._main_menu_items, "Create", -9)

        # add navigation stage and viewport context menus
        self._context_menu = omni.kit.context_menu.get_instance()
        self._stage_context_menus = []
        self._viewport_context_menus = []

        context_menu_dict = {"name": "Navigation NavMesh Context Menu", "populate_fn": self._build_context_menu}

        self._stage_context_menus.append(omni.kit.context_menu.add_menu(context_menu_dict, "CREATE", "omni.kit.widget.stage"))
        self._viewport_context_menus.append(omni.kit.context_menu.add_menu(context_menu_dict, "CREATE", "omni.kit.viewport.window"))

        self._add_button_menu_entries.append(
            PrimPathWidget.add_button_menu_entry(
                "Navigation/NavMesh Exclude",
                show_fn=partial(self._show_navmesh_exclude, apply_navmesh_exclude=True),
                onclick_fn=self._add_navmesh_exclude,
            )
        )
        self._add_button_menu_entries.append(
            PrimPathWidget.add_button_menu_entry(
                "Navigation/NavMesh Area",
                show_fn=partial(self._show_navmesh_area, apply_navmesh_area=True),
                onclick_fn=self._add_navmesh_area,
            )
        )

    def _show_navmesh_exclude(self, objects: dict, apply_navmesh_exclude=False):
        if "stage" in objects and "prim_list" in objects:
            stage = objects["stage"]
            if stage:
                prim_list = objects["prim_list"]
                for path in prim_list:
                    prim = path
                    if not isinstance(prim, Usd.Prim):
                        prim = stage.GetPrimAtPath(path)
                    if prim.IsInstanceProxy():
                        return False
                    if prim.IsA(UsdGeom.Xformable):
                        navmesh_exclude_applied = False
                        if prim.HasAPI(NavSchema.NavMeshExcludeAPI):
                            navmesh_exclude_applied = True
                        if apply_navmesh_exclude != navmesh_exclude_applied:
                            return True
        return False

    def _add_navmesh_exclude(self, payload: PrimSelectionPayload):
        stage = payload.get_stage()
        if stage:
            with omni.kit.undo.group():
                prim_paths_to_exclude = []
                for path in payload:
                    if path:
                        prim = stage.GetPrimAtPath(path)
                        if not prim.HasAPI(NavSchema.NavMeshExcludeAPI):
                            omni.kit.commands.execute(
                                "ApplyNavMeshAPICommand", prim_path=path, api=NavSchema.NavMeshExcludeAPI
                            )
                            prim_paths_to_exclude.append(path.pathString)
                if len(prim_paths_to_exclude) > 0:
                    navmesh_menu = self._navmesh_menu()
                    if navmesh_menu:
                        navmesh_menu.add_exclusion(list(prim_paths_to_exclude))

    def _show_navmesh_area(self, objects: dict, apply_navmesh_area=False):
        if "stage" in objects and "prim_list" in objects:
            stage = objects["stage"]
            if stage:
                prim_list = objects["prim_list"]
                for path in prim_list:
                    prim = path
                    if not isinstance(prim, Usd.Prim):
                        prim = stage.GetPrimAtPath(path)
                    if prim.IsInstanceProxy():
                        return False
                    if prim.IsA(UsdGeom.Xformable) or prim.IsA(UsdShade.Material):
                        navmesh_area_applied = False
                        if prim.HasAPI(NavSchema.NavMeshAreaAPI):
                            navmesh_area_applied = True
                        if apply_navmesh_area != navmesh_area_applied:
                            return True
        return False

    def _add_navmesh_area(self, payload: PrimSelectionPayload):
        stage = payload.get_stage()
        if stage:
            with omni.kit.undo.group():
                for path in payload:
                    if path:
                        prim = stage.GetPrimAtPath(path)
                        if not prim.HasAPI(NavSchema.NavMeshAreaAPI):
                            omni.kit.commands.execute(
                                "ApplyNavMeshAPICommand", prim_path=path, api=NavSchema.NavMeshAreaAPI
                            )
                refresh_property_window()

    def _on_menu_click(self, menu_item, objects: dict):
        position = objects["mouse_pos"] if "mouse_pos" in objects else None
        if menu_item == MENU_NAVMESH_INCLUDE_VOLUME:
            self._create_navmesh_volume(0, position)
        elif menu_item == MENU_NAVMESH_EXCLUDE_VOLUME:
            self._create_navmesh_volume(1, position)

    def on_shutdown(self):
        for add_button_menu_entry in self._add_button_menu_entries:
            PrimPathWidget.remove_button_menu_entry(add_button_menu_entry)
        omni.kit.menu.utils.remove_menu_items(self._main_menu_items, "Create")
        self._add_button_menu_entries = []
        self._stage_context_menus = []
        self._viewport_context_menus = []
        self._main_menu_items = []
        self._stage_menu = None
        self._deregister_actions()

    def _create_navmesh_volume(self, selected_volume_type: int, position=None):
        usd_context = omni.usd.get_context()
        selected_prim_paths = usd_context.get_selection().get_selected_prim_paths()
        stage = usd_context.get_stage()
        selected_prim_path = Sdf.Path.emptyPath
        if len(selected_prim_paths) == 1:
            prim = stage.GetPrimAtPath(selected_prim_paths[0])
            if prim.IsA(UsdGeom.Xformable):
                selected_prim_path = Sdf.Path(selected_prim_paths[0])

        omni.kit.commands.execute("CreateNavMeshVolumeCommand", parent_prim_path=selected_prim_path, volume_type=selected_volume_type, position=position)

    def _register_actions(self):
        action_registry = omni.kit.actions.core.get_action_registry()
        actions_tag = "NavMesh Actions"

        action_registry.register_action(
            self._ext_id,
            "create_navmesh_include_volume",
            lambda *_: self._create_navmesh_volume(0),
            display_name=f"Create->Navigation->{MENU_NAVMESH_INCLUDE_VOLUME}",
            description=f"Create {MENU_NAVMESH_INCLUDE_VOLUME}",
            tag=actions_tag,
        )

        action_registry.register_action(
            self._ext_id,
            "create_navmesh_exclude_volume",
            lambda *_: self._create_navmesh_volume(1),
            display_name=f"Create->Navigation->{MENU_NAVMESH_EXCLUDE_VOLUME}",
            description=f"Create {MENU_NAVMESH_EXCLUDE_VOLUME}",
            tag=actions_tag,
        )

    def _deregister_actions(self):
        action_registry = omni.kit.actions.core.get_action_registry()
        action_registry.deregister_all_actions_for_extension(self._ext_id)
