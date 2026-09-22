# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import carb
import omni.kit.context_menu
from ..orbit_camera import ViewSide
from typing import Optional, Tuple


def has_control_rig(objects):
    from ..anim_preview_model import AnimPreviewModel
    model: AnimPreviewModel = objects['model']
    skeleton = model.get_skeleton()
    if skeleton:
        prim = skeleton.GetPrim()
        if prim and prim.HasAttribute("controlRig:forwardAxis") and prim.HasAttribute("controlRig:upAxis"):
            return True

    return False


def show_camera_context_menu(
    previewer,
    side: ViewSide,
    rotating: bool,
    following: bool,
    module_path: str,
    position: Optional[Tuple[int, int]] = None,
):
    def check_follow():
        return previewer.follow_skeleton

    def check_rotate():
        return previewer.camera_manipulator.rotating

    context_menu: omni.kit.context_menu.ContextMenuExtension = omni.kit.context_menu.get_instance()
    if context_menu is None:
        carb.log_warn("Context menu is disabled.")
        return

    camera_menu_list = [
            { "name": {
                    'View':
                    [
                        {'name': 'Perspective', 'onclick_fn': lambda _: previewer._on_switch_view(ViewSide.DIAGONAL)},
                        {'name': 'Front', 'onclick_fn': lambda _: previewer._on_switch_view(ViewSide.FRONT)},
                        {'name': 'Right', 'onclick_fn': lambda _: previewer._on_switch_view(ViewSide.RIGHT)},
                        {'name': 'Top', 'onclick_fn': lambda _: previewer._on_switch_view(ViewSide.TOP)}
                    ]
                },
            },

            {
                "name": "Follow",
                "onclick_fn": lambda obj: previewer._on_follow_skeleton_changed(not check_follow()),
                "checked_fn": lambda obj: check_follow(),
            },

            {
                "name": "Orbit",
                "onclick_fn": lambda obj: previewer._on_animate_cam_changed(not check_rotate()),
                "checked_fn": lambda obj: check_rotate(),
            },
        ]

    objects = {}
    if position is not None:
        objects["menu_xpos"] = position[0]
        objects["menu_ypos"] = position[1]

    context_menu.show_context_menu('previewer_camera_context_menu', objects, camera_menu_list)


def show_visibility_context_menu(
    widget,
    model,
    show_skeleton: bool,
    show_mesh: bool,
    show_axes: bool,
    position: Optional[Tuple[int, int]] = None,
):
    context_menu: omni.kit.context_menu.ContextMenuExtension = omni.kit.context_menu.get_instance()
    if context_menu is None:
        carb.log_warn("Context menu is disabled.")
        return

    objects = {
        'model': model,
    }
    if position is not None:
        objects["menu_xpos"] = position[0]
        objects["menu_ypos"] = position[1]

    menu_list = [
        {
            "name": "Skeleton",
            "onclick_fn": lambda obj: model.set_show_skeleton(not model.get_show_skeleton()),
            "checked_fn": lambda obj: model.get_show_skeleton(),
        },

        {
            "name": "Mesh",
            "onclick_fn": lambda obj: model.set_show_mesh(not model.get_show_mesh()),
            "checked_fn": lambda obj: model.get_show_mesh(),
        },

        {
            "name": "Axes",
            "show_fn": has_control_rig,
            "onclick_fn": lambda obj: widget.set_show_axes(not widget.get_show_axes()),
            "checked_fn": lambda obj: widget.get_show_axes(),
        },
    ]

    menu_name = 'anim_preview_visibility_context_menu'

    context_menu.show_context_menu(menu_name, objects, menu_list)