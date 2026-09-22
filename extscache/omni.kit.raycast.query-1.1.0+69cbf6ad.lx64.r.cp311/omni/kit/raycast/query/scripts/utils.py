__all__ = ["raycast_from_mouse_ndc"]

import omni.kit.raycast.query as rq
from typing import Sequence, Callable


def raycast_from_mouse_ndc(
    mouse_ndc: Sequence[float],
    viewport_api: "ViewportAPI",
    on_complete_fn: Callable
):
    ndc_near = (mouse_ndc[0], mouse_ndc[1], -1)
    ndc_far = (mouse_ndc[0], mouse_ndc[1], 1)
    view_proj_inv = (viewport_api.view * viewport_api.projection).GetInverse()

    origin = view_proj_inv.Transform(ndc_near)
    dir = (view_proj_inv.Transform(ndc_far) - origin).GetNormalized()

    ray = rq.Ray(origin, dir)
    rqi = rq.acquire_raycast_query_interface()
    rqi.submit_raycast_query(ray, on_complete_fn)
