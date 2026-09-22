from ..utility.xform import get_total_xform
from ..utility.scene import get_first_selected, get_stage
from pxr import Gf, UsdGeom


def to_vec3d(v):
    return Gf.Vec3d(v[0], v[1], v[2])


def get_range_from_cube_mesh():
    selected = get_first_selected()
    translate = selected.GetAttribute("xformOp:translate").Get()
    scale = selected.GetAttribute("xformOp:scale").Get()
    low = translate - scale * 0.5 * 100
    high = translate + scale * 0.5 * 100
    return selected, translate, scale, Gf.Range3d(low, high)


def toggle_visibility(prim):
    visibility = prim.GetAttribute("visibility")
    if visibility.Get() == "inherited":
        visibility.Set("invisible")
    elif visibility.Get() == "invisible":
        visibility.Set("inherited")


def toggle_visibility_in_range():
    selected, translate, scale, range3d = get_range_from_cube_mesh()
    cnt = 0
    for prim in get_stage().Traverse():
        if UsdGeom.Xformable(prim) and prim != selected:
            position = to_vec3d(Gf.Vec4d(0, 0, 0, 1) * get_total_xform(prim))
            if range3d.Contains(position):
                toggle_visibility(prim)
                cnt += 1
