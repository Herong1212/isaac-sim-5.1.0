# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ContextMenu"]

import carb
import omni.usd
import omni.kit.usd.layers as layers

from functools import partial
from pxr import Usd, Sdf, UsdShade, UsdGeom, UsdLux, Kind
import omni.kit.app


class ContextMenu:
    """Class for mananging context menu and menu items for the Stage widget."""

    def __init__(self):
        """Creates the ContextMenu instance."""
        self.function_list = {}
        self._stage_model = None

    def destroy(self):
        """Destroys the ContextMenu instance, resets the function list."""
        self.function_list = {}
        self._stage_model = None

    def on_mouse_event(self, event):
        """
        ContextMenuEvent handler for the current context menu.

        Args:
            event (omni.kit.widget.stage.stage_delegate.ContextMenuEvent): The incoming ContextMenuEvent. It contains
                information of the stage, prim path and node expansion status in its payload.
        """
        import omni.kit.menu.core

        # check its expected event
        if event.type != int(omni.kit.menu.core.MenuEventType.ACTIVATE):
            return

        try:
            import omni.kit.context_menu
        except ModuleNotFoundError:
            return
        # get context menu core functionality & check its enabled
        context_menu = omni.kit.context_menu.get_instance()
        if context_menu is None:
            carb.log_error("context_menu is disabled!")
            return

        # get stage
        stage = event.payload.get("stage", None)
        if stage is None:
            carb.log_error("stage not avaliable")
            return None

        # get parameters passed by event
        prim_path = event.payload["prim_path"]

        # setup objects, this is passed to all functions
        objects = {}
        objects["use_hovered"] = True if prim_path else False
        objects["stage_win"] = self._stage_win
        objects["node_open"] = event.payload["node_open"]
        objects["stage"] = stage
        objects["function_list"] = self.function_list
        objects["stage_model"] = self._stage_model

        prim_list = []
        hovered_prim = event.payload["prim_path"]
        paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
        if len(paths) > 0:
            for path in paths:
                prim = stage.GetPrimAtPath(path)
                if prim:
                    prim_list.append(prim)
                    if prim == hovered_prim:
                        hovered_prim = None

        elif prim_path is not None:
            prim = stage.GetPrimAtPath(prim_path)
            if prim:
                prim_list.append(prim)

        if prim_list:
            objects["prim_list"] = prim_list
        if hovered_prim:
            objects["hovered_prim"] = stage.GetPrimAtPath(hovered_prim)

        # setup menu
        menu_dict = [
            {"populate_fn": context_menu.show_selected_prims_names},
            {"populate_fn": ContextMenu.show_create_menu},
            {"name": ""},
            {
                "name": "Clear Default Prim",
                "glyph": "menu_rename.svg",
                "show_fn": [context_menu.is_prim_selected, ContextMenu.is_prim_sudo_root, ContextMenu.has_default_prim],
                "onclick_fn": ContextMenu.clear_default_prim,
            },
            {
                "name": "Set as Default Prim",
                "glyph": "menu_rename.svg",
                "show_fn": [
                    context_menu.is_prim_selected,
                    context_menu.is_one_prim_selected,
                    ContextMenu.is_prim_sudo_root,
                    ContextMenu.no_default_prim,
                ],
                "onclick_fn": ContextMenu.set_default_prim,
            },
            {"name": ""},
            {
                "name": "Find in Content Browser",
                "glyph": "menu_search.svg",
                "show_fn": [
                    context_menu.is_prim_selected,
                    context_menu.is_one_prim_selected,
                    context_menu.can_show_find_in_browser,
                ],
                "onclick_fn": context_menu.find_in_browser,
            },
            {"name": ""},
            {
                "name": "Group Selected",
                "glyph": "group_selected.svg",
                "show_fn": context_menu.is_prim_selected,
                "onclick_fn": context_menu.group_selected_prims,
            },
            {
                "name": "Ungroup Selected",
                "glyph": "group_selected.svg",
                "show_fn": [
                    context_menu.is_prim_selected,
                    context_menu.is_prim_in_group,
                ],
                "onclick_fn": context_menu.ungroup_selected_prims,
            },
            {
                "name": "Duplicate",
                "glyph": "menu_duplicate.svg",
                "show_fn": [context_menu.is_prim_selected, context_menu.can_be_copied],
                "onclick_fn": context_menu.duplicate_prim,
            },
            {
                "name": "Rename",
                "glyph": "menu_rename.svg",
                "show_fn": [
                    context_menu.is_prim_selected,
                    context_menu.is_one_prim_selected,
                    context_menu.can_delete,
                    ContextMenu.has_rename_function
                ],
                "onclick_fn": ContextMenu.rename_prim,
            },
            {
                "name": "Delete",
                "glyph": "menu_delete.svg",
                "show_fn": [context_menu.is_prim_selected, context_menu.can_delete],
                "onclick_fn": context_menu.delete_prim,
            },
            {
                "name": "Save Selected",
                "glyph": "menu_save.svg",
                "show_fn": [context_menu.is_prim_selected],
                "onclick_action": ("omni.kit.widget.stage", "save_prim"),
            },
            {"name": ""},
            {
                "name": "Activate",
                "glyph": "menu_activate.svg",
                "show_fn": [context_menu.is_prim_selected, ContextMenu.is_prim_not_active],
                "onclick_action": ("omni.kit.widget.stage", "toggle_prims_active_state"),
            },
            {
                "name": "Deactivate",
                "glyph": "menu_deactivate.svg",
                "show_fn": [context_menu.is_prim_selected, ContextMenu.is_prim_active],
                "onclick_action": ("omni.kit.widget.stage", "toggle_prims_active_state"),
            },
            {"name": ""},
            {
                "name": "Refresh Reference",
                "glyph": "sync.svg",
                "name_fn": context_menu.refresh_reference_payload_name,
                "show_fn": [context_menu.is_prim_selected, context_menu.has_payload_or_reference],
                "onclick_fn": context_menu.refresh_payload_or_reference,
            },
            {
                "name": "Convert Payloads to References",
                "glyph": "menu_duplicate.svg",
                "show_fn": [
                    context_menu.is_prim_selected,
                    context_menu.has_payload,
                    context_menu.can_convert_references_or_payloads
                ],
                "onclick_fn": context_menu.convert_payload_to_reference,
            },
            {
                "name": "Convert References to Payloads",
                "glyph": "menu_duplicate.svg",
                "show_fn": [
                    context_menu.is_prim_selected,
                    context_menu.has_reference,
                    context_menu.can_convert_references_or_payloads
                ],
                "onclick_fn": context_menu.convert_reference_to_payload,
            },
            {
                "name": "Select Bound Objects",
                "glyph": "menu_search.svg",
                "show_fn": [context_menu.is_prim_selected, context_menu.is_material],
                "onclick_fn": context_menu.select_prims_using_material,
            },
            {
                "name": "Bind Material To Selected Objects",
                "glyph": "menu_material.svg",
                "show_fn": [
                    context_menu.is_prim_selected,
                    ContextMenu.is_hovered_prim_material,
                    context_menu.is_material_bindable,
                    context_menu.is_one_prim_selected,
                ],
                "onclick_fn": ContextMenu.bind_material_to_selected_prims,
            },
            {
                "name":
                {
                    'Expand':
                    [
                        {
                            "name": "Expand To:",
                            "show_fn": [ContextMenu.show_open_tree]
                        },
                        {
                            "name": "All",
                            "onclick_fn": ContextMenu.expand_all,
                            "show_fn": [ContextMenu.show_open_tree]
                        },
                        {
                            "name": "Component",
                            "onclick_fn": lambda o, k="component": ContextMenu.expand_to(o, k),
                            "show_fn": [ContextMenu.show_open_tree]
                        },
                        {
                            "name": "Group",
                            "onclick_fn": lambda o, k="group": ContextMenu.expand_to(o, k),
                            "show_fn": [ContextMenu.show_open_tree]
                        },
                        {
                            "name": "Assembly",
                            "onclick_fn": lambda o, k="assembly": ContextMenu.expand_to(o, k),
                            "show_fn": [ContextMenu.show_open_tree]
                        },
                        {
                            "name": "SubComponent",
                            "onclick_fn": lambda o, k="subcomponent": ContextMenu.expand_to(o, k),
                            "show_fn": [ContextMenu.show_open_tree]
                        },
                    ]
                },
                "glyph": "menu_plus.svg",
                "show_fn": [ContextMenu.show_open_tree],
            },
            {
                "name":
                {
                    'Collapse':
                    [
                        {
                            "name": "Collapse To:",
                            "show_fn": [ContextMenu.show_close_tree]
                        },
                        {
                            "name": "All",
                            "onclick_fn": ContextMenu.collapse_all,
                            "show_fn": [ContextMenu.show_close_tree]
                        },
                        {
                            "name": "Component",
                            "onclick_fn": lambda o, k="component": ContextMenu.collapse_to(o, k),
                            "show_fn": [ContextMenu.show_close_tree]
                        },
                        {
                            "name": "Group",
                            "onclick_fn": lambda o, k="group": ContextMenu.collapse_to(o, k),
                            "show_fn": [ContextMenu.show_close_tree]
                        },
                        {
                            "name": "Assembly",
                            "onclick_fn": lambda o, k="assembly": ContextMenu.collapse_to(o, k),
                            "show_fn": [ContextMenu.show_close_tree]
                        },
                        {
                            "name": "SubComponent",
                            "onclick_fn": lambda o, k="subcomponent": ContextMenu.collapse_to(o, k),
                            "show_fn": [ContextMenu.show_close_tree]
                        },
                    ]
                },
                "glyph": "menu_minus.svg",
                "show_fn": [ContextMenu.show_close_tree],
            },
            {"name": ""},
            {
                "name": "Assign Material",
                "glyph": "menu_material.svg",
                "show_fn_async": context_menu.can_assign_material_async,
                "onclick_fn": ContextMenu.bind_material_to_prim_dialog,
            },
            {"name": "", "show_fn_async": context_menu.can_assign_material_async},
            {
                "name": "Copy URL Link",
                "glyph": "menu_link.svg",
                "show_fn": [
                    context_menu.is_prim_selected,
                    context_menu.is_one_prim_selected,
                    context_menu.can_show_find_in_browser,
                    context_menu.can_use_find_in_browser,
                ],
                "onclick_fn": context_menu.copy_prim_url,
            },
            {
                "name": "Copy Prim Path",
                "glyph": "menu_link.svg",
                "show_fn": context_menu.is_prim_selected,
                "onclick_fn": context_menu.copy_prim_path,
            },
        ]

        if stage:
            layers_interface = layers.get_layers(omni.usd.get_context())
            auto_authoring = layers_interface.get_auto_authoring()
            layers_state = layers_interface.get_layers_state()
            edit_mode = layers_interface.get_edit_mode()
            if edit_mode == layers.LayerEditMode.SPECS_LINKING:
                per_layer_link_menu = []
                for layer in stage.GetLayerStack():
                    if auto_authoring.is_auto_authoring_layer(layer.identifier):
                        continue

                    layer_name = layers_state.get_layer_name(layer.identifier)
                    per_layer_link_menu.append(
                        {
                            "name":
                            {
                                f"{layer_name}":
                                [
                                    {
                                        "name": "Link Selected",
                                        "show_fn": [
                                            context_menu.is_prim_selected,
                                        ],
                                        "onclick_fn": partial(
                                            ContextMenu.link_selected, True,
                                            layer.identifier, False
                                        ),
                                    },
                                    {
                                        "name": "Link Selected Hierarchy",
                                        "show_fn": [
                                            context_menu.is_prim_selected,
                                        ],
                                        "onclick_fn": partial(
                                            ContextMenu.link_selected, True,
                                            layer.identifier, True
                                        ),
                                    },
                                    {
                                        "name": "Unlink Selected",
                                        "show_fn": [
                                            context_menu.is_prim_selected,
                                        ],
                                        "onclick_fn": partial(
                                            ContextMenu.link_selected, False,
                                            layer.identifier, False
                                        ),
                                    },
                                    {
                                        "name": "Unlink Selected Hierarchy",
                                        "show_fn": [
                                            context_menu.is_prim_selected,
                                        ],
                                        "onclick_fn": partial(
                                            ContextMenu.link_selected, False,
                                            layer.identifier, True
                                        ),
                                    },
                                    {
                                        "name": "Select Linked Prims",
                                        "show_fn": [
                                        ],
                                        "onclick_fn": ContextMenu.select_linked_prims,
                                    },
                                ]
                            }
                        }
                    )

                menu_dict.extend([{"name": ""}])
                menu_dict.append(
                    {
                        "name":
                        {
                            "Layers": per_layer_link_menu
                        },
                        "glyph": "menu_link.svg",
                    }
                )

            menu_dict.extend([{"name": ""}])
            menu_dict.append(
                {
                    "name":
                    {
                        "Locks": [
                            {
                                "name": "Lock Selected",
                                "show_fn": [
                                    context_menu.is_prim_selected,
                                ],
                                "onclick_fn": partial(
                                    ContextMenu.lock_selected, True,
                                    False
                                ),
                            },
                            {
                                "name": "Lock Selected Hierarchy",
                                "show_fn": [
                                    context_menu.is_prim_selected,
                                ],
                                "onclick_fn": partial(
                                    ContextMenu.lock_selected, True,
                                    True
                                ),
                            },
                            {
                                "name": "Unlock Selected",
                                "show_fn": [
                                    context_menu.is_prim_selected,
                                ],
                                "onclick_fn": partial(
                                    ContextMenu.lock_selected, False,
                                    False
                                ),
                            },
                            {
                                "name": "Unlock Selected Hierarchy",
                                "show_fn": [
                                    context_menu.is_prim_selected,
                                ],
                                "onclick_fn": partial(
                                    ContextMenu.lock_selected, False,
                                    True
                                ),
                            },
                            {
                                "name": "Select Locked Prims",
                                "show_fn": [
                                ],
                                "onclick_fn": ContextMenu.select_locked_prims,
                            },
                        ]
                    },
                    "glyph": "menu_lock.svg",
                }
            )

        menu_dict += omni.kit.context_menu.get_menu_dict("MENU", "")
        menu_dict += omni.kit.context_menu.get_menu_dict("MENU", "omni.kit.widget.stage")
        omni.kit.context_menu.reorder_menu_dict(menu_dict)

        def _get_kinds():
            builtin_kinds = ["model", "assembly", "group", "component", "subcomponent"]
            display_builtin_kinds = builtin_kinds[1:]
            plugin_kinds = list(set(Kind.Registry.GetAllKinds()) - set(builtin_kinds))
            display_builtin_kinds.extend(plugin_kinds)
            return display_builtin_kinds

        def _set_kind(kind_string):
            paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
            stage = omni.usd.get_context().get_stage()
            for p in paths:
                model = Usd.ModelAPI(stage.GetPrimAtPath(p))
                model.SetKind(kind_string)

        kind_list = _get_kinds()
        sub_menu = []

        menu = {}
        menu["name"] = "None"
        menu["onclick_fn"] = lambda i, kind_string="": _set_kind(kind_string)
        sub_menu.append(menu)

        for k in kind_list:
            menu = {}

            menu["name"] = str(k).capitalize()
            menu["onclick_fn"] = lambda i, kind_string=str(k): _set_kind(kind_string)
            sub_menu.append(menu)

        menu_dict.append(
            {
                "name": {
                    "Set Kind": sub_menu
                },
                "glyph": "none.svg"
            }
        )

        # show menu
        try:
            context_menu.show_context_menu("stagewindow", objects, menu_dict)
        except Exception as e:
            import traceback
            traceback.print_exc()

    # ---------------------------------------------- menu show functions ----------------------------------------------
    def is_prim_active(objects):
        """
        Checks if the selected prim is active.
        If the prim selection is not a single prim (eg. empty selection or multiple selected), returns False.

        Args:
            objects (Dict): The context object.

        Returns:
            bool: Whether the selected prim is active. If the prim selection is not a single prim, returns False.
        """
        if not "prim_list" in objects:
            return False
        prim_list = objects["prim_list"]
        prim = prim_list[0]

        return prim.IsActive()

    def is_prim_not_active(objects):
        """
        Checks if the selected prim is NOT active.
        If the prim selection is not a single prim (eg. empty selection or multiple selected), returns True.

        Args:
            objects (Dict): The context object.

        Returns:
            bool: Whether the selected prim is NOT active. If the prim selection is not a single prim, returns True.
        """
        return not ContextMenu.is_prim_active(objects)

    def is_prim_sudo_root(objects):
        """
        Checks if the selected prim is at the root level of the stage.
        If the prim selection is not a single prim (eg. empty selection or multiple selected), returns False.

        Args:
            objects (Dict): The context object.

        Returns:
            bool: Whether the selected prim is at root level. If the prim selection is not a single prim, returns False.
        """
        if not "prim_list" in objects:
            return False
        prim_list = objects["prim_list"]
        if len(prim_list) != 1:
            return False
        prim = prim_list[0]
        return prim.GetParent() == prim.GetStage().GetPseudoRoot()

    def has_default_prim(objects):
        """
        Checks if the selected prim is the default prim of the stage.
        If the prim selection is not a single prim (eg. empty selection or multiple selected), returns False. If the
        stage doesn't have a default prim, also returns False.

        Args:
            objects (Dict): The context object.

        Returns:
            bool: Whether the selected prim is the default prim. If the prim selection is not a single prim, returns False.
        """
        if not "prim_list" in objects:
            return False
        prim_list = objects["prim_list"]
        if len(prim_list) != 1:
            return False
        stage = objects["stage"]
        return stage.HasDefaultPrim() and stage.GetDefaultPrim() == prim_list[0]

    def no_default_prim(objects):
        """
        Checks if the selected prim is NOT the default prim of the stage.
        If the prim selection is not a single prim (eg. empty selection or multiple selected), returns True. If the
        stage doesn't have a default prim, also returns True.

        Args:
            objects (Dict): The context object.

        Returns:
            bool: Whether the selected prim is NOT the default prim. If the prim selection is not a single prim,
                returns False.
        """
        return not ContextMenu.has_default_prim(objects)

    def is_hovered_prim_material(objects):
        """
        Checks if the hoved prim is a USD Material prim.
        If no hovered prim detected, returns False.

        Args:
            objects (Dict): The context object.

        Returns:
            bool: Whether the hovered prim is a USD Material prim. If no hovered prim detected, returns False.
        """
        hovered_prim = objects.get("hovered_prim", None)
        if not hovered_prim:
            return False
        return hovered_prim.IsA(UsdShade.Material)

    def show_open_tree(objects):  # pragma: no cover
        """
        If the expansion related context menu items should be shown for the (first) selected prim.
        If the prim is a light or camera and doesn't have multiple children, items should not be shown. Otherwise, if
        the prim doesn't have any children, items should not be shown.
        If the current prim's associated tree node item is open, then items should not be shown.

         Args:
            objects (Dict): The context object.

        Returns:
            bool: Whether the expansion related context menu items should be shown for the (first) selected prim.
        """
        if not "prim_list" in objects:
            return False
        prim = objects["prim_list"][0]
        # https://github.com/PixarAnimationStudios/USD/commit/7540fdf3b2aa6b6faa0fce8e7b4c72b756286f51
        if prim.IsA(UsdGeom.Camera) or ((prim.HasAPI(UsdLux.LightAPI)) if hasattr(UsdLux, 'LightAPI') else prim.IsA(UsdLux.Light)):
            if len(prim.GetChildren()) <= 1:
                return False
        else:
            if len(prim.GetChildren()) == 0:
                return False

        if objects["node_open"]:
            return False
        else:
            return True

    def show_close_tree(objects):  # pragma: no cover
        """
        If the collapsion related context menu items should be shown for the (first) selected prim.
        If the prim is a light or camera and doesn't have multiple children, items should not be shown. Otherwise, if
        the prim doesn't have any children, items should not be shown.
        If the current prim's associated tree node item is open, then items should be shown.

         Args:
            objects (Dict): The context object.

        Returns:
            bool: Whether the collapsion related context menu items should be shown for the (first) selected prim.
        """

        if not "prim_list" in objects:
            return False
        prim = objects["prim_list"][0]
        # https://github.com/PixarAnimationStudios/USD/commit/7540fdf3b2aa6b6faa0fce8e7b4c72b756286f51
        if prim.IsA(UsdGeom.Camera) or ((prim.HasAPI(UsdLux.LightAPI)) if hasattr(UsdLux, 'LightAPI') else prim.IsA(UsdLux.Light)):
            if len(prim.GetChildren()) <= 1:
                return False
        else:
            if len(prim.GetChildren()) == 0:
                return False

        if objects["node_open"]:
            return True
        else:
            return False

    # ---------------------------------------------- menu onClick functions ----------------------------------------------

    def expand_all(objects):
        """
        Expands all hovered or selected prims.

        Args:
            objects (Dict): The context object.
        """
        prim = None
        if "hovered_prim" in objects and objects["hovered_prim"]:
            prim = objects["hovered_prim"]
        elif "prim_list" in objects and objects["prim_list"]:
            prim = objects["prim_list"]

        if not prim:
            return

        if isinstance(prim, list):
            prim_list = prim
        else:
            prim_list = [prim]

        def recurse_expand(prim):
            objects["stage_win"].context_menu_handler(
                cmd="opentree", prim_path=prim.GetPath().pathString
            )
            for p in prim.GetChildren():
                recurse_expand(p)
        for p in prim_list:
            if isinstance(p, Usd.Prim):
                recurse_expand(p)

    def expand_to(objects, kind):
        """
        Expands the hovered or selected prims recursively if the kind matches the given Kind.

        Args:
            objects (Dict): The context object.
            kind (str): The USD Kind to collapse.
        """
        prim = None
        if "hovered_prim" in objects and objects["hovered_prim"]:
            prim = objects["hovered_prim"]
        elif "prim_list" in objects and objects["prim_list"]:
            prim = objects["prim_list"]

        if not prim:
            return

        if isinstance(prim, list):
            prim_list = prim
        else:
            prim_list = [prim]

        def recurse_expand(prim, kind):
            expand = False
            model = Usd.ModelAPI(prim)
            if model.GetKind() != kind:
                for p in prim.GetChildren():
                    expand = recurse_expand(p, kind) or expand
            else:
                # do not expand the target kind
                return True

            if expand:
                objects["stage_win"].context_menu_handler(
                    cmd="opentree", prim_path=prim.GetPath().pathString
                )

            return expand
        for p in prim_list:
            if isinstance(p, Usd.Prim):
                recurse_expand(p, kind)

    def collapse_all(objects):
        """
        Collapses all hovered or selected prims.

        Args:
            objects (Dict): The context object.
        """
        prim = None
        if "hovered_prim" in objects and objects["hovered_prim"]:
            prim = objects["hovered_prim"]
        elif "prim_list" in objects and objects["prim_list"]:
            prim = objects["prim_list"]

        if not prim:
            return

        if isinstance(prim, list):
            prim_list = prim
        else:
            prim_list = [prim]

        for p in prim_list:
            if isinstance(p, Usd.Prim):
                objects["stage_win"].context_menu_handler(
                    cmd="closetree", prim_path=p.GetPath().pathString
                )

    def collapse_to(objects, kind):
        """
        Collapses the hovered or selected prims recursively if the kind matches the given Kind.

        Args:
            objects (Dict): The context object.
            kind (str): The USD Kind to collapse.
        """
        prim = None
        if "hovered_prim" in objects and objects["hovered_prim"]:
            prim = objects["hovered_prim"]
        elif "prim_list" in objects and objects["prim_list"]:
            prim = objects["prim_list"]

        if not prim:
            return

        if isinstance(prim, list):
            prim_list = prim
        else:
            prim_list = [prim]

        def recurse_collapse(prim, kind):
            collapse = False
            model = Usd.ModelAPI(prim)
            if model.GetKind() != kind:
                for p in prim.GetChildren():
                    collapse = recurse_collapse(p, kind) or collapse
            else:
                collapse = True

            if collapse:
                objects["stage_win"].context_menu_handler(
                    cmd="closetree", prim_path=prim.GetPath().pathString
                )
        for p in prim_list:
            if isinstance(p, Usd.Prim):
                recurse_collapse(p, kind)

    def link_selected(link_or_unlink, layer_identifier, hierarchy, objects):  # pragma: no cover
        """
        Lock or unlink selected prims.

        Args:
            link_or_unlink (bool): Links the spec paths if True, else the operation is unlink.
            layer_identifiers (Union[str, List[str]]): List of layer identifiers or single layer identifier.
            hierarchy (bool): Linking/Unlinking descendant specs or not.
            objects: The context object.
        """
        prim_list = objects.get("prim_list", None)
        if not prim_list:
            return

        prim_paths = []
        for prim in prim_list:
            prim_paths.append(prim.GetPath())

        if link_or_unlink:
            command = "LinkSpecs"
        else:
            command = "UnlinkSpecs"

        omni.kit.commands.execute(
            command,
            spec_paths=prim_paths,
            layer_identifiers=layer_identifier,
            hierarchy=hierarchy
        )

    def lock_selected(lock_or_unlock, hierarchy, objects):
        """
        Lock or unlock selected prims.

        Args:
            lock_or_unlock (bool): Locks the spec paths if True, else the operation is unlock.
            hierarchy (bool): Locking/Unlocking descendant specs or not.
            objects: The context object.
        """
        prim_list = objects.get("prim_list", None)
        if not prim_list:
            return

        prim_paths = []
        for prim in prim_list:
            prim_paths.append(prim.GetPath())

        if lock_or_unlock:
            command = "LockSpecs"
        else:
            command = "UnlockSpecs"

        omni.kit.commands.execute(
            command,
            spec_paths=prim_paths,
            hierarchy=hierarchy
        )

    def select_linked_prims(objects):  # pragma: no cover
        """
        Select all linked prims in the current usd context.

        Args:
            objects (Dict): The context object. Unused.
        """
        usd_context = omni.usd.get_context()
        links = omni.kit.usd.layers.get_all_spec_links(usd_context)
        prim_paths = [spec_path for spec_path in links.keys() if Sdf.Path(spec_path).IsPrimPath()]
        if prim_paths:
            old_prim_paths = usd_context.get_selection().get_selected_prim_paths()
            omni.kit.commands.execute(
                "SelectPrims", old_selected_paths=old_prim_paths,
                new_selected_paths=prim_paths, expand_in_stage=True
            )

    def select_locked_prims(objects):
        """
        Select all locked prims in the current usd context.

        Args:
            objects (Dict): The context object. Unused.
        """
        usd_context = omni.usd.get_context()
        locked_specs = omni.kit.usd.layers.get_all_locked_specs(usd_context)
        prim_paths = [spec_path for spec_path in locked_specs if Sdf.Path(spec_path).IsPrimPath()]
        if prim_paths:
            old_prim_paths = usd_context.get_selection().get_selected_prim_paths()
            omni.kit.commands.execute(
                "SelectPrims", old_selected_paths=old_prim_paths,
                new_selected_paths=prim_paths, expand_in_stage=True
            )

    def clear_default_prim(objects):
        """
        Clears the default prim of the stage.

        Args:
            objects (Dict): The context object.
        """
        objects["stage"].ClearDefaultPrim()

    def set_default_prim(objects):
        """
        Sets the (first) selected prim as the default prim of the stage.

        Args:
            objects (Dict): The context object.
        """
        objects["stage"].SetDefaultPrim(objects["prim_list"][0])

    def show_create_menu(objects):
        """
        Builds and shows the "Create" and "Add" menu.

        Args:
            objects (Dict): The context object.
        """
        prim_list = objects["prim_list"] if "prim_list" in objects else None
        omni.kit.context_menu.get_instance().build_create_menu(
            objects, prim_list, omni.kit.context_menu.get_menu_dict("CREATE", "omni.kit.widget.stage")
        )
        omni.kit.context_menu.get_instance().build_add_menu(
            objects, prim_list, omni.kit.context_menu.get_menu_dict("ADD", "omni.kit.widget.stage")
        )

    def bind_material_to_prim_dialog(objects):
        """
        Displays the dialog where users can select materials and bind to selected prims.
        Will not show the dialog if no prims are selected.

        Args:
            objects (Dict): The context object.
        """
        if not "prim_list" in objects:
            return
        omni.kit.material.library.bind_material_to_prims_dialog(objects["stage"], objects["prim_list"])

    def bind_material_to_selected_prims(objects):
        """
        Binds the hovered material prim to selected prims.
        If either the hovered prim or the prim list is empty, no operation will be done.

        Args:
            objects (Dict): The context object.
        """
        if not all(item in objects for item in ["hovered_prim", "prim_list"]):
            return
        material_prim = objects["hovered_prim"]
        prim_paths = [i.GetPath() for i in objects["prim_list"]]
        omni.kit.commands.execute(
            "BindMaterial", prim_path=prim_paths, material_path=material_prim.GetPath().pathString, strength=None
        )

    def has_rename_function(objects):
        """
        Checks whether there's a provided rename function in the current context object.

        Args:
            objects (Dict): The context object.

        Returns:
            bool: True if 'rename_item' is in function list
        """
        return "rename_item" in objects["function_list"]

    def rename_prim(objects):
        """
        Runs the provided 'rename_item' function on a prim.
        If the prim list provided in the context is empty or of multiple prims, it returns False without applying any
        rename function.

        Args:
            objects (Dict): The context object.

        Returns:
            Optional[bool]: False if the prim list provided is empty or is of multiple prims. Otherwise if a rename
                function is provided, it will run the function without returning.
        """
        if not "prim_list" in objects:
            return False
        prim_list = objects["prim_list"]
        if len(prim_list) != 1:
            return False
        prim = prim_list[0]

        if "rename_item" in objects["function_list"]:
            objects["function_list"]["rename_item"](prim.GetPath().pathString)

    @staticmethod
    def add_menu(menu_dict):
        """
        Adds the menu to the end of the context menu.
        Returns the MenuSubscription object that should be alive all the time. Once the returned object is destroyed,
        the added menu will be destroyed as well.

        Args:
            menu_dict: A dictionary containing menu settings. See ContextMenuExtension docs for information on values.

        Returns:
            MenuSubscription. Keep a copy of this as the custom menu will be removed when `release()` is explicitly
                called or when this is garbage collected.
        """
        return omni.kit.context_menu.add_menu(menu_dict, "MENU", "omni.kit.widget.stage")

    @staticmethod
    def add_create_menu(menu_dict):
        """
        Adds the menu to the end of the stage context create menu.
        Returns the MenuSubscription object that should be alive all the time. Once the returned object is destroyed,
        the added menu will be destroyed as well.

        Args:
            menu_dict: A dictionary containing menu settings. See ContextMenuExtension docs for information on values.

        Returns:
            MenuSubscription. Keep a copy of this as the custom menu will be removed when `release()` is explicitly
                called or when this is garbage collected.
        """
        return omni.kit.context_menu.add_menu(menu_dict, "CREATE", "omni.kit.widget.stage")
