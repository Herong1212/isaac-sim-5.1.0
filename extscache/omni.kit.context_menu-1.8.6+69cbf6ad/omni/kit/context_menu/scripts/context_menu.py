# Copyright (c) 2020-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""
Context menu implementation classes.
"""

__all__ = ['get_widget_instance', 'SETTING_HIDE_CREATE_MENU', 'ContextMenuExtension', 'get_instance', 'close_menu', 'reorder_menu_dict', 'post_notification', 'get_hovered_prim', 'add_menu', 'get_menu_dict', 'get_menu_event_stream']

import os, sys
import weakref
import asyncio
import carb
import omni.kit.usd.layers as layers
import omni.ext

from omni import ui
from functools import partial
from typing import Callable, List, Union, Tuple
from pathlib import Path
from pxr import Usd, Sdf, Gf, Tf, UsdShade, UsdGeom, Trace, UsdUtils, Kind
from .singleton import Singleton
from omni.kit.widget.context_menu import ContextMenuWidgetExtension
from omni.kit.widget.context_menu import get_instance as get_widget_instance
from omni.kit.widget.context_menu import add_menu, get_menu_dict, get_menu_event_stream, reorder_menu_dict


_extension_instance = None
TEST_DATA_PATH = ""
SETTING_HIDE_CREATE_MENU = "/exts/omni.kit.context_menu/hideCreateMenu"

class ContextMenuExtension(omni.ext.IExt):
    """Context menu core functionality.

    Example using viewport mouse event to trigger:

    .. code-block:: python

        class ContextMenu:
            def on_startup(self):
                # get window event stream
                import omni.kit.viewport_legacy
                viewport_win = get_viewport_interface().get_viewport_window()
                # on_mouse_event called when event dispatched
                self._stage_event_sub = viewport_win.get_mouse_event_stream().create_subscription_to_pop(self.on_mouse_event)

            def on_shutdown(self):
                # remove event
                self._stage_event_sub = None

            def on_mouse_event(self, event):
                import omni.kit.menu.core

                # check its expected event
                if event.type != int(omni.kit.menu.core.MenuEventType.ACTIVATE):
                    return

                # get context menu core functionality & check its enabled
                context_menu = omni.kit.context_menu.get_instance()
                if context_menu is None:
                    carb.log_error("context_menu is disabled!")
                    return

                # get parameters passed by event
                objects = {}
                objects["test_path"] = event.payload["test_path"]
                # setup objects, this is passed to all functions
                objects["test"] = "this is a test"

                # setup menu
                menu_list = [
                    # "name" is name shown on menu. (if name is "" then a menu ui.Separator is added. Can be combined with show_fn)
                    # "glyph" is icon shown on menu, can use full paths to extensions
                    # "name_fn" function to get menu item name
                    # "show_fn" function or list of functions used to decide if menu item is shown. All functions must return True to show
                    # "enabled_fn" function or list of functions used to decide if menu item is enabled. All functions must return True to be enabled
                    # "onclick_fn" function to be called when user clicks menu item
                    # "onclick_action" action to be called when user clicks menu item
                    # "checked_fn" function returns True/False and shows solid/grey tick
                    # "header" as be used with name of "" to use named ui.Separator
                    # "populate_fn" a function to be called to populate the menu. Can be combined with show_fn
                    # "appear_after" a identifier of menu name. Used by custom menus and will allow custom menu to change order
                    # "show_fn_async" this is async function to set items visible flag. These behave differently to show functions as the item will be created regardless and have its
                    #   visibility set to False and its upto show_fn_async callback to set the visible flag to True if required

                    {"name": "Test Menu", "glyph": "question.svg", "show_fn": [ContextMenu.has_reason_to_show, ContextMenu.has_another_reason_to_show],
                             "onclick_fn": ContextMenu.clear_default_prim },
                    {"name": "", "show_fn": ContextMenu.has_another_reason_to_show},
                    {"populate_fn": context_menu.show_create_menu},
                    {"name": ""},
                    {"name": "Copy URL Link", "glyph": "menu_link.svg", "onclick_fn": ContextMenu.copy_prim_url},
                ]

                # add custom menus
                menu_list += omni.kit.context_menu.get_menu_dict("MENU", "")
                menu_list += omni.kit.context_menu.get_menu_dict("MENU", "stagewindow")
                omni.kit.context_menu.reorder_menu_dict(menu_dict)

                # show menu
                context_menu.show_context_menu("stagewindow", objects, menu_list)

            # show_fn functions
            def has_reason_to_show(objects: dict):
                if not "test_path" in objects:
                    return False
                return True

            def has_another_reason_to_show(objects: dict):
                if not "test_path" in objects:
                    return False
                return True

            def copy_prim_url(objects: dict):
                try:
                    import omni.kit.clipboard

                    omni.kit.clipboard.copy("My hovercraft is full of eels")
                except ImportError:
                    carb.log_warn("Could not import omni.kit.clipboard.")
    """

    # ---------------------------------------------- menu global populate functions ----------------------------------------------

    @staticmethod
    def _set_prim_translation(stage, prim_path: Sdf.Path, translate: Gf.Vec3d):
        prim = stage.GetPrimAtPath(prim_path)
        if not prim or not prim.IsA(UsdGeom.Xformable):
            return

        xformable = UsdGeom.Xformable(prim)
        for op in xformable.GetOrderedXformOps():
            if op.GetOpType() == UsdGeom.XformOp.TypeTranslate and "pivot" not in op.SplitName():
                precision = op.GetPrecision()
                desired_translate = (
                    translate
                    if precision == UsdGeom.XformOp.Precision
                    else Gf.Vec3f(translate[0], translate[1], translate[2])
                )
                omni.kit.commands.execute("ChangeProperty", prop_path=op.GetAttr().GetPath().pathString, value=desired_translate, prev=None)
                break
            elif op.GetOpType() == UsdGeom.XformOp.TypeTransform:
                matrix = op.Get()
                matrix.SetTranslate(translate)
                omni.kit.commands.execute("ChangeProperty", prop_path=op.GetAttr().GetPath().pathString, value=matrix, prev=None)
                break

    @staticmethod
    def create_prim(objects: dict, prim_type: str, attributes: dict, create_group_xform: bool = False) -> None:
        """
        Create prims

        Args:
            objects: context_menu data
            prim_type: created prim's type
            attributes: created prim's custom attributes
            create_group_xform: passed to CreatePrimWithDefaultXformCommand
        """
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        with omni.kit.undo.group():
            with layers.active_authoring_layer_context(usd_context):
                if "mouse_pos" in objects and not create_group_xform:
                    mouse_pos = objects["mouse_pos"]
                    omni.kit.commands.execute(
                        "CreatePrimWithDefaultXform",
                        prim_type=prim_type,
                        attributes=attributes,
                        select_new_prim=True
                    )
                    paths = usd_context.get_selection().get_selected_prim_paths()
                    if stage:
                        for path in paths:
                            ContextMenuExtension._set_prim_translation(
                                stage, path, Gf.Vec3d(mouse_pos[0], mouse_pos[1], mouse_pos[2])
                            )
                elif create_group_xform:
                    paths = usd_context.get_selection().get_selected_prim_paths()
                    if stage.HasDefaultPrim() and stage.GetDefaultPrim().GetPath().pathString in paths:
                        post_notification("Cannot Group default prim")
                        return

                    omni.kit.commands.execute("GroupPrims", prim_paths=paths)
                else:
                    prim_path = None
                    if "use_hovered" in objects and objects["use_hovered"]:
                        prim = get_hovered_prim(objects)
                        if prim:
                            new_path = omni.usd.get_stage_next_free_path(stage, prim.GetPrimPath().pathString + "/" + prim_type, False)
                            future_prim = Usd.SchemaRegistry.GetTypeFromName(prim_type)
                            if omni.usd.can_prim_have_children(stage, Sdf.Path(new_path), future_prim):
                                prim_path = new_path
                            else:
                                post_notification(f"Cannot create prim below {prim.GetPrimPath().pathString} as nested prims are not supported for this type.")

                    omni.kit.commands.execute(
                        "CreatePrimWithDefaultXform",
                        prim_type=prim_type,
                        prim_path=prim_path,
                        attributes=attributes,
                        select_new_prim=True
                    )

    @staticmethod
    def create_mesh_prim(objects: dict, prim_type: str) -> None:
        """
        Create mesh prims

        Args:
            objects: context_menu data
            prim_type: created prim's type
        """
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        prim_path = None
        if "use_hovered" in objects and objects["use_hovered"]:
            prim = get_hovered_prim(objects)
            if prim:
                # mesh prims are always UsdGeom.Gprim so just check for ancestor prim_type
                new_path = omni.usd.get_stage_next_free_path(stage, prim.GetPrimPath().pathString + "/" + prim_type, False)
                if omni.usd.is_ancestor_prim_type(stage, Sdf.Path(new_path), UsdGeom.Gprim):
                    post_notification(f"Cannot create prim below {prim.GetPrimPath().pathString} as nested prims are not supported for this type.")
                else:
                    prim_path = new_path

        with omni.kit.undo.group():
            with layers.active_authoring_layer_context(usd_context):
                omni.kit.commands.execute(
                    "CreateMeshPrimWithDefaultXform", prim_type=prim_type,
                    prim_path=prim_path, select_new_prim=True, prepend_default_prim=False if prim_path else True,
                    above_ground=True
                )

                if "mouse_pos" in objects:
                    mouse_pos = objects["mouse_pos"]
                    paths = usd_context.get_selection().get_selected_prim_paths()
                    if stage:
                        for path in paths:
                            ContextMenuExtension._set_prim_translation(
                                stage, path, Gf.Vec3d(mouse_pos[0], mouse_pos[1], mouse_pos[2])
                            )

    def show_selected_prims_names(self, objects: dict, delegate=None) -> None:
        """
        Populate function that builds menu items with selected prim info

        Args:
            objects: context_menu data
        """
        import omni.kit.context_menu

        context_menu = omni.kit.context_menu.get_instance()
        if context_menu is None:
            carb.log_error("context_menu is disabled!")
            return

        paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
        hovered = None
        if "use_hovered" in objects and objects["use_hovered"]:
            hovered = omni.kit.context_menu.get_hovered_prim(objects)

        if not "prim_list" in objects and len(paths) == 0:
            menu_name = f"(nothing selected)"
        else:
            if "prim_list" in objects:
                paths = objects["prim_list"]

            if len(paths) > 1:
                menu_name = f"({len(paths)} models selected)"
            elif "prim_list" in objects:
                if paths[0].GetPath() == hovered.GetPrimPath() if hovered else None:
                    menu_name = f"({paths[0].GetPath().name} selected & hovered)"
                    hovered = None
                else:
                    menu_name = f"({paths[0].GetPath().name} selected)"

            else:
                menu_name = f"({os.path.basename(paths[0])} selected)"
        if hovered:
            menu_name += f"\n({hovered.GetPath().name} hovered)"

        context_menu._menu_title = ContextMenuWidgetExtension.uiMenuItem(
            f'{menu_name}',
            triggered_fn=None,
            enabled=False if delegate else True,
            delegate=delegate if delegate else ContextMenuWidgetExtension.default_delegate,
            tearable=True if delegate else False,
            glyph="menu_prim.svg"
        )
        if not carb.settings.get_settings().get(SETTING_HIDE_CREATE_MENU):
            ui.Separator()

    def show_create_menu(self, objects: dict):
        """
        Populate function that builds create menu

        Args:
            objects: context_menu data
        """
        prim = None
        prim_list = [objects["prim"]] if "prim" in objects else objects["prim_list"]

        self.build_create_menu(objects, prim_list)

    def build_create_menu(self, objects: dict, prim_list: list, custom_menu: dict = [], delegate=None):
        """
        Builds "Create" context sub-menu items
        """
        import omni.kit.context_menu

        def is_create_type_enabled(type: str):
            settings = carb.settings.get_settings()
            if type == "Shape":
                if settings.get("/app/primCreation/hideShapes") == True or \
                   settings.get("/app/primCreation/enableMenuShape") == False:
                       return False
                return True
            enabled = settings.get(f"/app/primCreation/enableMenu{type}")
            if enabled == True or enabled == False:
                return enabled
            return True


        if carb.settings.get_settings().get(SETTING_HIDE_CREATE_MENU):
            return

        custom_menu += omni.kit.context_menu.get_menu_dict("CREATE", "")
        usd_context = omni.usd.get_context()
        paths = usd_context.get_selection().get_selected_prim_paths()

        item_delegate = delegate if delegate else ContextMenuWidgetExtension.default_delegate

        style = delegate.get_style() if delegate and hasattr(delegate, "get_style") else ContextMenuWidgetExtension.default_delegate.get_style()
        item = self.menu(
            f'Create',
            style=style,
            delegate=item_delegate,
            glyph="menu_create.svg",
            submenu=True
        )
        with item:
            try:
                import omni.kit.primitive.mesh

                geometry_mesh_prim_list = omni.kit.primitive.mesh.get_geometry_mesh_prim_list()
                item = self.menu(f'Mesh', delegate=item_delegate, glyph="menu_prim.svg", submenu=True)
                with item:
                    for mesh in geometry_mesh_prim_list:
                        self.menu_item(mesh, triggered_fn=partial(ContextMenuExtension.create_mesh_prim, objects, mesh), delegate=item_delegate)
            except ModuleNotFoundError:
                pass

            if is_create_type_enabled("Shape"):
                def on_create_shape(objects, prim_type):
                    shapes = omni.usd.get_geometry_standard_prim_list()
                    shape_attrs = shapes.get(prim_type, {})
                    ContextMenuExtension.create_prim(objects, prim_type, shape_attrs)

                item = self.menu(f'Shape', delegate=item_delegate, glyph="menu_prim.svg", submenu=True)
                with item:
                    for geom in omni.usd.get_geometry_standard_prim_list().keys():
                        self.menu_item(
                            geom, triggered_fn=partial(on_create_shape, objects, geom), delegate=item_delegate
                        )

            if is_create_type_enabled("Light"):
                item = self.menu(f'Light', delegate=item_delegate, glyph="menu_light.svg", submenu=True)
                with item:
                    for light in omni.usd.get_light_prim_list():
                        self.menu_item(
                            light[0], triggered_fn=partial(ContextMenuExtension.create_prim, objects, light[1], light[2]), delegate=item_delegate
                        )

            try:
                import usd.schema.audio

                audio_prim_list = usd.schema.audio.get_audio_prim_list()
                if is_create_type_enabled("Audio") and audio_prim_list:
                    item = self.menu(f'Audio', delegate=item_delegate, glyph="menu_audio.svg", submenu=True)
                    with item:
                        for sound in audio_prim_list:
                            self.menu_item(
                                sound[0], triggered_fn=partial(ContextMenuExtension.create_prim, objects, sound[1], sound[2]), delegate=item_delegate
                            )
            except ModuleNotFoundError:
                pass

            if is_create_type_enabled("Camera"):
                self.menu_item(
                    f'Camera',
                    triggered_fn=partial(ContextMenuExtension.create_prim, objects, "Camera", {}),
                    glyph="menu_camera.svg",
                    delegate=item_delegate
                ),

            if is_create_type_enabled("Scope"):
                self.menu_item(
                    f'Scope',
                    triggered_fn=partial(ContextMenuExtension.create_prim, objects, "Scope", {}),
                    glyph="menu_scope.svg",
                    delegate=item_delegate
                ),

            if is_create_type_enabled("Xform"):
                self.menu_item(
                    f'Xform',
                    triggered_fn=partial(ContextMenuExtension.create_prim, objects, "Xform", {}),
                    glyph="menu_xform.svg",
                    delegate=item_delegate
                ),

            if custom_menu:
                for menu_entry in custom_menu:
                    if isinstance(menu_entry, list):
                        for item in menu_entry:
                            if self._build_menu(item, objects, delegate=item_delegate):
                                self.menu_item_count += 1
                    elif self._build_menu(menu_entry, objects, delegate=item_delegate):
                        self.menu_item_count += 1

    def build_add_menu(self, objects: dict, prim_list: list, custom_menu: list = None, delegate = None):
        """
        Builds "Add" context sub-menu items
        """
        import omni.kit.context_menu

        if carb.settings.get_settings().get(SETTING_HIDE_CREATE_MENU):
            return

        menu = omni.kit.context_menu.get_menu_dict("ADD", "")
        menu = menu + custom_menu
        if menu:
            root_menu = self.menu(
                f'Add', delegate=delegate if delegate else ContextMenuWidgetExtension.default_delegate, glyph="menu_add.svg", submenu=True)
            with root_menu:
                menu_item_count = self.menu_item_count
                for menu_entry in menu:
                    if isinstance(menu_entry, list):
                        for item in menu_entry:
                            if self._build_menu(item, objects, None):
                                self.menu_item_count += 1
                    elif self._build_menu(menu_entry, objects, None):
                        self.menu_item_count += 1
            if self.menu_item_count == menu_item_count:
                root_menu.visible = False

    def select_prims_using_material(self, objects: dict):
        """
        Select stage prims using material

        Args:
            objects: context_menu data
        """
        if not any(item in objects for item in ["prim", "prim_list"]):
            return
        prim_list = [objects["prim"]] if "prim" in objects else objects["prim_list"]

        omni.usd.get_context().get_selection().clear_selected_prim_paths()
        paths = []
        for mat_prim in prim_list:
            for prim in objects["stage"].Traverse():
                if omni.usd.is_prim_material_supported(prim):
                    mat, rel = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
                    if mat and mat.GetPrim().GetPath() == mat_prim.GetPath():
                        paths.append(prim.GetPath().pathString)
        omni.usd.get_context().get_selection().set_selected_prim_paths(paths, True)

    def find_in_browser(self, objects: dict) -> None:
        """
        Select prim in content_browser

        Args:
            objects: context_menu data
        """
        prim = objects["prim_list"][0]
        url_path = omni.usd.get_url_from_prim(prim)

        try:
            from omni.kit.window.content_browser import get_content_window

            content_browser = get_content_window()
            if content_browser:
                content_browser.navigate_to(url_path)
        except Exception as exc:
            carb.log_warn(f"find_in_browser error {exc}")

    def duplicate_prim(self, objects: dict):
        """
        Duplicate prims

        Args:
            objects: context_menu data
        """
        paths = []
        usd_context = omni.usd.get_context()
        usd_context.get_selection().clear_selected_prim_paths()
        edit_mode = layers.get_layers(usd_context).get_edit_mode()
        is_auto_authoring = edit_mode == layers.LayerEditMode.AUTO_AUTHORING
        omni.kit.undo.begin_group()
        for prim in objects["prim_list"]:
            old_prim_path = prim.GetPath().pathString
            new_prim_path = omni.usd.get_stage_next_free_path(objects["stage"], old_prim_path, False)
            omni.kit.commands.execute(
                "CopyPrim", path_from=old_prim_path, path_to=new_prim_path, exclusive_select=False,
                copy_to_introducing_layer=is_auto_authoring
            )
            paths.append(new_prim_path)
        omni.kit.undo.end_group()
        omni.usd.get_context().get_selection().set_selected_prim_paths(paths, True)

    def delete_prim(self, objects: dict, destructive=False):
        """
        Delete prims

        Args:
            objects: context_menu data
            destructive: If it's true, it will remove all corresponding prims in all layers.
                         Otherwise, it will deactivate the prim in current edit target if its def is not in the current edit target.
                         By default, it will be non-destructive.
        """
        prims = objects.get("prim_list", [])
        if prims:
            prim_paths = [prim.GetPath() for prim in prims]
            omni.kit.commands.execute("DeletePrims", paths=prim_paths, destructive=destructive)

    def copy_prim_url(self, objects: dict):
        """
        Copies URL of Prim in USDA references format.
        @planet.usda@</Planet>
        """
        paths = ""
        for prim in objects["prim_list"]:
            if paths:
                paths += " "
            paths += omni.usd.get_url_from_prim(prim)

        omni.kit.clipboard.copy(paths)

    def copy_prim_path(self, objects: dict) -> None:
        """
        Copy prims path to clipboard

        Args:
            objects: context_menu data
        """
        paths = ""
        for prim in objects["prim_list"]:
            if paths:
                paths += " "
            paths += f"{prim.GetPath()}"

        omni.kit.clipboard.copy(paths)

    def group_selected_prims(self, objects: dict):
        """
        Group prims

        Args:
            prims: list of prims
        """
        # because widget.layer and widget.stage can get confused if prims are just renamed. clear selection and wait a frame, then do the rename to allow for this
        omni.usd.get_context().get_selection().clear_selected_prim_paths()
        asyncio.ensure_future(self._group_list(objects))

    def ungroup_selected_prims(self, objects: dict):
        """
        Ungroup prims

        Args:
            prims: list of prims
        """
        # because widget.layer and widget.stage can get confused if prims are just renamed. clear selection and wait a frame, then do the rename to allow for this
        omni.usd.get_context().get_selection().clear_selected_prim_paths()
        asyncio.ensure_future(self._ungroup_list(objects))

    async def _group_list(self, objects: dict):
        await omni.kit.app.get_app().next_update_async()
        prim_list = [objects["prim"]] if "prim" in objects else objects["prim_list"]
        paths = []
        for prim in prim_list:
            paths.append(prim.GetPath().pathString)
        omni.usd.get_context().get_selection().set_selected_prim_paths(paths, True)
        omni.usd.get_context().get_selection().set_selected_prim_paths(paths, True)
        ContextMenuExtension.create_prim(objects, prim_type="Xform", attributes={}, create_group_xform=True)

    async def _ungroup_list(self, objects: dict):
        await omni.kit.app.get_app().next_update_async()
        prim_list = [objects["prim"]] if "prim" in objects else objects["prim_list"]
        paths = []
        for prim in prim_list:
            paths.append(prim.GetPath().pathString)
        omni.usd.get_context().get_selection().set_selected_prim_paths(paths, True)
        omni.usd.get_context().get_selection().set_selected_prim_paths(paths, True)

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        with omni.kit.undo.group():
            with layers.active_authoring_layer_context(usd_context):
                omni.kit.commands.execute("UngroupPrims", prim_paths=paths)

    def refresh_payload_or_reference(self, objects: dict):
        """
        Find layers containing prims and triggers reload.
        """
        async def reload(layer_handles):
            context = omni.usd.get_context()
            for layer in layer_handles:
                (all_layers, _, _) = UsdUtils.ComputeAllDependencies(layer.identifier)
                if all_layers:
                    layers_state = layers.get_layers_state(context)
                    all_dirty_layers = []
                    for dep_layer in all_layers:
                        if layers_state.is_layer_outdated(dep_layer.identifier):
                            all_dirty_layers.append(dep_layer)

                    if all_dirty_layers:
                        Sdf.Layer.ReloadLayers(all_dirty_layers)

        prim_list = [objects["prim"]] if "prim" in objects else objects["prim_list"]
        layer_handles = set()
        for prim in prim_list:
            for (ref, intro_layer) in omni.usd.get_composed_references_from_prim(prim):
                layer = Sdf.Find(intro_layer.ComputeAbsolutePath(ref.assetPath)) if ref.assetPath else None
                if layer:
                    layer_handles.add(layer)
            for (ref, intro_layer) in omni.usd.get_composed_payloads_from_prim(prim):
                layer = Sdf.Find(intro_layer.ComputeAbsolutePath(ref.assetPath)) if ref.assetPath else None
                if layer:
                    layer_handles.add(layer)

        asyncio.ensure_future(reload(layer_handles))

    def convert_payload_to_reference(self, objects: dict):
        """
        Converts selected prims from payload(s) to reference(s).
        """
        prim_list = [objects["prim"]] if "prim" in objects else objects["prim_list"]

        async def convert(prim_list):
            await omni.kit.app.get_app().next_update_async()
            with omni.kit.undo.group():
                with Sdf.ChangeBlock():
                    for prim in prim_list:
                        stage = prim.GetStage()
                        ref_and_layers = omni.usd.get_composed_payloads_from_prim(prim)
                        for payload, _ in ref_and_layers:
                            reference = Sdf.Reference(assetPath=payload.assetPath.replace("\\", "/"), primPath=payload.primPath, layerOffset=payload.layerOffset)
                            omni.kit.commands.execute("RemovePayload", stage=stage, prim_path=prim.GetPath(), payload=payload)
                            omni.kit.commands.execute("AddReference", stage=stage, prim_path=prim.GetPath(), reference=reference)

            try:
                property_window = omni.kit.window.property.get_window()
                if property_window:
                    property_window._window.frame.rebuild()
            except Exception:
                pass

        asyncio.ensure_future(convert(prim_list))

    def convert_reference_to_payload(self, objects: dict):
        """
        Converts selected prims from reference(s) to payload(s).
        """
        prim_list = [objects["prim"]] if "prim" in objects else objects["prim_list"]

        async def convert(prim_list):
            await omni.kit.app.get_app().next_update_async()
            with omni.kit.undo.group():
                with Sdf.ChangeBlock():
                    for prim in prim_list:
                        stage = prim.GetStage()
                        ref_and_layers = omni.usd.get_composed_references_from_prim(prim)
                        for reference, _ in ref_and_layers:
                            payload = Sdf.Payload(assetPath=reference.assetPath.replace("\\", "/"), primPath=reference.primPath, layerOffset=reference.layerOffset)
                            omni.kit.commands.execute("RemoveReference", stage=stage, prim_path=prim.GetPath(), reference=reference)
                            omni.kit.commands.execute("AddPayload", stage=stage, prim_path=prim.GetPath(), payload=payload)

            try:
                property_window = omni.kit.window.property.get_window()
                if property_window:
                    property_window._window.frame.rebuild()
            except Exception:
                pass

        asyncio.ensure_future(convert(prim_list))

    def refresh_reference_payload_name(self, objects: dict):
        """
        Checks if prims have references/payload and returns name

        Returns:
            (str): Name of payload/reference or None
        """
        if not any(item in objects for item in ["prim", "prim_list"]):
            return None
        prim_list = [objects["prim"]] if "prim" in objects else objects["prim_list"]
        if not prim_list:
            return None

        has_payload = self._prims_have_payloads(prim_list)
        has_reference = self._prims_have_references(prim_list)

        if has_payload and has_reference:
            return "Refresh Payload & Reference"
        elif has_payload:
            return "Refresh Payload"
        return "Refresh Reference"

    def get_prim_group(self, prim):
        """
        If the prim is or has a parent prim that is a group Kind, returns that prim otherwise None

        Args:
            prim (Usd.Prim): prim to get group from.

        Returns:
            (Usd.Prim) Group prim or None.
        """
        model_api = Usd.ModelAPI(prim)
        if model_api and Kind.Registry.IsA(model_api.GetKind(), "group"):
            return prim
        else:
            if prim.GetParent().IsValid():
                return self.get_prim_group(prim.GetParent())
            else:
                return None

    # ---------------------------------------------- menu show test functions ----------------------------------------------

    def is_one_prim_selected(self, objects: dict):
        """
        Checks if one prim is selected.

        Args:
            objects (dict): context_menu data
        Returns:
            (bool): True if one prim is selected otherwise False.
        """
        if not "prim_list" in objects:
            return False
        return len(objects["prim_list"]) == 1

    def is_material(self, objects: dict):
        """
        Checks if prims are UsdShade.Material

        Args:
            objects (dict): context_menu data
        Returns:
            (bool): True if prim is UsdShade.Material else False.
        """
        if not any(item in objects for item in ["prim", "prim_list"]):
            return
        prim_list = [objects["prim"]] if "prim" in objects else objects["prim_list"]

        for prim in prim_list:
            if not prim.IsA(UsdShade.Material):
                return False
        return True

    def has_payload_or_reference(self, objects: dict):
        """
        Checks if prims have payloads or references
        Args:
            objects (dict): context_menu data
        Returns:
            (bool): True if prims have payload or references otherwise False.
        """
        if not any(item in objects for item in ["prim", "prim_list"]):
            return False
        prim_list = [objects["prim"]] if "prim" in objects else objects["prim_list"]
        if not prim_list:
            return False

        return self._prims_have_references(prim_list) or self._prims_have_payloads(prim_list)

    def can_convert_references_or_payloads(self, objects):
        """
        Checks if references can be converted into payloads or vice versa.
        Args:
            objects (dict): context_menu data
        Returns:
            (bool): True if prims can be converted from to payload/reference otherwise False.
        """
        if not any(item in objects for item in ["prim", "prim_list"]):
            return False
        prim_list = [objects["prim"]] if "prim" in objects else objects["prim_list"]
        if not prim_list:
            return False

        for prim in prim_list:
            ref_and_layers = omni.usd.get_composed_references_from_prim(prim)
            if ref_and_layers:
                return True

            payload_and_layers = omni.usd.get_composed_payloads_from_prim(prim)
            if payload_and_layers:
                return True

        return False

    def _prims_have_payloads(self, prim_list):
        for prim in prim_list:
            for prim_spec in prim.GetPrimStack():
                if prim_spec.HasInfo(Sdf.PrimSpec.PayloadKey) and prim_spec.GetInfo(Sdf.PrimSpec.PayloadKey).ApplyOperations([]):
                    return True
        return False

    def _prims_have_references(self, prim_list):
        for prim in prim_list:
            for prim_spec in prim.GetPrimStack():
                if prim_spec.HasInfo(Sdf.PrimSpec.ReferencesKey) and prim_spec.GetInfo(Sdf.PrimSpec.ReferencesKey).ApplyOperations([]):
                    return True
        return False

    def has_payload(self, objects: dict):
        """
        Checks if prims have payload.

        Args:
            objects (dict): context_menu data
        Returns:
            (bool): True if prims has payload otherwise False.
        """
        if not any(item in objects for item in ["prim", "prim_list"]):
            return False
        prim_list = [objects["prim"]] if "prim" in objects else objects["prim_list"]
        if not prim_list:
            return False
        return self._prims_have_payloads(prim_list)

    def has_reference(self, objects: dict):
        """
        Checks if prims have references.
        Args:
            objects (dict): context_menu data
        Returns:
            (bool): True if prims have reference otherwise False.
        """
        if not any(item in objects for item in ["prim", "prim_list"]):
            return False
        prim_list = [objects["prim"]] if "prim" in objects else objects["prim_list"]
        if not prim_list:
            return False
        return self._prims_have_references(prim_list)

    def can_be_copied(self, objects: dict):
        """
        Checks if prims can be copied
        Args:
            objects (dict): context_menu data
        Returns:
            (bool): True if prims can be copied else False.
        """
        if not "prim_list" in objects:
            return False
        for prim in objects["prim_list"]:
            if not omni.usd.can_be_copied(prim):
                return False
        return True

    def can_use_find_in_browser(self, objects: dict):
        """
        Checks if "find" can be used in browser.

        Args:
            objects (dict): context_menu data
        Returns:
            (bool): True if prims are authored else False.
        """
        prim = objects["prim_list"][0]
        layer = omni.usd.get_sdf_layer(prim)
        authored_prim = omni.usd.get_authored_prim(prim)
        return authored_prim and authored_prim != prim

    def can_show_find_in_browser(self, objects: dict):
        """
        Checks if "find" can be shown in browser. IE one prim is selected and is authored.
        Args:
            objects (dict): context_menu data
        Returns:
            (bool): True if authored and has URL that is saved otherwise False.
        """
        if not any(item in objects for item in ["prim", "prim_list"]):
            return False
        prim_list = [objects["prim"]] if "prim" in objects else objects["prim_list"]
        if len(prim_list) != 1:
            return False

        prim = prim_list[0]
        url_path = omni.usd.get_url_from_prim(prim)
        if url_path is not None and url_path[0:5] == "anon:":
            url_path = None
        return url_path != None

    def can_delete(self, objects: dict):
        """
        Checks if prims can be deleted
        Args:
            objects (dict): context_menu data
        Returns:
            (bool): True if prim can be deleted otherwise False.
        """
        if not any(item in objects for item in ["prim", "prim_list"]):
            return False
        prim_list = [objects["prim"]] if "prim" in objects else objects["prim_list"]

        for prim in prim_list:
            if not prim.IsValid():
                return False
            no_delete = prim.GetMetadata("no_delete")
            if no_delete is not None and no_delete is True:
                return False
        return True

    async def can_assign_material_async(self, objects: dict, menu_item: ui.Widget):
        """
        async show function. The `menu_item` is created but not visible, if this item is shown then `menu_item.visible = True`
        This scans all the prims in the stage looking for a material, if one is found then it can "assign material"
        and `menu_item.visible = True`

        Args:
            objects (dict): context_menu data.
            menu_item: (uiMenuItem): menu item.
        """
        if carb.settings.get_settings().get_as_bool("/exts/omni.kit.context_menu/show_assign_material") == False:
            return

        if not self.is_prim_selected(objects) or not self.is_material_bindable(objects):
            return

        menu_item.visible = True
        return

    def is_prim_selected(self, objects: dict):
        """
        Checks if any prims are selected

        Args:
            objects (dict): context_menu data
        Returns:
            (bool): True if one or more prim is selected otherwise False.
        """
        if not any(item in objects for item in ["prim", "prim_list"]):
            return False
        return True

    def is_prim_in_group(self, objects: dict):
        """
        Checks if any prims are in group(s)

        Args:
            objects (dict): context_menu data
        Returns:
            (bool): True if prims are part of group otherwise False.
        """
        if not "stage" in objects or not "prim_list" in objects or not objects["stage"]:
            return False

        stage = objects["stage"]
        if not stage:
            return False

        prim_list = objects["prim_list"]
        for path in prim_list:
            if isinstance(path, Usd.Prim):
                prim = path
            else:
                prim = stage.GetPrimAtPath(path)
            if prim:
                if not self.get_prim_group(prim):
                    return False
        return True

    def is_material_bindable(self, objects: dict):
        """
        Checks if prims support material binding.

        Args:
            objects (dict): context_menu data
        Returns:
            (bool): True if prims can have bound materials otherwise False.
        """
        try:
            import omni.kit.material.library

            if not any(item in objects for item in ["prim", "prim_list"]):
                return False
            prim_list = [objects["prim"]] if "prim" in objects else objects["prim_list"]

            for prim in prim_list:
                if not omni.usd.is_prim_material_supported(prim):
                    return False
        except ModuleNotFoundError:
            return False

        return True

    def prim_is_type(self, objects: dict, type: Tf.Type) -> bool:
        """
        Checks if prims are given class/schema

        Args:
            objects (dict): context_menu data.
            type (Tf.Type): prim type to check.
        Returns:
            (bool): True if prims are of type `type` otherwise False.
        """
        if not "stage" in objects or not "prim_list" in objects or not objects["stage"]:
            return False

        stage = objects["stage"]
        if not stage:
            return False

        prim_list = objects["prim_list"]
        for path in prim_list:
            if isinstance(path, Usd.Prim):
                prim = path
            else:
                prim = stage.GetPrimAtPath(path)
            if prim:
                if not prim.IsA(type):
                    return False

        return len(prim_list) > 0

    # ---------------------------------------------- core functions ----------------------------------------------

    def __init__(self):
        """
        ContextMenuExtension init function.
        """
        super().__init__()
        self._clipboard = {}

    def on_startup(self, ext_id):
        """
        ContextMenuExtension startup function.

        Args:
            ext_id (str): Extension identifier.
        """
        global _extension_instance
        _extension_instance = self

        # backwards compatibility
        ContextMenuExtension.uiMenu = ContextMenuWidgetExtension.uiMenu
        ContextMenuExtension.uiMenuItem = ContextMenuWidgetExtension.uiMenuItem
        ContextMenuExtension.DefaultMenuDelegate = ContextMenuWidgetExtension.DefaultMenuDelegate
        ContextMenuExtension.default_delegate = ContextMenuWidgetExtension.DefaultMenuDelegate()

        self._content_window = None
        self._listeners = []

        manager = omni.kit.app.get_app().get_extension_manager()
        extension_path = manager.get_extension_path(ext_id)
        global TEST_DATA_PATH
        TEST_DATA_PATH = Path(extension_path).joinpath("data").joinpath("tests")

    def on_shutdown(self):
        """
        ContextMenuExtension shutdown function.
        """
        global _extension_instance
        _extension_instance = None
        self._listeners = None

        ContextMenuExtension.uiMenu = None
        ContextMenuExtension.uiMenuItem = None
        ContextMenuExtension.DefaultMenuDelegate = None
        ContextMenuExtension.default_delegate = None

    @property
    def name(self) -> str:
        """
        [omni.kit.widget.context_menu bridge function] Name of current context menu.

        Returns:
            (str): Name of current context menu.
        """
        return get_widget_instance().name

    @property
    def menu_item_count(self) -> int:
        """
        [omni.kit.widget.context_menu bridge function] Number of items in context menu.

        Returns:
            (int): number of menu items.
        """
        return get_widget_instance().menu_item_count

    @menu_item_count.setter
    def menu_item_count(self, value):
        """
        [omni.kit.widget.context_menu bridge function] Number of items in context menu.

        Args:
            value (int): new number of menu items.
        """
        get_widget_instance().menu_item_count = value

    def close_menu(self):
        """
        [omni.kit.widget.context_menu bridge function] Close currently open context menu. Used by tests not to leave context menu in bad state.
        """
        get_widget_instance().close_menu()
        self._content_window = None
        self._menu_title = None
        self._clipboard = {}

    def separator(self, name: str="") -> bool:
        """
        [omni.kit.widget.context_menu bridge function] Creates a ui.Separator named `name`.

        Args:
            name (str): Name of the menu separator. Optional.
        """
        return get_widget_instance().separator(name)

    def menu(self, *args, **kwargs):
        """
        [omni.kit.widget.context_menu bridge function]
        Creates a menu.

        Args:
            name (str): Name of the menu.
            delegate (ui.MenuDelegate): Specify the delegate to create a custom menu. Optional.
            glyph (str): Path of the glyph image to show before the menu name. Optional.
            submenu (bool): Enables the submenu marker. Optional.
            tearable (bool): The ability to tear the window off. Optional.

        Returns:
            (uiMenu): Menu item created.
        """
        return get_widget_instance().menu(*args, **kwargs)

    def menu_item(self, *args, **kwargs):
        """
        [omni.kit.widget.context_menu bridge function]
        Creates a menu item.

        Args:
            name (str): Name of the menu item.
            triggered_fn (Callable): Function to call when menu item is clicked. Optional.
            enabled (bool): Enable the menu item. Optional.
            checkable (bool): This property holds whether this menu item is checkable. A checkable item is one which has an on/off state. Optional.
            checked (bool): This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked. Optional.
            is_async_func (bool): Optional.
            delegate (ui.MenuDelegate): Specify the delegate to create a custom menu. Optional.
            additional_kwargs (dict): Additional keyword arguments to pass to ui.MenuItem. Optional.
            glyph (str): Path of the glyph image to show before the menu name. Optional.

        Returns:
            (uiMenuItem): Menu item created.
        """
        return get_widget_instance().menu_item(*args, **kwargs)

    def _get_fn_result(self, menu_entry: dict, name: str, objects: list):
        return get_widget_instance()._get_fn_result(menu_entry, name, objects)

    def _has_click_fn(self, menu_entry):
        return get_widget_instance()._has_click_fn(menu_entry)

    def _execute_action(self, action: Tuple, objects):
        return get_widget_instance()._execute_action(action, objects)

    def _set_hotkey_for_action(self, menu_entry: dict, menu_item: ui.MenuItem):
        get_widget_instance()._set_hotkey_for_action(menu_entry, menu_item)

    def _build_menu(self, menu_entry: dict, objects: dict, delegate) -> bool:
        return get_widget_instance()._build_menu(menu_entry, objects, delegate)

    def _is_menu_visible(self, menu_entry: dict, objects: dict):
        if not self._get_fn_result(menu_entry, "show_fn", objects):
            return False
        if "populate_fn" in menu_entry:
            return True
        return True

    def show_context_menu(self, menu_name: str, objects: dict, menu_list: List[dict], min_menu_entries: int = 1, **kwargs) -> None:
        """
        [omni.kit.widget.context_menu bridge function]
        build context menu from menu_list

        Args:
            menu_name: menu name
            objects: context_menu data
            menu_list: list of dictionaries containing context menu values
            min_menu_entries: minimal number of menu needed for menu to be visible
        """
        # setup globals
        objects["clipboard"] = self._clipboard
        if "stage" not in objects:
            # TODO: We can't use `context.get_stage()` because this context
            # menu can be called for Stage Viewer and it has own stage.
            objects["stage"] = omni.usd.get_context().get_stage()

        get_widget_instance().show_context_menu(menu_name, objects, menu_list, **kwargs)

    @omni.kit.app.deprecated("Use omni.kit.material.library.bind_material_to_prims_dialog() instead")
    def bind_material_to_prims_dialog(self, stage: Usd.Stage, prims: list):
        """
        [deprecated]
        Shows bind_material_to_prims_dialog.

        Replaced by omni.kit.material.library.bind_material_to_prims_dialog()
        """
        carb.log_warn("omni.kit.context_menu.get_instance().bind_material_to_prims_dialog() is deprecated. Use omni.kit.material.library.bind_material_to_prims_dialog() instead")

        import omni.kit.material.library
        omni.kit.material.library.bind_material_to_prims_dialog(stage, prims)

    def get_context_menu(self):
        """
        [omni.kit.widget.context_menu bridge function] Gets current context_menu.

        Returns:
            (str): Current context_menu.
        """
        return get_widget_instance().get_context_menu()

################## public static functions ##################


def get_instance():
    """
    Get instance of context menu class

    Returns:
        (ContextMenuExtension): Instance of class.
    """
    return _extension_instance


def close_menu():
    """
    Close currently open context menu. Used by tests not to leave context menu in bad state.
    """
    if _extension_instance:
        _extension_instance.close_menu()


def post_notification(message: str, info: bool = False, duration: int = 3):
    """
    Post a notification via omni.kit.notification_manager.

    Args:
        message (str): The notification text.
        info (bool): notification is NotificationStatus.INFO when True otherwise NotificationStatus.WARNING
        duration (int): The duration (in seconds) after which the notification will be hidden.
                        This duration only works if hide_after_timeout is True.
    """
    try:
        import omni.kit.notification_manager as nm
        if info:
            type = nm.NotificationStatus.INFO
        else:
            type = nm.NotificationStatus.WARNING

        nm.post_notification(message, status=type, duration=duration)
    except ModuleNotFoundError:
        carb.log_warn(message)


def get_hovered_prim(objects):
    """
    Get prim currently under mouse cursor or None.

    Args:
        objects (dict): context_menu data

    Returns:
        (Usd.Prim): Prim that is hovered by mouse cursor or None.
    """
    if "hovered_prim" in objects:
        return objects["hovered_prim"]

    if "prim_list" in objects and len(objects['prim_list'])==1:
        return objects['prim_list'][0]

    return None
