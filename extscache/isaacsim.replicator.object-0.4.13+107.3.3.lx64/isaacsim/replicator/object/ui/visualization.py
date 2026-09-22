import warp as wp
from pxr import UsdGeom, Gf, Vt
import random
from ..utility.scene import (
    create_or_get_prim_attribute,
    get_attribute_sdf_type,
    get_stage,
    create_and_bind_material_shader,
    create_or_get,
)
from pxr import UsdShade, Gf

# --------- range visualization with point cloud ---------

VISUALIZER_POINT_SIZE = 10
NUM_VIS_POINTS = 8000


def is_geometry(prim):
    return str(prim.GetTypeName()) in ["Cone", "Cube", "Sphere", "Cylinder", "Capsule", "Torus", "Plane", "Mesh"]


def initialize_visualizer_tentative(ext):
    if ext.visualizer_points_prim is None or not ext.visualizer_points_prim.GetPrim().IsValid():
        ext.visualizer_points_prim = UsdGeom.Points.Define(get_stage(), "/World/PointCloudVisualizer")
        ext.visualizer_points_prim.GetWidthsAttr().Set([VISUALIZER_POINT_SIZE])
        visualizer_shader = UsdShade.Shader(
            create_or_get(
                f"{ext.visualizer_points_prim.GetPath().pathString}/Material/Shader",
                lambda: create_and_bind_material_shader(
                    f"{ext.visualizer_points_prim.GetPath().pathString}/Material",
                    "OmniGlass",
                    ext.visualizer_points_prim.GetPrim(),
                ),
            )
        )
        visualizer_shader.GetInput("glass_color").Set(
            Gf.Vec3f(0, 0.9, 0.8)
        )
        visualizer_shader.GetInput("glass_ior").Set(1.2)


# return a list of points, each rotated by a random angle specified by the low and high values
@wp.kernel
def rotate_axis_distributed(points: wp.array(dtype=wp.vec3), axis_index: int, low: float, high: float, seed: wp.uint32):
    i = wp.tid()
    angle = wp.randf(seed + wp.uint32(i), low, high)
    if axis_index == 0:
        axis = wp.vec3(1.0, 0.0, 0.0)
    elif axis_index == 1:
        axis = wp.vec3(0.0, 1.0, 0.0)
    else:
        axis = wp.vec3(0.0, 0.0, 1.0)
    q = wp.quat_from_axis_angle(axis, wp.radians(angle))
    points[i] = wp.quat_rotate(q, points[i])


@wp.kernel
def translate_distributed(points: wp.array(dtype=wp.vec3), low: wp.vec3, high: wp.vec3, seed: wp.uint32):
    i = wp.tid()

    rand_x = low[0] + (high[0] - low[0]) * wp.randf(seed + wp.uint32(i))
    rand_y = low[1] + (high[1] - low[1]) * wp.randf(seed + wp.uint32(i + 1))
    rand_z = low[2] + (high[2] - low[2]) * wp.randf(seed + wp.uint32(i + 2))
    p = points[i]
    points[i] = wp.vec3(p[0] + rand_x, p[1] + rand_y, p[2] + rand_z)


MAX_SEED = 99999


def launch_rotate_axis_distributed(points, num_dimensions, axis_index, low, high):
    wp.launch(
        kernel=rotate_axis_distributed,
        dim=num_dimensions,
        inputs=[points, axis_index, low, high, random.randint(0, MAX_SEED)],
        device="cuda",
    )


def launch_translate_distributed(points, num_dimensions, low, high):
    wp.launch(
        kernel=translate_distributed,
        dim=num_dimensions,
        inputs=[points, wp.vec3(low), wp.vec3(high), random.randint(0, MAX_SEED)],
        device="cuda",
    )


# generate N points, each goes through the randomized range of transform operations
def process(num_dimensions, input_range):
    points = wp.zeros(shape=num_dimensions, dtype=wp.vec3, device="cuda")
    for op in reversed(input_range):
        if op[0] == "rotateX":
            launch_rotate_axis_distributed(points, num_dimensions, 0, op[1], op[2])
        elif op[0] == "rotateY":
            launch_rotate_axis_distributed(points, num_dimensions, 1, op[1], op[2])
        elif op[0] == "rotateZ":
            launch_rotate_axis_distributed(points, num_dimensions, 2, op[1], op[2])
        elif op[0] == "translate":
            launch_translate_distributed(points, num_dimensions, op[1], op[2])
    return Vt.Vec3dArray.FromNumpy(points.numpy())


def show_range_wp(input_range, ext):
    if input_range == []:
        return

    points = process(NUM_VIS_POINTS, input_range)
    initialize_visualizer_tentative(ext)
    ext.visualizer_points_prim.GetPointsAttr().Set(points)


# returns a list of tuples, each tuple contains the op type ("translate"), the start value, and the end value, equaling the op value at initialization
def get_xform_range(prim):
    def _flatten(value):
        if isinstance(value, float):
            return value
        elif len(value) > 1:
            return list(value)

    # if it's xformOp:translate_local, returns translate
    def _get_op_name(name):  # noqa: R504 simplify function
        name = name[len("xformOp:") :]
        name = name.replace(":", "_")
        r = name.find("_")
        if r != -1:
            return name[:r]
        return name

    op_order = UsdGeom.Xform(prim).GetXformOpOrderAttr().Get()
    if op_order is None:
        return []
    res = []
    for op in op_order:
        op_name = _get_op_name(op)
        if op_name in ["translate", "rotateX", "rotateY", "rotateZ", "scale"]:
            attr = prim.GetAttribute(op)
            attr_start = create_or_get_prim_attribute(
                prim, op.replace("xformOp", "xformOpStart"), get_attribute_sdf_type(attr)
            )
            attr_end = create_or_get_prim_attribute(prim, op.replace("xformOp", "xformOpEnd"), get_attribute_sdf_type(attr))
            _attr_start = _flatten(attr_start.Get())
            _attr_end = _flatten(attr_end.Get())
            res.append((op_name, _attr_start, _attr_end))
    return res


# show randomization range for the selected prim
def update_range(ext):
    if ext.selected_prim is not None and ext.selected_prim.IsValid() and is_geometry(ext.selected_prim):
        show_range_wp(get_xform_range(ext.selected_prim), ext)


# --------- range adjustment with ui ---------
