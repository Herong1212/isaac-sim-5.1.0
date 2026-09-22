"""A few helpers for supporting Fabric Scene Delegate being enabled or not in tests.
   Once FSD is always enabled, we can remove this.
"""

import carb.settings as settings
import omni.usd
from pxr import Gf, Usd, UsdGeom
from usdrt import Gf as GfRT
from usdrt import Usd as UsdRT


# ------------------------------------------------------------------------
def get_stage_rt() -> UsdRT.Stage:
    return UsdRT.Stage.Attach(omni.usd.get_context().get_stage_id())


# ------------------------------------------------------------------------
def use_fsd() -> bool:
    return settings.get_settings().get_as_bool("/app/useFabricSceneDelegate")


# ------------------------------------------------------------------------
def get_transform(src: Usd.Prim, world_space=False) -> Gf.Matrix4d:
    """Helper to get the transform of a prim, accounting for FSD being enabled"""
    if use_fsd():
        if world_space:
            return (
                get_stage_rt().GetPrimAtPath(src.GetPrimPath().pathString).GetAttribute("omni:fabric:worldMatrix").Get()
            )
        return get_stage_rt().GetPrimAtPath(src.GetPrimPath().pathString).GetAttribute("omni:fabric:localMatrix").Get()
    xform_cache = UsdGeom.XformCache()
    if world_space:
        return xform_cache.GetLocalToWorldTransform(src)
    return xform_cache.GetLocalTransformation(src)[0]


# ------------------------------------------------------------------------
def get_translation(src: Usd.Prim, world_space=False) -> Gf.Vec3d:
    """Helper to get the translation of a prim, accounting for FSD being enabled"""
    xform = get_transform(src, world_space)
    return xform.ExtractTranslation()


# ------------------------------------------------------------------------
def get_rotation(src: Usd.Prim, world_space=False) -> Gf.Rotation:
    """Helper to extract the rotation of a prim, accounting for FSD being enabled"""
    xform = get_transform(src, world_space)
    return xform.GetOrthonormalized().ExtractRotation()


# ------------------------------------------------------------------------
def get_rotation_xyz(src: Usd.Prim, world_space=False) -> Gf.Vec3f:
    """Helper to get the rotation of a prim, accounting for FSD being enabled"""
    rotation = get_rotation(src, world_space)
    if use_fsd():
        angles = rotation.Decompose(GfRT.Vec3d.ZAxis(), GfRT.Vec3d.YAxis(), GfRT.Vec3d.XAxis())
        return GfRT.Vec3f(angles[2], angles[1], angles[0])
    angles = rotation.Decompose(Gf.Vec3d.ZAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.XAxis())
    return Gf.Vec3f(angles[2], angles[1], angles[0])


# ------------------------------------------------------------------------
def is_close(a, b, tolerance):
    """Wrapper for Gf.IsClose. When mixing modules, put the GfRT object first."""
    if settings.get_settings().get_as_bool("/app/useFabricSceneDelegate"):
        if isinstance(a, Gf.Matrix4d):
            rt_obj = GfRT.Matrix4d()
            for i in range(4):
                rt_obj.SetRow(i, list(a.GetRow(i)))
            a = rt_obj
        elif isinstance(a, Gf.Vec3d):
            a = GfRT.Vec3d(a[0], a[1], a[2])
        return GfRT.IsClose(a, b, tolerance)
    return Gf.IsClose(a, b, tolerance)
