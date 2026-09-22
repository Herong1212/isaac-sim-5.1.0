import math
import numpy as np
from pxr import Gf


# TODO METROPERF-822: Add use comments and consider reorganizing util functions to different util classes
class RotationUtil:
    @staticmethod
    def get_trig(deg):
        rad = math.radians(deg)
        return math.cos(rad), math.sin(rad)

    @staticmethod
    def rot_x(deg):
        c, s = RotationUtil.get_trig(deg)
        return Gf.Matrix3d(1, 0, 0, 0, c, s, 0, -s, c)

    @staticmethod
    def rot_y(deg):
        c, s = RotationUtil.get_trig(deg)
        return Gf.Matrix3d(c, 0, -s, 0, 1, 0, s, 0, c)

    @staticmethod
    def rot_z(deg):
        c, s = RotationUtil.get_trig(deg)
        return Gf.Matrix3d(c, s, 0, -s, c, 0, 0, 0, 1)

    @staticmethod
    def rot_x_np(deg):
        c, s = RotationUtil.get_trig(deg)
        return np.array([[1, 0, 0], [0, c, s], [0, -s, c]])

    @staticmethod
    def rot_y_np(deg):
        c, s = RotationUtil.get_trig(deg)
        return np.array([[c, 0, -s], [0, 1, 0], [s, 0, c]])

    @staticmethod
    def rot_z_np(deg):
        c, s = RotationUtil.get_trig(deg)
        return np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]])

    @staticmethod
    def quat_to_mat3(q):
        w = q.GetReal()
        x = q.GetImaginary()[0]
        y = q.GetImaginary()[1]
        z = q.GetImaginary()[2]

        sqw = w * w
        sqx = x * x
        sqy = y * y
        sqz = z * z

        invs = 1 / (sqx + sqy + sqz + sqw)
        m00 = (sqx - sqy - sqz + sqw) * invs
        m11 = (-sqx + sqy - sqz + sqw) * invs
        m22 = (-sqx - sqy + sqz + sqw) * invs

        tmp1 = x * y
        tmp2 = z * w
        m10 = 2.0 * (tmp1 + tmp2) * invs
        m01 = 2.0 * (tmp1 - tmp2) * invs

        tmp1 = x * z
        tmp2 = y * w
        m20 = 2.0 * (tmp1 - tmp2) * invs
        m02 = 2.0 * (tmp1 + tmp2) * invs
        tmp1 = y * z
        tmp2 = x * w
        m21 = 2.0 * (tmp1 + tmp2) * invs
        m12 = 2.0 * (tmp1 - tmp2) * invs
        m = Gf.Matrix3d(m00, m01, m02, m10, m11, m12, m20, m21, m22)
        return m.GetTranspose()

    @staticmethod
    def xyz_from_mat3(_r):
        r = _r.GetTranspose()
        if r[2][0] != -1 and r[2][0] != 1:
            theta = -math.asin(r[2][0])
            psi = math.atan2(r[2][1], r[2][2])
            phi = math.atan2(r[1][0], r[0][0])
        else:
            phi = 0
            if r[2][0] == -1:
                theta = math.pi / 2
                psi = phi + math.atan2(r[0][1], r[0][2])
            else:
                theta = -math.pi / 2
                psi = -phi + math.atan2(-r[0][1], -r[0][2])
        return Gf.Vec3d(math.degrees(psi), math.degrees(theta), math.degrees(phi))

    @staticmethod
    def yxz_from_mat3(r):
        if r[1][2] != -1 and r[1][2] != 1:
            x = math.asin(r[1][2])
            y = math.atan2(-r[0][2], r[2][2])
            z = math.atan2(-r[1][0], r[1][1])
        else:
            z = 0
            if r[1][2] == -1:
                x = -math.pi / 2
                y = math.atan2(-r[0][1], r[2][1])
                z = 0  #
            else:
                x = math.pi / 2
                y = 0  #
                z = math.atan2(r[0][1], -r[2][1])
        return Gf.Vec3d(math.degrees(x), math.degrees(y), math.degrees(z))

    # TODO: xyz a misnomer? Should this be "rotation"?
    @staticmethod
    def get_xlate_and_xyz_from_xform(xform):
        xlate = xform.ExtractTranslation()
        rotation = xform.ExtractRotation()
        mat3 = RotationUtil.quat_to_mat3(rotation.GetQuat())
        xyz = RotationUtil.xyz_from_mat3(mat3)
        return xlate, xyz

    @staticmethod
    def get_xlate_and_yxz_from_xform(xform):
        xlate = xform.ExtractTranslation()
        rotation = xform.ExtractRotation()
        mat3 = RotationUtil.quat_to_mat3(rotation.GetQuat())
        yxz = RotationUtil.yxz_from_mat3(mat3)
        return xlate, yxz
