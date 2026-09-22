import traceback

import carb
import omni.graph.core as og
import usdrt.Usd as UsdRtUsd
from pxr import Usd


# ==============================================================================================================
def get_usd_rt_stage(stage: Usd.Stage) -> UsdRtUsd.Stage:
    """
    Gets the usdrt.Usd.Stage corresponding to the pxr.Usd.Stage

    Args:
        stage: the standard Usd.Stage
    Return:
        Returns the usdrt.Usd.Stage object corresponding to the input stage.
        If the fabric stage cannot be retrieved, returns None.
    """
    try:
        from pxr import UsdUtils

        stage_id = UsdUtils.StageCache.Get().GetId(stage).ToLongInt()
        fabric_active_for_stage = UsdRtUsd.Stage.StageWithHistoryExists(stage_id)
        if fabric_active_for_stage:
            return UsdRtUsd.Stage.Attach(stage_id)
    except ImportError:
        carb.log_warn(f"usdrt.Usd.Stage unavailable: {traceback.format_exc()}")
    return None


# ==============================================================================================================
def get_prims_of_types(stage: Usd.Stage, type_names: list[str]) -> list[Usd.Prim]:
    """
    Gets the prims with the given type names found in the scene.

    Internally, the function uses usdrt.Stage to fetch the prim paths with the required types.
    The USD stage is used to resolve the prim paths into Usd.Prim.

    Args:
        stage: the USD stage where the prims are found
        type_names: the list of types we're interested in
    Return:
        Returns a list of prims with the given types. If no prims are found, returns an empty list.
    """
    # With FSD enabled, this ensures that all pending USD changes have been processed prior to
    # scanning the stage
    og._internal.flush_usd()  # noqa PLW0212

    usdrt_stage = get_usd_rt_stage(stage)
    all_paths: list[str] = []
    for type_name in type_names:
        all_paths = all_paths + usdrt_stage.GetPrimsWithTypeName(type_name)

    return [stage.GetPrimAtPath(prim_path.GetString()) for prim_path in all_paths]
