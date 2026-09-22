# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["warm_up_ui_material"]

import carb
import carb.tokens
import omni.usd
import pxr.Sdf
import pxr.Tf
import pxr.UsdGeom
from carb.events import IEvent, ISubscription
from omni.usd import StageEventType, UsdContext
from pxr.Gf import Vec3f as GfVec3f
from pxr.Usd import Stage as UsdStage
from pxr.UsdShade import ConnectableAPI, Material, MaterialBindingAPI, Shader

stage_event_sub: ISubscription | None
_cache_prim_path: str = "/__xr__material_cache_prim"


# noinspection PyTypeChecker
# noinspection PyNoneFunctionAssignment,PyUnresolvedReferences
def _force_load_ui_shader(_: IEvent | None):
    usd_context: UsdContext = omni.usd.get_context()
    stage: UsdStage = usd_context.get_stage()
    if not stage:
        carb.log_error("No stage was available")

    # Define a prim
    with pxr.Usd.EditContext(stage, stage.GetSessionLayer()):
        cache_prim: pxr.UsdGeom.Cube = pxr.UsdGeom.Cube.Define(stage, _cache_prim_path)
        cache_prim.GetPrim().SetMetadata("hide_in_stage_window", True)
        usd_context.set_pickable(_cache_prim_path, False)

        # Make the prim very tiny
        xformable: pxr.UsdGeom.Xformable = pxr.UsdGeom.Xformable.Get(stage, _cache_prim_path)
        api = pxr.UsdGeom.XformCommonAPI(xformable)
        api.SetScale(GfVec3f(0.0001, 0.0001, 0.0001), pxr.Usd.TimeCode.Default())

        # Add a shader
        mdl_name = "OmniUIScene"
        mdl_path = carb.tokens.get_tokens_interface().resolve(
            "${omni.kit.xr.scene_view.core}/assets/" + mdl_name + ".mdl"
        )
        shader: Shader = Shader.Define(stage, f"{_cache_prim_path}/shader")
        shader.SetSourceAsset(mdl_path, "mdl")

        # Tell the shader to use the mdl_name sub-identifier from the MDL file
        sub_attr = shader.GetPrim().CreateAttribute(
            "info:mdl:sourceAsset:subIdentifier",
            pxr.Sdf.ValueTypeNames.Token,
            False,  # is custom
            pxr.Sdf.VariabilityUniform,
        )
        sub_attr.Set(mdl_name)

        # Add a material
        material: Material = Material.Define(stage, f"{_cache_prim_path}/material")

        # Assign the shader to the material
        mat_output = material.CreateSurfaceOutput("")  # renderContext
        mat_output.ConnectToSource(ConnectableAPI(shader), "out")

        # Assign the material to the prim
        binding_api: MaterialBindingAPI = MaterialBindingAPI.Apply(cache_prim.GetPrim())
        binding_api.Bind(
            material,
            "",  # binding strength
            "",  # material purpose
        )

    global stage_event_sub
    stage_event_sub = usd_context.get_stage_event_stream().create_subscription_to_pop_by_type(
        StageEventType.ASSETS_LOADED, _destroy_the_evidence
    )


def _destroy_the_evidence(_: IEvent | None):
    global stage_event_sub
    stage_event_sub = None

    usd_context: UsdContext = omni.usd.get_context()
    stage: UsdStage = usd_context.get_stage()
    with pxr.Usd.EditContext(stage, stage.GetSessionLayer()):
        stage.RemovePrim(_cache_prim_path)


def warm_up_ui_material():
    global stage_event_sub
    usd_context: UsdContext = omni.usd.get_context()
    if usd_context.get_stage() is not None:
        _force_load_ui_shader(None)
    else:
        stage_event_sub = usd_context.get_stage_event_stream().create_subscription_to_pop_by_type(
            StageEventType.OPENED, _force_load_ui_shader
        )
