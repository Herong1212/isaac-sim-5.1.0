# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import os
import carb
import omni.kit.app
import omni.usd
from pxr import Sdf, UsdRender, Gf, Usd


ViewportObjectsSettingDict = {
    "guide/selection": "/app/viewport/outline/enabled",
    "scene/lights": "/app/viewport/show/lights",
    "scene/audio": "/app/viewport/show/audio",
    "scene/cameras": "/app/viewport/show/camera",
    "guide/grid": "/app/viewport/grid/enabled"
}


def get_num_pattern_file_path(frames_dir, file_name, num_pattern, frame_num, file_type, renumber_frames=False, renumber_offset=0):
    if renumber_frames:
        renumbered_frames = frame_num + renumber_offset
    else:
        renumbered_frames = frame_num
    abs_frame_num = abs(renumbered_frames)
    padding_length = len(num_pattern.strip(".")[len(str(abs_frame_num)) :])
    if renumbered_frames >= 0:
        padded_string = "0" * padding_length + str(renumbered_frames)
    else:
        padded_string = "-" + "0" * padding_length + str(abs_frame_num)
    filename = ".".join((file_name, padded_string, file_type.strip(".")))
    frame_path = os.path.join(frames_dir, filename)
    return frame_path


def is_ext_enabled(ext_name):
    ext_manager = omni.kit.app.get_app().get_extension_manager()
    return ext_manager.is_extension_enabled(ext_name)


def check_render_product_ext_availability():
    return is_ext_enabled("omni.graph.image.nodes")


def is_valid_render_product_prim_path(prim_path):
    try:
        import omni.usd
        from pxr import UsdRender

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        prim = stage.GetPrimAtPath(prim_path)
        if prim:
            return prim.IsA(UsdRender.Product)
        else:
            return False
    except Exception as e:
        return False


class RenderProductCaptureHelper:
    @staticmethod
    def prepare_render_product_for_capture(render_product_prim_path, new_camera, new_resolution):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        working_layer = stage.GetSessionLayer()
        prim = stage.GetPrimAtPath(render_product_prim_path)
        path_new = omni.usd.get_stage_next_free_path(stage, render_product_prim_path, False)
        if prim.IsA(UsdRender.Product):
            try:
                with Usd.EditContext(stage, working_layer):
                    omni.kit.commands.execute("CopyPrim", path_from=render_product_prim_path, path_to=path_new, duplicate_layers=False, combine_layers=True,exclusive_select=True)
                    prim_new = stage.GetPrimAtPath(path_new)
                    if prim_new.IsA(UsdRender.Product):
                        omni.usd.editor.set_no_delete(prim_new, False)
                        prim_new.GetAttribute("resolution").Set(new_resolution)
                        prim_new.GetRelationship("camera").SetTargets([new_camera])
                    else:
                        path_new = ""
            except Exception as e:
                carb.log_warn(f"Failed to copy the render product {render_product_prim_path} due to {e}.")
                path_new = ""
        else:
            path_new = ""
        return path_new

    @staticmethod
    def remove_render_product_for_capture(render_product_prim_path):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        working_layer = stage.GetSessionLayer()
        prim = working_layer.GetPrimAtPath(render_product_prim_path)
        if prim:
            if prim.nameParent:
                name_parent = prim.nameParent
            else:
                name_parent = working_layer.pseudoRoot

            if not name_parent:
                return

            name = prim.name
            if name in name_parent.nameChildren:
                del name_parent.nameChildren[name]
