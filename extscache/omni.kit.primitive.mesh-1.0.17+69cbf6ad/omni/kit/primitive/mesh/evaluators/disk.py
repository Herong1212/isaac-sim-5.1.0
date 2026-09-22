from .utils import get_int_setting, build_int_slider
from .utils import generate_disk
from .abstract_shape_evaluator import AbstractShapeEvaluator
from pxr import Gf


class DiskEvaluator(AbstractShapeEvaluator):
    SETTING_OBJECT_HALF_SCALE = "/persistent/app/mesh_generator/shapes/disk/object_half_scale"
    SETTING_U_SCALE = "/persistent/app/mesh_generator/shapes/disk/u_scale"
    SETTING_V_SCALE = "/persistent/app/mesh_generator/shapes/disk/v_scale"

    def __init__(self, attributes: dict):
        super().__init__(attributes)

    def eval(self, **kwargs):
        half_scale = kwargs.get("half_scale", None)
        if half_scale is None or half_scale <= 0:
            half_scale = self.get_default_half_scale()

        num_u_verts_scale = kwargs.get("u_verts_scale", None)
        if num_u_verts_scale is None or num_u_verts_scale <= 0:
            num_u_verts_scale = get_int_setting(DiskEvaluator.SETTING_U_SCALE, 1)

        num_v_verts_scale = kwargs.get("v_verts_scale", None)
        if num_v_verts_scale is None or num_v_verts_scale <= 0:
            num_v_verts_scale = get_int_setting(DiskEvaluator.SETTING_V_SCALE, 1)

        up_axis = kwargs.get("up_axis", "Y")
        origin = Gf.Vec3f(0.0)

        # Disk will be approximated by quads composed from inner circle
        # to outer circle. The parameter `u_patches` means the segments
        # of circle. And v_patches means the number of segments (circles)
        # in radius direction.
        u_patches = kwargs.get("u_patches", 32)
        v_patches = kwargs.get("v_patches", 1)

        num_u_verts_scale = max(num_u_verts_scale, 1)
        num_v_verts_scale = max(num_v_verts_scale, 1)
        u_patches = u_patches * num_u_verts_scale
        v_patches = v_patches * num_v_verts_scale
        u_patches = max(int(u_patches), 3)
        v_patches = max(int(v_patches), 1)

        center_point = Gf.Vec3f(0.0)
        return generate_disk(center_point, u_patches, v_patches, origin, half_scale, up_axis)

    @staticmethod
    def build_setting_ui():
        from omni import ui
        DiskEvaluator._half_scale_slider = build_int_slider(
            "Object Half Scale", DiskEvaluator.SETTING_OBJECT_HALF_SCALE, 50, 10, 1000
        )
        ui.Spacer(height=5)

        DiskEvaluator._u_scale_slider = build_int_slider("U Verts Scale", DiskEvaluator.SETTING_U_SCALE, 1, 1, 10)
        ui.Spacer(height=5)

        DiskEvaluator._v_scale_slider = build_int_slider("V Verts Scale", DiskEvaluator.SETTING_V_SCALE, 1, 1, 10)

    @staticmethod
    def reset_setting():
        DiskEvaluator._half_scale_slider.set_value(DiskEvaluator.get_default_half_scale())
        DiskEvaluator._u_scale_slider.set_value(1)
        DiskEvaluator._v_scale_slider.set_value(1)
    
    @staticmethod
    def get_default_half_scale():
        half_scale = get_int_setting(DiskEvaluator.SETTING_OBJECT_HALF_SCALE, 50)

        return half_scale
