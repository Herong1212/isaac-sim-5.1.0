# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import weakref
import carb
import omni.kit.undo

from omni import ui
from functools import partial
from pxr import Sdf
from .prim_spec_item import PrimSpecItem, PrimSpecSpecifier
from .layer_item import LayerItem
from .layer_model_utils import LayerModelUtils
from omni.kit.usd.layers import LayerUtils
from .singleton import Singleton


@Singleton
class CustomMenuList:
    """
    The singleton object that holds custom context menu. Other extensions can
    add items to this object using `ContextMenu.get_instance`.
    """

    def __init__(self):
        self.__custom_menu_list = {}
        self.__counter = 0

    def add_menu(self, menu):
        menu_id = self.__counter
        self.__custom_menu_list[menu_id] = menu
        self.__counter += 1
        return menu_id

    def remove_menu(self, menu_id):
        del self.__custom_menu_list[menu_id]

    def get_menu_list(self):
        result = []
        for key, menu in self.__custom_menu_list.items():
            result += menu

        return result


class ContextMenuEvent:
    """The object comatible with ContextMenu"""

    def __init__(self, item: weakref, expanded=None):
        self.type = 0
        self.payload = {"item": item, "node_open": expanded}


class ContextMenu:
    """ Context menu for the layers widget"""
    def __init__(self, usd_context):
        """
        Initializes the ContextMenu with a specific USD context.

        Args:
            usd_context(omni.usd.UsdContext): The USD context to be associated with this context menu.
        """
        self.tree_view = None
        self._usd_context = usd_context

    def on_mouse_event(self, event):
        """Handles mouse events and show context menu  based on the event type.

        Args:
            event: An event object containing details about the mouse event.

        Returns:
            None if the module is not found or if the event type is not ACTIVATE.
        """
        import omni.kit.menu.core

        # check its expected event
        if event.type != int(omni.kit.menu.core.MenuEventType.ACTIVATE):
            return

        try:
            import omni.kit.context_menu
        except ModuleNotFoundError:
            return None

        # get context menu core functionality & check its enabled
        context_menu = omni.kit.context_menu.get_instance()
        if context_menu is None:
            carb.log_error("context_menu is disabled!")
            return None

        # get stage
        stage = self._usd_context.get_stage()
        if stage is None:
            carb.log_error("stage not avaliable")
            return None

        # get parameters passed by event
        item = event.payload["item"]
        node_expanded = event.payload["node_open"]

        prim_item_list = []
        layer_item_list = []
        selections = self.tree_view().selection
        if item and item() and self.tree_view and self.tree_view():
            for selected_item in selections:
                if isinstance(selected_item, PrimSpecItem):
                    prim_item_list.append(weakref.ref(selected_item))
                elif isinstance(selected_item, LayerItem):
                    layer_item_list.append(weakref.ref(selected_item))

        # setup objects, this is passed to all functions
        objects = {}
        objects["item"] = item
        objects["prim_item_list"] = prim_item_list
        objects["layer_item_list"] = layer_item_list
        objects["node_open"] = node_expanded
        objects["stage"] = stage
        objects["tree_view"] = self.tree_view

        if self.is_over_specifier(objects):
            delete_prim_title = "Delete Delta"
        else:
            delete_prim_title = "Delete"
        # setup menu
        menu_list = [
            {
                "name": "Set Default Edit Layer",
                "glyph": "menu_rename.svg",
                "show_fn": [
                    ContextMenu.is_layer_item,
                    ContextMenu.is_auto_authoring_or_spec_linking_mode,
                    ContextMenu.is_not_missing_layer,
                    ContextMenu.is_layer_not_locked,
                    ContextMenu.is_layer_writable,
                    ContextMenu.is_layer_and_parent_unmuted,
                    ContextMenu.is_not_edit_layer,
                ],
                "onclick_fn": ContextMenu.set_edit_layer,
            },
            {
                "name": "Set Authoring Layer",
                "glyph": "menu_rename.svg",
                "show_fn": [
                    ContextMenu.is_layer_item,
                    ContextMenu.is_not_missing_layer,
                    ContextMenu.is_layer_not_locked,
                    ContextMenu.is_layer_writable,
                    ContextMenu.is_layer_and_parent_unmuted,
                    ContextMenu.is_not_auto_authoring_and_spec_linking_mode,
                    ContextMenu.can_set_as_edit_target
                ],
                "onclick_fn": ContextMenu.set_authoring_layer,
            },
            {
                "name": "Create Sublayer",
                "glyph": "menu_create_sublayer.svg",
                "show_fn": [
                    ContextMenu.no_items_selected,
                    ContextMenu.can_edit_root_layer,
                ],
                "onclick_fn": ContextMenu.create_sublayer,
            },
            {
                "name": "Insert Sublayer",
                "glyph": "menu_insert_sublayer.svg",
                "show_fn": [
                    ContextMenu.no_items_selected,
                    ContextMenu.can_edit_root_layer,
                ],
                "onclick_fn": ContextMenu.insert_sublayer,
            },
            {"name": ""},
            {
                "name": "Create Sublayer",
                "glyph": "menu_create_sublayer.svg",
                "show_fn": [
                    ContextMenu.is_layer_item,
                    ContextMenu.is_not_missing_layer,
                    ContextMenu.is_layer_writable,
                    ContextMenu.is_layer_not_locked,
                    ContextMenu.is_layer_and_parent_unmuted,
                    ContextMenu.can_edit_sublayer
                ],
                "onclick_fn": ContextMenu.create_sublayer,
            },
            {
                "name": "Insert Sublayer",
                "glyph": "menu_insert_sublayer.svg",
                "show_fn": [
                    ContextMenu.is_layer_item,
                    ContextMenu.is_not_missing_layer,
                    ContextMenu.is_layer_writable,
                    ContextMenu.is_layer_not_locked,
                    ContextMenu.is_layer_and_parent_unmuted,
                    ContextMenu.can_edit_sublayer
                ],
                "onclick_fn": ContextMenu.insert_sublayer,
            },
            {
                "name": "New Anonymous Sublayer",
                "glyph": "menu_create_sublayer.svg",
                "show_fn": [
                    ContextMenu.is_layer_item,
                    ContextMenu.is_not_missing_layer,
                    ContextMenu.is_layer_writable,
                    ContextMenu.is_layer_not_locked,
                    ContextMenu.is_layer_and_parent_unmuted,
                    ContextMenu.is_from_session_layer_tree,
                    ContextMenu.can_edit_sublayer
                ],
                "onclick_fn": ContextMenu.create_anonymous_sublayer,
            },
            {
                "name": "Merge Down One",
                "glyph": "menu_merge_down.svg",
                "show_fn": [
                    ContextMenu.is_layer_item,
                    ContextMenu.is_not_missing_layer,
                    ContextMenu.is_layer_writable,
                    ContextMenu.is_layer_not_locked,
                    ContextMenu.is_layer_and_parent_unmuted,
                    ContextMenu.is_not_reserved_layer,
                    ContextMenu.can_merge_layer_down,
                    ContextMenu.is_not_from_session_layer_tree,
                    ContextMenu.can_edit_sublayer
                ],
                "onclick_fn": ContextMenu.merge_down_one,
            },
            {
                "name": "Flatten Sublayers",
                "glyph": "menu_flatten_layers.svg",
                "show_fn": [
                    ContextMenu.is_layer_item,
                    ContextMenu.has_sublayers,
                    ContextMenu.is_not_missing_layer,
                    ContextMenu.is_not_from_session_layer_tree,
                    ContextMenu.has_no_layers_locked,
                    ContextMenu.can_flatten_sublayers
                ],
                "onclick_fn": ContextMenu.flatten_sublayers,
            },
            {"name": ""},
            {
                "name": "Save",
                "glyph": "menu_save.svg",
                "show_fn": [
                    ContextMenu.is_layer_item,
                    ContextMenu.is_not_missing_layer,
                    ContextMenu.is_layer_writable,
                    ContextMenu.is_layer_not_locked,
                    ContextMenu.is_layer_and_parent_unmuted,
                    ContextMenu.is_not_anonymous_layer,
                    ContextMenu.is_layer_dirty,
                    ContextMenu.is_not_live_layer
                ],
                "onclick_fn": ContextMenu.save_layer,
            },
            {
                "name": "Save a Copy",
                "glyph": "menu_save_as.svg",
                "show_fn": [ContextMenu.is_layer_item, ContextMenu.is_not_missing_layer],
                "onclick_fn": ContextMenu.save_layer_as,
            },
            {
                "name": "Save As",
                "glyph": "menu_save_as.svg",
                "show_fn":
                [
                    ContextMenu.is_layer_item,
                    ContextMenu.is_not_missing_layer,
                    ContextMenu.is_layer_and_parent_unmuted,
                    ContextMenu.is_not_reserved_layer,
                    ContextMenu.is_not_live_layer,
                    ContextMenu.can_edit_sublayer
                ],
                "onclick_fn": ContextMenu.save_layer_as_and_replace,
            },
            {"name": ""},
            {
                "name": "Reload Layer",
                "glyph": "menu_refresh.svg",
                "show_fn": [
                    ContextMenu.is_layer_item,
                    ContextMenu.is_not_missing_layer,
                    ContextMenu.is_not_anonymous_layer,
                    ContextMenu.is_layer_not_locked,
                    ContextMenu.is_layer_and_parent_unmuted,
                    ContextMenu.is_not_live_layer
                ],
                "onclick_fn": ContextMenu.reload_layer,
            },
            {
                "name": "Remove Layer",
                "glyph": "menu_remove_layer.svg",
                "show_fn": [
                    ContextMenu.is_layer_item,
                    ContextMenu.is_layer_not_locked,
                    ContextMenu.is_not_reserved_layer,
                    ContextMenu.is_not_live_layer,
                    ContextMenu.can_edit_sublayer,
                    ContextMenu.can_edit_sublayer_parent,
                    ContextMenu.is_not_authoring_layer,
                ],
                "onclick_fn": ContextMenu.remove_layer,
            },
            {
                "name": delete_prim_title,
                "glyph": "menu_delete.svg",
                "show_fn": [
                    ContextMenu.is_prim_spec_item,
                    ContextMenu.is_layer_writable,
                    ContextMenu.is_layer_not_locked,
                    ContextMenu.is_layer_and_parent_unmuted,
                    ContextMenu.can_delete_prim,
                ],
                "onclick_fn": ContextMenu.prim_delete,
            },
            {
                "name": "Move Selections To This Layer",
                "glyph": "menu_duplicate.svg",
                "show_fn": [
                    ContextMenu.is_layer_item,
                    ContextMenu.is_layer_writable,
                    ContextMenu.is_layer_not_locked,
                    ContextMenu.is_layer_and_parent_unmuted,
                    ContextMenu.can_edit_sublayer,
                    self.has_selections
                ],
                "onclick_fn": self.move_prims,
            },
            {"name": ""},
            {
                "name": "Refresh Reference",
                "glyph": "sync.svg",
                "name_fn": ContextMenu.refresh_reference_payload_name,
                "show_fn": [ContextMenu.is_prim_spec_item, ContextMenu.has_payload_or_reference],
                "onclick_fn": lambda o: context_menu.refresh_payload_or_reference(ContextMenu._stage_window_object(o))
            },
            {
                "name": "Select Bound Objects",
                "glyph": "menu_search.svg",
                "show_fn": ContextMenu.is_material,
                "onclick_fn": lambda o: context_menu.select_prims_using_material(ContextMenu._stage_window_object(o))
            },
            {"populate_fn": ContextMenu.show_open_close_tree},
            {"name": ""},
            {
                "name": "Copy URL Link",
                "glyph": "menu_link.svg",
                "show_fn": [
                    ContextMenu.has_any_items_selected
                ],
                "onclick_fn": ContextMenu.copy_url},
            {
                "name": "Find in Content Browser",
                "glyph": "menu_search.svg",
                "show_fn": [
                    ContextMenu.is_layer_item,
                    ContextMenu.is_not_missing_layer,
                    ContextMenu.is_not_anonymous_layer,
                ],
                "onclick_fn": ContextMenu.find_in_browser,
            }
        ]
        """
        menu_list = [

        ]
        """

        layer_item = ContextMenu._get_layer_item(objects)
        if layer_item and layer_item.model.spec_linking_mode:
            menu_list.append({
                "name":
                {
                    "Prim Linking":
                    [
                        {
                            "name": "Link Selected",
                            "show_fn": [
                                self.has_selections,
                                ContextMenu.is_layer_item,
                                ContextMenu.is_not_missing_layer,
                            ],
                            "onclick_fn": self.link_selected_prims
                        },
                        {
                            "name": "Link Selected Hierarchy",
                            "show_fn": [
                                self.has_selections,
                                ContextMenu.is_layer_item,
                                ContextMenu.is_not_missing_layer,
                            ],
                            "onclick_fn": self.link_selected_prims_with_hierarchy,
                        },
                        {
                            "name": "Unlink Selected",
                            "show_fn": [
                                self.has_selections,
                                ContextMenu.is_layer_item,
                                ContextMenu.is_not_missing_layer,
                            ],
                            "onclick_fn": self.unlink_selected_prims,
                        },
                        {
                            "name": "Unlink Selected Hierarchy",
                            "show_fn": [
                                self.has_selections,
                                ContextMenu.is_layer_item,
                                ContextMenu.is_not_missing_layer,
                            ],
                            "onclick_fn": self.unlink_selected_prims_with_hierarchy,
                        },
                        {
                            "name": "Select Linked Prims",
                            "show_fn": [
                                ContextMenu.is_layer_item,
                                ContextMenu.is_not_missing_layer,
                            ],
                            "onclick_fn": self.select_linked_prims,
                        },
                        {
                            "name": "Clear All Linked Prims",
                            "show_fn": [
                                ContextMenu.is_layer_item,
                                ContextMenu.is_not_missing_layer,
                            ],
                            "onclick_fn": self.clear_all_linked_prims,
                        }
                    ]
                },
                "glyph": "menu_link.svg",
            })

        menu_list += CustomMenuList().get_menu_list()

        # show menu
        context_menu.show_context_menu("layers_widget", objects, menu_list)

    def is_over_specifier(self, objects):
        """
        Check if the selected prim item's specifier is 'OVER_ONLY'.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        prim_item = ContextMenu._get_prim_spec_item(objects)
        if not prim_item:
            return False

        return prim_item.specifier == PrimSpecSpecifier.OVER_ONLY

    # ---------------------------------------------- menu show test functions ----------------------------------------------
    def _get_layer_item(objects) -> LayerItem:
        item = objects["item"]
        if not item or not item():
            return None

        if isinstance(item(), PrimSpecItem):
            return item().layer_item
        elif isinstance(item(), LayerItem):
            return item()

        return None

    def _get_prim_spec_item(objects):
        item = objects["item"]
        if not item or not item():
            return None

        if isinstance(item(), PrimSpecItem):
            return item()

        return None

    def link_selected_prims(self, objects):  # pragma: no cover
        """
        Link the selected prims to a specific layer item.

        Args:
            objects (dict): A dictionary containing selected item information.
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if not layer_item:
            return

        selections = self._usd_context.get_selection().get_selected_prim_paths()
        omni.kit.commands.execute(
            "LinkSpecs",
            spec_paths=selections,
            layer_identifiers=layer_item.identifier,
            additive=True, hierarchy=False,
            usd_context=self._usd_context
        )

    def link_selected_prims_with_hierarchy(self, objects):  # pragma: no cover
        """
        Link the selected prims to a specific layer item with hierarchy.

        Args:
            objects (dict): A dictionary containing selected item information.
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if not layer_item:
            return

        selections = self._usd_context.get_selection().get_selected_prim_paths()
        omni.kit.commands.execute(
            "LinkSpecs",
            spec_paths=selections,
            layer_identifiers=layer_item.identifier,
            additive=True, hierarchy=True,
            usd_context=self._usd_context
        )

    def unlink_selected_prims(self, objects):  # pragma: no cover
        """
        Unlink the selected prims to a specific layer item.

        Args:
            objects (dict): A dictionary containing selected item information.
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if not layer_item:
            return

        selections = self._usd_context.get_selection().get_selected_prim_paths()
        omni.kit.commands.execute(
            "UnlinkSpecs",
            spec_paths=selections,
            layer_identifiers=layer_item.identifier,
            hierarchy=False,
            usd_context=self._usd_context
        )

    def unlink_selected_prims_with_hierarchy(self, objects):  # pragma: no cover
        """
        Unlink the selected prims to a specific layer item with hierarchy.

        Args:
            objects (dict): A dictionary containing selected item information.
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if not layer_item:
            return

        selections = self._usd_context.get_selection().get_selected_prim_paths()
        omni.kit.commands.execute(
            "UnlinkSpecs",
            spec_paths=selections,
            layer_identifiers=layer_item.identifier,
            hierarchy=True,
            usd_context=self._usd_context
        )

    def select_linked_prims(self, objects):  # pragma: no cover
        """
        Select the linked prims from a specific layer item.

        Args:
            objects (dict): A dictionary containing selected item information.
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if not layer_item:
            return

        all_links = omni.kit.usd.layers.get_spec_links_for_layers(self._usd_context, layer_item.identifier)
        spec_paths = all_links.get(layer_item.identifier, None)
        if spec_paths:
            prim_paths = [spec_path for spec_path in spec_paths if Sdf.Path(spec_path).IsPrimPath()]
            if prim_paths:
                old_prim_paths = self._usd_context.get_selection().get_selected_prim_paths()
                omni.kit.commands.execute(
                    "SelectPrims", old_selected_paths=old_prim_paths,
                    new_selected_paths=prim_paths, expand_in_stage=True
                )

    def clear_all_linked_prims(self, objects):  # pragma: no cover
        """
        Clear all the linked prims from a specific layer item.

        Args:
            objects (dict): A dictionary containing selected item information.
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if not layer_item:
            return

        omni.kit.commands.execute(
            "UnlinkSpecs",
            spec_paths="/",
            layer_identifiers=layer_item.identifier,
            hierarchy=True,
            usd_context=self._usd_context
        )

    def show_open_close_tree(objects):
        """
        Toggle tree from a specific layer/prim item.

        Args:
            objects (dict): A dictionary containing selected item information.
        """
        tree_view = objects["tree_view"]
        item = objects["item"]
        if not item or not tree_view() or not item():
            return False

        if not item().has_children:
            return

        def expand_item(objects, expanded):
            tree_view = objects["tree_view"]
            item = objects["item"]
            if not tree_view() or not item():
                return False

            if tree_view().is_expanded(item()) != expanded:
                return

            tree_view().set_expanded(item(), not expanded, False)

        try:
            import omni.kit.context_menu
            from omni.kit.context_menu import ContextMenuExtension
            omni.kit.context_menu.get_instance().separator("layer")
            expanded = tree_view().is_expanded(item())
            if expanded:
                objects["tree_item"] = ContextMenuExtension.uiMenuItem(
                    f'Collapse Tree',
                    triggered_fn=partial(expand_item, objects, expanded),
                    glyph="menu_minus.svg"
            )
            else:
                objects["tree_item"] = ContextMenuExtension.uiMenuItem(
                    f'Expand Tree',
                    triggered_fn=partial(expand_item, objects, expanded),
                    glyph="menu_plus.svg"
            )
        except ModuleNotFoundError:
            pass

    def is_item_expaned(objects):  # pragma: no cover
        """Unused."""

        tree_view = objects["tree_view"]
        item = objects["item"]
        if not tree_view() or not item():
            return False

        return tree_view.is_expanded(item)

    def has_any_items_selected(objects):
        """
        Check any items selected.

        Args:
            objects (dict): A dictionary containing selected item information.
            
        Returns:
            bool: True if any item selected, otherwise False.    
        """
        return not ContextMenu.no_items_selected(objects)

    def no_items_selected(objects):
        """
        Check any items selected.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool: False if any item selected, otherwise True.  
        """
        item = objects["item"]
        return item is None

    def is_layer_item(objects):
        """
        Check if the selected item is layer item.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool: True if selected item is layer item, otherwise True.  
        """
        item = objects["item"]

        return item and item() and isinstance(item(), LayerItem)

    def has_selections(self, objects):
        """
        If the usd context has selectetions.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool: True if any thing selected in usd context, otherwise False.  
        """
        selection = self._usd_context.get_selection()
        paths = selection.get_selected_prim_paths()
        return len(paths) > 0

    def is_prim_spec_item(objects):
        """
        Check if the selected item is prim spec item.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool: True if selected item is prim spec item, otherwise True.  
        """
        item = objects["item"]

        return item and item() and isinstance(item(), PrimSpecItem)

    def is_auto_authoring_or_spec_linking_mode(objects):
        """
        Check if the selected item is in spec linking mode or auto authoring mode.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        return ContextMenu.is_spec_linking_mode(objects) or ContextMenu.is_auto_authoring_mode(objects)

    def is_not_auto_authoring_and_spec_linking_mode(objects):
        """
        Check if the selected item is not in spec linking mode and auto authoring mode.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        return not ContextMenu.is_auto_authoring_or_spec_linking_mode(objects)

    def can_be_set_as_authoring_target(objects):  # pragma: no cover
        """
        Check if the selected item can be set as authoring target.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if not layer_item or not layer_item.model:
            return False

        value = not layer_item.model.root_layer_item.is_in_live_session
        return ContextMenu.is_not_auto_authoring_and_spec_linking_mode(objects) and value

    def is_spec_linking_mode(objects):
        """
        Check if the selected item is in spec linking mode.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if not layer_item or not layer_item.model:
            return False

        return layer_item.model.spec_linking_mode

    def is_auto_authoring_mode(objects):
        """
        Check if the selected item is in auto authoring mode.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if not layer_item or not layer_item.model:
            return False

        return layer_item.model.auto_authoring_mode

    def is_edit_layer(objects):
        """
        Check if the selected item is edit layer item.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        item = ContextMenu._get_layer_item(objects)
        return item and item.edit_layer_in_auto_authoring_mode

    def is_not_edit_layer(objects):
        """
        Check if the selected item is not edit layer item.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        return not ContextMenu.is_edit_layer(objects)

    def is_authoring_layer(objects):
        """
        Check if the selected item is authoring layer.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        item = ContextMenu._get_layer_item(objects)
        return item and item.is_edit_target

    def is_not_authoring_layer(objects):
        """
        Check if the selected item is not authoring layer.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        return not ContextMenu.is_authoring_layer(objects)

    def is_reserved_layer(objects):
        """
        Check if the selected item is reserved layer.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        item = ContextMenu._get_layer_item(objects)
        return item and item.reserved

    def is_not_reserved_layer(objects):
        """
        Check if the selected item is not reserved layer.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        return not ContextMenu.is_reserved_layer(objects)

    def is_omni_layer(objects):  # pragma: no cover
        """
        Check if the selected item is omniverse layer.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        item = ContextMenu._get_layer_item(objects)
        return item.is_omni_layer

    def is_not_omni_layer(objects):  # pragma: no cover
        """
        Check if the selected item is not omniverse layer.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        return not ContextMenu.is_omni_layer(objects)

    def is_missing_layer(objects):
        """
        Check if the selected item is missing layer.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        item = ContextMenu._get_layer_item(objects)
        return item and item.missing

    def is_not_missing_layer(objects):
        """
        Check if the selected item is not missing layer.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        return not ContextMenu.is_missing_layer(objects)

    def is_from_session_layer_tree(objects):
        """
        Check if the selected item is from session layer tree.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        item = ContextMenu._get_layer_item(objects)
        return item and item.from_session_layer

    def is_not_from_session_layer_tree(objects):
        """
        Check if the selected item is not from session layer tree.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        return not ContextMenu.is_from_session_layer_tree(objects)

    def can_delete_prim(objects):
        """
        Check if the selected item can be deleted.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        prim_item = ContextMenu._get_prim_spec_item(objects)
        if not prim_item:
            return False

        layer_item = ContextMenu._get_layer_item(objects)
        if not layer_item or not layer_item.model:
            return False

        stage = objects["stage"]
        prim = stage.GetPrimAtPath(prim_item.path)

        read_only = omni.usd.editor.is_no_delete(prim)
        if read_only:
            return False

        # You can remove prims always for live session layer.
        is_live_sync_layer = ContextMenu.is_live_syncing_layer(objects)
        if is_live_sync_layer:
            return True

        # Otherwise, you cannot remove anything if root layer is in live.
        root_in_live = layer_item.model.root_layer_item.is_in_live_session
        if root_in_live:
            return False

        # Or if the current layer is in live, you cannot remove base prims.
        if layer_item.is_in_live_session:
            return False

        return True

    def is_material(objects):
        """
        Check if the selected item's type is material.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        prim_item = ContextMenu._get_prim_spec_item(objects)
        if not prim_item:
            return False

        return prim_item.type_name == "Material"

    def is_anonymous_layer(objects):
        """
        Check if the selected layer item  is anonymous layer.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        item = ContextMenu._get_layer_item(objects)
        return item and Sdf.Layer.IsAnonymousLayerIdentifier(item.identifier)

    def is_not_anonymous_layer(objects):
        """
        Check if the selected layer item is not anonymous layer.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        return not ContextMenu.is_anonymous_layer(objects)

    def is_layer_or_parent_muted(objects):
        """
        Check if the selected layer item is muted or parent muted.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        layer_item = ContextMenu._get_layer_item(objects)
        return layer_item.muted_or_parent_muted

    def is_layer_and_parent_unmuted(objects):
        """
        Check if the selected layer item is muted and parent muted.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        return not ContextMenu.is_layer_or_parent_muted(objects)

    def is_layer_locked_by_other(objects):  # pragma: no cover
        """Deprecated."""

        return False

    def is_layer_not_locked_by_other(objects):  # pragma: no cover
        """
        Check if the selected layer item is not locked by other.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        return not ContextMenu.is_layer_locked_by_other(objects)

    def is_layer_locked(objects):
        """
        Check if the selected layer item is locked.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        layer_item = ContextMenu._get_layer_item(objects)
        return layer_item.locked

    def is_layer_not_locked(objects):
        """
        Check if the selected layer item is not locked.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        return not ContextMenu.is_layer_locked(objects)

    def is_layer_read_only(objects):
        """
        Check if the selected layer item is not locked.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        layer_item = ContextMenu._get_layer_item(objects)
        return not layer_item.editable

    def is_layer_writable(objects):
        """
        Check if the selected layer item is writable.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        return not ContextMenu.is_layer_read_only(objects)

    def is_layer_dirty(objects):
        """
        Check if the selected layer item is dirty.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        layer_item = ContextMenu._get_layer_item(objects)
        return layer_item.dirty

    def has_no_layers_locked(objects):
        """
        Check if the selected item has not layers locked.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if not layer_item or not layer_item.model:
            return
        return not layer_item.model.has_any_layers_locked()

    def has_sublayers(objects):
        """
        Check if the selected stage has sublayers.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        stage = objects["stage"]
        return len(stage.GetRootLayer().subLayerPaths) > 0

    def can_merge_layer_down(objects):
        """
        Check if the selected layer item can be merged down.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        layer_item = ContextMenu._get_layer_item(objects)
        parent_layer = layer_item.parent
        if not parent_layer:
            return False

        position = LayerUtils.get_sublayer_position_in_parent(parent_layer.identifier, layer_item.identifier)
        if position == -1:
            return False

        if position < len(parent_layer.sublayers) - 1:
            return True

        return False

    def has_payload_or_reference(objects: dict):
        """
        checks if prim has references
        
        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        prim_item = ContextMenu._get_prim_spec_item(objects)
        if not prim_item or not prim_item.prim_spec:
            return False

        return prim_item.prim_spec.HasInfo(Sdf.PrimSpec.ReferencesKey) or prim_item.prim_spec.HasInfo(Sdf.PrimSpec.PayloadKey)

    def refresh_reference_payload_name(objects: dict):
        """
        checks if prims have references/payload and returns name

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        prim_item = ContextMenu._get_prim_spec_item(objects)
        if not prim_item or not prim_item.prim_spec:
            return None

        prim = objects["stage"].GetPrimAtPath(prim_item.prim_spec.path)
        if not prim.HasAuthoredReferences() and not prim.HasAuthoredPayloads():
            return None

        if prim.HasAuthoredReferences() and prim.HasAuthoredPayloads():
            return "Refresh Payload & Reference"
        if prim.HasAuthoredReferences():
            return "Refresh Reference"
        if prim.HasAuthoredPayloads():
            return "Refresh Payload"
        return None

    # ---------------------------------------------- menu onClick functions ----------------------------------------------

    @staticmethod
    def _get_content_window():
        try:
            import omni.kit.window.content_browser as content

            return content.get_content_window()
        except Exception as e:
            pass

        return None

    def _stage_window_object(objects: dict) -> dict:
        prim = objects["stage"].GetPrimAtPath(ContextMenu._get_prim_spec_item(objects).prim_spec.path)
        return {"prim_list": [prim], "stage": objects["stage"]}

    def find_in_browser(objects):
        """
        Navigate to selected layer's file if found it in content browser.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if not layer_item:
            return

        content_window = ContextMenu._get_content_window()
        if not content_window:
            return

        content_window.navigate_to(layer_item.identifier)

    def copy_url(objects):
        """
        Copy the selected item's url to clipboard.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        item = objects["item"]
        if not item():
            return

        if isinstance(item(), PrimSpecItem):
            url = item().path.pathString
        elif isinstance(item(), LayerItem):
            url = item().identifier

        omni.kit.clipboard.copy(url)

    def set_edit_layer(objects):
        """
        Set the selected layer as default edit layer.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if not layer_item or not layer_item.model:
            return

        layer_item.model.default_edit_layer = layer_item.identifier

    def set_authoring_layer(objects):
        """
        Set the selected layer as authoring layer.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if not layer_item or not layer_item.model:
            return

        layer_item.model.set_edit_target(layer_item, True)

    def can_edit_root_layer(objects):
        """
        Check if selected tree view can edit root layer.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        tree_view = objects["tree_view"]
        if not tree_view():
            return False

        layer_item = tree_view().model.root_layer_item
        return LayerModelUtils.can_edit_sublayer(layer_item)

    def can_edit_sublayer(objects):
        """
        Check if selected layer item can edit sublayer.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if not layer_item or not layer_item.model:
            return

        return LayerModelUtils.can_edit_sublayer(layer_item)

    def can_edit_sublayer_parent(objects):
        """
        Check if selected layer item's parent can edit sublayer.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if not layer_item or not layer_item.model or not layer_item.parent:
            return

        return LayerModelUtils.can_edit_sublayer(layer_item.parent)

    def can_set_as_edit_target(objects):
        """
        Check if selected layer can set as edit target.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if not layer_item or not layer_item.model:
            return

        return LayerModelUtils.can_set_as_edit_target(layer_item)

    def can_not_edit_sublayer(objects):
        """
        Check if selected layer item can edit sublayer.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        return not ContextMenu.can_edit_sublayer(objects)

    def can_flatten_sublayers(objects):
        """
        Check if selected layer item can flatten sublayer.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if not layer_item or not layer_item.model:
            return False

        return not layer_item.model.is_in_live_session

    def copy_layer_url(objects):  # pragma: no cover
        """Deprecated."""

        if "layer" not in objects:
            return

        omni.kit.clipboard.copy(objects["layer_id"])

    def create_sublayer(objects, anonymous=False):
        """
        Create sublayer for selected layer item.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if not layer_item:
            tree_view = objects["tree_view"]
            if not tree_view():
                return False

            layer_item = tree_view().model.root_layer_item

        LayerModelUtils.create_sublayer(layer_item, 0, anonymous)

    def create_anonymous_sublayer(objects):
        """
        Create anonymous sublayer for selected layer item.

        Args:
            objects (dict): A dictionary containing selected item information.
        """
        ContextMenu.create_sublayer(objects, True)

    def is_live_syncing_layer(objects):
        """
        Check if selected layer item is live syncing layer.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if layer_item:
            return layer_item.is_live_session_layer

        return False

    def is_not_live_layer(objects):
        """
        Check if selected layer item is not live syncing layer.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        return not ContextMenu.is_live_syncing_layer(objects)

    def is_live_session_layer(objects):  # pragma: no cover
        """
        Check if selected layer item is live session layer.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if layer_item:
            return layer_item.is_live_session_layer

        return False

    def is_not_live_session_layer(objects):  # pragma: no cover
        """
        Check if selected layer item is not live session layer.

        Args:
            objects (dict): A dictionary containing selected item information.

        Returns:
            bool
        """
        return not ContextMenu.is_live_session_layer(objects)

    def insert_sublayer(objects):
        """
        Insert sublayer into selected layer item.

        Args:
            objects (dict): A dictionary containing selected item information.
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if not layer_item:
            tree_view = objects["tree_view"]
            if not tree_view():
                return False

            layer_item = tree_view().model.root_layer_item

        LayerModelUtils.insert_sublayer(layer_item, 0)

    def save_layer(objects):
        """
        Save selected layer.

        Args:
            objects (dict): A dictionary containing selected item information.
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if not layer_item:
            return

        LayerModelUtils.save_layer(layer_item)

    def save_layer_as(objects):
        """
        Save selected layer, it will open a file picker dialog to select save path.

        Args:
            objects (dict): A dictionary containing selected item information.
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if not layer_item:
            return

        LayerModelUtils.save_layer_as(layer_item)

    def save_layer_as_and_replace(objects):
        """
        Save selected layer, it will open a file picker dialog to select save path,
        and overwrite the exist layer file.

        Args:
            objects (dict): A dictionary containing selected item information.
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if not layer_item:
            return

        LayerModelUtils.save_layer_as(layer_item, True)

    def merge_down_one(objects):
        """
        Merge selected layer items down to one.

        Args:
            objects (dict): A dictionary containing selected item information.
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if not layer_item:
            return

        LayerModelUtils.merge_layer_down(layer_item)

    def flatten_sublayers(objects):
        """
        Faltten selected layer item.

        Args:
            objects (dict): A dictionary containing selected item information.
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if not layer_item:
            return

        LayerModelUtils.flatten_all_layers(layer_item.model)

    def remove_layer(objects):
        """
        Remove selected layer item.

        Args:
            objects (dict): A dictionary containing selected item information.
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if not layer_item:
            return

        layer_item_list = objects["layer_item_list"]
        if len(layer_item_list) <= 1:
            LayerModelUtils.remove_layer(layer_item)
        else:
            all_items = []
            locked_layers = []
            for weak_item in layer_item_list:
                if not weak_item or not weak_item():
                    continue

                if layer_item == weak_item():
                    continue

                if weak_item().locked:
                    locked_layers.append(weak_item().identifier)
                    continue

                all_items.append(weak_item())

            all_items.append(layer_item)
            LayerModelUtils.remove_layers(all_items)

            if locked_layers:
                identifiers = ""
                for identifier in locked_layers:
                    identifiers += f"\n{identifier}"

                try:
                    import omni.kit.notification_manager as nm
                    nm.post_notification(
                        "Locked layers cannot be removed:\n" + identifiers,
                        status=nm.NotificationStatus.WARNING
                    )
                except ModuleNotFoundError:
                    pass

    def reload_layer(objects):
        """
        Reload selected layer item.

        Args:
            objects (dict): A dictionary containing selected item information.
        """
        layer_item = ContextMenu._get_layer_item(objects)
        LayerModelUtils.reload_layer(layer_item)

    def prim_delete(objects):
        """
        Delete selected prim spec item.

        Args:
            objects (dict): A dictionary containing selected item information.
        """
        if not ContextMenu.is_prim_spec_item(objects):
            return

        prim_item_list = objects["prim_item_list"]
        valid_prim_items = []
        for prim_item in prim_item_list:
            if prim_item and prim_item():
                valid_prim_items.append(prim_item())
        LayerModelUtils.remove_prim_spec_items(valid_prim_items)

    def move_prims(self, objects):
        """
        Move selected prim spec item.

        Args:
            objects (dict): A dictionary containing selected item information.
        """
        layer_item = ContextMenu._get_layer_item(objects)
        if not layer_item or not layer_item.layer:
            return

        selection = self._usd_context.get_selection()
        paths = selection.get_selected_prim_paths()
        stage = self._usd_context.get_stage()
        if stage and paths:
            omni.kit.commands.execute(
                "StitchPrimSpecsToLayer",
                prim_paths=paths,
                target_layer_identifier=layer_item.identifier
            )

    @staticmethod
    def add_menu(menu_list):
        """
        Add the menu to the end of the context menu. Return the object that
        should be alive all the time. Once the returned object is destroyed,
        the added menu is destroyed as well.
        """

        class MenuSubscription:
            def __init__(self, menu_id):
                self.__id = menu_id

            def __del__(self):
                CustomMenuList().remove_menu(self.__id)

        menu_id = CustomMenuList().add_menu(menu_list)
        return MenuSubscription(menu_id)
