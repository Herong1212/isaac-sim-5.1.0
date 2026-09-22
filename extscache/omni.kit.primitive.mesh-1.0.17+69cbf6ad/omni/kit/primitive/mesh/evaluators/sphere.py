import math
from .utils import get_int_setting, build_int_slider
from .utils import transform_point
from .abstract_shape_evaluator import AbstractShapeEvaluator
from pxr import Gf


class SphereEvaluator(AbstractShapeEvaluator):
    SETTING_OBJECT_HALF_SCALE = "/persistent/app/mesh_generator/shapes/shpere/object_half_scale"
    SETTING_U_SCALE = "/persistent/app/mesh_generator/shapes/sphere/u_scale"
    SETTING_V_SCALE = "/persistent/app/mesh_generator/shapes/sphere/v_scale"

    def __init__(self, attributes: dict):
        super().__init__(attributes)

    def _eval(self, u, v, up_axis):
        theta = u * 2.0 * math.pi
        phi = (v - 0.5) * math.pi
        cos_phi = math.cos(phi)

        if up_axis == "Y":
            x = cos_phi * math.cos(theta)
            y = math.sin(phi)
            z = cos_phi * math.sin(theta)
        else:
            x = cos_phi * math.cos(theta)
            y = cos_phi * math.sin(theta)
            z = math.sin(phi)

        return Gf.Vec3f(x, y, z)

    def eval(self, **kwargs):
        half_scale = kwargs.get("half_scale", None)
        if half_scale is None or half_scale <= 0:
            half_scale = self.get_default_half_scale()

        num_u_verts_scale = kwargs.get("u_verts_scale", None)
        if num_u_verts_scale is None or num_u_verts_scale <= 0:
            num_u_verts_scale = get_int_setting(SphereEvaluator.SETTING_U_SCALE, 1)

        num_v_verts_scale = kwargs.get("v_verts_scale", None)
        if num_v_verts_scale is None or num_v_verts_scale <= 0:
            num_v_verts_scale = get_int_setting(SphereEvaluator.SETTING_V_SCALE, 1)

        up_axis = kwargs.get("up_axis", "Y")
        origin = Gf.Vec3f(0.0)

        u_patches = kwargs.get("u_patches", 32)
        v_patches = kwargs.get("v_patches", 16)

        num_u_verts_scale = max(num_u_verts_scale, 1)
        num_v_verts_scale = max(num_v_verts_scale, 1)
        u_patches = u_patches * num_u_verts_scale
        v_patches = v_patches * num_v_verts_scale
        u_patches = max(int(u_patches), 3)
        v_patches = max(int(v_patches), 2)

        u_delta = 1.0 / u_patches
        v_delta = 1.0 / v_patches

        num_u_verts = u_patches
        num_v_verts = v_patches + 1

        points = []
        normals = []
        sts = []
        face_indices = []
        face_vertex_counts = []

        if up_axis == "Y":
            bottom_point = Gf.Vec3f(0.0, -1.0, 0.0)
        else:
            bottom_point = Gf.Vec3f(0.0, 0.0, -1.0)
        point = transform_point(bottom_point, origin, half_scale)
        points.append(point)

        for j in range(1, num_v_verts - 1):
            v = j * v_delta
            for i in range(num_u_verts):
                u = i * u_delta
                point = self._eval(u, v, up_axis)
                point = transform_point(point, origin, half_scale)
                points.append(Gf.Vec3f(point))

        if up_axis == "Y":
            top_point = Gf.Vec3f(0.0, 1.0, 0.0)
        else:
            top_point = Gf.Vec3f(0.0, 0.0, 1.0)
        point = transform_point(top_point, origin, half_scale)
        points.append(point)

        def calc_index(i, j):
            if j == 0:
                return 0
            elif j == num_v_verts - 1:
                return len(points) - 1
            else:
                i = i if i < num_u_verts else 0
                return (j - 1) * num_u_verts + i + 1

        def get_uv(i, j):
            if up_axis == "Y":
                u = 1 - i * u_delta
                v = j * v_delta
            else:
                u = i * u_delta
                v = j * v_delta
            return Gf.Vec2f(u, v)

        # Generate body
        for j in range(v_patches):
            for i in range(u_patches):
                # Index 0 is the bottom hat point
                vindex00 = calc_index(i, j)
                vindex10 = calc_index(i + 1, j)
                vindex11 = calc_index(i + 1, j + 1)
                vindex01 = calc_index(i, j + 1)
                st00 = get_uv(i, j)
                st10 = get_uv(i + 1, j)
                st11 = get_uv(i + 1, j + 1)
                st01 = get_uv(i, j + 1)
                p0 = points[vindex00]
                p1 = points[vindex10]
                p2 = points[vindex11]
                p3 = points[vindex01]

                # Use face varying uv
                if up_axis == "Y":
                    if vindex11 == vindex01:
                        sts.extend([st00, st01, st10])
                        face_indices.extend((vindex00, vindex01, vindex10))
                        face_vertex_counts.append(3)
                        normals.extend([p0, p3, p1])
                    elif vindex00 == vindex10:
                        sts.extend([st00, st01, st11])
                        face_indices.extend((vindex00, vindex01, vindex11))
                        face_vertex_counts.append(3)
                        normals.extend([p0, p3, p2])
                    else:
                        sts.extend([st00, st01, st11, st10])
                        face_indices.extend((vindex00, vindex01, vindex11, vindex10))
                        face_vertex_counts.append(4)
                        normals.extend([p0, p3, p2, p1])
                else:
                    if vindex11 == vindex01:
                        sts.extend([st00, st10, st01])
                        face_indices.extend((vindex00, vindex10, vindex01))
                        face_vertex_counts.append(3)
                        normals.extend([p0, p1, p3])
                    elif vindex00 == vindex10:
                        sts.extend([st00, st11, st01])
                        face_indices.extend((vindex00, vindex11, vindex01))
                        face_vertex_counts.append(3)
                        normals.extend([p0, p2, p3])
                    else:
                        sts.extend([st00, st10, st11, st01])
                        face_indices.extend((vindex00, vindex10, vindex11, vindex01))
                        face_vertex_counts.append(4)
                        normals.extend([p0, p1, p2, p3])

        return points, normals, sts, face_indices, face_vertex_counts

    @staticmethod
    def build_setting_ui():
        from omni import ui
        SphereEvaluator._half_scale_slider = build_int_slider(
            "Object Half Scale", SphereEvaluator.SETTING_OBJECT_HALF_SCALE, 50, 10, 1000
        )
        ui.Spacer(height=5)

        SphereEvaluator._u_scale_slider = build_int_slider(
            "U Verts Scale", SphereEvaluator.SETTING_U_SCALE, 1, 1, 10
        )
        ui.Spacer(height=5)

        SphereEvaluator._v_scale_slider = build_int_slider(
            "V Verts Scale", SphereEvaluator.SETTING_V_SCALE, 1, 1, 10
        )

    @staticmethod
    def reset_setting():
        SphereEvaluator._half_scale_slider.set_value(SphereEvaluator.get_default_half_scale())
        SphereEvaluator._u_scale_slider.set_value(1)
        SphereEvaluator._v_scale_slider.set_value(1)
    
    @staticmethod
    def get_default_half_scale():
        half_scale = get_int_setting(SphereEvaluator.SETTING_OBJECT_HALF_SCALE, 50)

        return half_scale
