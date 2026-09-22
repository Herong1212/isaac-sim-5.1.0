from __future__ import annotations
import pxr.Gf._gf
import typing
import Boost.Python
import pxr.Gf

__all__ = [
    "Abs",
    "Absf",
    "ApplyGamma",
    "BBox3d",
    "Camera",
    "Ceil",
    "Ceilf",
    "Clamp",
    "Clampf",
    "CompDiv",
    "CompMult",
    "ConvertDisplayToLinear",
    "ConvertLinearToDisplay",
    "Cross",
    "DegreesToRadians",
    "Dot",
    "DualQuatd",
    "DualQuatf",
    "DualQuath",
    "Exp",
    "Expf",
    "FindClosestPoints",
    "FitPlaneToPoints",
    "Floor",
    "Floorf",
    "Frustum",
    "GetComplement",
    "GetDisplayGamma",
    "GetHomogenized",
    "GetLength",
    "GetNormalized",
    "GetProjection",
    "HomogeneousCross",
    "Interval",
    "IsClose",
    "Lerp",
    "Lerpf",
    "Line",
    "LineSeg",
    "Log",
    "Logf",
    "MIN_ORTHO_TOLERANCE",
    "MIN_VECTOR_LENGTH",
    "Matrix2d",
    "Matrix2f",
    "Matrix3d",
    "Matrix3f",
    "Matrix4d",
    "Matrix4f",
    "Max",
    "Min",
    "Mod",
    "Modf",
    "MultiInterval",
    "Normalize",
    "Plane",
    "Pow",
    "Powf",
    "Project",
    "Quatd",
    "Quaternion",
    "Quatf",
    "Quath",
    "RadiansToDegrees",
    "Range1d",
    "Range1f",
    "Range2d",
    "Range2f",
    "Range3d",
    "Range3f",
    "Ray",
    "Rect2i",
    "Rotation",
    "Round",
    "Roundf",
    "Sgn",
    "Size2",
    "Size3",
    "Slerp",
    "Sqr",
    "Sqrt",
    "Sqrtf",
    "Transform",
    "Vec2d",
    "Vec2f",
    "Vec2h",
    "Vec2i",
    "Vec3d",
    "Vec3f",
    "Vec3h",
    "Vec3i",
    "Vec4d",
    "Vec4f",
    "Vec4h",
    "Vec4i"
]


class BBox3d(Boost.Python.instance):
    """
    Arbitrarily oriented 3D bounding box
    """
    @staticmethod
    def Combine(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ComputeAlignedBox(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ComputeAlignedRange(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ComputeCentroid(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetBox(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetInverseMatrix(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMatrix(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetRange(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetVolume(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def HasZeroAreaPrimitives(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Set(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetHasZeroAreaPrimitives(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetMatrix(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetRange(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Transform(*args, **kwargs) -> typing.Any: ...
    @property
    def box(self) -> None:
        """
        :type: None
        """
    @property
    def hasZeroAreaPrimitives(self) -> None:
        """
        :type: None
        """
    @property
    def matrix(self) -> None:
        """
        :type: None
        """
    __instance_size__ = 336
    pass
class Camera(Boost.Python.instance):
    class FOVDirection(pxr.Tf.Tf_PyEnumWrapper, pxr.Tf.Enum, Boost.Python.instance):
        @staticmethod
        def GetValueFromName(*args, **kwargs) -> typing.Any: ...
        _baseName = 'Camera'
        allValues: tuple # value = (Gf.Camera.FOVHorizontal, Gf.Camera.FOVVertical)
        pass
    class Projection(pxr.Tf.Tf_PyEnumWrapper, pxr.Tf.Enum, Boost.Python.instance):
        @staticmethod
        def GetValueFromName(*args, **kwargs) -> typing.Any: ...
        _baseName = 'Camera'
        allValues: tuple # value = (Gf.Camera.Perspective, Gf.Camera.Orthographic)
        pass
    @staticmethod
    def GetFieldOfView(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetFromViewAndProjectionMatrix(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetOrthographicFromAspectRatioAndSize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetPerspectiveFromAspectRatioAndFieldOfView(*args, **kwargs) -> typing.Any: ...
    @property
    def aspectRatio(self) -> None:
        """
        :type: None
        """
    @property
    def clippingPlanes(self) -> None:
        """
        :type: None
        """
    @property
    def clippingRange(self) -> None:
        """
        :type: None
        """
    @property
    def fStop(self) -> None:
        """
        :type: None
        """
    @property
    def focalLength(self) -> None:
        """
        :type: None
        """
    @property
    def focusDistance(self) -> None:
        """
        :type: None
        """
    @property
    def frustum(self) -> None:
        """
        :type: None
        """
    @property
    def horizontalAperture(self) -> None:
        """
        :type: None
        """
    @property
    def horizontalApertureOffset(self) -> None:
        """
        :type: None
        """
    @property
    def horizontalFieldOfView(self) -> None:
        """
        :type: None
        """
    @property
    def projection(self) -> None:
        """
        :type: None
        """
    @property
    def transform(self) -> None:
        """
        :type: None
        """
    @property
    def verticalAperture(self) -> None:
        """
        :type: None
        """
    @property
    def verticalApertureOffset(self) -> None:
        """
        :type: None
        """
    @property
    def verticalFieldOfView(self) -> None:
        """
        :type: None
        """
    APERTURE_UNIT = 0.1
    DEFAULT_HORIZONTAL_APERTURE = 20.955
    DEFAULT_VERTICAL_APERTURE = 15.290799999999999
    FOCAL_LENGTH_UNIT = 0.1
    FOVHorizontal: pxr.Gf.FOVDirection # value = Gf.Camera.FOVHorizontal
    FOVVertical: pxr.Gf.FOVDirection # value = Gf.Camera.FOVVertical
    Orthographic: pxr.Gf.Projection # value = Gf.Camera.Orthographic
    Perspective: pxr.Gf.Projection # value = Gf.Camera.Perspective
    __instance_size__ = 216
    pass
class DualQuatd(Boost.Python.instance):
    @staticmethod
    def GetConjugate(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDual(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetIdentity(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetInverse(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetLength(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNormalized(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetReal(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetTranslation(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetZero(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Normalize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetDual(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetReal(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetTranslation(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Transform(*args, **kwargs) -> typing.Any: ...
    @property
    def dual(self) -> None:
        """
        :type: None
        """
    @property
    def real(self) -> None:
        """
        :type: None
        """
    pass
class DualQuatf(Boost.Python.instance):
    @staticmethod
    def GetConjugate(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDual(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetIdentity(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetInverse(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetLength(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNormalized(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetReal(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetTranslation(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetZero(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Normalize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetDual(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetReal(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetTranslation(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Transform(*args, **kwargs) -> typing.Any: ...
    @property
    def dual(self) -> None:
        """
        :type: None
        """
    @property
    def real(self) -> None:
        """
        :type: None
        """
    pass
class DualQuath(Boost.Python.instance):
    @staticmethod
    def GetConjugate(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDual(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetIdentity(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetInverse(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetLength(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNormalized(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetReal(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetTranslation(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetZero(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Normalize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetDual(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetReal(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetTranslation(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Transform(*args, **kwargs) -> typing.Any: ...
    @property
    def dual(self) -> None:
        """
        :type: None
        """
    @property
    def real(self) -> None:
        """
        :type: None
        """
    pass
class Frustum(Boost.Python.instance):
    """
    Basic view frustum
    """
    class ProjectionType(pxr.Tf.Tf_PyEnumWrapper, pxr.Tf.Enum, Boost.Python.instance):
        @staticmethod
        def GetValueFromName(*args, **kwargs) -> typing.Any: ...
        _baseName = 'Frustum'
        allValues: tuple # value = (Gf.Frustum.Orthographic, Gf.Frustum.Perspective)
        pass
    @staticmethod
    def ComputeAspectRatio(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ComputeCorners(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ComputeCornersAtDistance(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ComputeLookAtPoint(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ComputeNarrowedFrustum(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ComputePickRay(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ComputeProjectionMatrix(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ComputeUpVector(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ComputeViewDirection(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ComputeViewFrame(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ComputeViewInverse(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ComputeViewMatrix(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def FitToSphere(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetFOV(*args, **kwargs) -> typing.Any: 
        """
        Returns the horizontal fov of the frustum. The fov of the
        frustum is not necessarily the same value as displayed in
        the viewer. The displayed fov is a function of the focal
        length or FOV avar. The frustum's fov may be different due
        to things like lens breathing.

        If the frustum is not of type GfFrustum::Perspective, the
        returned FOV will be 0.0.
        """
    @staticmethod
    def GetNearFar(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetOrthographic(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetPerspective(*args, **kwargs) -> typing.Any: 
        """
        Returns the current perspective frustum values suitable
        for use by SetPerspective.  If the current frustum is a
        perspective projection, the return value is a tuple of
        fieldOfView, aspectRatio, nearDistance, farDistance).
        If the current frustum is not perspective, the return
        value is None.
        """
    @staticmethod
    def GetPosition(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetProjectionType(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetReferencePlaneDepth(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetRotation(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetViewDistance(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetWindow(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Intersects(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IntersectsViewVolume(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetNearFar(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetOrthographic(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetPerspective(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetPosition(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetPositionAndRotationFromMatrix(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetProjectionType(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetRotation(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetViewDistance(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetWindow(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Transform(*args, **kwargs) -> typing.Any: ...
    @property
    def nearFar(self) -> None:
        """
        :type: None
        """
    @property
    def position(self) -> None:
        """
        :type: None
        """
    @property
    def projectionType(self) -> None:
        """
        :type: None
        """
    @property
    def rotation(self) -> None:
        """
        :type: None
        """
    @property
    def viewDistance(self) -> None:
        """
        :type: None
        """
    @property
    def window(self) -> None:
        """
        :type: None
        """
    Orthographic: pxr.Gf.ProjectionType # value = Gf.Frustum.Orthographic
    Perspective: pxr.Gf.ProjectionType # value = Gf.Frustum.Perspective
    __instance_size__ = 152
    pass
class Interval(Boost.Python.instance):
    """
    Basic mathematical interval class
    """
    @staticmethod
    def Contains(*args, **kwargs) -> typing.Any: 
        """
        Returns true if x is inside the interval.

        Returns true if x is inside the interval.
        """
    @staticmethod
    def GetFullInterval(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMax(*args, **kwargs) -> typing.Any: 
        """
        Get the maximum value.
        """
    @staticmethod
    def GetMin(*args, **kwargs) -> typing.Any: 
        """
        Get the minimum value.
        """
    @staticmethod
    def GetSize(*args, **kwargs) -> typing.Any: 
        """
        The width of the interval
        """
    @staticmethod
    def In(*args, **kwargs) -> typing.Any: 
        """
        Returns true if x is inside the interval.
        """
    @staticmethod
    def Intersects(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsEmpty(*args, **kwargs) -> typing.Any: 
        """
        True if the interval is empty.
        """
    @staticmethod
    def IsFinite(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsMaxClosed(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsMaxFinite(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsMaxOpen(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsMinClosed(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsMinFinite(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsMinOpen(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetMax(*args, **kwargs) -> typing.Any: 
        """
        Set the maximum value.

        Set the maximum value and boundary condition.
        """
    @staticmethod
    def SetMin(*args, **kwargs) -> typing.Any: 
        """
        Set the minimum value.

        Set the minimum value and boundary condition.
        """
    @property
    def finite(self) -> None:
        """
        :type: None
        """
    @property
    def isEmpty(self) -> None:
        """
        True if the interval is empty.

        :type: None
        """
    @property
    def max(self) -> None:
        """
        The maximum value.

        :type: None
        """
    @property
    def maxClosed(self) -> None:
        """
        :type: None
        """
    @property
    def maxFinite(self) -> None:
        """
        :type: None
        """
    @property
    def maxOpen(self) -> None:
        """
        :type: None
        """
    @property
    def min(self) -> None:
        """
        The minimum value.

        :type: None
        """
    @property
    def minClosed(self) -> None:
        """
        :type: None
        """
    @property
    def minFinite(self) -> None:
        """
        :type: None
        """
    @property
    def minOpen(self) -> None:
        """
        :type: None
        """
    @property
    def size(self) -> None:
        """
        The width of the interval.

        :type: None
        """
    __instance_size__ = 56
    pass
class Line(Boost.Python.instance):
    """
    Line class
    """
    @staticmethod
    def FindClosestPoint(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDirection(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetPoint(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Set(*args, **kwargs) -> typing.Any: ...
    @property
    def direction(self) -> None:
        """
        :type: None
        """
    __instance_size__ = 72
    pass
class LineSeg(Boost.Python.instance):
    """
    Line segment class
    """
    @staticmethod
    def FindClosestPoint(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDirection(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetLength(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetPoint(*args, **kwargs) -> typing.Any: ...
    @property
    def direction(self) -> None:
        """
        :type: None
        """
    @property
    def length(self) -> None:
        """
        :type: None
        """
    __instance_size__ = 80
    pass
class Matrix2d(Boost.Python.instance):
    @staticmethod
    def GetColumn(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDeterminant(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetInverse(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetRow(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetTranspose(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Set(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetColumn(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetDiagonal(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetIdentity(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetRow(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetZero(*args, **kwargs) -> typing.Any: ...
    __safe_for_unpickling__ = True
    dimension = (2, 2)
    pass
class Matrix2f(Boost.Python.instance):
    @staticmethod
    def GetColumn(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDeterminant(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetInverse(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetRow(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetTranspose(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Set(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetColumn(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetDiagonal(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetIdentity(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetRow(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetZero(*args, **kwargs) -> typing.Any: ...
    __safe_for_unpickling__ = True
    dimension = (2, 2)
    pass
class Matrix3d(Boost.Python.instance):
    @staticmethod
    def ExtractRotation(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetColumn(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDeterminant(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetHandedness(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetInverse(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetOrthonormalized(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetRow(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetTranspose(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsLeftHanded(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsRightHanded(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Orthonormalize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Set(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetColumn(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetDiagonal(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetIdentity(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetRotate(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetRow(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetScale(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetZero(*args, **kwargs) -> typing.Any: ...
    __safe_for_unpickling__ = True
    dimension = (3, 3)
    pass
class Matrix3f(Boost.Python.instance):
    @staticmethod
    def ExtractRotation(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetColumn(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDeterminant(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetHandedness(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetInverse(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetOrthonormalized(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetRow(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetTranspose(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsLeftHanded(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsRightHanded(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Orthonormalize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Set(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetColumn(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetDiagonal(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetIdentity(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetRotate(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetRow(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetScale(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetZero(*args, **kwargs) -> typing.Any: ...
    __safe_for_unpickling__ = True
    dimension = (3, 3)
    pass
class Matrix4d(Boost.Python.instance):
    @staticmethod
    def ExtractRotation(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ExtractRotationMatrix(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ExtractRotationQuat(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ExtractTranslation(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Factor(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetColumn(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDeterminant(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDeterminant3(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetHandedness(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetInverse(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetOrthonormalized(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetRow(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetRow3(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetTranspose(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def HasOrthogonalRows3(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsLeftHanded(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsRightHanded(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Orthonormalize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def RemoveScaleShear(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Set(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetColumn(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetDiagonal(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetIdentity(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetLookAt(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetRotate(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetRotateOnly(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetRow(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetRow3(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetScale(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetTransform(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetTranslate(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetTranslateOnly(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetZero(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Transform(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def TransformAffine(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def TransformDir(*args, **kwargs) -> typing.Any: ...
    __safe_for_unpickling__ = True
    dimension = (4, 4)
    pass
class Matrix4f(Boost.Python.instance):
    @staticmethod
    def ExtractRotation(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ExtractRotationMatrix(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ExtractRotationQuat(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ExtractTranslation(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Factor(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetColumn(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDeterminant(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDeterminant3(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetHandedness(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetInverse(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetOrthonormalized(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetRow(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetRow3(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetTranspose(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def HasOrthogonalRows3(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsLeftHanded(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsRightHanded(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Orthonormalize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def RemoveScaleShear(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Set(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetColumn(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetDiagonal(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetIdentity(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetLookAt(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetRotate(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetRotateOnly(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetRow(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetRow3(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetScale(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetTransform(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetTranslate(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetTranslateOnly(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetZero(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Transform(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def TransformAffine(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def TransformDir(*args, **kwargs) -> typing.Any: ...
    __safe_for_unpickling__ = True
    dimension = (4, 4)
    pass
class MultiInterval(Boost.Python.instance):
    @staticmethod
    def Add(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ArithmeticAdd(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Clear(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Contains(*args, **kwargs) -> typing.Any: 
        """
        Returns true if x is inside the multi-interval.

        Returns true if x is inside the multi-interval.

        Returns true if x is inside the multi-interval.
        """
    @staticmethod
    def GetBounds(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetComplement(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetContainingInterval(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetFullInterval(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNextNonContainingInterval(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetPriorNonContainingInterval(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetSize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Intersect(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsEmpty(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Remove(*args, **kwargs) -> typing.Any: ...
    @property
    def bounds(self) -> None:
        """
        :type: None
        """
    @property
    def isEmpty(self) -> None:
        """
        :type: None
        """
    @property
    def size(self) -> None:
        """
        :type: None
        """
    __instance_size__ = 72
    pass
class Plane(Boost.Python.instance):
    @staticmethod
    def GetDistance(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDistanceFromOrigin(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetEquation(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNormal(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IntersectsPositiveHalfSpace(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Project(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Reorient(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Set(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Transform(*args, **kwargs) -> typing.Any: ...
    @property
    def distanceFromOrigin(self) -> None:
        """
        :type: None
        """
    @property
    def normal(self) -> None:
        """
        :type: None
        """
    __instance_size__ = 56
    pass
class Quatd(Boost.Python.instance):
    @staticmethod
    def GetConjugate(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetIdentity(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetImaginary(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetInverse(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetLength(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNormalized(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetReal(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetZero(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Normalize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetImaginary(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetReal(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Transform(*args, **kwargs) -> typing.Any: ...
    @property
    def imaginary(self) -> None:
        """
        :type: None
        """
    @property
    def real(self) -> None:
        """
        :type: None
        """
    pass
class Quaternion(Boost.Python.instance):
    """
    Quaternion class
    """
    @staticmethod
    def GetIdentity(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetImaginary(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetInverse(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetLength(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNormalized(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetReal(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetZero(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Normalize(*args, **kwargs) -> typing.Any: ...
    @property
    def imaginary(self) -> None:
        """
        :type: None
        """
    @property
    def real(self) -> None:
        """
        :type: None
        """
    __instance_size__ = 56
    pass
class Quatf(Boost.Python.instance):
    @staticmethod
    def GetConjugate(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetIdentity(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetImaginary(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetInverse(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetLength(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNormalized(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetReal(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetZero(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Normalize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetImaginary(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetReal(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Transform(*args, **kwargs) -> typing.Any: ...
    @property
    def imaginary(self) -> None:
        """
        :type: None
        """
    @property
    def real(self) -> None:
        """
        :type: None
        """
    pass
class Quath(Boost.Python.instance):
    @staticmethod
    def GetConjugate(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetIdentity(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetImaginary(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetInverse(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetLength(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNormalized(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetReal(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetZero(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Normalize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetImaginary(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetReal(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Transform(*args, **kwargs) -> typing.Any: ...
    @property
    def imaginary(self) -> None:
        """
        :type: None
        """
    @property
    def real(self) -> None:
        """
        :type: None
        """
    pass
class Range1d(Boost.Python.instance):
    @staticmethod
    def Contains(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDistanceSquared(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetIntersection(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMax(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMidpoint(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMin(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetSize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetUnion(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IntersectWith(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsEmpty(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetEmpty(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetMax(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetMin(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def UnionWith(*args, **kwargs) -> typing.Any: ...
    @property
    def max(self) -> None:
        """
        :type: None
        """
    @property
    def min(self) -> None:
        """
        :type: None
        """
    __instance_size__ = 40
    dimension = 1
    pass
class Range1f(Boost.Python.instance):
    @staticmethod
    def Contains(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDistanceSquared(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetIntersection(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMax(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMidpoint(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMin(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetSize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetUnion(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IntersectWith(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsEmpty(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetEmpty(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetMax(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetMin(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def UnionWith(*args, **kwargs) -> typing.Any: ...
    @property
    def max(self) -> None:
        """
        :type: None
        """
    @property
    def min(self) -> None:
        """
        :type: None
        """
    __instance_size__ = 32
    dimension = 1
    pass
class Range2d(Boost.Python.instance):
    @staticmethod
    def Contains(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetCorner(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDistanceSquared(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetIntersection(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMax(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMidpoint(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMin(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetQuadrant(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetSize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetUnion(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IntersectWith(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsEmpty(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetEmpty(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetMax(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetMin(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def UnionWith(*args, **kwargs) -> typing.Any: ...
    @property
    def max(self) -> None:
        """
        :type: None
        """
    @property
    def min(self) -> None:
        """
        :type: None
        """
    __instance_size__ = 56
    dimension = 2
    unitSquare: pxr.Gf.Range2d # value = Gf.Range2d(Gf.Vec2d(0.0, 0.0), Gf.Vec2d(1.0, 1.0))
    pass
class Range2f(Boost.Python.instance):
    @staticmethod
    def Contains(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetCorner(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDistanceSquared(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetIntersection(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMax(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMidpoint(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMin(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetQuadrant(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetSize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetUnion(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IntersectWith(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsEmpty(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetEmpty(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetMax(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetMin(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def UnionWith(*args, **kwargs) -> typing.Any: ...
    @property
    def max(self) -> None:
        """
        :type: None
        """
    @property
    def min(self) -> None:
        """
        :type: None
        """
    __instance_size__ = 40
    dimension = 2
    unitSquare: pxr.Gf.Range2f # value = Gf.Range2f(Gf.Vec2f(0.0, 0.0), Gf.Vec2f(1.0, 1.0))
    pass
class Range3d(Boost.Python.instance):
    @staticmethod
    def Contains(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetCorner(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDistanceSquared(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetIntersection(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMax(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMidpoint(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMin(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetOctant(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetSize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetUnion(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IntersectWith(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsEmpty(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetEmpty(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetMax(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetMin(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def UnionWith(*args, **kwargs) -> typing.Any: ...
    @property
    def max(self) -> None:
        """
        :type: None
        """
    @property
    def min(self) -> None:
        """
        :type: None
        """
    __instance_size__ = 72
    dimension = 3
    unitCube: pxr.Gf.Range3d # value = Gf.Range3d(Gf.Vec3d(0.0, 0.0, 0.0), Gf.Vec3d(1.0, 1.0, 1.0))
    pass
class Range3f(Boost.Python.instance):
    @staticmethod
    def Contains(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetCorner(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDistanceSquared(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetIntersection(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMax(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMidpoint(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMin(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetOctant(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetSize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetUnion(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IntersectWith(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsEmpty(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetEmpty(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetMax(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetMin(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def UnionWith(*args, **kwargs) -> typing.Any: ...
    @property
    def max(self) -> None:
        """
        :type: None
        """
    @property
    def min(self) -> None:
        """
        :type: None
        """
    __instance_size__ = 48
    dimension = 3
    unitCube: pxr.Gf.Range3f # value = Gf.Range3f(Gf.Vec3f(0.0, 0.0, 0.0), Gf.Vec3f(1.0, 1.0, 1.0))
    pass
class Ray(Boost.Python.instance):
    @staticmethod
    def FindClosestPoint(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetPoint(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Intersect(*args, **kwargs) -> typing.Any: 
        """
        Intersects the ray with the triangle formed by points p0,
        p1, and p2.  The first item in the tuple is true if the ray
        intersects the triangle. dist is the the parametric
        distance to the intersection point, the barycentric
        coordinates of the intersection point, and the front-facing
        flag. The barycentric coordinates are defined with respect
        to the three vertices taken in order.  The front-facing
        flag is True if the intersection hit the side of the
        triangle that is formed when the vertices are ordered
        counter-clockwise (right-hand rule).

        Barycentric coordinates are defined to sum to 1 and satisfy
        this relationsip:

            intersectionPoint = (barycentricCoords[0] * p0 +
                                 barycentricCoords[1] * p1 +
                                 barycentricCoords[2] * p2);
        ----------------------------------------------------------------------

        Intersects the ray with the Gf.Plane.  The first item in
        the returned tuple is true if the ray intersects the plane.
        dist is the parametric distance to the intersection point
        and frontfacing is true if the intersection is on the side
        of the plane toward which the plane's normal points.
        ----------------------------------------------------------------------

        Intersects the plane with an sphere. intersects is true if
        the ray intersects it at all within the sphere. If there is
        an intersection then enterDist and exitDist will be the
        parametric distances to the two intersection points.
        ----------------------------------------------------------------------

        Intersects the plane with an infinite cylinder. intersects
        is true if the ray intersects it at all within the
        sphere. If there is an intersection then enterDist and
        exitDist will be the parametric distances to the two
        intersection points.
        ----------------------------------------------------------------------

        Intersects the plane with an cylinder. intersects
        is true if the ray intersects it at all within the
        sphere. If there is an intersection then enterDist and
        exitDist will be the parametric distances to the two
        intersection points.
        ----------------------------------------------------------------------
        """
    @staticmethod
    def SetEnds(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetPointAndDirection(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Transform(*args, **kwargs) -> typing.Any: ...
    @property
    def direction(self) -> None:
        """
        :type: None
        """
    @property
    def startPoint(self) -> None:
        """
        :type: None
        """
    __instance_size__ = 72
    pass
class Rect2i(Boost.Python.instance):
    @staticmethod
    def Contains(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetArea(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetCenter(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetHeight(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetIntersection(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMax(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMaxX(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMaxY(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMin(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMinX(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMinY(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNormalized(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetSize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetUnion(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetWidth(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsEmpty(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsNull(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsValid(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetMax(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetMaxX(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetMaxY(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetMin(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetMinX(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetMinY(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Translate(*args, **kwargs) -> typing.Any: ...
    @property
    def max(self) -> None:
        """
        :type: None
        """
    @property
    def maxX(self) -> None:
        """
        :type: None
        """
    @property
    def maxY(self) -> None:
        """
        :type: None
        """
    @property
    def min(self) -> None:
        """
        :type: None
        """
    @property
    def minX(self) -> None:
        """
        :type: None
        """
    @property
    def minY(self) -> None:
        """
        :type: None
        """
    __instance_size__ = 40
    pass
class Rotation(Boost.Python.instance):
    """
    3-space rotation
    """
    @staticmethod
    def Decompose(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def DecomposeRotation(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def DecomposeRotation3(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetAngle(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetAxis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetInverse(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetQuat(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetQuaternion(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def MatchClosestEulerRotation(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def RotateOntoProjected(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetAxisAngle(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetIdentity(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetQuat(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetQuaternion(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetRotateInto(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def TransformDir(*args, **kwargs) -> typing.Any: ...
    @property
    def angle(self) -> None:
        """
        :type: None
        """
    @property
    def axis(self) -> None:
        """
        :type: None
        """
    __instance_size__ = 56
    pass
class Size2(Boost.Python.instance):
    """
    A 2D size class
    """
    @staticmethod
    def Set(*args, **kwargs) -> typing.Any: ...
    __instance_size__ = 40
    dimension = 2
    pass
class Size3(Boost.Python.instance):
    """
    A 3D size class
    """
    @staticmethod
    def Set(*args, **kwargs) -> typing.Any: ...
    __instance_size__ = 48
    dimension = 3
    pass
class Transform(Boost.Python.instance):
    @staticmethod
    def GetMatrix(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetPivotOrientation(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetPivotPosition(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetRotation(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetScale(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetTranslation(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Set(*args, **kwargs) -> typing.Any: 
        """
        Set method used by old 2x code. (Deprecated)
        """
    @staticmethod
    def SetIdentity(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetMatrix(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetPivotOrientation(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetPivotPosition(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetRotation(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetScale(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetTranslation(*args, **kwargs) -> typing.Any: ...
    @property
    def pivotOrientation(self) -> None:
        """
        :type: None
        """
    @property
    def pivotPosition(self) -> None:
        """
        :type: None
        """
    @property
    def rotation(self) -> None:
        """
        :type: None
        """
    @property
    def scale(self) -> None:
        """
        :type: None
        """
    @property
    def translation(self) -> None:
        """
        :type: None
        """
    __instance_size__ = 160
    pass
class Vec2d(Boost.Python.instance):
    @staticmethod
    def Axis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetComplement(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDot(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetLength(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNormalized(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetProjection(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Normalize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def XAxis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def YAxis(*args, **kwargs) -> typing.Any: ...
    __isGfVec = True
    __safe_for_unpickling__ = True
    dimension = 2
    pass
class Vec2f(Boost.Python.instance):
    @staticmethod
    def Axis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetComplement(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDot(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetLength(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNormalized(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetProjection(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Normalize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def XAxis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def YAxis(*args, **kwargs) -> typing.Any: ...
    __isGfVec = True
    __safe_for_unpickling__ = True
    dimension = 2
    pass
class Vec2h(Boost.Python.instance):
    @staticmethod
    def Axis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetComplement(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDot(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetLength(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNormalized(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetProjection(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Normalize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def XAxis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def YAxis(*args, **kwargs) -> typing.Any: ...
    __isGfVec = True
    __safe_for_unpickling__ = True
    dimension = 2
    pass
class Vec2i(Boost.Python.instance):
    @staticmethod
    def Axis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDot(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def XAxis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def YAxis(*args, **kwargs) -> typing.Any: ...
    __isGfVec = True
    __safe_for_unpickling__ = True
    dimension = 2
    pass
class Vec3d(Boost.Python.instance):
    @staticmethod
    def Axis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def BuildOrthonormalFrame(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetComplement(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetCross(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDot(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetLength(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNormalized(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetProjection(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Normalize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def OrthogonalizeBasis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def XAxis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def YAxis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ZAxis(*args, **kwargs) -> typing.Any: ...
    __isGfVec = True
    __safe_for_unpickling__ = True
    dimension = 3
    pass
class Vec3f(Boost.Python.instance):
    @staticmethod
    def Axis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def BuildOrthonormalFrame(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetComplement(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetCross(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDot(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetLength(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNormalized(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetProjection(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Normalize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def OrthogonalizeBasis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def XAxis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def YAxis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ZAxis(*args, **kwargs) -> typing.Any: ...
    __isGfVec = True
    __safe_for_unpickling__ = True
    dimension = 3
    pass
class Vec3h(Boost.Python.instance):
    @staticmethod
    def Axis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def BuildOrthonormalFrame(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetComplement(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetCross(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDot(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetLength(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNormalized(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetProjection(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Normalize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def OrthogonalizeBasis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def XAxis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def YAxis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ZAxis(*args, **kwargs) -> typing.Any: ...
    __isGfVec = True
    __safe_for_unpickling__ = True
    dimension = 3
    pass
class Vec3i(Boost.Python.instance):
    @staticmethod
    def Axis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDot(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def XAxis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def YAxis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ZAxis(*args, **kwargs) -> typing.Any: ...
    __isGfVec = True
    __safe_for_unpickling__ = True
    dimension = 3
    pass
class Vec4d(Boost.Python.instance):
    @staticmethod
    def Axis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetComplement(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDot(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetLength(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNormalized(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetProjection(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Normalize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def WAxis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def XAxis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def YAxis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ZAxis(*args, **kwargs) -> typing.Any: ...
    __isGfVec = True
    __safe_for_unpickling__ = True
    dimension = 4
    pass
class Vec4f(Boost.Python.instance):
    @staticmethod
    def Axis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetComplement(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDot(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetLength(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNormalized(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetProjection(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Normalize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def WAxis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def XAxis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def YAxis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ZAxis(*args, **kwargs) -> typing.Any: ...
    __isGfVec = True
    __safe_for_unpickling__ = True
    dimension = 4
    pass
class Vec4h(Boost.Python.instance):
    @staticmethod
    def Axis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetComplement(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDot(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetLength(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNormalized(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetProjection(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Normalize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def WAxis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def XAxis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def YAxis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ZAxis(*args, **kwargs) -> typing.Any: ...
    __isGfVec = True
    __safe_for_unpickling__ = True
    dimension = 4
    pass
class Vec4i(Boost.Python.instance):
    @staticmethod
    def Axis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDot(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def WAxis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def XAxis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def YAxis(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ZAxis(*args, **kwargs) -> typing.Any: ...
    __isGfVec = True
    __safe_for_unpickling__ = True
    dimension = 4
    pass
def Abs(*args, **kwargs) -> typing.Any:
    pass
def Absf(f) -> float:
    """
    f : float

    Use instead of Abs() to return the absolute value of f as a float instead of a double.
    """
def ApplyGamma(*args, **kwargs) -> typing.Any:
    pass
def Ceil(*args, **kwargs) -> typing.Any:
    pass
def Ceilf(f) -> float:
    """
    f : float

    Use instead of Ceil() to return the ceiling of f as a float instead of a double.
    """
def Clamp(*args, **kwargs) -> typing.Any:
    pass
def Clampf(f) -> float:
    """
    f : float

    Use instead of Clamp() to return the clamped value of f as a float instead of a double.
    """
def CompDiv(*args, **kwargs) -> typing.Any:
    pass
def CompMult(*args, **kwargs) -> typing.Any:
    pass
def ConvertDisplayToLinear(*args, **kwargs) -> typing.Any:
    pass
def ConvertLinearToDisplay(*args, **kwargs) -> typing.Any:
    pass
def Cross(*args, **kwargs) -> typing.Any:
    pass
def DegreesToRadians(*args, **kwargs) -> typing.Any:
    pass
def Dot(*args, **kwargs) -> typing.Any:
    pass
def Exp(*args, **kwargs) -> typing.Any:
    pass
def Expf(f) -> float:
    """
    f : float

    Use instead of Exp() to return the exponent of f as a float instead of a double.
    """
def FindClosestPoints(*args, **kwargs) -> typing.Any:
    """
    l1 : GfLine
    l2 : GfLine

    Computes the closest points between two lines, returning a tuple.  The first item in the tuple is true if the linesintersect.  The two points are returned in p1 and p2.  The parametric distance of each point on the lines is returned in t1 and t2.
    ----------------------------------------------------------------------

    l1 : GfLine
    s2 : GfLineSeg

    Computes the closest points between a line and a line segment, returning a tuple. The first item in the tuple is true if they intersect. The two points are returned in p1 and p2.  The parametric distance of each point on the line and line segment is returned in t1 and t2.
    ----------------------------------------------------------------------

    l1 : GfLineSeg
    l2 : GfLineSeg

    Computes the closest points between two line segments, returning a tuple.  The first item in the tuple is true if they intersect.  The two points are returned in p1 and p2.  The parametric distance of each point on the line and line segment is returned in t1 and t2.
    ----------------------------------------------------------------------

    r1 : GfRay
    l2 : GfLine

    Computes the closest points between a ray and a line,
    returning a tuple. The first item in the tuple is true if they intersect. The two points are returned in p1 and p2.
    The parametric distance of each point on the ray and line is
    returned in t1 and t2.
    ----------------------------------------------------------------------

    r1 : GfRay
    s2 : GfLineSeg

    Computes the closest points between a ray and a line segment,
    returning a tuple. The first item in the tuple is true if they intersect. The two points are returned in p1 and p2.
    The parametric distance of each point on the ray and line
    segment is returned in t1 and t2.
    ----------------------------------------------------------------------
    """
def FitPlaneToPoints(*args, **kwargs) -> typing.Any:
    pass
def Floor(*args, **kwargs) -> typing.Any:
    pass
def Floorf(f) -> float:
    """
    f : float

    Use instead of Floor() to return the floor of f as a float instead of a double.
    """
def GetComplement(*args, **kwargs) -> typing.Any:
    pass
def GetDisplayGamma(*args, **kwargs) -> typing.Any:
    pass
def GetHomogenized(*args, **kwargs) -> typing.Any:
    pass
def GetLength(*args, **kwargs) -> typing.Any:
    pass
def GetNormalized(*args, **kwargs) -> typing.Any:
    pass
def GetProjection(*args, **kwargs) -> typing.Any:
    pass
def HomogeneousCross(*args, **kwargs) -> typing.Any:
    pass
def IsClose(*args, **kwargs) -> typing.Any:
    pass
def Lerp(*args, **kwargs) -> typing.Any:
    pass
def Lerpf(f) -> float:
    """
    f : float

    Use instead of Lerp() to return the linear interpolation of f as a float instead of a double.
    """
def Log(*args, **kwargs) -> typing.Any:
    pass
def Logf(f) -> float:
    """
    f : float

    Use instead of Log() to return the logarithm of f as a float instead of a double.
    """
def Max(*args, **kwargs) -> typing.Any:
    pass
def Min(*args, **kwargs) -> typing.Any:
    pass
def Mod(*args, **kwargs) -> typing.Any:
    pass
def Modf(f) -> float:
    """
    f : float

    Use instead of Mod() to return the modulus of f as a float instead of a double.
    """
def Normalize(*args, **kwargs) -> typing.Any:
    pass
def Pow(*args, **kwargs) -> typing.Any:
    pass
def Powf(f) -> float:
    """
    f : float

    Use instead of Pow() to return the power of f as a float instead of a double.
    """
def Project(*args, **kwargs) -> typing.Any:
    pass
def RadiansToDegrees(*args, **kwargs) -> typing.Any:
    pass
def Round(*args, **kwargs) -> typing.Any:
    pass
def Roundf(f) -> float:
    """
    f : float

    Use instead of Round() to return the rounded value of f as a float instead of a double.
    """
def Sgn(*args, **kwargs) -> typing.Any:
    pass
def Slerp(*args, **kwargs) -> typing.Any:
    pass
def Sqr(*args, **kwargs) -> typing.Any:
    pass
def Sqrt(*args, **kwargs) -> typing.Any:
    pass
def Sqrtf(f) -> float:
    """
    f : float

    Use instead of Sqrt() to return the square root of f as a float instead of a double.
    """
def _HalfRoundTrip(*args, **kwargs) -> typing.Any:
    pass
MIN_ORTHO_TOLERANCE = 1e-06
MIN_VECTOR_LENGTH = 1e-10
__MFB_FULL_PACKAGE_NAME = 'gf'
