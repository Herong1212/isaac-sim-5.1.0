import math

from .utils import (
    get_int_setting, build_int_slider, modify_winding_order,
    transform_point, inverse_u, inverse_v, generate_disk
)
from .abstract_shape_evaluator import AbstractShapeEvaluator
from pxr import Gf
from typing import List, Tuple


class ConeEvaluator(AbstractShapeEvaluator):
    SETTING_OBJECT_HALF_SCALE = "/persistent/app/mesh_generator/shapes/cone/object_half_scale"
    SETTING_U_SCALE = "/persistent/app/mesh_generator/shapes/cone/u_scale"
    SETTING_V_SCALE = "/persistent/app/mesh_generator/shapes/cone/v_scale"
    SETTING_W_SCALE = "/persistent/app/mesh_generator/shapes/cone/w_scale"

    def __init__(self, attributes: dict):
        super().__init__(attributes)
        self.radius = 1.0
        self.height = 2.0

    # The sequence must be kept in the same as generate_circle_points
    # in the u direction to share points with the cap.
    def _eval(self, up_axis, u, v) -> Tuple[Gf.Vec3f, Gf.Vec3f]:
        theta = u * 2.0 * math.pi
        x = (1 - v) * math.cos(theta)
        h = v * self.height - 1
        if up_axis == "Y":
            z = (1 - v) * math.sin(theta)
            point = Gf.Vec3f(x, h, z)
            dpdu = Gf.Vec3f(-2.0 * math.pi * z, 0.0, 2.0 * math.pi * x)
            dpdv = Gf.Vec3f(-x / (1 - v), self.height, -z / (1 - v))
            normal = dpdv ^ dpdu
            normal = normal.GetNormalized()
        else:
            y = (1 - v) * math.sin(theta)
            point = Gf.Vec3f(x, y, h)
            dpdu = Gf.Vec3f(-2.0 * math.pi * y, 2.0 * math.pi * x, 0)
            dpdv = Gf.Vec3f(-x / (1 - v), -y / (1 - v), self.height)
            normal = dpdu ^ dpdv
            normal = normal.GetNormalized()

        return point, normal

    def eval(self, **kwargs):
        half_scale = kwargs.get("half_scale", None)
        if half_scale is None or half_scale <= 0:
            half_scale = self.get_default_half_scale()
        
        num_u_verts_scale = kwargs.get("u_verts_scale", None)
        if num_u_verts_scale is None or num_u_verts_scale <= 0:
            num_u_verts_scale = get_int_setting(ConeEvaluator.SETTING_U_SCALE, 1)
        
        num_v_verts_scale = kwargs.get("v_verts_scale", None)
        if num_v_verts_scale is None or num_v_verts_scale <= 0:
            num_v_verts_scale = get_int_setting(ConeEvaluator.SETTING_V_SCALE, 3)
        
        num_w_verts_scale = kwargs.get("w_verts_scale", None)
        if num_w_verts_scale is None or num_w_verts_scale <= 0:
            num_w_verts_scale = get_int_setting(ConeEvaluator.SETTING_W_SCALE, 1)

        num_u_verts_scale = max(num_u_verts_scale, 1)
        num_v_verts_scale = max(num_v_verts_scale, 1)
        num_w_verts_scale = max(num_w_verts_scale, 1)

        up_axis = kwargs.get("up_axis", "Y")
        origin = Gf.Vec3f(0.0)
        u_patches = kwargs.get("u_patches", 64)
        v_patches = kwargs.get("v_patches", 1)
        w_patches = kwargs.get("w_patches", 1)

        u_patches = u_patches * num_u_verts_scale
        v_patches = v_patches * num_v_verts_scale
        w_patches = w_patches * num_w_verts_scale
        u_patches = max(int(u_patches), 3)
        v_patches = max(int(v_patches), 1)
        w_patches = max(int(w_patches), 1)

        accuracy = 0.00001
        u_delta = 1.0 / u_patches
        v_delta = (1.0 - accuracy) / v_patches

        num_u_verts = u_patches
        num_v_verts = v_patches + 1

        points: List[Gf.Vec3f] = []
        point_normals: List[Gf.Vec3f] = []
        normals: List[Gf.Vec3f] = []
        sts: List[Gf.Vec2f] = []
        face_indices: List[int] = []
        face_vertex_counts: List[int] = []

        for j in range(num_v_verts):
            for i in range(num_u_verts):
                u = i * u_delta
                v = j * v_delta
                point, normal = self._eval(up_axis, u, v)
                point = transform_point(point, origin, half_scale)
                points.append(point)
                point_normals.append(normal)

        def calc_index(i, j):
            i = i if i < num_u_verts else 0
            base_index = j * num_u_verts
            point_index = base_index + i
            return point_index

        def get_uv(i, j):
            u = 1 - i * u_delta if i < num_u_verts else 0.0
            v = j * v_delta if j != num_v_verts - 1 else 1.0
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

                # Right-hand order
                if up_axis == "Y":
                    sts.extend([uv00, uv01, uv11, uv10])
                    face_indices.extend((vindex00, vindex01, vindex11, vindex10))
                    normals.extend(
                        [
                            point_normals[vindex00],
                            point_normals[vindex01],
                            point_normals[vindex11],
                            point_normals[vindex10],
                        ]
                    )
                else:
                    sts.extend([inverse_u(uv00), inverse_u(uv10), inverse_u(uv11), inverse_u(uv01)])
                    face_indices.extend((vindex00, vindex10, vindex11, vindex01))
                    normals.extend(
                        [
                            point_normals[vindex00],
                            point_normals[vindex10],
                            point_normals[vindex11],
                            point_normals[vindex01],
                        ]
                    )
                face_vertex_counts.append(4)

        # Add hat
        if up_axis == "Y":
            bottom_center_point = Gf.Vec3f(0, -1, 0)
            top_center_point = Gf.Vec3f(0, 1 - accuracy, 0)
        else:
            bottom_center_point = Gf.Vec3f(0, 0, -1)
            top_center_point = Gf.Vec3f(0, 0, 1 - accuracy)
        
        def add_hat(center_point, rim_points_start_index, w_patches, invert_wind_order=False):
            bt_points, _, bt_sts, bt_face_indices, bt_face_vertex_counts = generate_disk(
                center_point, u_patches, w_patches, origin, half_scale, up_axis
            )

            # Total points before adding hat
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
            
        # Add top hat to close shape
        top_hat_start_index = len(points) - num_u_verts
        add_hat(top_center_point, top_hat_start_index, 1)

        # Add bottom hat to close shape
        add_hat(bottom_center_point, 0, w_patches, True)
        
        return points, normals, sts, face_indices, face_vertex_counts

    @staticmethod
    def build_setting_ui():
        from omni import ui
        ConeEvaluator._half_scale_slider = build_int_slider(
            "Object Half Scale", ConeEvaluator.SETTING_OBJECT_HALF_SCALE, 50, 10, 1000
        )
        ui.Spacer(height=5)

        ConeEvaluator._u_scale_slider = build_int_slider(
            "U Verts Scale", ConeEvaluator.SETTING_U_SCALE, 1, 1, 10,
            "Tessellation Level in Horizontal Direction"
        )
        ui.Spacer(height=5)

        ConeEvaluator._v_scale_slider = build_int_slider(
            "V Verts Scale", ConeEvaluator.SETTING_V_SCALE, 1, 1, 10, "Tessellation Level in Vertical Direction"
        )
        ui.Spacer(height=5)
        
        ConeEvaluator._w_scale_slider = build_int_slider(
            "W Verts Scale", ConeEvaluator.SETTING_W_SCALE, 1, 1, 10, "Tessellation Level of Bottom Cap"
        )

    @staticmethod
    def reset_setting():
        ConeEvaluator._half_scale_slider.set_value(ConeEvaluator.get_default_half_scale())
        ConeEvaluator._u_scale_slider.set_value(1)
        ConeEvaluator._v_scale_slider.set_value(1)
        ConeEvaluator._w_scale_slider.set_value(1)
    
    @staticmethod
    def get_default_half_scale():
        half_scale = get_int_setting(ConeEvaluator.SETTING_OBJECT_HALF_SCALE, 50)

        return half_scale

