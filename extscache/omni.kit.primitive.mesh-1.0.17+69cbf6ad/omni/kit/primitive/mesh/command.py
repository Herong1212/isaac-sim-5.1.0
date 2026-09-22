"""This module provides commands to create various mesh primitives with default transformations in a USD stage."""

__all__ = ["CreateMeshPrimWithDefaultXformCommand", "CreateMeshPrimCommand"]

import omni
import carb.settings
from pxr import UsdGeom, Usd, Vt, Sdf, Gf
from .evaluators import _get_all_evaluators
import omni.kit.commands

PERSISTENT_SETTINGS_PREFIX = "/persistent"


class CreateMeshPrimWithDefaultXformCommand(omni.kit.commands.Command):
    """A command class to create mesh primitives with default transformations in a USD stage.

    This command supports creating various types of mesh primitives such as Plane, Sphere, Cone, Cylinder, Disk, Torus, and Cube.
    It also handles setting up default transformations and attributes for the newly created mesh based on persistent settings and keyword arguments provided during initialization.
    """

    def __init__(self, prim_type: str, **kwargs):
        """
        Creates primitive.

        Args:
            prim_type (str): It supports Plane/Sphere/Cone/Cylinder/Disk/Torus/Cube.

        kwargs:
            object_origin (Gf.Vec3f): Position of mesh center in stage units.

            u_patches (int): The number of patches to tessellate U direction.

            v_patches (int): The number of patches to tessellate V direction.

            w_patches (int): The number of patches to tessellate W direction.
                             It only works for Cone/Cylinder/Cube.

            half_scale (float): Half size of mesh in centimeters. Default is None, which means it's controlled by settings.

            u_verts_scale (int): Tessellation Level of U. It's a multiplier of u_patches.

            v_verts_scale (int): Tessellation Level of V. It's a multiplier of v_patches.

            w_verts_scale (int): Tessellation Level of W. It's a multiplier of w_patches.
                                 It only works for Cone/Cylinder/Cube.
                                 For Cone/Cylinder, it's to tessellate the caps.
                                 For Cube, it's to tessellate along z-axis.

            above_ground (bool): It will offset the center of mesh above the ground plane if it's True,
                False otherwise. It's False by default. This param only works when param object_origin is not given.
                Otherwise, it will be ignored.
        """

        self._prim_type = prim_type[0:1].upper() + prim_type[1:].lower()
        self._usd_context = omni.usd.get_context(kwargs.get("context_name", ""))
        self._selection = self._usd_context.get_selection()
        self._stage = self._usd_context.get_stage()
        self._settings = carb.settings.get_settings()
        self._default_path = kwargs.get("prim_path", None)
        self._select_new_prim = kwargs.get("select_new_prim", True)
        self._prepend_default_prim = kwargs.get("prepend_default_prim", True)
        self._above_round = kwargs.get("above_ground", False)

        self._attributes = {**kwargs}
        # Supported mesh types should have an associated evaluator class
        self._evaluator_class = _get_all_evaluators()[prim_type]
        assert isinstance(self._evaluator_class, type)

    def do(self):
        """Executes the command to create the mesh primitive."""
        self._prim_path = None
        if self._default_path:
            path = omni.usd.get_stage_next_free_path(self._stage, self._default_path, self._prepend_default_prim)
        else:
            path = omni.usd.get_stage_next_free_path(self._stage, "/" + self._prim_type, self._prepend_default_prim)
        mesh = UsdGeom.Mesh.Define(self._stage, path)

        prim = mesh.GetPrim()
        defaultXformOpType = self._settings.get(PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultXformOpType")
        defaultRotationOrder = self._settings.get(PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultRotationOrder")
        defaultXformPrecision = self._settings.get(
            PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultXformOpPrecision"
        )
        vec3_type = Sdf.ValueTypeNames.Double3 if defaultXformPrecision == "Double" else Sdf.ValueTypeNames.Float3
        quat_type = Sdf.ValueTypeNames.Quatd if defaultXformPrecision == "Double" else Sdf.ValueTypeNames.Quatf

        up_axis = UsdGeom.GetStageUpAxis(self._stage)
        self._attributes["up_axis"] = up_axis

        half_scale = self._attributes.get("half_scale", None)
        if half_scale is None or half_scale <= 0.0:
            half_scale = self._evaluator_class.get_default_half_scale()

        object_origin = self._attributes.get("object_origin", None)
        if object_origin is None and self._above_round:
            # To move the mesh above the ground.
            if self._prim_type != "Disk" and self._prim_type != "Plane":
                if self._prim_type != "Torus":
                    offset = half_scale
                else:
                    # The tube of torus is half of the half_scale.
                    offset = half_scale / 2.0

                # Scale it to make sure it matches stage units.
                units = UsdGeom.GetStageMetersPerUnit(mesh.GetPrim().GetStage())
                if Gf.IsClose(units, 0.0, 1e-6):
                    units = 0.01

                scale = 0.01 / units
                offset = offset * scale

                if up_axis == "Y":
                    object_origin = Gf.Vec3f(0.0, offset, 0.0)
                else:
                    object_origin = Gf.Vec3f(0.0, 0.0, offset)
            else:
                object_origin = Gf.Vec3f(0.0)
        elif isinstance(object_origin, list):
            object_origin = Gf.Vec3f(*object_origin)
        elif not object_origin:
            object_origin = Gf.Vec3f(0.0)

        default_translate = Gf.Vec3d(object_origin) if defaultXformPrecision == "Double" else object_origin
        default_euler = Gf.Vec3d(0.0, 0.0, 0.0) if defaultXformPrecision == "Double" else Gf.Vec3f(0.0, 0.0, 0.0)
        default_scale = Gf.Vec3d(1.0, 1.0, 1.0) if defaultXformPrecision == "Double" else Gf.Vec3f(1.0, 1.0, 1.0)
        default_orient = (
            Gf.Quatd(1.0, Gf.Vec3d(0.0, 0.0, 0.0))
            if defaultXformPrecision == "Double"
            else Gf.Quatf(1.0, Gf.Vec3f(0.0, 0.0, 0.0))
        )
        mat4_type = Sdf.ValueTypeNames.Matrix4d  # there is no Matrix4f in SdfValueTypeNames
        if defaultXformOpType == "Scale, Rotate, Translate":
            attr_translate = prim.CreateAttribute("xformOp:translate", vec3_type, False)
            attr_translate.Set(default_translate)
            attr_rotate_name = "xformOp:rotate" + defaultRotationOrder
            attr_rotate = prim.CreateAttribute(attr_rotate_name, vec3_type, False)
            attr_rotate.Set(default_euler)
            attr_scale = prim.CreateAttribute("xformOp:scale", vec3_type, False)
            attr_scale.Set(default_scale)
            attr_order = prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.TokenArray, False)
            attr_order.Set(["xformOp:translate", attr_rotate_name, "xformOp:scale"])
        if defaultXformOpType == "Scale, Orient, Translate":
            attr_translate = prim.CreateAttribute("xformOp:translate", vec3_type, False)
            attr_translate.Set(default_translate)
            attr_rotate = prim.CreateAttribute("xformOp:orient", quat_type, False)
            attr_rotate.Set(default_orient)
            attr_scale = prim.CreateAttribute("xformOp:scale", vec3_type, False)
            attr_scale.Set(default_scale)
            attr_order = prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.TokenArray, False)
            attr_order.Set(["xformOp:translate", "xformOp:orient", "xformOp:scale"])
        if defaultXformOpType == "Transform":
            attr_matrix = prim.CreateAttribute("xformOp:transform", mat4_type, False)
            attr_matrix.Set(Gf.Matrix4d(1.0))
            attr_order = prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.TokenArray, False)
            attr_order.Set(["xformOp:transform"])

        self._prim_path = path
        if self._select_new_prim:
            self._selection.set_prim_path_selected(path, True, False, True, True)

        self._define_mesh(mesh)
        return self._prim_path

    def undo(self):
        """Undoes the creation of the mesh primitive."""
        if self._prim_path:
            self._stage.RemovePrim(self._prim_path)

    def _define_mesh(self, mesh):
        evaluator = self._evaluator_class(self._attributes)

        points = []
        normals = []
        sts = []
        point_indices = []
        face_vertex_counts = []

        points, normals, sts, point_indices, face_vertex_counts = evaluator.eval(**self._attributes)

        units = UsdGeom.GetStageMetersPerUnit(mesh.GetPrim().GetStage())
        if Gf.IsClose(units, 0.0, 1e-6):
            units = 0.01

        # Scale points to make sure it's already in centimeters
        scale = 0.01 / units
        points = [point * scale for point in points]

        mesh.GetPointsAttr().Set(Vt.Vec3fArray(points))
        mesh.GetNormalsAttr().Set(Vt.Vec3fArray(normals))
        mesh.GetFaceVertexIndicesAttr().Set(point_indices)
        mesh.GetFaceVertexCountsAttr().Set(face_vertex_counts)
        mesh.SetNormalsInterpolation("faceVarying")

        prim = mesh.GetPrim()

        # https://github.com/PixarAnimationStudios/USD/commit/592b4d39edf5daf0534d467e970c95462a65d44b
        # UsdGeom.Imageable.CreatePrimvar deprecated in v19.03 and removed in v22.08
        sts_primvar = UsdGeom.PrimvarsAPI(prim).CreatePrimvar("st", Sdf.ValueTypeNames.TexCoord2fArray)
        sts_primvar.SetInterpolation("faceVarying")
        sts_primvar.Set(Vt.Vec2fArray(sts))
        mesh.CreateSubdivisionSchemeAttr("none")

        attr = prim.GetAttribute(UsdGeom.Tokens.extent)
        if attr:
            bounds = UsdGeom.Boundable.ComputeExtentFromPlugins(UsdGeom.Boundable(prim), Usd.TimeCode.Default())
            if bounds:
                attr.Set(bounds)

        # set the new prim as the active selection
        if self._select_new_prim:
            self._selection.set_selected_prim_paths([prim.GetPath().pathString], False)


# For back compatibility.
class CreateMeshPrimCommand(CreateMeshPrimWithDefaultXformCommand):
    """A command class for creating a mesh primitive in a USD stage with default transformations.

    This class is a specialized command for generating various types of mesh primitives such as Plane, Sphere, Cone, etc., and applies a default transformation to them. It extends the CreateMeshPrimWithDefaultXformCommand class.

    Args:
        prim_type (str): The type of primitive mesh to create. Supported types include 'Plane', 'Sphere', 'Cone', 'Cylinder', 'Disk', 'Torus', 'Cube'.

    Keyword Args:
        object_origin (Gf.Vec3f): The position of the mesh center in the stage units.
        u_patches (int): The number of patches for tessellating the U direction.
        v_patches (int): The number of patches for tessellating the V direction.
        w_patches (int): The number of patches for tessellating the W direction; only applies to 'Cone', 'Cylinder', and 'Cube'.
        half_scale (float): Half the size of the mesh in centimeters; if None, it's controlled by settings.
        u_verts_scale (int): Tessellation level multiplier for the U direction.
        v_verts_scale (int): Tessellation level multiplier for the V direction.
        w_verts_scale (int): Tessellation level multiplier for the W direction; for 'Cone' and 'Cylinder', it tessellates the caps, for 'Cube', it tessellates along the z-axis.
        above_ground (bool): If True, offsets the mesh center above the ground plane; applicable when 'object_origin' is not provided. Defaults to False.
        context_name (str): The name of the USD context. Defaults to an empty string.
        prim_path (str): The path where the new primitive will be created. If None, a default path is generated.
        select_new_prim (bool): Whether to select the new primitive after creation. Defaults to True.
        prepend_default_prim (bool): If True, prepends the default primitive name to the newly created prim path. Defaults to True.
    """

    def __init__(self, prim_type: str, **kwargs):
        """Initializes the command to create a mesh primitive."""
        super().__init__(prim_type, **kwargs)


omni.kit.commands.register(CreateMeshPrimCommand)
omni.kit.commands.register(CreateMeshPrimWithDefaultXformCommand)
