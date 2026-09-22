# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["UsdPrimDropDelegate", "UsdShadeDropDelegate"]

from typing import Callable

from pxr import Usd, Sdf, Gf, UsdShade

import carb
import omni.ui
import omni.kit.commands

from .scene_drop_delegate import SceneDropDelegate


class UsdPrimDropDelegate(SceneDropDelegate):
    def __init__(self, preview_setting: str = None, **kwargs):
        super().__init__(**kwargs)
        self.reset_state()

    @property
    def dragging_prim(self):
        return self.__usd_prim_dragged

    @dragging_prim.setter
    def dragging_prim(self, prim: Usd.Prim):
        self.__usd_prim_dragged = prim

    @property
    def world_space_pos(self):
        return self.__world_space_pos

    @world_space_pos.setter
    def world_space_pos(self, world_space_pos: Gf.Vec3d):
        self.__world_space_pos = world_space_pos

    def reset_state(self):
        self.__usd_prim_dragged = None
        self.__world_space_pos = None

    def accepted(self, drop_data: dict):
        self.reset_state()
        # XXX: Poor deliniation of file vs Sdf.Path
        prim_path = drop_data.get("mime_data")
        if prim_path.find(".") > 0:
            return False

        # If there is no Usd.Stage, then it can't be a prim for this stage
        usd_context, stage = self.get_context_and_stage(drop_data)  # noqa PLW0612
        if stage is None:
            return False

        # Check if it's a path to a valid Usd.Prim and save it if so
        prim = stage.GetPrimAtPath(prim_path)
        if prim is None or not prim.IsValid():
            return False

        self.dragging_prim = prim
        return True

    def add_drop_marker(self, drop_data: dict, world_space_pos: Gf.Vec3d):
        prim = self.dragging_prim
        if prim:
            self.world_space_pos = world_space_pos
            super().add_drop_marker(drop_data, world_space_pos)

    # Overide drop behavior, material drop doesn't draw anything
    def dropped(self, drop_data: dict):
        usd_context, stage = self.get_context_and_stage(drop_data)  # noqa PLW0612
        if stage is None:
            return

        dropped_prim = self.dragging_prim
        if (dropped_prim is None) or (not dropped_prim.IsValid()):
            return

        dropped_onto = drop_data.get("prim_path")
        if dropped_onto is None:
            return
        dropped_onto = stage.GetPrimAtPath(dropped_onto)
        if (dropped_onto is None) or (not dropped_onto.IsValid()):
            return

        dropped_onto_model = drop_data.get("model_path")
        dropped_onto_model = stage.GetPrimAtPath(dropped_onto_model) if dropped_onto_model else None

        self.handle_prim_drop(stage, dropped_prim, dropped_onto, dropped_onto_model)

    def collect_child_paths(self, prim: Usd.Prim, filter_fn: Callable):
        had_child, children = False, []
        for child in prim.GetFilteredChildren(Usd.PrimAllPrimsPredicate):
            had_child = True
            if filter_fn(child):
                children.append(child.GetPath())
        return children if had_child else [prim.GetPath()]

    def handle_prim_drop(self, stage: Usd.Stage, dropped_prim: Usd.Prim, dropped_onto: Usd.Prim,
                         dropped_onto_model: Usd.Prim):
        raise RuntimeError("UsdPrimDropDelegate.dropped not overidden")


class UsdShadeDropDelegate(UsdPrimDropDelegate):
    @property
    def binding_strength(self):
        strength = carb.settings.get_settings().get("/persistent/app/stage/materialStrength")
        return strength or "weakerThanDescendants"

    @property
    def honor_picking_mode(self):
        return True

    def accepted(self, drop_data: dict):
        if super().accepted(drop_data):
            return self.dragging_prim.IsA(UsdShade.Material)
        return False

    # Overide draw behavior, material drop doesn't draw anything
    def add_drop_marker(self, drop_data: dict, world_space_pos: Gf.Vec3d):
        return

    def bind_material(self, prim_paths, material_path: Sdf.Path):
        omni.kit.commands.execute("BindMaterialCommand", prim_path=prim_paths,
                                  material_path=material_path, strength=self.binding_strength)

    def show_bind_menu(self, prim_path: Sdf.Path, model_path: Sdf.Path, material_path: Sdf.Path):
        def __apply_material(target):
            if target:
                self.bind_material(prim_paths=target, material_path=material_path)

        import omni.kit.material.library
        omni.kit.material.library.drop_material(prim_path.pathString,
                                                model_path.pathString,
                                                apply_material_fn=__apply_material)

    def handle_prim_drop(self, stage: Usd.Stage, dropped_prim: Usd.Prim, dropped_onto: Usd.Prim, dropped_onto_model: Usd.Prim):
        if dropped_onto_model:
            prim_path = dropped_onto.GetPath()
            model_path = dropped_onto_model.GetPath()
            material_path = dropped_prim.GetPath()
            self.show_bind_menu(prim_path, model_path, material_path)
            return

        prim_paths = [dropped_onto.GetPath()]
        if prim_paths:
            self.bind_material(prim_paths, dropped_prim.GetPath())
