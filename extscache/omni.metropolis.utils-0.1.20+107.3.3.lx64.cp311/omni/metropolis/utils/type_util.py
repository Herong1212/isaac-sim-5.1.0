import re
import carb
from pxr import Gf

"""
------------------------Conversion Utility for Different Data Type------------------------
"""


class TypeUtil:

    @staticmethod
    def carb_float3_to_gf_vec3d(float3: carb.Float3):
        return Gf.Vec3d(float3[0], float3[1], float3[2])

    @staticmethod
    def carb_float4_to_gf_quatd(float4: carb.Float4):
        quat = Gf.Quatd()
        quat.SetReal(float4[3])
        quat.SetImaginary(float4[0], float4[1], float4[2])
        return quat

    @staticmethod
    def gf_quatd_to_carb_float4(quatd: Gf.Quatd):
        gf_i = quatd.GetImaginary()
        return carb.Float4(gf_i[0], gf_i[1], gf_i[2], quatd.GetReal())

    @staticmethod
    def gf_vec3_to_carb_float3(vec3: Gf.Vec3d):
        return carb.Float3(vec3[0], vec3[1], vec3[2])

    @staticmethod
    def str_to_carb_float3(s: str) -> carb.Float3:
        """Parse a string of (x, y, z) into carb.Float3. Return None if parsing fails."""
        p = re.compile(r"\(([+|-]?\d*(\.\d*)?\s*\,\s*[+|-]?\d*(\.\d*)?\s*\,\s*[+|-]?\d*(\.\d*)?)\)")
        m = p.fullmatch(s)
        if not m:
            carb.log_warn(f"String \'{s}\' is not a valid Float3 stirng. Convert to Float3 fails.")
            return None
        nums = s.replace(" ", "").replace("(", "").replace(")", "").split(",")
        return carb.Float3(float(nums[0]), float(nums[1]), float(nums[2]))
