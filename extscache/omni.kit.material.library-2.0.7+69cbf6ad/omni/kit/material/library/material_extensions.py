"""Material utility UI for omni.kit.window.content_browser (Bind material) & omni.kit.context_menu (Create/Material)."""
# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["MaterialUIExtensions"]

import asyncio
import os
import asyncio
import carb
import omni.kit.usd.layers as layers
import omni.kit.app
from typing import Any, Optional, Callable, List
from pxr import Usd, Sdf, Gf, Tf, UsdShade, UsdGeom, Trace, UsdUtils
from .material_dialog import MaterialDialogs


class MaterialUIExtensions:
    """Material utility UI for omni.kit.window.content_browser (Bind material) & omni.kit.context_menu (Create/Material)."""
    def __init__(self):
        """Material utility UI for omni.kit.window.content_browser (Bind material) & omni.kit.context_menu (Create/Material)."""
        self._context_menu = []
        self._content_menu_items = []
        self._listeners = []
        self._material_preferences = None
        self._material_dialogs = None

        async def add_menus():
            import omni.kit.material.library

            await omni.kit.material.library.get_mdl_list_async()

            manager = omni.kit.app.get_app().get_extension_manager()
            self._listeners.append(
                    manager.subscribe_to_extension_enable(
                        on_enable_fn=lambda _: self._add_content_window_menus(),
                        on_disable_fn=lambda _: self._remove_content_window_menus(),
                        ext_name="omni.kit.window.content_browser",
                        hook_name="omni.kit.material.library omni.kit.window.content_browser listener",
                    )
                )

            try:
                import omni.kit.context_menu

                self._listeners.append(
                        manager.subscribe_to_extension_enable(
                            on_enable_fn=lambda _: self._add_context_menus(),
                            on_disable_fn=lambda _: self._remove_context_menus(),
                            ext_name="omni.kit.context_menu",
                            hook_name="omni.kit.material.library omni.kit.context_menu listener",
                        )
                    )
            except ModuleNotFoundError:
                pass

            self._material_dialogs = MaterialDialogs()

        asyncio.ensure_future(add_menus())

    def __del__(self): # pragma: no cover
        omni.kit.material.library.remove_material_list_refresh_callback(self._add_context_menus)
        if self._material_dialogs:
            self._material_dialogs.destroy()
        del self._material_dialogs
        self._listeners = None;

    # --- context menus ---

    def _add_context_menus(self):
        # this can trigger before material lists are fully-loaded, so set callback to re-build menus
        self._remove_context_menus()
        omni.kit.material.library.add_material_list_refresh_callback(self._add_context_menus)

        # NOTE: prim_list is not available...
        submenu_dict = []
        submenus = {}
        for mat in omni.kit.material.library.get_material_list():
            if mat.name == "GROUP":
                submenu_dict.append({'name': '', 'header': mat.submenu})

            elif mat.submenu:
                if not mat.submenu in submenus:
                    submenus[mat.submenu] = []
                    submenu_dict.append({'name': { mat.submenu: submenus[mat.submenu]}})
                submenus[mat.submenu].append({'name': mat.name, 'onclick_fn': lambda o, fn=mat.create_fn, b=mat.block: MaterialUIExtensions.create_material_and_assign(objects=o, create_fn=fn, blocking=b)})
            else:
                submenu_dict.append({'name': mat.name, 'onclick_fn': lambda o, fn=mat.create_fn, b=mat.block: MaterialUIExtensions.create_material_and_assign(objects=o, create_fn=fn, blocking=b)})

        menu_dict = {'glyph': "menu_material.svg", 'name': { 'Material': submenu_dict }}
        self._context_menu = omni.kit.context_menu.add_menu(menu_dict, "CREATE")

    def _remove_context_menus(self):
        self._context_menu = None

    @staticmethod
    def create_material_and_assign(objects: dict, create_fn: Callable, blocking: bool=True) -> None:
        """
        create material and bind to prims

        Args:
            objects: (dict): dictionary of prims
            create_fn: create material function
            blocking: block and call create_fn
        """
        prim_list = []
        if "prim" in objects:
            prim_list = [objects["prim"]]
        elif "prim_list" in objects:
            prim_list = objects["prim_list"]

        usd_context = omni.usd.get_context()
        with layers.active_authoring_layer_context(usd_context):
            def assign_to_prim(mtl_list):
                with omni.kit.undo.group():
                    for prim in prim_list:
                        if omni.usd.is_prim_material_supported(prim):
                            for mtl_created in mtl_list:
                                omni.kit.commands.execute(
                                    "BindMaterialCommand",
                                    prim_path=prim.GetPath().pathString,
                                    material_path=mtl_created,
                                    strength=None,
                                )

            if blocking:
                mtl_list = []
                create_fn(mtl_created_list=mtl_list)
                assign_to_prim(mtl_list)
            else:
                create_fn(bind_selected_prims=True)

    # --- content window menus ---

    @staticmethod
    def _can_show_content_bind_material(content_url):
        paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
        stage = omni.usd.get_context().get_stage()
        if not stage:
            return False
        for path in paths:
            prim = stage.GetPrimAtPath(path)
            if not prim or not omni.usd.is_prim_material_supported(prim):
                return False

        ext = os.path.splitext(content_url)[1]
        return ext == ".mdl" and len(paths) > 0

    @staticmethod
    def _content_bind_material(mdl_path):
        import omni.kit.material.library

        prim_list = omni.usd.get_context().get_selection().get_selected_prim_paths()
        def bind_mdl(mdl_prim: Usd.Prim):
            material_strength = UsdShade.Tokens.weakerThanDescendants
            omni.kit.commands.execute(
                "BindMaterial", prim_path=prim_list, material_path=mdl_prim.GetPath(), strength=material_strength
            )
            omni.usd.get_context().get_selection().set_selected_prim_paths([mdl_prim.GetPath().pathString], True)

        stage = omni.usd.get_context().get_stage()

        if mdl_path.startswith('"') or mdl_path.startswith("'"):
            mdl_path = mdl_path[1:]
        if mdl_path.endswith('"') or mdl_path.endswith("'"):
            mdl_path = mdl_path[:-1]
        mtl_name, _ = os.path.splitext(os.path.basename(mdl_path))

        def loaded_mdl_subids(mtl_list, mdl_path, filename):
            if not mtl_list:
                return

            if len(mtl_list) > 1:
                omni.kit.material.library.custom_material_dialog(mdl_path=mdl_path, bind_prim_paths=prim_list)
                return

            bind_material_path = omni.kit.material.library.create_mdl_material(
                stage=stage,
                mtl_url=mdl_path,
                mtl_name=mtl_name,
                on_create_fn=bind_mdl,
                mtl_real_name=mtl_list[0].name if len(mtl_list) > 0 else "")

        # get subids from material
        asyncio.ensure_future(omni.kit.material.library.get_subidentifier_from_mdl(mdl_file=mdl_path, on_complete_fn=lambda l, p=mdl_path, n=mtl_name: loaded_mdl_subids(mtl_list=l, mdl_path=p, filename=n), show_alert=True))

    def _add_content_window_menus(self):
        import omni.kit.window.content_browser

        self._content_menu_items = []

        try:
            import omni.kit.window.content_browser as content

            icon_path = f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/data/icons"
            self._content_window = content.get_content_window()
            self._content_menu_items.append(
                self._content_window.add_context_menu(
                    "Bind material to selected prim(s)",
                    f"{icon_path}/icoMaterial_16.png",
                    click_fn=lambda b, c: MaterialUIExtensions._content_bind_material(c),
                    show_fn=lambda b: MaterialUIExtensions._can_show_content_bind_material(b),
                )
            )
        except: # pragma: no cover
            carb.log_warn("context_menu failed to create content window menus")

    def _remove_content_window_menus(self): # pragma: no cover
        if self._content_window:
            self._content_window.delete_context_menu("Bind material to selected prim(s)")
            self._content_window = None
            self._content_menu_items = None

    # ---- misc ----

    def bind_material_to_prims_dialog(self, stage: Usd.Stage, prims: list) -> None:
        """
        Show bind material to prims dialog.

        Args:
            stage (Usd.Stage): stage
            prims (list): list of prims to bind material to.
        """
        # self._material_dialogs has not been initialized yet, create a temporary one
        if self._material_dialogs == None:
            self._material_dialogs = MaterialDialogs()

        return self._material_dialogs.bind_material_to_prims_dialog(stage, prims)
