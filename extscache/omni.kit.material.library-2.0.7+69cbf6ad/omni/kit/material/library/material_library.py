"""Material library utility functions."""

__all__ = [
    "bind_material_to_selected_prims",
    "get_material_prim_path",
    "create_mdl_material",
    "create_mtlx_material",
    "get_material_filename_from_prim",
    "CreateAndBindMdlMaterialFromLibrary",
    "CreateAndBindMtlxSurfaceFromLibrary",
    "CreateAndBindPreviewSurfaceFromLibrary",
    "CreateAndBindPreviewSurfaceTextureFromLibrary",
    "MaterialLibraryExtension",
    "get_mdl_lib_paths",
    "get_mdl_lib_paths_private",
    "get_mdl_usd_source_asset_list",
    "get_material_hidden_list",
    "get_material_show_list",
    "get_mdl_list_async",
    "get_mdl_list",
    "add_material_list_refresh_callback",
    "remove_material_list_refresh_callback",
    "delayed_material_list_refresh",
    "add_material_list_item",
    "remove_material_list_item",
    "material_list_refresh",
    "get_material_list",
    "custom_material_dialog",
    "get_subidentifier_from_material",
    "get_subidentifier_from_mdl",
    "drop_material",
    "multi_descendents_dialog",
    "remove_mdl_from_cache",
    "get_material_enums",
    "bind_material_to_prims_dialog",
    "add_usd_source_asset_path_to_mtl_lib",
    "remove_usd_source_asset_path_from_mtl_lib",
    "add_to_mtl_lib",
    "remove_from_mtl_lib",
    "get_cache_filename"
]

import re
import os
import fnmatch
import functools
import asyncio
import json
import carb
import carb.settings
import omni.kit.commands
import omni.usd
import omni.ext
from carb.eventdispatcher import get_eventdispatcher
from dataclasses import dataclass
from enum import Enum, IntEnum
from pxr import Tf, Sdf, Usd, UsdShade
from typing import List, Dict
from itertools import chain
from pathlib import Path
from .mdl_schema import MDLSchema
from .multi_descendents_dialog import _multi_descendents_dialog
from .material_actions import register_actions, deregister_actions
from .material_extensions import MaterialUIExtensions
from .drop_material import _drop_material


PERSISTENT_SETTINGS_PREFIX = "/persistent"
SETTING_MATERIAL_LIBRARY_LIB_PATHS = "/exts/omni.kit.material.library/lib_paths"
SETTING_MATERIAL_LIBRARY_USD_SOURCE_ASSET_LIST = "/exts/omni.kit.material.library/usd_source_asset_list"


@dataclass
class MaterialItem:
    name: str
    create_fn: callable=None
    block: bool=True
    submenu: str=""
    is_private: bool=False

    # legacy index support
    def __getitem__(self, key):
        match key:
            case 0:
                return self.name
            case 1:
                return self.create_fn
            case 2:
                return self.block
            case 3:
                return self.submenu
            case 4:
                return self.is_private
            case _:
                raise IndexError('list index out of range')
        return None


class ReadyState(IntEnum):
    NOT_READY = 0
    JSON_READY = 1
    APP_READY = 2
    ALL_READY = JSON_READY | APP_READY


material_instance = None
material_ready_state = ReadyState.NOT_READY
mdl_list_cache = dict()

# Kai Rohmer: until we have decided on how to pick sub-ids (automatically) it is probably safest
# to show the entire list.
full_subid_list = True

def bind_material_to_selected_prims(material_prim_path: Sdf.Path, paths: list):
    """
    Bind material to selected prims.

    Args:
        material_prim_path (Sdf.Path): Prim path of material.
        paths (list): List of prims to bind material to.

    """
    stage = omni.usd.get_context().get_stage()
    material_prim = stage.GetPrimAtPath(material_prim_path)
    if material_prim:
        for path in paths:
            prim = stage.GetPrimAtPath(path)
            if prim and omni.usd.is_prim_material_supported(prim):
                omni.kit.commands.execute("BindMaterial", prim_path=path, material_path=material_prim_path)


def get_material_prim_path(material_prim_name: str):
    """
    Make valid material prim path from material_prim_name.

    Args:
        material_prim_name (str): Prim path of material.

    Returns:
        (str): Path of "/Looks" prim
        (Sdf.Path): Valid material prim path.
    """
    stage = omni.usd.get_context().get_stage()
    if stage:
        if stage.HasDefaultPrim():
            looks_path = stage.GetDefaultPrim().GetPath().pathString + "/Looks"
        else:
            looks_path = "/Looks"
        material_prim_path = omni.usd.get_stage_next_free_path(
            stage, looks_path + "/" + omni.usd.make_valid_identifier(material_prim_name), False
        )
        if not stage.GetPrimAtPath(looks_path):
            return looks_path, material_prim_path
        else:
            return None, material_prim_path
    return None, None


def create_mdl_material(stage: Usd.Stage, mtl_url: str, mtl_name: str, on_create_fn: callable, mtl_real_name: str=""):
    """
    Create material prim from .mdl file.

    Args:
        stage (Usd.Stage): stage.
        mtl_url (str): path of material mdl file.
        mtl_name (str): Prim material name to create.
        on_create_fn (callable): Callback when material is created.
        mtl_real_name (str): Optional override for `mtl_name`

    Returns:
        (str): new material path or None.
    """
    mtl_prim_name = re.sub("_{2,}", "_", omni.usd.make_valid_identifier(mtl_real_name if mtl_real_name else mtl_name))
    if stage.HasDefaultPrim():
        mtl_path = omni.usd.get_stage_next_free_path(
            stage, "{}/Looks/{}".format(stage.GetDefaultPrim().GetPath(), mtl_prim_name), False
        )
    else:
        mtl_path = omni.usd.get_stage_next_free_path(
            stage, "/Looks/{}".format(mtl_prim_name), False
        )

    with omni.kit.undo.group():
        omni.kit.commands.execute("CreateMdlMaterialPrim", mtl_url=mtl_url, mtl_name=mtl_real_name if mtl_real_name else mtl_name, mtl_path=mtl_path)
        mat_prim = stage.GetPrimAtPath(mtl_path)
        if mat_prim:
            on_create_fn(mat_prim)
            return mtl_path
    return None


def create_mtlx_material(stage: Usd.Stage, mtlx_url: str, on_create_fn: callable, base_name: str=""):
    """
    Create materialX prim from .mdl file.

    Args:
        stage (Usd.Stage): stage.
        mtlx_url (str): path of materialX mdl file.
        on_create_fn (callable): Callback when materialX is created.
        base_name (str): Optional override for materialX name

    Returns:
        (str): new materialX path or None.
    """
    default_base_name = Path(mtlx_url).stem
    base_prim_name = re.sub("_{2,}", "_", omni.usd.make_valid_identifier(base_name if base_name else default_base_name))

    if stage.HasDefaultPrim():
        base_path = omni.usd.get_stage_next_free_path(
            stage, "{}/Looks/{}".format(stage.GetDefaultPrim().GetPath(), base_prim_name), False
        )
    else:
        base_path = omni.usd.get_stage_next_free_path(
            stage, "/Looks/{}".format(base_prim_name), False
        )

    with omni.kit.undo.group():
        omni.kit.commands.execute("CreateMtlxMaterialPrim", mtlx_url=mtlx_url, base_path=base_path)

        # single .mtlx file could contain multiple materials. use the found-first material
        materials_prim = stage.GetPrimAtPath(Sdf.Path(base_path).AppendPath("Materials"))
        if materials_prim:
            children = materials_prim.GetChildren()
            if children:
                mtl_prim = children[0]
                if mtl_prim:
                    on_create_fn(mtl_prim)
                    return mtl_prim.GetPath().pathString
    return None


def get_material_filename_from_prim(prim: Usd.Prim) -> str:
    """
    Gets material thumbnail image path for prim.

    Args:
        prim (Usd.Prim): Prim to get thumbnail image path for.

    Returns:
        (str): Thumbnail image path, image path may not exist.
    """
    shader = omni.usd.get_shader_from_material(prim)
    if shader:
        asset = shader.GetSourceAsset("mdl")
        if asset:
            filename = asset.resolvedPath.replace("\\", "/")
            return os.path.dirname(filename) + "/.thumbs/256x256/" + os.path.basename(filename) + ".png"
    return ""


def get_path_private_state(path: str):
    if path[-2:] == ":1":
        return path[:-2], True

    return path, False


def set_path_private_state(path: str, is_private: bool):
    return f"{path}:1" if is_private else path


def get_private_marker(item):
    return "_" if item.is_private else ""


class CreateAndBindMdlMaterialFromLibrary(omni.kit.commands.Command):
    """
    Creates material prim from Core MDL Library.
    """
    def __init__(self,
                 mdl_name: str,
                 mtl_name: str = "",
                 mtl_created_list: list = None,
                 bind_selected_prims: list = False,
                 select_new_prim: bool = True,
                 prim_name: str = "",
                 on_created_fn: callable = None):
        """
        Creates material prim from Core MDL Library, and bind to provided prim list.

        Args:
            mdl_name (str): MDL name from Core MDL Library.
            mtl_name (str): The material name from MDL. It's also the sub-identifier to be used for the shader.
                            If `prim_name` param is not specified, it will also be used as the prim_name. If mtl_name is empty,
                            it will use file name of `mdl_name` (without extension) by default.
            mtl_created_list (list): Created prims with get added to this list.
            bind_selected_prims (List[Sdf.Path]): Prims to be bound to the newly created material prim.
            select_new_prim: If it's to select the newly created material prim.
            prim_name (str): The prim name to be created. It will be created with path "/$RootPrimName/Looks/$prim_name".
                            If prim_name is not specified, it will use `mtl_name` instead.
            on_created_fn (callable): function called when material prim is created & attributes are loaded
        """
        self._mdl_name = mdl_name
        if not mtl_name:
            file_name = os.path.basename(self._mdl_name)
            self._mtl_name, _ = os.path.splitext(file_name)
        else:
            self._mtl_name = mtl_name

        self._new_looks_path = None
        self._mtl_created_list = mtl_created_list
        self._bind_selected_prims = bind_selected_prims
        self._select_new_prim = select_new_prim
        self._on_created_fn = on_created_fn
        if not prim_name:
            self._prim_name = mtl_name
        else:
            self._prim_name = prim_name

    def do(self):
        self._new_looks_path, material_prim_path = get_material_prim_path(self._prim_name)
        if self._new_looks_path:
            omni.kit.commands.execute(
                "CreatePrim", prim_path=self._new_looks_path, prim_type="Scope", select_new_prim=False
            )
        if material_prim_path:
            prim_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()

            omni.kit.commands.execute(
                "CreateMdlMaterialPrim",
                mtl_url=self._mdl_name,
                mtl_name=self._mtl_name,
                mtl_path=material_prim_path,
                select_new_prim=self._select_new_prim,
            )
            if self._bind_selected_prims:
                bind_material_to_selected_prims(material_prim_path, prim_paths)
            if self._mtl_created_list is not None:
                self._mtl_created_list.append(material_prim_path)
            if self._on_created_fn:
                async def on_completed(shader_prim):
                    self._on_created_fn(shader_prim)

                stage = omni.usd.get_context().get_stage()
                asyncio.ensure_future(on_completed(omni.usd.get_shader_from_material(stage.GetPrimAtPath(material_prim_path), True)))

    def undo(self):
        if self._new_looks_path:
            stage = omni.usd.get_context().get_stage()
            stage.RemovePrim(self._new_looks_path)


class CreateAndBindMtlxSurfaceFromLibrary(omni.kit.commands.Command):
    """
    Creates MaterialX surface material prim.
    """
    def __init__(self, mtlx_id: str = None, mtl_name: str = None, mtl_created_list: list = None, bind_selected_prims: list = False):
        """
        Creates MaterialX surface material prim.

        Args:
            mtlx_id (str): ID from MaterialX node library. It must be a surface shader node.
            mtl_name (str): The material prim name.
            mtl_created_list (list): List a add created prim to.
            bind_selected_prims (list): List of prims to bind materials to.
        """
        self._new_looks_path = None
        self._mtlx_id = mtlx_id
        self._mtl_name = mtl_name
        self._mtl_created_list = mtl_created_list
        self._bind_selected_prims = bind_selected_prims

    def do(self):
        self._new_looks_path, material_prim_path = get_material_prim_path(self._mtl_name)

        # create scope "Look"
        if self._new_looks_path:
            omni.kit.commands.execute(
                "CreatePrim", prim_path=self._new_looks_path, prim_type="Scope", select_new_prim=False
            )

        # create material prim
        stage = omni.usd.get_context().get_stage()
        material_prim_path = omni.usd.get_stage_next_free_path(stage, material_prim_path, False)
        prim = stage.DefinePrim(material_prim_path, "Material")
        if not prim:
            carb.log_error(f"failed to create material {material_prim_path}")
            self.undo()
            return

        material_prim = UsdShade.Material.Get(stage, prim.GetPath())

        node_type = "mtlx"

        # create shader node
        shader_prim = omni.kit.commands.execute(
            "CreateShaderPrimFromSdrCommand",
            parent_path=material_prim_path,
            identifier=self._mtlx_id,
            select_new_prim=True,
            node_type=node_type
        )

        if not shader_prim[1]:
            carb.log_error(f"failed to create shader {self._mtlx_id}")
            self.undo()
            return

        # connect shader output to material output "mtlx:surface"
        shader_out = shader_prim[1].GetOutput("out")
        if shader_out:
            material_prim.CreateSurfaceOutput(node_type).ConnectToSource(shader_out)

        # bind selected prim
        if self._bind_selected_prims:
            prim_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
            bind_material_to_selected_prims(material_prim_path, prim_paths)

        if self._mtl_created_list is not None:
            self._mtl_created_list.append(material_prim_path)

        # select created material prim
        omni.usd.get_context().get_selection().set_prim_path_selected(material_prim_path, True, True, True, True)

    def undo(self):
        if self._new_looks_path:
            stage = omni.usd.get_context().get_stage()
            stage.RemovePrim(self._new_looks_path)


class CreateAndBindPreviewSurfaceFromLibrary(omni.kit.commands.Command):
    """
    Creates PreviewSurface material prim.
    """
    def __init__(self, mtl_created_list: list = None, bind_selected_prims: list = False):
        """
        Creates PreviewSurface material prim.

        Args:
            mtl_created_list (list): List a add created prim to.
            bind_selected_prims (list): List of prims to bind materials to.
        """
        self._new_looks_path = None
        self._mtl_created_list = mtl_created_list
        self._bind_selected_prims = bind_selected_prims

    def do(self):
        mtl_name = "PreviewSurface"
        self._new_looks_path, material_prim_path = get_material_prim_path(mtl_name)
        if self._new_looks_path:
            omni.kit.commands.execute(
                "CreatePrim", prim_path=self._new_looks_path, prim_type="Scope", select_new_prim=False
            )
        if material_prim_path:
            prim_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()

            omni.kit.commands.execute(
                "CreatePreviewSurfaceMaterialPrim", mtl_path=material_prim_path, select_new_prim=True
            )
            if self._bind_selected_prims:
                bind_material_to_selected_prims(material_prim_path, prim_paths)
            if self._mtl_created_list is not None:
                self._mtl_created_list.append(material_prim_path)

    def undo(self):
        if self._new_looks_path:
            stage = omni.usd.get_context().get_stage()
            stage.RemovePrim(self._new_looks_path)


class CreateAndBindPreviewSurfaceTextureFromLibrary(omni.kit.commands.Command):
    """
    Creates PreviewSurfaceTexture material prim.
    """
    def __init__(self, mtl_created_list: list = None, bind_selected_prims: list = False):
        """
        Creates PreviewSurfaceTexture material prim.

        Args:
            mtl_created_list (list): List a add created prim to.
            bind_selected_prims (list): List of prims to bind materials to.
        """
        self._new_looks_path = None
        self._mtl_created_list = mtl_created_list
        self._bind_selected_prims = bind_selected_prims

    def do(self):
        mtl_name = "PreviewSurfaceTexture"
        self._new_looks_path, material_prim_path = get_material_prim_path(mtl_name)
        if self._new_looks_path:
            omni.kit.commands.execute(
                "CreatePrim", prim_path=self._new_looks_path, prim_type="Scope", select_new_prim=False
            )
        if material_prim_path:
            prim_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()

            omni.kit.commands.execute(
                "CreatePreviewSurfaceTextureMaterialPrim", mtl_path=material_prim_path, select_new_prim=True
            )
            if self._bind_selected_prims:
                bind_material_to_selected_prims(material_prim_path, prim_paths)
            if self._mtl_created_list is not None:
                self._mtl_created_list.append(material_prim_path)

    def undo(self):
        if self._new_looks_path:
            stage = omni.usd.get_context().get_stage()
            stage.RemovePrim(self._new_looks_path)


class MaterialLibraryExtension(omni.ext.IExt):
    """Material extension class."""
    class __StaticDataModel():
        def __init__(self):
            self._modal_window = None
            self._async_task = []
            self._mtl_names = {}
            self._mtl_relative_paths = {}
            self._mdl_dir = None
            self._material_subid_cache = {}
            self._material_group_cache = {}
            self._material_enum_cache = {}
            self._material_mdl_enum_list = {}

        def destroy(self):
            if self._modal_window:
                self._modal_window.destroy()

            self._modal_window = None
            self._async_task = None
            self._mtl_names = None
            self._mtl_relative_paths = None
            self._mdl_dir = None
            self._material_subid_cache = None
            self._material_group_cache = None
            self._material_enum_cache = None
            self._material_mdl_enum_list = None

        def make_path_kit(self, mdl_path):
            kit_path = carb.tokens.get_tokens_interface().resolve("${kit}").replace("\\", "/")
            if mdl_path.replace("\\", "/").lower().startswith(kit_path.lower()):
                return "${kit}" + mdl_path[len(kit_path):]
            return mdl_path

    class SubIDEntry():
        """SubIDEntry is helper class to assist with neuraylib data and name string."""
        def __init__(self, name: str, annotations: dict, is_material: bool):
            """Initialize class function.

            Args:
                name (str): Name of material  sub-identifier.
                annotations (dict): Dictionary of values from neuraylib for this material.
                is_material (bool): Is this a material entry? Value from neuraylib.
            """
            self.name = name
            self.annotations = annotations
            self.is_material = is_material

        def replace(self, oldvalue, newvalue):
            """String replace on material name.

            Args:
                oldvalue (str): The string to search for.
                newvalue (str): The string to replace the `oldvalue` with.

            Returns:
                (str): new string.
            """
            return self.name.replace(oldvalue, newvalue)

        def __str__(self) -> str:
            return self.name

        def __repr__(self) -> str:
            return self.name


    def __init__(self):
        super().__init__()
        self._ov_neuray_lib = None
        self._material_menu_list = []
        self._material_actions = set()

    def _refresh_create_menu(self):
        self._remove_create_menu()
        self._build_menus()

    def _remove_create_menu(self):
        try:
            import omni.kit.menu.utils

            if self._material_menu_list:
                omni.kit.menu.utils.remove_menu_items(self._material_menu_list, "Create")
                self._material_menu_list = []
        except ModuleNotFoundError:
            pass

    def _build_menus(self):
        try:
            from omni.kit.menu.utils import MenuItemDescription, MenuItemOrder

            sub_menu = []
            sub_menus = {}
            mat_list = omni.kit.material.library.get_material_list()
            for mat in mat_list:
                private_marker = get_private_marker(mat)
                action_name = f"{private_marker}create_{mat.name.lower().replace(' ', '_')}_material_and_assign"

                if mat.name == "GROUP":
                    sub_menu.append(MenuItemDescription(header=mat.submenu))
                elif mat.submenu:
                    if not mat.submenu in sub_menus:
                        sub_menus[mat.submenu] = []
                        sub_menu.append(
                            MenuItemDescription(
                                name=mat.submenu,
                                sub_menu=sub_menus[mat.submenu],
                            )
                        )
                    sub_menus[mat.submenu].append(MenuItemDescription(name=mat.name, onclick_action=("omni.kit.material.library", action_name)))
                else:
                    sub_menu.append(MenuItemDescription(name=mat.name, onclick_action=("omni.kit.material.library", action_name)))

            self._material_menu_list = [
                MenuItemDescription(
                    name="Material",
                    glyph="menu_material.svg",
                    appear_after=["Xform", MenuItemOrder.LAST],
                    sub_menu=sub_menu,
                )
            ]
            omni.kit.menu.utils.add_menu_items(self._material_menu_list, "Create")
        except ModuleNotFoundError:
            pass

    def on_startup(self, ext_id):
        """Startup function

        Args:
            ext_id (str): Extension id.
        """
        global material_instance

        material_instance = self

        self.menus = []
        self._material_list_refresh_list = []
        self._material_list_custom_item_list = {}
        self._static_data = MaterialLibraryExtension.__StaticDataModel()
        self._reload_mdl_subids = None
        self._preferences_pages = []
        self._hooks = []

        ext_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        self._ext_name = omni.ext.get_extension_name(ext_id)
        self._cache_filename = carb.tokens.get_tokens_interface().resolve("${cache}/material_cache.json")

        self._settings = carb.settings.get_settings()
        if self._settings:
            self._settings.set_default_string("/persistent/exts/omni.kit.material.library/browserPath", "")
            self._settings.set_default_string("/persistent/app/properties/material/mdlForceRawForUsage", "anisotropy,anisotropy_rotation,metalness,normal,occlusion,opacity,roughness,transparency")
            self._static_data._mdl_dir = self._settings.get("/persistent/exts/omni.kit.material.library/browserPath")
            self._static_data._default_lib_paths = []
            for path in carb.settings.get_settings().get(SETTING_MATERIAL_LIBRARY_LIB_PATHS):
                path, is_private = get_path_private_state(path)
                self._static_data._default_lib_paths.append(carb.tokens.get_tokens_interface().resolve(path))

        created_actions = register_actions(self._ext_name, MaterialLibraryExtension)
        self._material_actions.update(created_actions)

        omni.kit.material.library.add_material_list_refresh_callback(self._refresh_create_menu)

        # add event for when SETTING_MATERIAL_LIBRARY_LIB_PATHS changes
        self._update_setting1 = omni.kit.app.SettingChangeSubscription(SETTING_MATERIAL_LIBRARY_LIB_PATHS, self._reload_material_subids)
        self._update_setting2 = omni.kit.app.SettingChangeSubscription(SETTING_MATERIAL_LIBRARY_USD_SOURCE_ASSET_LIST, self._reload_material_subids)

        manager = omni.kit.app.get_app().get_extension_manager()
        self._hooks.append(
            manager.subscribe_to_extension_enable(
                on_enable_fn=lambda _: self._register_page(),
                on_disable_fn=lambda _: self._unregister_page(),
                ext_name="omni.kit.window.preferences",
                hook_name="omni.kit.material.library omni.kit.window.preferences listener",
            )
        )

        # initialize material watcher for fast material prim access
        # NOTE: This creates a UsdNotice handler on the default UsdContext/stage; nothing else
        #
        omni.kit.material.library.initalize_material_utils()

        self._context_menu_extensions = MaterialUIExtensions()

        # Listen for the app ready event to preload base materials
        def _on_app_ready(_):
            global material_ready_state

            self._preload_base_material()
            self._app_ready_sub = None
            material_ready_state |= ReadyState.APP_READY

        self._app_ready_sub = get_eventdispatcher().observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_APP_READY, on_event=_on_app_ready, observer_name="Material library preload"
        )

    def on_shutdown(self):
        """Shutdown function"""
        global material_ready_state

        material_ready_state = ReadyState.NOT_READY
        self._app_ready_sub = None
        deregister_actions(self._ext_name)
        self._unregister_page()

        self._free_rtx_mdl()
        omni.kit.material.library.remove_material_list_refresh_callback(self._refresh_create_menu)
        self._material_list_refresh_list = None
        self._update_menu = None
        self._remove_create_menu()
        global material_instance
        material_instance = None
        self.menus = []
        self._hooks = []
        self._static_data.destroy()
        self._static_data = None
        omni.kit.material.library.destroy_material_utils()

    def _make_path_kit(self, mdl_path):
        return self._static_data.make_path_kit(mdl_path)

    def _preload_base_material(self):
        # try to load cache data
        app = omni.kit.app.get_app()
        cache_mdl = self._settings.get_as_bool("/exts/omni.kit.material.library/cache_mdl") if self._settings else False
        cache_version = self._settings.get_as_string("/exts/omni.kit.material.library/cache_version") if self._settings else "0"
        cache_version = f"{app.get_app_name()}-{app.get_app_version()}.v{cache_version}"

        def on_load_complete():
            self._register_material_actions()
            self._build_menus()
            omni.kit.material.library.material_list_refresh()

        if cache_mdl:
            try:
                global mdl_list_cache

                def cache_built():
                    on_load_complete()

                    # save caches as json
                    cache_dict = {cache_version: {"mdl_cache": mdl_list_cache,
                                                  "mdl_groups": self._static_data._material_group_cache,
                                                  "mdl_enums": self._static_data._material_enum_cache}}

                    with open(self._cache_filename, 'w') as file:
                        file.write(json.dumps(cache_dict))

                    global material_ready_state
                    material_ready_state |= ReadyState.JSON_READY


                with open(self._cache_filename, 'r') as file:
                    # load caches from json
                    cache_dict = json.load(file)
                    # check its correct version
                    if not cache_version in cache_dict:
                        raise FileNotFoundError(f"{self._cache_filename} is incorrect version")

                    mdl_list_cache.update(cache_dict[cache_version]["mdl_cache"])
                    self._static_data._material_group_cache.update(cache_dict[cache_version]["mdl_groups"])
                    self._static_data._material_enum_cache.update(cache_dict[cache_version]["mdl_enums"])

                    carb.log_info(f"Material cache loaded {self._cache_filename}")
                    # preload OmniPBR material only
                    asyncio.ensure_future(self.__preload_base_material_subids(on_complete_fn=cache_built, only_preload=["OmniPBR.mdl"], spreadload=False))
                    on_load_complete()
            except (json.JSONDecodeError, FileNotFoundError, KeyError, IndexError) as error:
                carb.log_info(f"Failed to load {self._cache_filename}. Regenerating material cache")
                asyncio.ensure_future(self.__preload_base_material_subids(on_complete_fn=cache_built, spreadload=False))
        else:
            carb.log_info("Material caching disabled")
            asyncio.ensure_future(self.__preload_base_material_subids(on_complete_fn=on_load_complete, spreadload=True))

    def _register_page(self):
        from omni.kit.window.preferences import register_page
        from .pages.material_page import MaterialPreferences
        from .pages.rendering_page import RenderingPreferences

        self._preferences_pages.append(register_page(MaterialPreferences()))
        self._preferences_pages.append(register_page(RenderingPreferences()))

    def _unregister_page(self):
        if self._preferences_pages:
            import omni.kit.window.preferences

            for page in self._preferences_pages:
                omni.kit.window.preferences.unregister_page(page)

            self._preferences_pages = None

    def _reload_material_subids(self, new_lib_paths, event_type):
        global material_ready_state

        if event_type != carb.settings.ChangeEventType.CHANGED or material_ready_state != ReadyState.ALL_READY or self._reload_mdl_subids:
            return

        async def load_mdl_subids():
            global material_ready_state

            self._reload_mdl_subids = None
            new_lib_paths = carb.settings.get_settings().get(SETTING_MATERIAL_LIBRARY_LIB_PATHS)
            carb.log_warn(f"/exts/omni.kit.material.library/lib_paths has changed to \"{new_lib_paths}\" reloading subid & rebuilding menus")

            if self._material_menu_list:
                self._remove_create_menu()

            mdl_list_cache["all"] = []
            mdl_list_cache["hidden"] = []

            await self.__preload_base_material_subids()
            self._register_material_actions()
            self._build_menus()
            omni.kit.material.library.material_list_refresh()

            material_ready_state = ReadyState.ALL_READY

        # set NOT_READY so get_mdl_list_async won't return until ALL_READY is set by load_mdl_subids
        material_ready_state = ReadyState.NOT_READY
        self._reload_mdl_subids = asyncio.ensure_future(load_mdl_subids())

    def _preload_rtx_mdl(self):
        try:
            import omni.mdl.neuraylib

            if not self._ov_neuray_lib:
                self._ov_neuray_lib = omni.mdl.neuraylib.get_neuraylib()
        except:
            carb.log_warn("failed to import omni.mdl.neuraylib")

    def _free_rtx_mdl(self):
        self._ov_neuray_lib = None

    async def __preload_base_material_subids(self, on_complete_fn: callable=None, only_preload:str="", spreadload: bool=False):
        global mdl_list_cache

        mdl_lib_paths = get_mdl_lib_paths_private()
        hidden_list = get_material_hidden_list()
        mdl_list = []
        mdl_list_hidden = []
        if only_preload:
            mdl_list = mdl_list_cache["all"]
            mdl_list_hidden = mdl_list_cache["hidden"]

        if spreadload:
            # wait for vsync to prevent startup time hogging
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()

        def populate_list(subid_list, mdl_path, mdl_name, target_list, is_private):
            if len(subid_list) == 1:
                # NOTE: Must be List NOT Tuple's. json can't save Tuple and will convert them
                # to Lists. Then on cache reload the `new_item in target_list` will not work.

                new_item = [mdl_name, self._make_path_kit(mdl_path), None, is_private]
                if not new_item in target_list:
                    target_list.append(new_item)
            else:
                for subid in subid_list:
                    # NOTE: Must be List NOT Tuple's. json can't save Tuple and will convert them
                    # to Lists. Then on cache reload the `new_item in target_list` will not work.
                    new_item = [str(subid), self._make_path_kit(mdl_path), mdl_name, is_private]
                    if not new_item in target_list:
                        target_list.append(new_item)

        for dirpath, is_private in mdl_lib_paths:
            (result, entries) = await omni.client.list_async(dirpath)
            if result != omni.client.Result.OK:
                carb.log_error(f"preload_base_material_subids {result} reading {dirpath}")
                continue

            for entry in entries:
                mtl_name = entry.relative_path

                if only_preload and not mtl_name in only_preload:
                    continue

                if spreadload:
                    # wait for vsync to prevent startup time hogging
                    await omni.kit.app.get_app().next_update_async()

                mdl_path = omni.client.combine_urls(f"{dirpath}/", mtl_name)
                name, ext = os.path.splitext(mtl_name)

                if ext.lower() != ".mdl":
                    continue

                subid_list = await self.get_subidentifier_from_mdl(mdl_path)
                self._static_data._mtl_names[mtl_name] = [mtl_name, mdl_path, subid_list]
                # TODO key 'mtl_name' does not have a '.mdl' extension but all existing entries have

                populate_list(subid_list, mdl_path, name, mdl_list, is_private)
                if not mdl_path.lower() in (name.lower() for name in hidden_list):
                    populate_list(subid_list, mdl_path, name, mdl_list_hidden, is_private)

        mdl_list_cache["all"] = mdl_list
        mdl_list_cache["hidden"] = mdl_list_hidden

        if on_complete_fn:
            on_complete_fn()

    def _register_material_actions(self):
        for mat in omni.kit.material.library.get_material_list():
            if mat.name != "GROUP":
                private_marker = get_private_marker(mat)
                action_name = f"{private_marker}create_{mat.name.lower().replace(' ', '_')}_material_and_assign"

                if not action_name in self._material_actions:
                    self._material_actions.add(action_name)
                    omni.kit.actions.core.get_action_registry().register_action(
                        self._ext_name,
                        action_name,
                        mat.create_fn,
                        display_name=action_name,
                        description=f"Create {mat.name} Material & Assign To Selected Prims",
                        tag="Material Library Actions"
                    )

    def _show_alert_message(self, message):
        import omni.kit.notification_manager as nm
        return nm.post_notification(message, status=nm.NotificationStatus.WARNING)

    def remove_mdl_from_cache(self, shader_prim_path: str):
        """
        Remove material from cache. Call by Material Watcher when re-loading modified mdl files.

        Args:
            shader_prim_path (str): material prim path to remove from cache.
        """
        # get mdl name from prim
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(shader_prim_path) if stage and shader_prim_path else None
        shader = UsdShade.Shader(prim) if prim else None
        asset = shader.GetSourceAsset("mdl") if shader else None
        mdl_file = asset.resolvedPath if asset else None
        kit_mdl_file = self._make_path_kit(mdl_file) if mdl_file else None

        if mdl_file:
            if kit_mdl_file in self._static_data._material_subid_cache:
                del self._static_data._material_subid_cache[kit_mdl_file]
            if kit_mdl_file in self._static_data._material_group_cache:
                del self._static_data._material_group_cache[kit_mdl_file]
            if kit_mdl_file in self._static_data._material_mdl_enum_list:
                for enum in self._static_data._material_mdl_enum_list[kit_mdl_file]:
                    del self._static_data._material_enum_cache[enum]
                del self._static_data._material_mdl_enum_list[kit_mdl_file]

    async def get_subidentifier_from_material(self, prim, on_complete_fn: callable, use_functions: bool=False, show_alert: bool=False):
        """
        get sub-identifier list from material prim asynchronously.

        Args:
            prim (Usd.Prim): prim to get material & material sub-identifiers from.
            on_complete_fn (callable): function to call with list of sub-identifier when completed.
            use_functions (bool): if True only list materials and not functions otherwise return all sub-identifiers.
            show_alert (bool): show alert if bad material.

        Returns:
            (list): list of sub-identifier

        """
        # get mdl name from prim
        usd_prim = prim.prim if hasattr(prim, "prim") else prim
        shader = UsdShade.Shader(usd_prim)
        asset = shader.GetSourceAsset("mdl") if shader else None
        mdl_file = asset.resolvedPath if asset else None
        if not mdl_file:
            on_complete_fn([])
            return []
        return await self.get_subidentifier_from_mdl(mdl_file, on_complete_fn, use_functions, show_alert)

    async def get_subidentifier_from_mdl(self, mdl_file: str, on_complete_fn: callable=None, use_functions: bool=False, show_alert: bool=False):
        """
        get sub-identifier list from mdl file asynchronously.

        Args:
            mdl_file (str): mdl_file to get material sub-identifiers from.
            on_complete_fn (callable): function to call with list of sub-identifier when completed.
            use_functions (bool): if True only list materials and not functions otherwise return all sub-identifiers.
            show_alert (bool): show alert if bad material.

        Returns:
            (list): list of sub-identifier

        """
        if not mdl_file:
            carb.log_error(f"get_subidentifier_from_mdl: no mdl_file")
            if on_complete_fn:
                on_complete_fn([])
            return []

        kit_mdl_file = self._make_path_kit(mdl_file) if mdl_file else None
        if kit_mdl_file in self._static_data._material_subid_cache:
            subid_list = self._static_data._material_subid_cache[kit_mdl_file]
            if not use_functions:
                subid_list = [item for item in subid_list if item.is_material]

            if not subid_list and show_alert:
                self._show_alert_message(f"{os.path.basename(mdl_file)} doesn't contain any usable materials")

            if on_complete_fn:
                on_complete_fn(subid_list)
            return subid_list

        def get_func_parameter_types(func, for_display):
            parameter_type_names = ""
            if len(func.parameterTypeNames) > 0:
                parameter_type_names += "("
                for t in func.parameterTypeNames:
                    parameter_type_names += f"{t}, " if for_display else f"{t},"
                parameter_type_names = (parameter_type_names[:-2] if for_display else parameter_type_names[:-1]) + ")"
            else:
                parameter_type_names = "()"
            return parameter_type_names

        def get_func_annotations(func, is_material):
            annotations = {}
            parameter_type_names = get_func_parameter_types(func, False)
            parameter_type_names_for_display = get_func_parameter_types(func, True)

            if func.annotations:
                anno: pymdl.Annotation
                for anno in func.annotations:
                    arg: pymdl.Argument
                    for arg_name, arg in anno.arguments.items():
                        if arg_name != "collapsed": # ignoring that for now TODO handle it properly
                            annotations[anno.simpleName] = arg.value # note, this only takes the deepest name as group name
                                                                     # they, should be nested if subgroup and sub-subgroup
                                                                     # are available
            if not "display_name" in annotations:
                # add a display name even if there is none
                annotations["display_name"] = f"{func.mdlSimpleName}"

            # overriding display name is not the best option however.. we might need the old. create a new one.
            display_name = annotations["display_name"]
            if is_material:
                annotations["subid_token"] = func.mdlSimpleName
                annotations["subid_display_name"] = display_name
            else:
                annotations["subid_token"] = f"{func.mdlSimpleName}{parameter_type_names}" if full_subid_list else func.mdlSimpleName
                annotations["subid_display_name"] = f"{display_name} {parameter_type_names_for_display}" if full_subid_list else display_name

            return annotations

        def get_module(module, transaction, static_data: MaterialLibraryExtension.__StaticDataModel):
            from omni.mdl import pymdl, pymdlsdk
            nonlocal subid_list

            neuray = pymdlsdk.attach_ineuray(self._ov_neuray_lib.getNeurayAPI())

            def isMaterial(transaction: pymdlsdk.ITransaction, functionDbName: str):
                with transaction.access_as(pymdlsdk.IFunction_definition, functionDbName) as m:
                    return m.is_material()

            def isExported(transaction: pymdlsdk.ITransaction, functionDbName: str):
                with transaction.access_as(pymdlsdk.IFunction_definition, functionDbName) as f:
                    return f.is_exported()

            def inspect_enum(ee : pymdlsdk.IType_enumeration, enums):
                if ee.is_valid_interface():
                    enum_symbol: str = ee.get_symbol()
                    for index in range(ee.get_size()):
                        enum_name: str = ee.get_value_name(index)
                        enum_display_name: str = enum_name
                        annotations = pymdl.AnnotationBlock(ee.get_value_annotations(index))
                        for a in annotations:
                            if a._simpleName == 'display_name':
                                enum_display_name = a._arguments.get("name").value

                        enums[enum_name] = enum_display_name

            with neuray.get_api_component(pymdlsdk.IMdl_factory) as mdl_factory, \
                 mdl_factory.create_type_factory(transaction) as tf:

                for funcName in module.functions:
                    overloads = module.functions[funcName]

                    process_overloads: bool = True
                    for func in overloads:
                        func: pymdl.FunctionDefinition = func
                        if not process_overloads:
                            break

                        if isExported(transaction, func.dbName):
                            # loop over the parameter types to see if we need to add enums to the cache
                            for arg in func.parameters.values():
                                arg: pymdl.Argument = arg
                                arg_type: pymdl.Type = arg.type
                                if arg_type.kind == pymdlsdk.IType.Kind.TK_ENUM:
                                    arg_type_symbol: str = arg_type.symbol

                                    # add the enum info to the cache
                                    if arg_type_symbol not in static_data._material_enum_cache:
                                        ee = tf.create_enum(arg_type_symbol)
                                        if ee.is_valid_interface():
                                            static_data._material_enum_cache[arg_type_symbol] = {}
                                            inspect_enum(ee.get_interface(pymdlsdk.IType_enumeration), static_data._material_enum_cache[arg_type_symbol])
                                            if not mdl_file in static_data._material_mdl_enum_list:
                                                static_data._material_mdl_enum_list[mdl_file] = []
                                            if not arg_type_symbol in static_data._material_mdl_enum_list[mdl_file]:
                                                static_data._material_mdl_enum_list[mdl_file].append(arg_type_symbol)

                            if process_overloads:
                                is_material = isMaterial(transaction, func.dbName)
                                annotations = get_func_annotations(func, is_material)
                                subid_list.append(MaterialLibraryExtension.SubIDEntry(func.mdlSimpleName, annotations, is_material))
                                if not full_subid_list:
                                    process_overloads = False  # Kai Rohmer: use only 1st one, this makes the annotations questionable though


        def cmp_iu_order(a, b):
            ui_order_a = 0
            ui_order_b = 0
            if "ui_order" in a.annotations:
                ui_order_a = int(a.annotations["ui_order"])
            if "ui_order" in b.annotations:
                ui_order_b = int(b.annotations["ui_order"])

            if ui_order_a > ui_order_b:
                return 1
            elif ui_order_a < ui_order_b:
                return -1
            return 0

        subid_list = []
        if not await self.__process_rtx_neuraylib(mdl_file, get_module) and show_alert:
            self._show_alert_message(f"{os.path.basename(mdl_file)} can not be loaded. Are there syntax errors?")
            return subid_list # return and don't fill the cache

        subid_list = sorted(subid_list, key=functools.cmp_to_key(cmp_iu_order))
        kit_mdl_file = self._make_path_kit(mdl_file) if mdl_file else None

        if subid_list:
            self._static_data._material_subid_cache[kit_mdl_file] = subid_list

        if not use_functions:
            subid_list = [item for item in subid_list if item.is_material]
        if not subid_list and show_alert:
            self._show_alert_message(f"{os.path.basename(mdl_file)} doesn't contain any usable materials")

        if on_complete_fn:
            on_complete_fn(subid_list)
        return subid_list

    async def __process_rtx_neuraylib(self, mdl_file: str, module_process_fn: callable):
        module = None
        transaction = None

        # load rtx_neuray_lib
        if not self._ov_neuray_lib:
            self._preload_rtx_mdl()
            if not self._ov_neuray_lib:
                return False

        try:
            from omni.mdl import pymdlsdk
            from omni.mdl import pymdl

            # we need to load modules to OV using the omni.mdl.neuraylib
            # on the c++ side this is async, here it is blocking if the module is not loaded yet by the renderer
            ov_module = await omni.mdl.neuraylib.create_mdl_module_async(mdl_file)

            # when the module is loaded we can use the high-level python binding to inspect the module
            if ov_module and ov_module.valid():
                # feed the transaction instance into the python binding
                ov_neuray_lib_transaction_handle = self._ov_neuray_lib.createReadingTransaction(ov_module.dbScopeName)
                transaction: pymdlsdk.ITransaction = pymdlsdk.attach_itransaction(ov_neuray_lib_transaction_handle)
                module: pymdl.Module = pymdl.Module._fetchFromDb(transaction, ov_module.dbName)

                # you can already free all low level objects here
                self._ov_neuray_lib.destroyMdlModule(ov_module)

                # inspect the module
                if module:
                    module_process_fn(module, transaction, self._static_data)
        finally:
            # release the transaction and neuray
            if transaction:
                transaction.abort()
            transaction = None

        if module == None:
            carb.log_warn(f"process_ov_neuraylib: failed to get module from {mdl_file}")
            # in case the `ov_module`` or `module` is invalid we report False to not fill the cache
            return False
        else:
            return True

    @staticmethod
    def _create_material_and_assign(create_fn, *_):
        usd_context = omni.usd.get_context()
        with omni.kit.usd.layers.active_authoring_layer_context(usd_context):
            create_fn(bind_selected_prims=True)

    @staticmethod
    def _show_mdl_importer(title: str, click_apply_fn: callable = None):
        try:
            from omni.kit.window.file_importer import get_file_importer

            def on_filter_item(filename: str, filter_postfix: str, filter_ext: str) -> bool:
                if filename:
                    _, ext = os.path.splitext(filename)
                    if filter_ext == "*":
                        return True
                    elif filter_ext == "*.mdl" and ext == ".mdl":
                        return True
                    else:
                        return False
                return True

            file_importer = get_file_importer()
            if file_importer:
                file_importer.show_window(
                    title=title,
                    import_button_label="Select",
                    import_handler=click_apply_fn,
                    file_postfix_options=None,
                    file_extension_types=[("*.mdl", "MDL Files"), ("*", "All Files")],
                    file_filter_handler=on_filter_item,
                )
        except ModuleNotFoundError:
            pass

    @staticmethod
    def _show_mtlx_importer(title: str, click_apply_fn: callable=None):
        try:
            from omni.kit.window.file_importer import get_file_importer

            def on_filter_item(filename: str, filter_postfix: str, filter_ext: str) -> bool:
                if filename:
                    _, ext = os.path.splitext(filename)
                    if filter_ext == "*":
                        return True
                    elif filter_ext == "*.mtlx" and ext == ".mtlx":
                        return True
                    else:
                        return False
                return True

            file_importer = get_file_importer()
            if file_importer:
                file_importer.show_window(
                    title=title,
                    import_button_label="Select",
                    import_handler=click_apply_fn,
                    file_postfix_options=None,
                    file_extension_types=[("*.mtlx", "MTLX Files"), ("*", "All Files")],
                    file_filter_handler=on_filter_item,
                )
        except ModuleNotFoundError:
            pass

    @staticmethod
    def _custom_material_dialog(static_data: __StaticDataModel, absolute_mdl_path: str, on_complete_fn: callable, bind_prim_paths: list):
        import omni.ui as ui
        from omni.kit.window.filepicker import FilePickerDialog

        relative_mdl_path = omni.usd.make_path_relative_to_current_edit_target(absolute_mdl_path)
        if absolute_mdl_path and relative_mdl_path and os.path.normpath(absolute_mdl_path) != os.path.normpath(relative_mdl_path):
            static_data._mtl_relative_paths[absolute_mdl_path] = relative_mdl_path

        class ComboListItem(ui.AbstractItem):
            def __init__(self, item):
                super().__init__()
                if isinstance(item, MaterialLibraryExtension.SubIDEntry):
                    self.real_value = item.name
                    if "subid_display_name" in item.annotations:
                        self.model = ui.SimpleStringModel(item.annotations['subid_display_name'])
                    elif "display_name" in item.annotations:
                        self.model = ui.SimpleStringModel(item.annotations['display_name'])
                    else:
                        self.model = ui.SimpleStringModel(item.name)
                else:
                    self.real_value = item
                    self.model = ui.SimpleStringModel(item)

        class ComboListModel(ui.AbstractItemModel):
            def __init__(self, item_list, default_index):
                super().__init__()
                self._default_index = default_index
                self._current_index = ui.SimpleIntModel(default_index)
                self._current_index.add_value_changed_fn(lambda a: self._item_changed(None))
                self._item_list = item_list
                self._items = []
                if item_list:
                    for item in item_list:
                        self._items.append(ComboListItem(item))

            def get_item_children(self, item):
                return self._items

            def get_item_list(self):
                return self._item_list

            def get_item_value_model(self, item=None, column_id=-1):
                if item is None:
                    return self._current_index
                return item.model

            def get_current_index(self):
                return self._current_index.get_value_as_int()

            def set_current_index(self, index):
                self._current_index.set_value(index)

            def get_current_string(self):
                return self._items[self._current_index.get_value_as_int()].model.get_value_as_string()

            def get_real_current_string(self):
                return self._items[self._current_index.get_value_as_int()].real_value

            def is_default(self):
                return self.get_current_index() == self._default_index


        def close_modal_window():
            static_data._modal_window.visible = False

            async def free():
                static_data._modal_window.destroy()
                static_data._modal_window = None

            asyncio.ensure_future(free())


        def create_material(mdl_combo: ui.ComboBox, subid_combo: ui.ComboBox):
            mdl_name = mdl_combo.model.get_real_current_string()
            mdl_real_subid_name = subid_combo.model.get_real_current_string()
            mdl_display_subid_name = subid_combo.model.get_current_string()

            def on_create(material_prim):
                shader = UsdShade.Material(material_prim).ComputeSurfaceSource("mdl")[0]
                # TODO encoded names
                # make sure the sub-identifier is correct for functions and materials
                # materials need to strip the parameter type list
                # functions are stored with signature
                shader.SetSourceAssetSubIdentifier(mdl_real_subid_name, "mdl")

                paths = []
                if bind_prim_paths:
                    # convert str/Sdf.Paths to list[str] without triggering Sdf.Path warnings
                    paths = list(filter(None, [path.pathString if isinstance(path, Sdf.Path) else path for path in bind_prim_paths]))

                if paths:
                    omni.kit.commands.execute(
                        "BindMaterialCommand",
                        prim_path=paths,
                        material_path=material_prim.GetPath(),
                        strength=None,
                    )
                    omni.usd.get_context().get_selection().set_selected_prim_paths(paths, True)
                else:
                    omni.usd.get_context().get_selection().set_selected_prim_paths([material_prim.GetPath().pathString], True)

                if on_complete_fn:
                    on_complete_fn(material_prim)

            mtl_name, mdl_path, _ = static_data._mtl_names[mdl_name]

            stage = omni.usd.get_context().get_stage()
            close_modal_window()
            create_mdl_material(stage=stage, mtl_url=mdl_path, mtl_name=mdl_display_subid_name, mtl_real_name=mdl_real_subid_name, on_create_fn=on_create)

        def mdl_combo_set_on_changed(mdl_combo):
            def combo_changed(combo_model, item):
                key = mdl_combo.model.get_current_string()
                if key in static_data._mtl_names:
                    mtl_name, mdl_path, mtl_subids = static_data._mtl_names[key]
                    subid_combo.model = ComboListModel(mtl_subids, 0)

            mdl_combo.model.add_item_changed_fn(combo_changed)


        def mdl_browser_select(filename: str, dirname: str, mdl_combo: ui.ComboBox, subid_combo: ui.ComboBox):
            if dirname:
                static_data._mdl_dir = dirname
                carb.settings.get_settings().set_string("/persistent/exts/omni.kit.material.library/browserPath", dirname)

            mdl_path = None
            if dirname:
                mdl_path = f"{dirname}/{filename}"
            elif filename:
                mdl_path = filename

            def loaded_mdl_subids(mtl_list, filename):
                try:
                    mtl_name, mdl_path, _ = static_data._mtl_names[filename]
                    static_data._mtl_names[filename] = [mtl_name, mdl_path, mtl_list]

                    item_list = mdl_combo.model.get_item_list()
                    if item_list:
                        item_list.append(filename)
                    else:
                        item_list = [filename]
                    mdl_combo.model = ComboListModel(item_list, len(item_list)-1)
                    mdl_combo_set_on_changed(mdl_combo)
                    subid_combo.model = ComboListModel(mtl_list, 0)
                except Exception as exc:
                    carb.log_error(f"error {exc}")

            mtl_name = os.path.basename(mdl_path)
            static_data._mtl_names[filename] = [mtl_name, mdl_path, None]
            static_data._async_task.append(
                asyncio.ensure_future(
                    omni.kit.material.library.get_subidentifier_from_mdl(mdl_file=mdl_path, on_complete_fn=lambda l, f=filename: loaded_mdl_subids(mtl_list=l, filename=f))))

        materials_list = []
        materials_index = 0
        for key in static_data._mtl_names:
            mtl_name, mdl_path, mtl_subids = static_data._mtl_names[key]
            materials_list.append(key)

        window_flags = ui.WINDOW_FLAGS_NO_RESIZE | ui.WINDOW_FLAGS_NO_SCROLLBAR #ui.WINDOW_FLAGS_MODAL
        static_data._modal_window = ui.Window("Create Material", width=600, height=150, flags=window_flags, visible=False)
        with static_data._modal_window.frame:
            with ui.VStack(height=0):
                ui.Spacer(height=15)
                with ui.HStack():
                    ui.Spacer(width=25)
                    ui.Label("Identifier", width=100)
                    mdl_combo = ui.ComboBox(ComboListModel(materials_list, materials_index), height=10)
                    ui.Spacer(width=5)
                    browser_icon = ui.Button("", width=20, height=20, style={"margin": 0, "image_url": "resources/icons/folder.png"}, identifier="create_material_browse_files")
                    ui.Spacer(width=25)

                ui.Spacer(height=10)

                with ui.HStack():
                    ui.Spacer(width=25)
                    ui.Label("subIdentifier", width=100)
                    subid_combo = ui.ComboBox(ComboListModel([], -1), height=10, identifier="create_material_subid_combo")
                    ui.Spacer(width=25)

                ui.Spacer(height=20)

                with ui.HStack():
                    ui.Spacer(width=200)
                    ui.Button("Create", width=100, clicked_fn=lambda w1=mdl_combo, w2=subid_combo: create_material(w1, w2), identifier="create_material_ok_button")
                    ui.Button("Cancel", width=100, clicked_fn=close_modal_window, identifier="create_material_cancel_button")


        mdl_combo_set_on_changed(mdl_combo)

        # update subid_combo
        if materials_list:
            mtl_name, mdl_path, mtl_subids = static_data._mtl_names[materials_list[materials_index]]
        else:
            mtl_subids = []

        subid_combo.model = ComboListModel(mtl_subids, 0)

        import_handler = lambda filename, dirname, selections: MaterialLibraryExtension._on_selected_mdl(filename, dirname)
        browser_icon.set_mouse_pressed_fn(lambda x, y, b, m: MaterialLibraryExtension._show_mdl_importer("Select MDL###custom_dialog", import_handler))

        if absolute_mdl_path:
            try:
                filename = os.path.basename(absolute_mdl_path)
                dirname = os.path.dirname(absolute_mdl_path)
                mdl_browser_select(filename, dirname, mdl_combo, subid_combo)
            except Exception as exc:
                carb.log_error(f"error {exc}")

        static_data._modal_window.visible = True


    @staticmethod
    async def _on_create_mdl_material(mdl_url: str, mdl_name: str, mtl_name: str, mtl_created_list: list = None, bind_selected_prims: list = False, prim_name: str = ""):
        static_data = material_instance._static_data

        # materials from default lib_paths don't use full paths, ones added to lib_paths later need to
        use_full_path = True
        for path in static_data._default_lib_paths:
            if path.lower() in mdl_url.lower():
                use_full_path = False
                break

        if bind_selected_prims == None:
            bind_selected_prims = omni.usd.get_context().get_selection().get_selected_prim_paths()

        get_subids = True
        if mtl_name in static_data._mtl_names:
            mtl_name, mdl_url, subid_list = static_data._mtl_names[mtl_name]
            get_subids = False if subid_list else True

        if get_subids:
            subid_list = await omni.kit.material.library.get_subidentifier_from_mdl(mdl_url)
            static_data._mtl_names[mtl_name] = [mtl_name, mdl_url, subid_list]

        omni.kit.commands.execute(
            "CreateAndBindMdlMaterialFromLibrary",
            mdl_name=mdl_url if use_full_path else mdl_name,
            mtl_name=mtl_name,
            mtl_created_list=mtl_created_list,
            bind_selected_prims=bind_selected_prims,
            prim_name=prim_name
        )


    @staticmethod
    def _on_create_mtlx_material(mtlx_id: str, mtl_name: str, mtl_created_list: list = None, bind_selected_prims: list = False):
        omni.kit.commands.execute(
            "CreateAndBindMtlxSurfaceFromLibrary",
            mtlx_id=mtlx_id,
            mtl_name=mtl_name,
            mtl_created_list=mtl_created_list,
            bind_selected_prims=bind_selected_prims
        )


    @staticmethod
    def _on_create_preview_surface(mtl_created_list=None, bind_selected_prims=True):
        omni.kit.commands.execute(
            "CreateAndBindPreviewSurfaceFromLibrary",
            mtl_created_list=mtl_created_list,
            bind_selected_prims=bind_selected_prims,
        )


    @staticmethod
    def _on_create_preview_surface_texture(mtl_created_list=None, bind_selected_prims=True):
        omni.kit.commands.execute(
            "CreateAndBindPreviewSurfaceTextureFromLibrary",
            mtl_created_list=mtl_created_list,
            bind_selected_prims=bind_selected_prims,
        )


    @staticmethod
    def _on_create_custom_mdl_material(mtl_created_list=None, bind_selected_prims=True):
        bind_prim_paths = []
        if bind_selected_prims:
            bind_prim_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()

        MaterialLibraryExtension._show_mdl_importer("Select MDL", lambda filename, dirname, selections: MaterialLibraryExtension._on_selected_mdl(filename, dirname, bind_prim_paths))


    @staticmethod
    def _on_create_custom_mtlx_material(mtl_created_list=None, bind_selected_prims=True):
        bind_prim_paths = []
        if bind_selected_prims:
            bind_prim_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()

        MaterialLibraryExtension._show_mtlx_importer("Select MTLX", lambda filename, dirname, selections: MaterialLibraryExtension._on_selected_mtlx(filename, dirname, bind_prim_paths))


    @staticmethod
    def _on_selected_mdl(filename: str, dirname: str, bind_prim_paths=[]):
        if dirname and filename:
            mdl_path = f"{dirname}/{filename}"
        elif filename:
            mdl_path = filename
        else:
            return


        def bind_mdl(mdl_prim: Usd.Prim):
            material_strength = UsdShade.Tokens.weakerThanDescendants
            omni.kit.commands.execute(
                "BindMaterial", prim_path=bind_prim_paths, material_path=mdl_prim.GetPath(), strength=material_strength
            )
            omni.usd.get_context().get_selection().set_selected_prim_paths([mdl_prim.GetPath().pathString], True)

        def loaded_mdl_subids(mtl_list: list, filename: str):
            if len(mtl_list) > 1:
                omni.kit.material.library.custom_material_dialog(mdl_path=mdl_path, on_complete_fn=None, bind_prim_paths=bind_prim_paths)
                return

            stage = omni.usd.get_context().get_stage()
            mtl_name, _ = os.path.splitext(os.path.basename(mdl_path))
            bind_material_path = omni.kit.material.library.create_mdl_material(
                stage=stage,
                mtl_url=mdl_path,
                mtl_name=mtl_name,
                on_create_fn=bind_mdl,
                mtl_real_name=mtl_list[0].name if len(mtl_list) > 0 else "")

        asyncio.ensure_future(omni.kit.material.library.get_subidentifier_from_mdl(mdl_path, lambda l, f=filename: loaded_mdl_subids(mtl_list=l, filename=f)))


    @staticmethod
    def _on_selected_mtlx(filename: str, dirname: str, bind_prim_paths=[]):
        if dirname and filename:
            mtlx_path = f"{dirname}/{filename}"
        elif filename:
            mtlx_path = filename
        else:
            return

        def bind_material(mtl_prim: Usd.Prim):
            omni.kit.commands.execute(
                "BindMaterial",
                prim_path=bind_prim_paths,
                material_path=mtl_prim.GetPath(),
                strength=UsdShade.Tokens.weakerThanDescendants
            )
            omni.usd.get_context().get_selection().set_selected_prim_paths([mtl_prim.GetPath().pathString], True)

        stage = omni.usd.get_context().get_stage()
        omni.kit.material.library.create_mtlx_material(
            stage=stage,
            mtlx_url=mtlx_path,
            on_create_fn=bind_material
        )

    def get_cache_filename(self):
        return omni.usd.correct_filename_case(self._cache_filename)

def get_mdl_lib_paths():
    """
    Get material library paths. Which is "/exts/omni.kit.material.library/lib_paths"

    Returns:
        (list): list of paths
    """
    mdl_lib_paths = []
    for path in carb.settings.get_settings().get(SETTING_MATERIAL_LIBRARY_LIB_PATHS):
        path, is_private = get_path_private_state(path)
        mdl_lib_paths.append(carb.tokens.get_tokens_interface().resolve(path))

    return mdl_lib_paths

def get_mdl_lib_paths_private():
    """
    Get material library paths with additional private info. Which is "/exts/omni.kit.material.library/lib_paths"

    Returns:
        (list): list of tuple(path, is_private)
    """
    mdl_lib_private = []
    for path in carb.settings.get_settings().get(SETTING_MATERIAL_LIBRARY_LIB_PATHS):
        path, is_private = get_path_private_state(path)
        mdl_lib_private.append((carb.tokens.get_tokens_interface().resolve(path), is_private))

    return mdl_lib_private

def get_mdl_usd_source_asset_list():
    """
    Get material source asset file, from "/exts/omni.kit.material.library/usd_source_asset_list".
    used by `add_usd_source_asset_path_to_mtl_lib` function.
    """
    source_asset_list_json = carb.settings.get_settings().get(SETTING_MATERIAL_LIBRARY_USD_SOURCE_ASSET_LIST)
    if not source_asset_list_json:
        return []
    return json.loads(str(source_asset_list_json))

def get_material_hidden_list():
    """
    Gets list of hidden materials, which is /exts/omni.kit.material.library/ui_hidden_list.
    """
    hidden_list = []
    hidden_mdls = carb.settings.get_settings().get("/exts/omni.kit.material.library/ui_hidden_list")
    for mdl in hidden_mdls:
        hidden_list.append(os.path.normpath(carb.tokens.get_tokens_interface().resolve(mdl)).replace("\\", "/"))
    return hidden_list

def get_material_show_list():
    """
    Get material show list, this is used to create a subset of materials for `get_material_list` function.
    Uses "/exts/omni.kit.material.library/ui_show_list"
    """
    show_list = []
    show_mdls = carb.settings.get_settings().get("/exts/omni.kit.material.library/ui_show_list")
    for mdl in show_mdls:
        show_list.append(os.path.normpath(carb.tokens.get_tokens_interface().resolve(mdl)).replace("\\", "/"))
    return show_list

async def get_mdl_list_async(use_hidden=False, wait_for_ready=True, get_private=False, expand_paths: bool=True):
    """
    Gets list of materials asynchronously. Can wait if mdl_list_cache is not complete yet.

    Args:
        use_hidden (bool): Include hidden materials. See `get_material_hidden_list`
        get_private (bool): Including private parameter in list
        expand_paths (bool): List with absolute paths not ${kit} tokens

    Returns:
        (list): list of materials
    """
    max_wait = 1000
    while not mdl_list_cache or (wait_for_ready and material_ready_state != ReadyState.ALL_READY):
        await omni.kit.app.get_app().next_update_async()
        max_wait -= 1
        if max_wait == 0:
            carb.log_warn(f"get_mdl_list_async: mdl_list_cache is not complete")
            return []

    return get_mdl_list(use_hidden, get_private, expand_paths)


def get_mdl_list(use_hidden: bool=False, get_private: bool=False, expand_paths: bool=True):
    """
    Gets list of materials asynchronously. Can return [] if mdl_list_cache is not complete yet.

    Args:
        use_hidden (bool): Include hidden materials. See `get_material_hidden_list`
        get_private (bool): Including private parameter in list
        expand_paths (bool): List with absolute paths not ${kit} tokens

    Returns:
        (list): list of materials
    """
    if not mdl_list_cache:
        carb.log_warn(f"get_mdl_list: mdl_list_cache is not complete")
        return []

    if use_hidden:
        mdl_list = mdl_list_cache["hidden"]
    else:
        mdl_list = mdl_list_cache["all"]

    new_mdl_list = mdl_list
    if expand_paths:
        # paths are expected to be absolute, so expand paths
        new_mdl_list = []
        for a, b, c, d in mdl_list:
            new_mdl_list.append((a, carb.tokens.get_tokens_interface().resolve(b), c, d))

    if get_private:
        return new_mdl_list

    return [(a, b, c) for a, b, c, d in new_mdl_list]


def add_material_list_refresh_callback(on_refresh_fn: callable):
    """
    Add callback to trigger when material library UI refreshes.

    Args:
        on_refresh_fn (callable): Callback to be called when UI refreshes.
    """
    if material_instance and not on_refresh_fn in material_instance._material_list_refresh_list:
        material_instance._material_list_refresh_list.append(on_refresh_fn)


def remove_material_list_refresh_callback(on_refresh_fn: callable):
    """
    Remove callback to trigger when material library UI refreshes.

    Args:
        on_refresh_fn (callable): Callback to be removed.
    """
    if material_instance and on_refresh_fn in material_instance._material_list_refresh_list:
        material_instance._material_list_refresh_list.remove(on_refresh_fn)


async def delayed_material_list_refresh():
    """
    Async refresh material_list.
    """
    await omni.kit.app.get_app().next_update_async()
    if not mdl_list_cache:
        return asyncio.ensure_future(delayed_material_list_refresh())

    omni.kit.material.library.material_list_refresh()


def add_material_list_item(name: str, on_call_fn: callable, refresh: bool=True):
    """
    Add custom material, this will also get added to context menu Create menu.

    Args:
        name (str): Material name.
        on_call_fn (callable): Material created callback.
        refresh (bool): Refresh UI Flag.
    """
    if material_instance:
        material_instance._material_list_custom_item_list[name] = on_call_fn
        if refresh:
            if not mdl_list_cache:
                return asyncio.ensure_future(omni.kit.material.library.delayed_material_list_refresh())

            omni.kit.material.library.material_list_refresh()


def remove_material_list_item(name: str, refresh: bool=True):
    """
    Remove custom material, this will also get removed from context menu Create menu.

    Args:
        name (str): Material name.
        refresh (bool): Refresh UI Flag.
    """
    if material_instance and name in material_instance._material_list_custom_item_list:
        del material_instance._material_list_custom_item_list[name]
        if refresh:
            if not mdl_list_cache:
                return asyncio.ensure_future(omni.kit.material.library.delayed_material_list_refresh())

            omni.kit.material.library.material_list_refresh()


def material_list_refresh():
    """
    Remove custom material, this will also get removed from context menu Create menu.

    Args:
        name (str): Material name.
        refresh (bool): Refresh UI Flag.
    """
    if material_instance:
        for fn in material_instance._material_list_refresh_list:
            fn()


def get_material_list():
    """
    Builds a list of materials and other information, used by omni.kit.context_menu and omni.kit.menu.create

    Returns:
        (list) list of lists:
            sub-list is either:
                "GROUP" & material group name.
                Material name, create material function, blocking parameter passed to create_material_and_assign, list of material sub identifiers.
    """
    static_data = material_instance._static_data if material_instance else None
    if not static_data:
        carb.log_warn(f"get_material_list Failed because omni.kit.material.library is not loaded")
        return

    mat_list = []
    mdl_build_list = []
    group_lookup = {}
    show_list = get_material_show_list()
    show_ui_groups = carb.settings.get_settings().get("/exts/omni.kit.material.library/show_ui_groups")

    def add_group_mat_list(new_item_list: list):
        nonlocal mat_list
        nonlocal show_ui_groups

        if show_ui_groups:
            mat_list.append(new_item_list)
            return True
        return False

    def add_to_mat_list(new_item_list: MaterialItem):
        nonlocal mat_list
        nonlocal show_list

        # if show_list empty add everything otherwise add anything matching, wild-cards allowed.
        if not show_list or any(fnmatch.fnmatch(new_item_list[0], show_item) for show_item in show_list):
            mat_list.append(new_item_list)
            return True
        return False

    # gets groups
    for mtl_name, mdl_path, submenu, is_private in get_mdl_list(use_hidden=True, get_private=True):
        group = "unknown"

        kit_mdl_path = static_data.make_path_kit(mdl_path) if mdl_path else None
        if kit_mdl_path in static_data._material_group_cache:
            group = static_data._material_group_cache[kit_mdl_path]
        elif kit_mdl_path in static_data._material_subid_cache:
            subid_list = static_data._material_subid_cache[kit_mdl_path]
            for item in subid_list:
                if "in_group" in item.annotations:
                    group = item.annotations['in_group']
                    static_data._material_group_cache[kit_mdl_path] = group

        if group == "unknown" and submenu:
            filename = os.path.basename(mdl_path)
            lookup_name = filename.replace("Presets.mdl", "")
            if lookup_name in group_lookup:
                group = group_lookup[lookup_name]

        group_lookup[mtl_name] = group
        display_name: str = mtl_name.replace("_", " ")
        mdl_build_list.append((mtl_name, mdl_path, submenu, group, display_name, is_private))

    # map source asset info to the existing material list
    # the idea would be to go without loading the actual module here
    # the only drawback is that the display name has to be provided manually
    source_asset_list: List = get_mdl_usd_source_asset_list()
    for entry in source_asset_list:
        mdl_path: str = entry["source_asset_path"]  # Note, this should not be an absolute path!
        mtl_name: str = entry["source_asset_subid"]
        group: str = entry["group_name"]
        submenu: str = entry["submenu_name"]
        # TODO use display name from annotation maybe? but we haven't loaded the module yet
        display_name: str = entry["display_name"] if entry["display_name"] else mtl_name.replace("_", " ")
        group_lookup[mtl_name] = group
        mdl_build_list.append((mtl_name, mdl_path, submenu, group, display_name, is_private))

    mdl_build_list = sorted(mdl_build_list, key=lambda item: item[3])

    use_groups = bool(len(set(group_lookup.values())) > 1)
    last_group = "None"
    group_count = 0
    for mtl_name, mdl_path, submenu, group, display_name, is_private in mdl_build_list:
        if last_group != group and use_groups:
            last_group = group
            add_group_mat_list(MaterialItem(name="GROUP", submenu=group))

        filename = os.path.basename(mdl_path)
        if add_to_mat_list(
            MaterialItem(
                name=display_name,
                create_fn=lambda mdl_name=filename, mtl_name=mtl_name, mdl_url=mdl_path, mtl_created_list=None, bind_selected_prims=None, prim_name=display_name:
                    asyncio.ensure_future(
                        MaterialLibraryExtension._on_create_mdl_material(
                            mdl_url=mdl_url,
                            mdl_name=mdl_name,
                            mtl_name=mtl_name,
                            mtl_created_list=mtl_created_list,
                            bind_selected_prims=bind_selected_prims,
                            prim_name=prim_name,
                        )
                    ),
                block=True,
                submenu=submenu,
                is_private=is_private
            )
        ):
            group_count +=1

    # MaterialX materials
    add_group_mat_list(MaterialItem(name="GROUP", submenu="MaterialX Materials"))
    add_to_mat_list(
        MaterialItem(
            name="OpenPBR Surface",
            create_fn=lambda mtl_created_list=None, bind_selected_prims=True:
                MaterialLibraryExtension._on_create_mtlx_material(
                    mtlx_id="ND_open_pbr_surface_surfaceshader",
                    mtl_name="OpenPBR",
                    mtl_created_list=mtl_created_list,
                    bind_selected_prims=bind_selected_prims,
                ),
            block=True,
        )
    )
    add_to_mat_list(
        MaterialItem(
            name="Standard Surface",
            create_fn=lambda mtl_created_list=None, bind_selected_prims=True:
                MaterialLibraryExtension._on_create_mtlx_material(
                    mtlx_id="ND_standard_surface_surfaceshader",
                    mtl_name="StandardSurface",
                    mtl_created_list=mtl_created_list,
                    bind_selected_prims=bind_selected_prims,
                ),
            block=True,
        )
    )

    # USD materials
    add_group_mat_list(MaterialItem(name="GROUP", submenu="USD Materials"))
    add_to_mat_list(
        MaterialItem(
            name="USD Preview Surface",
            create_fn=lambda mtl_created_list=None, bind_selected_prims=True:
                MaterialLibraryExtension._on_create_preview_surface(
                    mtl_created_list=mtl_created_list,
                    bind_selected_prims=bind_selected_prims,
                ),
            block=True,
        )
    )
    add_to_mat_list(
        MaterialItem(
            name="USD Preview Surface Texture",
            create_fn=lambda mtl_created_list=None, bind_selected_prims=True:
                MaterialLibraryExtension._on_create_preview_surface_texture(
                    mtl_created_list=mtl_created_list,
                    bind_selected_prims=bind_selected_prims,
                ),
            block=True,
        )
    )

    # custom materials
    add_group_mat_list(MaterialItem(name="GROUP", submenu="Custom Materials"))
    add_to_mat_list(
        MaterialItem(
            name="Add MDL File",
            create_fn=lambda mtl_created_list=None, bind_selected_prims=True:
                MaterialLibraryExtension._on_create_custom_mdl_material(
                    mtl_created_list=mtl_created_list,
                    bind_selected_prims=bind_selected_prims,
                ),
            block=False,
        )
    )
    add_to_mat_list(
        MaterialItem(
            name="Add MaterialX Reference",
            create_fn=lambda mtl_created_list=None, bind_selected_prims=True:
                MaterialLibraryExtension._on_create_custom_mtlx_material(
                    mtl_created_list=mtl_created_list,
                    bind_selected_prims=bind_selected_prims,
                ),
            block=False,
        )
    )

    for item in material_instance._material_list_custom_item_list:
        add_to_mat_list(MaterialItem(name=item, create_fn=material_instance._material_list_custom_item_list[item], block=False))

    if show_list and show_ui_groups:
        # purge any empty groups
        last_entry = None
        for item in mat_list.copy():
            if last_entry and item.name == 'GROUP' and last_entry.name == 'GROUP':
                mat_list.remove(last_entry)
            last_entry = item

        # purge last entry if group
        while mat_list and mat_list[-1].name == "GROUP":
            mat_list.pop()

    return mat_list


def custom_material_dialog(mdl_path: str, on_complete_fn: callable=None, bind_prim_paths: list=[]):
    """
    Show custom material dialog.

    Args:
        mdl_path (str): Mdl path.
        on_complete_fn (callable): Function called when material dialog Cleated button is clicked.
        bind_prim_paths (list): List of prims path to bind material to.
    """
    return MaterialLibraryExtension._custom_material_dialog(material_instance._static_data,
                                                            absolute_mdl_path=mdl_path,
                                                            on_complete_fn=on_complete_fn,
                                                            bind_prim_paths=bind_prim_paths)

def get_cache_filename():
    if material_instance:
        return material_instance.get_cache_filename()
    return ""


async def get_subidentifier_from_material(prim: Usd.Prim, on_complete_fn: callable, use_functions: bool=False, show_alert: bool=False):
    """
    get sub-identifier list from material prim asynchronously.

    Args:
        prim (Usd.Prim): prim to get material & material sub-identifier from.
        on_complete_fn (callable): function to call with list of sub-identifier when completed.
        use_functions (bool): if True only list materials and not functions otherwise return all sub-identifiers.
        show_alert (bool): show alert if bad material.

    Returns:
        (list): list of sub-identifier

    """
    return await material_instance.get_subidentifier_from_material(prim, on_complete_fn, use_functions, show_alert)

async def get_subidentifier_from_mdl(mdl_file: str, on_complete_fn: callable = None, use_functions: bool=False, show_alert: bool=False):
    """
    get sub-identifier list from mdl file asynchronously.

    Args:
        mdl_file (str): mdl_file to get material sub-identifiers from.
        on_complete_fn (callable): function to call with list of sub-identifier when completed.
        use_functions (bool): if True only list materials and not functions otherwise return all sub-identifiers.
        show_alert (bool): show alert if bad material.

    Returns:
        (list): list of sub-identifier

    """
    return await material_instance.get_subidentifier_from_mdl(mdl_file, on_complete_fn, use_functions, show_alert)

def drop_material(prim_path: str, model_path: str, apply_material_fn: callable):
    """
    Build bind material menu UI.

    Args:
        prim_path (str): Prim path.
        model_path (str): Model Path:
        apply_material_fn (callable): Bind material callback.
    """
    return _drop_material(prim_path, model_path, apply_material_fn=apply_material_fn)

def multi_descendents_dialog(prim_paths: list, on_click_fn: callable):
    """
    Show multi descendants dialog.

    Args:
        prim_paths (list): Prim path list.
        apply_material_fn (callable): Prim selected callback.
    """
    return _multi_descendents_dialog(prim_paths, on_click_fn=on_click_fn)

def remove_mdl_from_cache(shader_prim_path: str):
    """
    Remove material from cache. Call by Material Watcher when re-loading modified mdl files.

    Args:
        shader_prim_path (str): material prim path.
    """
    return material_instance.remove_mdl_from_cache(shader_prim_path)

def get_material_enums():
    """
    Get material Enum data.

    Returns:
        (dict): material enum dictionary.
    """
    return material_instance._static_data._material_enum_cache

def bind_material_to_prims_dialog(stage: Usd.Stage, prims: list) -> None:
    """
    Show dialog to user, so they an select material and bind to prims.

    Args:
        stage (Usd.Stage): stage
        prims (list): list of prims to bind to.
    """
    material_instance._context_menu_extensions.bind_material_to_prims_dialog(stage, prims)

def add_usd_source_asset_path_to_mtl_lib(source_asset_path: str, source_asset_subid: str, group_name: str, submenu_name: str = None, display_name: str = None):
    """
    Adds a material to the context menu.

    Args:
        source_asset_path (str): The USD Identifier corresponding to the source asset path of a USD Shader Node.
        source_asset_subid (str): The USD Sub-identifier corresponding to the source asset sub-identifier of a USD Shader Node.
        group_name (str): The menu entries are grouped. Select an existing one or creates a new group.
        submenu_name (str): Entries can be sorted into a submenu. If not set, the entry will appear top-level.
        display_name (str): Display name of the entry in the menu. If not set, a default value will be used.

    Returns:
        (bool): True on success otherwise False.
    """
    # check if that material/function is already registered, if so we can return
    source_asset_list: List = get_mdl_usd_source_asset_list()
    for entry in source_asset_list:
        if entry["source_asset_path"] == source_asset_path and entry["source_asset_subid"] == source_asset_subid:
            return False

    # create a new entry and add it to list, stored in json format
    new_entry: Dict = {}
    new_entry["source_asset_path"] = source_asset_path
    new_entry["source_asset_subid"] = source_asset_subid
    new_entry["group_name"] = group_name
    new_entry["submenu_name"] = submenu_name
    new_entry["display_name"] = display_name
    source_asset_list.append(new_entry)

    carb.settings.get_settings().set(SETTING_MATERIAL_LIBRARY_USD_SOURCE_ASSET_LIST, json.dumps(source_asset_list))
    carb.log_info(f"Registering MDL using USD Source Asset: {source_asset_path} Sub-Identifier: {source_asset_subid}")
    return True

def remove_usd_source_asset_path_from_mtl_lib(source_asset_path: str, source_asset_subid: str):
    """
    Removes a material from the context menu.

    Args:
        source_asset_path (str):    The USD Identifier corresponding to the source asset path of a USD Shader Node.
        source_asset_subid (str):   The USD Sub-identifier corresponding to the source asset sub-identifier of a USD Shader Node.
    """

    # check if that material/function is already registered, if so we can return
    source_asset_list: List = get_mdl_usd_source_asset_list()
    found: bool = False
    for entry in source_asset_list:
        if entry["source_asset_path"] == source_asset_path and entry["source_asset_subid"] == source_asset_subid:
            source_asset_list.remove(entry)
            found = True
            break

    if found:
        carb.settings.get_settings().set(SETTING_MATERIAL_LIBRARY_USD_SOURCE_ASSET_LIST, json.dumps(source_asset_list))
        carb.log_info(f"Unregistering MDL using USD Source Asset: {source_asset_path} Sub-Identifier: {source_asset_subid}")
    return found

def add_to_mtl_lib(folder_paths: list[str], is_private: bool=False) -> list[str]:
    """
    Add custom folder to list of folders to generate context menu "Create/Materials" from.

    Args:
        folder_paths (list): List of folder paths to add.
        is_private: (bool): Actions start with "_" to be excluded from actions_api.md
    Returns:
        (list): Updated list of folders used to generate context menu "Create/Materials".
    """
    mdl_paths: List[str] = list(carb.settings.get_settings().get(SETTING_MATERIAL_LIBRARY_LIB_PATHS))

    for folder_path in folder_paths:
        if not folder_path in mdl_paths:
            mdl_paths.insert(0, set_path_private_state(folder_path, is_private))

    carb.settings.get_settings().set(SETTING_MATERIAL_LIBRARY_LIB_PATHS, mdl_paths)
    carb.log_info(f"Registering MDL Folder: {folder_path}")

    return mdl_paths

def remove_from_mtl_lib(folder_paths: list[str]) -> list[str]:
    """
    Remove custom folder to list of folders to generate context menu "Create/Materials" from.

    Args:
        folder_paths (list): List of folder paths to remove.

    Returns:
        (list): Updated list of folders usded to generate context menu "Create/Materials".
    """
    mdl_paths: List[str] = list(carb.settings.get_settings().get(SETTING_MATERIAL_LIBRARY_LIB_PATHS))

    for folder_path in folder_paths:
        fpath = set_path_private_state(folder_path, True)
        if fpath in mdl_paths:
            mdl_paths.remove(fpath)
        elif folder_path in mdl_paths:
            mdl_paths.remove(folder_path)

    carb.settings.get_settings().set(SETTING_MATERIAL_LIBRARY_LIB_PATHS, mdl_paths)
    carb.log_info(f"Unregistering MDL Folder: {folder_path}")

    return mdl_paths
