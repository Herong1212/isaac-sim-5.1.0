import usdrt
from pxr import Gf, Sdf


def convert_usdrt_to_usd(value):
    if value is None:
        return value
    if isinstance(value, usdrt.Sdf.Path):
        return Sdf.Path(value.pathString)
    if isinstance(value, usdrt.Sdf.AssetPath):
        return Sdf.AssetPath(value.path)
    if isinstance(value, usdrt.Gf.Vec3d):
        return Gf.Vec3d(value[0], value[1], value[2])
    if isinstance(value, usdrt.Gf.Vec3f):
        return Gf.Vec3f(value[0], value[1], value[2])
    if isinstance(value, usdrt.Gf.Vec3h):
        return Gf.Vec3h(value[0], value[1], value[2])
    if isinstance(value, usdrt.Gf.Vec3i):
        return Gf.Vec3i(value[0], value[1], value[2])
    if isinstance(value, usdrt.Gf.Vec2d):
        return Gf.Vec2d(value[0], value[1])
    if isinstance(value, usdrt.Gf.Vec2f):
        return Gf.Vec2f(value[0], value[1])
    if isinstance(value, usdrt.Gf.Vec2h):
        return Gf.Vec2h(value[0], value[1])
    if isinstance(value, usdrt.Gf.Vec2i):
        return Gf.Vec2i(value[0], value[1])
    if isinstance(value, usdrt.Gf.Vec4d):
        return Gf.Vec4d(value[0], value[1], value[2], value[3])
    if isinstance(value, usdrt.Gf.Vec4f):
        return Gf.Vec4f(value[0], value[1], value[2], value[3])
    if isinstance(value, usdrt.Gf.Vec4h):
        return Gf.Vec4h(value[0], value[1], value[2], value[3])
    if isinstance(value, usdrt.Gf.Vec4i):
        return Gf.Vec4i(value[0], value[1], value[2], value[3])
    if isinstance(value, usdrt.Gf.Transform):
        return Gf.Transform(
            value[0],
            value[1],
            value[2],
            value[3],
            value[4],
            value[5],
            value[6],
            value[7],
            value[8],
            value[9],
            value[10],
            value[11],
            value[12],
            value[13],
            value[14],
            value[15],
        )
    if isinstance(value, usdrt.Gf.Rotation):
        return Gf.Rotation(value.angle, Gf.Vec3d(value.axis[0], value.axis[1], value.axis[2]))
    if isinstance(value, usdrt.Gf.Quatd):
        return Gf.Quatd(value.real, Gf.Vec3d(value.imaginary[0], value.imaginary[1], value.imaginary[2]))
    if isinstance(value, usdrt.Gf.Quatf):
        return Gf.Quatf(value.real, Gf.Vec3f(value.imaginary[0], value.imaginary[1], value.imaginary[2]))
    if isinstance(value, usdrt.Gf.Quath):
        return Gf.Quath(value.real, Gf.Vec3h(value.imaginary[0], value.imaginary[1], value.imaginary[2]))
    if isinstance(value, usdrt.Gf.Range1d):
        return Gf.Range1d(value.min, value.max)
    if isinstance(value, usdrt.Gf.Range1f):
        return Gf.Range1f(value.min, value.max)
    if isinstance(value, usdrt.Gf.Range2d):
        return Gf.Range2d(Gf.Vec2d(value.min[0], value.min[1]), Gf.Vec2d(value.max[0], value.max[1]))
    if isinstance(value, usdrt.Gf.Range2f):
        return Gf.Range2f(Gf.Vec2f(value.min[0], value.min[1]), Gf.Vec2f(value.max[0], value.max[1]))
    if isinstance(value, usdrt.Gf.Range3d):
        return Gf.Range3d(
            Gf.Vec3d(value.min[0], value.min[1], value.min[2]), Gf.Vec3d(value.max[0], value.max[1], value.max[2])
        )
    if isinstance(value, usdrt.Gf.Range3f):
        return Gf.Range3f(
            Gf.Vec3f(value.min[0], value.min[1], value.min[2]), Gf.Vec3f(value.max[0], value.max[1], value.max[2])
        )
    if isinstance(value, usdrt.Gf.Matrix2d):
        return Gf.Matrix2d(value[0], value[1], value[2], value[3])
    if isinstance(value, usdrt.Gf.Matrix2f):
        return Gf.Matrix2f(value[0], value[1], value[2], value[3])
    if isinstance(value, usdrt.Gf.Matrix3d):
        return Gf.Matrix3d(
            value[0][0],
            value[0][1],
            value[0][2],
            value[1][0],
            value[1][1],
            value[1][2],
            value[2][0],
            value[2][1],
            value[2][2],
        )
    if isinstance(value, usdrt.Gf.Matrix3f):
        return Gf.Matrix3f(
            value[0][0],
            value[0][1],
            value[0][2],
            value[1][0],
            value[1][1],
            value[1][2],
            value[2][0],
            value[2][1],
            value[2][2],
        )
    if isinstance(value, usdrt.Gf.Matrix4d):
        return Gf.Matrix4d(
            value[0][0],
            value[0][1],
            value[0][2],
            value[0][3],
            value[1][0],
            value[1][1],
            value[1][2],
            value[1][3],
            value[2][0],
            value[2][1],
            value[2][2],
            value[2][3],
            value[3][0],
            value[3][1],
            value[3][2],
            value[3][3],
        )
    if isinstance(value, usdrt.Gf.Matrix4f):
        return Gf.Matrix4f(
            value[0][0],
            value[0][1],
            value[0][2],
            value[0][3],
            value[1][0],
            value[1][1],
            value[1][2],
            value[1][3],
            value[2][0],
            value[2][1],
            value[2][2],
            value[2][3],
            value[3][0],
            value[3][1],
            value[3][2],
            value[3][3],
        )
    if isinstance(value, usdrt.Vt.AssetArray):
        vec = []
        for v in value:
            vec.append(Sdf.AssetPath(v.path, v.resolvedPath))
        return Sdf.AssetPathArray(vec)
    if isinstance(value, list):
        vec = []
        for v in value:
            vec.append(convert_usdrt_to_usd(v))
        return vec

    return value
