# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides functionality for material selection and manipulation in a context menu, including checking material selection, copying, pasting, and navigating to materials within the USD stage."""

__all__ = []

from typing import Set

import carb
import omni.kit.widget.context_menu
from pxr import Usd, UsdShade

material_clipboard = []


# menu functions....
def is_material_selected(objects):
    """Checks if a material is selected.

    Args:
        objects (dict): A dictionary containing the material primitive under the key 'material_prim'.

    Returns:
        bool: True if the material primitive is not None, False otherwise."""
    material_prim = objects["material_prim"]
    if material_prim:
        return True
    return False


def is_multiple_material_selected(objects):  # pragma: no cover
    """Determines if more than one material is selected.

    Args:
        objects (dict): A dictionary containing the stage object with key 'stage' to access USD prim paths.

    Returns:
        bool: True if more than one unique material is selected, False otherwise."""
    selected_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
    mtl_list = []
    for path in selected_paths:
        prim = objects["stage"].GetPrimAtPath(path)
        if not prim:
            return False
        bound_material, _ = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
        if bound_material and bound_material not in mtl_list:
            mtl_list.append(bound_material)
    return len(mtl_list) > 1


def is_material_copied(objects):
    """Checks if any material has been copied to the clipboard.

    Args:
        objects (dict): A dictionary containing relevant data and objects for the operation.

    Returns:
        bool: True if the material clipboard is not empty, False otherwise."""
    return len(material_clipboard) > 0


def is_bindable_prim_selected(objects):
    """Checks if any selected prim is supported for material binding.

    Args:
        objects (dict): A dictionary with 'stage' key providing access to USD stage.

    Returns:
        bool: True if at least one selected prim is bindable, False otherwise."""
    for prim_path in omni.usd.get_context().get_selection().get_selected_prim_paths():
        prim = objects["stage"].GetPrimAtPath(prim_path)
        if prim and omni.usd.is_prim_material_supported(prim):
            return True
    return False


def is_prim_selected(self, objects: dict):
    """Checks if any prims are selected in the given objects.

    Args:
        self: The instance of the class.
        objects (dict): A dictionary containing prims and related information, expected to
            have 'prim' or 'prim_list' as keys to check for selected prims.

    Returns:
        bool: True if any prim is selected, False otherwise."""
    if not any(item in objects for item in ["prim", "prim_list"]):
        return False
    return True


def is_paste_all(objects):
    """Determines whether the paste all operation is applicable.

    Args:
        objects (dict): A dictionary containing the USD stage and prim information.

    Returns:
        bool: True if the number of selected prim paths is greater than the number of materials in the clipboard, otherwise False.
    """
    return len(omni.usd.get_context().get_selection().get_selected_prim_paths()) > len(material_clipboard)


def goto_material(objects):
    """Navigates to the selected material in the USD stage.

    Args:
        objects (dict): A dictionary containing the 'material_prim' key with the material primitive to navigate to.
    """
    material_prim = objects["material_prim"]
    if material_prim:
        omni.usd.get_context().get_selection().set_prim_path_selected(
            material_prim.GetPath().pathString, True, True, True, True
        )


def copy_material(objects: dict, copy_all: bool):
    """Copies the materials bound to the selected prims into the clipboard.

    Args:
        objects (dict): A dictionary containing 'prim_list', which is a list of
            prims whose materials are to be copied.
        copy_all (bool): A flag indicating whether to copy all materials or not.

    """
    global material_clipboard

    material_clipboard = []
    for prim in objects["prim_list"]:
        mat, rel = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
        material_path = mat.GetPath().pathString if mat else None
        material_strength = (
            UsdShade.MaterialBindingAPI.GetMaterialBindingStrength(rel)
            if rel
            else UsdShade.Tokens.weakerThanDescendants
        )
        material_clipboard.append((material_path, material_strength))


def paste_material(objects: dict):
    """Pastes copied material(s) to selected prim paths in the USD stage.

    Args:
        objects (dict): A dictionary containing the USD stage and potentially other relevant information required to perform the paste operation.
    """
    selected_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
    prims = [objects["stage"].GetPrimAtPath(p) for p in selected_paths]

    with omni.kit.undo.group():
        max_paste = len(material_clipboard)
        for index, prim in enumerate(prims):
            if index >= max_paste:
                break
            material_path, material_strength = material_clipboard[index]
            if material_path:
                omni.kit.commands.execute(
                    "BindMaterial",
                    prim_path=prim.GetPath(),
                    material_path=material_path,
                    strength=material_strength,
                )


def paste_material_all(objects: dict):
    """Pastes material to selected prims in a round-robin fashion from a clipboard.

    Args:
        objects (dict): A dictionary containing the stage and possibly other relevant information for
            operation. Expected to have a 'stage' key with a value that allows access to prims via
            GetPrimAtPath method."""
    selected_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
    prims = [objects["stage"].GetPrimAtPath(p) for p in selected_paths]

    with omni.kit.undo.group():
        max_paste = len(material_clipboard)
        for index, prim in enumerate(prims):
            material_path, material_strength = material_clipboard[index % max_paste]
            if material_path:
                omni.kit.commands.execute(
                    "BindMaterial",
                    prim_path=prim.GetPath(),
                    material_path=material_path,
                    strength=material_strength,
                )


def get_paste_name(objects):
    """Generates a name for the paste operation based on the number of materials in the clipboard.

    Args:
        objects (dict): The dictionary containing references to various objects such as materials, prims, etc.

    Returns:
        str: A string indicating the paste operation name. If only one material is in the clipboard, it returns 'Paste'; otherwise,
             it includes the number of materials in parentheses, e.g., 'Paste (3 Materials)'."""
    if len(material_clipboard) < 2:
        return "Paste"
    return f"Paste ({len(material_clipboard)} Materials)"


def show_context_menu(stage, material_path, bound_prims: Set[Usd.Prim]):
    """Displays a context menu for material-related actions on the given stage and bound prims.

    Args:
        stage (:obj:`Usd.Stage`): The USD stage where the operations will be performed.
        material_path (str): The path to the material in the USD stage.
        bound_prims (Set[:obj:`Usd.Prim`]): A set of USD Prims that are bound to the material."""
    # get context menu core functionality & check its enabled
    context_menu = omni.kit.widget.context_menu.get_instance()
    if context_menu is None:  # pragma: no cover
        carb.log_error("context_menu is disabled!")
        return

    # setup objects, this is passed to all functions
    if not stage:  # pragma: no cover
        return

    objects = {"material_prim": stage.GetPrimAtPath(material_path), "prim_list": bound_prims, "stage": stage}

    # setup menu
    menu_dict = [
        {"name": "Copy", "enabled_fn": [], "onclick_fn": lambda o: copy_material(o, False)},
        {
            "name_fn": get_paste_name,
            "show_fn": [is_bindable_prim_selected, is_material_copied],
            "onclick_fn": paste_material,
        },
        {"name": "", "show_fn": is_material_selected},
        {"name": "Select Material", "show_fn": is_material_selected, "onclick_fn": goto_material},
    ]

    # show menu
    menu_dict += omni.kit.widget.context_menu.get_menu_dict("MENU_THUMBNAIL", "")
    omni.kit.widget.context_menu.reorder_menu_dict(menu_dict)
    context_menu.show_context_menu("material_thumbnail", objects, menu_dict)
