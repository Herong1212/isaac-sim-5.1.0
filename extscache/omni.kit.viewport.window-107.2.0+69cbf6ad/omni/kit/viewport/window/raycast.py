# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from typing import Sequence, Callable

import carb


USE_RAYCAST_SETTING = "/exts/omni.kit.viewport.window/useRaycastQuery"


def perform_raycast_query(
    viewport_api: "ViewportAPI",  # noqa F821
    mouse_ndc: Sequence[float],
    mouse_pixel: Sequence[float],
    on_complete_fn: Callable,
    query_name: str = ""
):
    raycast_success = False
    if (
        viewport_api.hydra_engine == "rtx"
        and carb.settings.get_settings().get(USE_RAYCAST_SETTING)
    ):
        try:
            import omni.kit.raycast.query as rq

            def rtx_query_complete(ray, result: "RayQueryResult", *args, **kwargs):  # noqa F821
                prim_path = result.get_target_usd_path()
                if result.valid:
                    world_space_pos = result.hit_position
                else:
                    world_space_pos = (0, 0, 0)

                on_complete_fn(prim_path, world_space_pos, *args, **kwargs)

            rq.utils.raycast_from_mouse_ndc(
                mouse_ndc,
                viewport_api,
                rtx_query_complete
            )
            raycast_success = True
        except ImportError:
            pass

    if not raycast_success:
        viewport_api.request_query(
            mouse_pixel,
            on_complete_fn,
            query_name=query_name
        )
