from .utils import (
    get_int_setting, build_int_slider, modify_winding_order,
    generate_circle_points, transform_point, inverse_u, inverse_v, generate_disk
)
from .abstract_shape_evaluator import AbstractShapeEvaluator
from pxr import Gf
from typing import List


class CylinderEvaluator(AbstractShapeEvaluator):
    SETTING_OBJECT_HALF_SCALE = "/persistent/app/mesh_generator/shapes/cylinder/object_half_scale"
    SETTING_U_SCALE = "/persistent/app/mesh_generator/shapes/cylinder/u_scale"
    SETTING_V_SCALE = "/persistent/app/mesh_generator/shapes/cylinder/v_scale"
    SETTING_W_SCALE = "/persistent/app/mesh_generator/shapes/cylinder/w_scale"

    def __init__(self, attributes: dict):
        super().__init__(attributes)

    def eval(self, **kwargs):
        half_scale = kwargs.get("half_scale", None)
        if half_scale is None or half_scale <= 0:
            half_scale = self.get_default_half_scale()
        
        num_u_verts_scale = kwargs.get("u_verts_scale", None)
        if num_u_verts_scale is None or num_u_verts_scale <= 0:
            num_u_verts_scale = get_int_setting(CylinderEvaluator.SETTING_U_SCALE, 1)
        
        num_v_verts_scale = kwargs.get("v_verts_scale", None)
        if num_v_verts_scale is None or num_v_verts_scale <= 0:
            num_v_verts_scale = get_int_setting(CylinderEvaluator.SETTING_V_SCALE, 1)
        
        num_w_verts_scale = kwargs.get("w_verts_scale", None)
        if num_w_verts_scale is None or num_w_verts_scale <= 0:
            num_w_verts_scale = get_int_setting(CylinderEvaluator.SETTING_W_SCALE, 1)

        up_axis = kwargs.get("up_axis", "Y")
        origin = Gf.Vec3f(0.0)

        u_patches = kwargs.get("u_patches", 32)
        v_patches = kwargs.get("v_patches", 1)
        w_patches = kwargs.get("w_patches", 1)
        u_patches = u_patches * num_u_verts_scale
        v_patches = v_patches * num_v_verts_scale
        w_patches = w_patches * num_w_verts_scale
        u_patches = max(int(u_patches), 3)
        v_patches = max(int(v_patches), 1)
        w_patches = max(int(w_patches), 1)

        u_delta = 1.0 / (u_patches if u_patches != 0 else 1)
        v_delta = 1.0 / (v_patches if v_patches != 0 else 1)

        # open meshes need an extra vert on the end to create the last patch
        # closed meshes reuse the vert at index 0 to close their final patch
        num_u_verts = u_patches
        num_v_verts = v_patches + 1

        points: List[Gf.Vec3f] = []
        normals: List[Gf.Vec3f] = []
        sts: List[Gf.Vec2f] = []
        face_indices: List[int] = []
        face_vertex_counts: List[int] = []

        # generate circle points
        circle_points, _ = generate_circle_points(up_axis, num_u_verts, u_delta)
        for j in range(num_v_verts):
            for i in range(num_u_verts):
                v = j * v_delta
                point = circle_points[i]
                if up_axis == "Y":
                    point[1] = 2.0 * (v - 0.5)
                else:
                    point[2] = 2.0 * (v - 0.5)
                point = transform_point(point, origin, half_scale)
                points.append(point)

        def calc_index(i, j):
            ii = i if i < num_u_verts else 0
            jj = j if j < num_v_verts else 0
            return jj * num_u_verts + ii

        def get_uv(i, j):
            u = 1 - i * u_delta if i < num_u_verts else 0.0
            v = j * v_delta if j < num_v_verts else 1.0
            return Gf.Vec2f(u, v)

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
                p00 = points[vindex00]
                p10 = points[vindex10]
                p11 = points[vindex11]
                p01 = points[vindex01]

                # Right-hand order
                if up_axis == "Y":
                    sts.extend([uv00, uv01, uv11, uv10])
                    face_indices.extend((vindex00, vindex01, vindex11, vindex10))
                    normals.append(Gf.Vec3f(p00[0], 0, p00[2]))
                    normals.append(Gf.Vec3f(p01[0], 0, p01[2]))
                    normals.append(Gf.Vec3f(p11[0], 0, p11[2]))
                    normals.append(Gf.Vec3f(p10[0], 0, p10[2]))
                else:
                    sts.extend([inverse_u(uv00), inverse_u(uv10), inverse_u(uv11), inverse_u(uv01)])
                    face_indices.extend((vindex00, vindex10, vindex11, vindex01))
                    normals.append(Gf.Vec3f(p00[0], p00[1], 0))
                    normals.append(Gf.Vec3f(p10[0], p10[1], 0))
                    normals.append(Gf.Vec3f(p11[0], p11[1], 0))
                    normals.append(Gf.Vec3f(p01[0], p01[1], 0))
                face_vertex_counts.append(4)

        # Add hat
        if up_axis == "Y":
            bottom_center_point = Gf.Vec3f(0, -1, 0)
            top_center_point = Gf.Vec3f(0, 1, 0)
        else:
            bottom_center_point = Gf.Vec3f(0, 0, -1)
            top_center_point = Gf.Vec3f(0, 0, 1)

        def add_hat(center_point, rim_points_start_index, w_patches, invert_wind_order=False):
            bt_points, _, bt_sts, bt_face_indices, bt_face_vertex_counts = generate_disk(
                center_point, u_patches, w_patches, origin, half_scale, up_axis
            )

            total_points = len(points)

            # Skips shared points
            points.extend(bt_points[num_u_verts:])

            if invert_wind_order:
                modify_winding_order(bt_face_vertex_counts, bt_sts)
                for st in bt_sts:
                    sts.append(inverse_v(st))
            else:
                sts.extend(bt_sts)
            face_vertex_counts.extend(bt_face_vertex_counts)
            normals.extend([center_point] * len(bt_face_indices))

            # Remapping cap points
            for i, index in enumerate(bt_face_indices):
                if index >= num_u_verts:
                    bt_face_indices[i] += total_points - num_u_verts
                else:
                    bt_face_indices[i] += rim_points_start_index
            if invert_wind_order:
               modify_winding_order(bt_face_vertex_counts, bt_face_indices)
            face_indices.extend(bt_face_indices)
            
        top_hat_start_index = len(points) - num_u_verts

        # Add bottom hat to close shape
        add_hat(bottom_center_point, 0, w_patches, True)
        
        # Add top hat to close shape
        add_hat(top_center_point, top_hat_start_index, w_patches)

        return points, normals, sts, face_indices, face_vertex_counts

    @staticmethod
    def build_setting_ui():
        from omni import ui
        CylinderEvaluator._half_scale_slider = build_int_slider(
            "Object Half Scale", CylinderEvaluator.SETTING_OBJECT_HALF_SCALE, 50, 10, 1000
        )
        ui.Spacer(height=5)

        CylinderEvaluator._u_scale_slider = build_int_slider(
            "U Verts Scale", CylinderEvaluator.SETTING_U_SCALE, 1, 1, 10,
            "Tessellation Level in Horizontal Direction"
        )
        ui.Spacer(height=5)

        CylinderEvaluator._v_scale_slider = build_int_slider(
            "V Verts Scale", CylinderEvaluator.SETTING_V_SCALE, 1, 1, 10,
            "Tessellation Level in Vertical Direction"
        )
        ui.Spacer(height=5)
        
        CylinderEvaluator._w_scale_slider = build_int_slider(
            "W Verts Scale", CylinderEvaluator.SETTING_W_SCALE, 1, 1, 10,
            "Tessellation Level of Bottom and Top Caps"
        )

    @staticmethod
    def reset_setting():
        CylinderEvaluator._half_scale_slider.set_value(CylinderEvaluator.get_default_half_scale())
        CylinderEvaluator._u_scale_slider.set_value(1)
        CylinderEvaluator._v_scale_slider.set_value(1)
        CylinderEvaluator._w_scale_slider.set_value(1)
    
    @staticmethod
    def get_default_half_scale():
        half_scale = get_int_setting(CylinderEvaluator.SETTING_OBJECT_HALF_SCALE, 50)

        return half_scale
