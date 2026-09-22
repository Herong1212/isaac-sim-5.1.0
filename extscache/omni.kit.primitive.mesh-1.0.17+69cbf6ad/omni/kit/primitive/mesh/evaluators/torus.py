import math
from .utils import get_int_setting, build_int_slider
from .utils import transform_point
from .abstract_shape_evaluator import AbstractShapeEvaluator
from pxr import Gf


class TorusEvaluator(AbstractShapeEvaluator):
    SETTING_OBJECT_HALF_SCALE = "/persistent/app/mesh_generator/shapes/torus/object_half_scale"
    SETTING_U_SCALE = "/persistent/app/mesh_generator/shapes/torus/u_scale"
    SETTING_V_SCALE = "/persistent/app/mesh_generator/shapes/torus/v_scale"

    def __init__(self, attributes: dict):
        super().__init__(attributes)
        self.hole_radius = 1.0
        self.tube_radius = 0.5

    def _eval(self, up_axis, u, v):
        theta = u * 2.0 * math.pi
        phi = v * 2.0 * math.pi - 0.5 * math.pi

        rad_cos_phi = self.tube_radius * math.cos(phi)
        cos_theta = math.cos(theta)
        sin_phi = math.sin(phi)
        sin_theta = math.sin(theta)
        x = (self.hole_radius + rad_cos_phi) * cos_theta
        nx = self.hole_radius * cos_theta

        if up_axis == "Y":
            y = self.tube_radius * sin_phi
            z = (self.hole_radius + rad_cos_phi) * sin_theta
            ny = 0
            nz = self.hole_radius * sin_theta
        else:
            y = (self.hole_radius + rad_cos_phi) * sin_theta
            z = self.tube_radius * sin_phi
            ny = self.hole_radius * sin_theta
            nz = 0

        point = Gf.Vec3f(x, y, z)

        # construct the normal by creating a vector from the center point of the tube to the surface
        normal = Gf.Vec3f(x - nx, y - ny, z - nz)
        normal = normal.GetNormalized()

        return point, normal

    def eval(self, **kwargs):
        half_scale = kwargs.get("half_scale", None)
        if half_scale is None or half_scale <= 0:
            half_scale = self.get_default_half_scale()

        num_u_verts_scale = kwargs.get("u_verts_scale", None)
        if num_u_verts_scale is None or num_u_verts_scale <= 0:
            num_u_verts_scale = get_int_setting(TorusEvaluator.SETTING_U_SCALE, 1)
        
        num_v_verts_scale = kwargs.get("v_verts_scale", None)
        if num_v_verts_scale is None or num_v_verts_scale <= 0:
            num_v_verts_scale = get_int_setting(TorusEvaluator.SETTING_V_SCALE, 1)

        up_axis = kwargs.get("up_axis", "Y")
        origin = Gf.Vec3f(0.0)

        u_patches = kwargs.get("u_patches", 32)
        v_patches = kwargs.get("v_patches", 32)

        num_u_verts_scale = max(num_u_verts_scale, 1)
        num_v_verts_scale = max(num_v_verts_scale, 1)
        u_patches = u_patches * num_u_verts_scale
        v_patches = v_patches * num_v_verts_scale
        u_patches = max(int(u_patches), 3)
        v_patches = max(int(v_patches), 3)

        u_delta = 1.0 / u_patches
        v_delta = 1.0 / v_patches

        num_u_verts = u_patches
        num_v_verts = v_patches

        points = []
        point_normals = []
        sts = []
        face_indices = []
        face_vertex_counts = []

        for j in range(num_v_verts):
            v = j * v_delta
            for i in range(num_u_verts):
                u = i * u_delta
                point, point_normal = self._eval(up_axis, u, v)
                point = transform_point(point, origin, half_scale)
                points.append(point)
                point_normals.append(point_normal)

        def calc_index(i, j):
            ii = i if i < num_u_verts else 0
            jj = j if j < num_v_verts else 0
            return jj * num_u_verts + ii

        def get_uv(i, j):
            if up_axis == "Y":
                u = 1 - i * u_delta if i < num_u_verts else 0.0
            else:
                u = i * u_delta if i < num_u_verts else 1.0
            v = j * v_delta if j < num_v_verts else 1.0
            return Gf.Vec2f(u, v)

        # Last patch from last vert to first vert to close shape
        normals = []
        for j in range(v_patches):
            for i in range(u_patches):
                vindex00 = calc_index(i, j)
                vindex10 = calc_index(i + 1, j)
                vindex11 = calc_index(i + 1, j + 1)
                vindex01 = calc_index(i, j + 1)

                # Use face varying uv
                face_vertex_counts.append(4)
                if up_axis == "Y":
                    sts.append(get_uv(i, j))
                    sts.append(get_uv(i, j + 1))
                    sts.append(get_uv(i + 1, j + 1))
                    sts.append(get_uv(i + 1, j))
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
                    sts.append(get_uv(i, j))
                    sts.append(get_uv(i + 1, j))
                    sts.append(get_uv(i + 1, j + 1))
                    sts.append(get_uv(i, j + 1))
                    face_indices.extend((vindex00, vindex10, vindex11, vindex01))
                    normals.extend(
                        [
                            point_normals[vindex00],
                            point_normals[vindex10],
                            point_normals[vindex11],
                            point_normals[vindex01],
                        ]
                    )

        return points, normals, sts, face_indices, face_vertex_counts

    @staticmethod
    def build_setting_ui():
        from omni import ui
        TorusEvaluator._half_scale_slider = build_int_slider(
            "Object Half Scale", TorusEvaluator.SETTING_OBJECT_HALF_SCALE, 50, 10, 1000
        )
        ui.Spacer(height=5)

        TorusEvaluator._u_scale_slider = build_int_slider("U Verts Scale", TorusEvaluator.SETTING_U_SCALE, 1, 1, 10)
        ui.Spacer(height=5)

        TorusEvaluator._v_scale_slider = build_int_slider("V Verts Scale", TorusEvaluator.SETTING_V_SCALE, 1, 1, 10)

    @staticmethod
    def reset_setting():
        TorusEvaluator._half_scale_slider.set_value(TorusEvaluator.get_default_half_scale())
        TorusEvaluator._u_scale_slider.set_value(1)
        TorusEvaluator._v_scale_slider.set_value(1)
    
    @staticmethod
    def get_default_half_scale():
        half_scale = get_int_setting(TorusEvaluator.SETTING_OBJECT_HALF_SCALE, 50)

        return half_scale
