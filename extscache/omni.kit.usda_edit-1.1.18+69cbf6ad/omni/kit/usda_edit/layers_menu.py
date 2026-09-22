# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from . import editor
from .layer_watch import LayerWatch
from .usda_edit_utils import is_extension_loaded, post_notification


def layers_available() -> bool:
    """Returns True if the extension "omni.kit.widget.layers" is loaded"""
    return is_extension_loaded("omni.kit.widget.layers")


class LayersMenu:
    """
    When this object is alive, Layers 2.0 has the additional context menu
    with the items that allow to edit the layer in the external editor.
    """

    def __init__(self):
        import omni.kit.widget.layers as layers

        self.__menu_subscription = layers.ContextMenu.add_menu(
            [
                {"name": ""},
                {
                    "name": "Edit...",
                    "glyph": "menu_rename.svg",
                    "show_fn": [
                        layers.ContextMenu.is_layer_item,
                        layers.ContextMenu.is_not_missing_layer,
                        layers.ContextMenu.is_layer_writable,
                        layers.ContextMenu.is_layer_not_locked_by_other,
                        layers.ContextMenu.is_layer_and_parent_unmuted,
                        LayersMenu.is_not_editing,
                    ],
                    "onclick_fn": LayersMenu.start_editing,
                },
                {
                    "name": "Finish editing",
                    "glyph": "menu_delete.svg",
                    "show_fn": [layers.ContextMenu.is_layer_item, LayersMenu.is_editing],
                    "onclick_fn": LayersMenu.stop_editing,
                },
            ]
        )

    def destroy(self):
        """Stop all watchers and remove the menu from Layers 2.0"""
        self.__menu_subscription = None
        LayerWatch().stop_all()

    @staticmethod
    def start_editing(objects):
        """Start watching for the layer and run the editor"""
        item = objects["item"]

        identifier = item().identifier
        usda_filename = LayerWatch().start_watch(identifier)
        if not editor.run_editor(usda_filename):
            post_notification("No text editor can be found!")

    @staticmethod
    def stop_editing(objects):
        """Stop watching for the layer and remove the temporary files"""
        item = objects["item"]

        identifier = item().identifier
        LayerWatch().stop_watch(identifier)

    @staticmethod
    def is_editing(objects):
        """Returns true if the layer is already watched"""
        item = objects["item"]

        identifier = item().identifier
        return LayerWatch().has_watch(identifier)

    @staticmethod
    def is_not_editing(objects):
        """Returns true if the layer is not watched"""
        return not LayersMenu.is_editing(objects)
