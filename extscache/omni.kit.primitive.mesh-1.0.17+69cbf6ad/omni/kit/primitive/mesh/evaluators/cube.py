from .utils import get_int_setting, build_int_slider, generate_plane, modify_winding_order
from .abstract_shape_evaluator import AbstractShapeEvaluator
from pxr import Gf


class CubeEvaluator(AbstractShapeEvaluator):
    SETTING_OBJECT_HALF_SCALE = "/persistent/app/mesh_generator/shapes/cube/object_half_scale"
    SETTING_U_SCALE = "/persistent/app/mesh_generator/shapes/cube/u_scale"
    SETTING_V_SCALE = "/persistent/app/mesh_generator/shapes/cube/v_scale"
    SETTING_W_SCALE = "/persistent/app/mesh_generator/shapes/cube/w_scale"

    def __init__(self, attributes: dict):
        super().__init__(attributes)

    def eval(self, **kwargs):
        half_scale = kwargs.get("half_scale", None)
        if half_scale is None or half_scale <= 0:
            half_scale = self.get_default_half_scale()

        num_u_verts_scale = kwargs.get("u_verts_scale", None)
        if num_u_verts_scale is None or num_u_verts_scale <= 0:
            num_u_verts_scale = get_int_setting(CubeEvaluator.SETTING_U_SCALE, 1)

        num_v_verts_scale = kwargs.get("v_verts_scale", None)
        if num_v_verts_scale is None or num_v_verts_scale <= 0:
            num_v_verts_scale = get_int_setting(CubeEvaluator.SETTING_V_SCALE, 1)

        num_w_verts_scale = kwargs.get("w_verts_scale", None)
        if num_w_verts_scale is None or num_w_verts_scale <= 0:
            num_w_verts_scale = get_int_setting(CubeEvaluator.SETTING_W_SCALE, 1)

        up_axis = kwargs.get("up_axis", "Y")
        origin = Gf.Vec3f(0.0)

        u_patches = kwargs.get("u_patches", 1)
        v_patches = kwargs.get("v_patches", 1)
        w_patches = kwargs.get("w_patches", 1)
        u_patches = u_patches * num_u_verts_scale
        v_patches = v_patches * num_v_verts_scale
        w_patches = w_patches * num_w_verts_scale
        u_patches = max(int(u_patches), 1)
        v_patches = max(int(v_patches), 1)
        w_patches = max(int(w_patches), 1)

        [x, y, z] = origin

        (
            xy_plane_points, xy_plane_normals, xy_plane_sts,
            xy_plane_face_indices, xy_plane_face_vertex_counts
        ) = generate_plane(Gf.Vec3f(x, y, z + half_scale), half_scale, u_patches, v_patches, "Z")

        (
            xz_plane_points, xz_plane_normals, xz_plane_sts,
            xz_plane_face_indices, xz_plane_face_vertex_counts
        ) = generate_plane(Gf.Vec3f(x, y - half_scale, z), half_scale, u_patches, w_patches, "Y")

        (
            yz_plane_points, yz_plane_normals, yz_plane_sts,
            yz_plane_face_indices, yz_plane_face_vertex_counts
        ) = generate_plane(Gf.Vec3f(x - half_scale, y, z), half_scale, v_patches, w_patches, "X")

        points = []
        normals = []
        sts = []
        face_indices = []
        face_vertex_counts = []

        # XY planes
        points.extend(xy_plane_points)
        normals.extend([Gf.Vec3f(0, 0, 1)] * len(xy_plane_normals))
        sts.extend(xy_plane_sts)
        face_indices.extend(xy_plane_face_indices)
        face_vertex_counts.extend(xy_plane_face_vertex_counts)

        total_indices = len(points)
        plane_points = [point + Gf.Vec3f(0, 0, -2.0 * half_scale) for point in xy_plane_points]
        points.extend(plane_points)
        normals.extend([Gf.Vec3f(0, 0, -1)] * len(xy_plane_normals))
        modify_winding_order(xy_plane_face_vertex_counts, xy_plane_sts)
        plane_sts = [Gf.Vec2f(1 - st[0], st[1]) for st in xy_plane_sts]
        sts.extend(plane_sts)
        plane_face_indices = [index + total_indices for index in xy_plane_face_indices]
        modify_winding_order(xy_plane_face_vertex_counts, plane_face_indices)
        face_indices.extend(plane_face_indices)
        face_vertex_counts.extend(xy_plane_face_vertex_counts)

        # xz planes
        total_indices = len(points)
        plane_points = [point + Gf.Vec3f(0, 2.0 * half_scale, 0) for point in xz_plane_points]
        points.extend(plane_points)
        normals.extend([Gf.Vec3f(0, 1, 0)] * len(xz_plane_normals))
        sts.extend(xz_plane_sts)
        plane_face_indices = [index + total_indices for index in xz_plane_face_indices]
        face_indices.extend(plane_face_indices)
        face_vertex_counts.extend(xz_plane_face_vertex_counts)

        total_indices = len(points)
        points.extend(xz_plane_points)
        normals.extend([Gf.Vec3f(0, -1, 0)] * len(xz_plane_normals))
        modify_winding_order(xz_plane_face_vertex_counts, xz_plane_sts)
        plane_sts = [Gf.Vec2f(st[0], 1 - st[1]) for st in xz_plane_sts]
        sts.extend(plane_sts)
        plane_face_indices = [index + total_indices for index in xz_plane_face_indices]
        modify_winding_order(xz_plane_face_vertex_counts, plane_face_indices)
        face_indices.extend(plane_face_indices)
        face_vertex_counts.extend(xz_plane_face_vertex_counts)

        # yz planes
        total_indices = len(points)
        points.extend(yz_plane_points)
        normals.extend([Gf.Vec3f(-1, 0, 0)] * len(yz_plane_normals))
        plane_sts = [Gf.Vec2f(st[1], st[0]) for st in yz_plane_sts]
        sts.extend(plane_sts)
        plane_face_indices = [index + total_indices for index in yz_plane_face_indices]
        face_indices.extend(plane_face_indices)
        face_vertex_counts.extend(yz_plane_face_vertex_counts)

        total_indices = len(points)
        plane_points = [point + Gf.Vec3f(2.0 * half_scale, 0, 0) for point in yz_plane_points]
        points.extend(plane_points)
        normals.extend([Gf.Vec3f(1, 0, 0)] * len(yz_plane_normals))
        modify_winding_order(yz_plane_face_vertex_counts, yz_plane_sts)
        plane_sts = [Gf.Vec2f(1 - st[1], st[0]) for st in yz_plane_sts]
        sts.extend(plane_sts)
        plane_face_indices = [index + total_indices for index in yz_plane_face_indices]
        modify_winding_order(yz_plane_face_vertex_counts, plane_face_indices)
        face_indices.extend(plane_face_indices)
        face_vertex_counts.extend(yz_plane_face_vertex_counts)

        # Welds the edges of cube
        keep = [True] * len(points)
        index_remap = [-1] * len(points)
        keep_points = []
        for i in range(0, len(points)):
            if not keep[i]:
                continue

            keep_points.append(points[i])
            index_remap[i] = len(keep_points) - 1
            for j in range(i + 1, len(points)):
                if Gf.IsClose(points[j], points[i], 1e-6):
                    keep[j] = False
                    index_remap[j] = len(keep_points) - 1

        for i in range(len(face_indices)):
            face_indices[i] = index_remap[face_indices[i]]

        return keep_points, normals, sts, face_indices, face_vertex_counts

    @staticmethod
    def build_setting_ui():
        from omni import ui
        CubeEvaluator._half_scale_slider = build_int_slider(
            "Object Half Scale", CubeEvaluator.SETTING_OBJECT_HALF_SCALE, 50, 10, 1000
        )
        ui.Spacer(height=5)

        CubeEvaluator._u_scale_slider = build_int_slider(
            "U Verts Scale", CubeEvaluator.SETTING_U_SCALE, 1, 1, 10,
            "Tessellation Level along X Axis"
        )
        ui.Spacer(height=5)

        CubeEvaluator._v_scale_slider = build_int_slider(
            "V Verts Scale", CubeEvaluator.SETTING_V_SCALE, 1, 1, 10,
            "Tessellation Level along Y Axis"
        )
        ui.Spacer(height=5)

        CubeEvaluator._w_scale_slider = build_int_slider(
            "W Verts Scale", CubeEvaluator.SETTING_W_SCALE, 1, 1, 10,
            "Tessellation Level along Z Axis"
        )

    @staticmethod
    def reset_setting():
        CubeEvaluator._half_scale_slider.set_value(CubeEvaluator.get_default_half_scale())
        CubeEvaluator._u_scale_slider.set_value(1)
        CubeEvaluator._v_scale_slider.set_value(1)
        CubeEvaluator._w_scale_slider.set_value(1)

    @staticmethod
    def get_default_half_scale():
        half_scale = get_int_setting(CubeEvaluator.SETTING_OBJECT_HALF_SCALE, 50)

        return half_scale
