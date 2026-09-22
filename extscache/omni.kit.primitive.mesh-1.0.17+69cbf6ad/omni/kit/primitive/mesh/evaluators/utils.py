import math
import carb.settings

from pxr import Gf
from typing import List, Tuple
from numbers import Number


def _save_settings(model, setting):
    value = model.get_value_as_int()
    carb.settings.get_settings().set(setting, value)


def build_int_slider(name, setting, default_value, min_value, max_value, tooltip=None):
    from omni import ui
    layout = ui.HStack(height=0)
    with layout:
        ui.Spacer(width=20, height=0)
        ui.Label(name, height=0, name="text")
        model = ui.IntSlider(name="text", min=min_value, max=max_value, height=0, aligment=ui.Alignment.LEFT).model
        value = get_int_setting(setting, default_value)
        model.set_value(value)
        ui.Spacer(width=20, height=0)
        model.add_value_changed_fn(lambda m: _save_settings(m, setting))

        if tooltip:
            layout.set_tooltip(tooltip)

        return model


def inverse_u(uv) -> Gf.Vec2f:
    return Gf.Vec2f(1 - uv[0], uv[1])


def inverse_v(uv) -> Gf.Vec2f:
    return Gf.Vec2f(uv[0], 1 - uv[1])


def inverse_uv(uv) -> Gf.Vec2f:
    return Gf.Vec2f(1 - uv[0], 1 - uv[1])


def transform_point(point: Gf.Vec3f, origin: Gf.Vec3f, half_scale: float) -> Gf.Vec3f:
    return half_scale * point + origin


def generate_circle_points(
    up_axis, num_points, delta, center_point=Gf.Vec3f(0.0)
) -> Tuple[List[Gf.Vec3f], List[Gf.Vec2f]]:
    points: List[Gf.Vec3f] = []
    point_sts: List[Gf.Vec2f] = []

    for i in range(num_points):
        theta = i * delta * math.pi * 2
        if up_axis == "Y":
            point = Gf.Vec3f(math.cos(theta), 0.0, math.sin(theta))
            st = Gf.Vec2f(1.0 - point[0] / 2.0, (1.0 + point[2]) / 2.0)
        else:
            point = Gf.Vec3f(math.cos(theta), math.sin(theta), 0.0)
            st = Gf.Vec2f((1.0 - point[0]) / 2.0, (1.0 + point[1]) / 2.0)
        point_sts.append(st)
        points.append(point + center_point)

    return points, point_sts


def get_int_setting(key, default_value):
    settings = carb.settings.get_settings()
    settings.set_default(key, default_value)
    value = settings.get_as_int(key)

    return value


def generate_disk(
    center_point: Gf.Vec3f, u_patches: int, v_patches: int,
    origin: Gf.Vec3f, half_scale: float, up_axis="Y"
) -> Tuple[List[Gf.Vec3f], List[Gf.Vec3f], List[Gf.Vec2f], List[int], List[int]]:
    u_delta = 1.0 / u_patches
    v_delta = 1.0 / v_patches

    num_u_verts = u_patches
    num_v_verts = v_patches + 1

    points: List[Gf.Vec3f] = []
    normals: List[Gf.Vec3f] = []
    sts: List[Gf.Vec2f] = []
    face_indices: List[int] = []
    face_vertex_counts: List[int] = []

    center_point = transform_point(center_point, origin, half_scale)
    circle_points, _ = generate_circle_points(up_axis, u_patches, 1.0 / u_patches)
    for i in range(num_v_verts - 1):
        v = v_delta * i
        for j in range(num_u_verts):
            point = transform_point(circle_points[j], (0, 0, 0), half_scale * (1 - v))
            points.append(point + center_point)

    # Center point
    points.append(center_point)

    def calc_index(i, j):
        ii = i if i < num_u_verts else 0
        base_index = j * num_u_verts
        if j == num_v_verts - 1:
            return base_index
        else:
            return base_index + ii

    def get_uv(i, j):
        vindex = calc_index(i, j)
        # Ensure all axis to be [-1, 1]
        point = (points[vindex] - origin) / half_scale
        if up_axis == "Y":
            st = (Gf.Vec2f(-point[0], -point[2]) + Gf.Vec2f(1, 1)) / 2
        else:
            st = (Gf.Vec2f(point[0], point[1]) + Gf.Vec2f(1)) / 2
        
        return st

    # Generating quads or triangles of the center
    for j in range(v_patches):
        for i in range(u_patches):
            vindex00 = calc_index(i, j)
            vindex10 = calc_index(i + 1, j)
            vindex11 = calc_index(i + 1, j + 1)
            vindex01 = calc_index(i, j + 1)
            uv00 = get_uv(i, j)
            uv10 = get_uv(i + 1, j)
            uv11 = get_uv(i + 1, j + 1)
            uv01 = get_uv(i, j + 1)

            # Right-hand order
            if up_axis == "Y":
                if vindex11 == vindex01:
                    sts.extend([inverse_u(uv00), inverse_u(uv01), inverse_u(uv10)])
                    face_indices.extend((vindex00, vindex01, vindex10))
                else:
                    sts.extend([inverse_u(uv00), inverse_u(uv01), inverse_u(uv11), inverse_u(uv10)])
                    face_indices.extend((vindex00, vindex01, vindex11, vindex10))
                normal = Gf.Vec3f(0.0, 1.0, 0.0)
            else:
                if vindex11 == vindex01:
                    sts.extend([uv00, uv10, uv01])
                    face_indices.extend((vindex00, vindex10, vindex01))
                else:
                    sts.extend([uv00, uv10, uv11, uv01])
                    face_indices.extend((vindex00, vindex10, vindex11, vindex01))
                normal = Gf.Vec3f(0.0, 0.0, 1.0)

            if vindex11 == vindex01:
                face_vertex_counts.append(3)
                normals.extend([normal] * 3)
            else:
                face_vertex_counts.append(4)
                normals.extend([normal] * 4)

    return points, normals, sts, face_indices, face_vertex_counts


def generate_plane(origin, half_scale, u_patches, v_patches, up_axis):
    if isinstance(half_scale, Number):
        [w, h, d] = half_scale, half_scale, half_scale
    else:
        [w, h, d] = half_scale
    [x, y, z] = origin[0], origin[1], origin[2]

    num_u_verts = u_patches + 1
    num_v_verts = v_patches + 1

    points = []
    normals = []
    sts = []
    face_indices = []
    face_vertex_counts = []

    u_delta = 1.0 / u_patches
    v_delta = 1.0 / v_patches
    if up_axis == "Y":
        w_delta = 2.0 * w * u_delta
        h_delta = 2.0 * d * v_delta
        bottom_left = Gf.Vec3f(x - w, y, z - d)
        for i in range(num_v_verts):
            for j in range(num_u_verts):
                point = bottom_left + Gf.Vec3f(j * w_delta, 0.0, i * h_delta)
                points.append(point)
    elif up_axis == "Z":
        w_delta = 2.0 * w / u_patches
        h_delta = 2.0 * h / v_patches
        bottom_left = Gf.Vec3f(x - w, y - h, z)
        for i in range(num_v_verts):
            for j in range(num_u_verts):
                point = bottom_left + Gf.Vec3f(j * w_delta, i * h_delta, 0.0)
                points.append(point)
    else:  # X up
        w_delta = 2.0 * h / u_patches
        h_delta = 2.0 * d / v_patches
        bottom_left = Gf.Vec3f(x, y - h, z - d)
        for i in range(num_v_verts):
            for j in range(num_u_verts):
                point = bottom_left + Gf.Vec3f(0, j * w_delta, i * h_delta)
                points.append(point)

    def calc_index(i, j):
        ii = i if i < num_u_verts else 0
        jj = j if j < num_v_verts else 0
        return jj * num_u_verts + ii

    def get_uv(i, j):
        u = i * u_delta if i < num_u_verts else 1.0
        if up_axis == "Y":
            v = 1 - j * v_delta if j < num_v_verts else 0.0
        else:
            v = j * v_delta if j < num_v_verts else 1.0

        return Gf.Vec2f(u, v)

    # Generating quads
    for j in range(v_patches):
        for i in range(u_patches):
            vindex00 = calc_index(i, j)
            vindex10 = calc_index(i + 1, j)
            vindex11 = calc_index(i + 1, j + 1)
            vindex01 = calc_index(i, j + 1)
            uv00 = get_uv(i, j)
            uv10 = get_uv(i + 1, j)
            uv11 = get_uv(i + 1, j + 1)
            uv01 = get_uv(i, j + 1)

            # Right-hand order
            if up_axis == "Y":
                sts.extend([uv00, uv01, uv11, uv10])
                face_indices.extend((vindex00, vindex01, vindex11, vindex10))
                normal = Gf.Vec3f(0.0, 1.0, 0.0)
            elif up_axis == "Z":
                sts.extend([uv00, uv10, uv11, uv01])
                face_indices.extend((vindex00, vindex10, vindex11, vindex01))
                normal = Gf.Vec3f(0.0, 0.0, 1.0)
            else:  # X
                sts.extend([uv00, uv01, uv11, uv10])
                face_indices.extend((vindex00, vindex01, vindex11, vindex10))
                normal = Gf.Vec3f(0.0, 1.0, 0.0)
            face_vertex_counts.append(4)
            normals.extend([normal] * 4)

    return points, normals, sts, face_indices, face_vertex_counts


def modify_winding_order(face_counts, face_indices):
    total = 0
    for count in face_counts:
        if count >= 3:
            start = total + 1
            end = total + count
            face_indices[start:end] = face_indices[start:end][::-1]
        total += count
