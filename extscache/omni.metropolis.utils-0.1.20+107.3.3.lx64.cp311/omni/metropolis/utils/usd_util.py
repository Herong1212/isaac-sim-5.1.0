import carb
from pxr import Gf, Usd, UsdGeom, UsdSkel, Sdf, UsdPhysics
from .math_util import MathUtil, MathNumpyUtil
import numpy as np
import omni.usd
from typing import Optional, Dict, Tuple, List, Union, Any
import os
from pathlib import Path

"""
------------------------Getters/Setters for Prims------------------------
"""


class USDUtil:
    @staticmethod
    def is_valid_prim(prim=None, stage=None, prim_path=None):
        # if prim is not provided, check whether prim path and stage provide a valid prim
        if prim is None and prim_path is not None:
            if stage is None:
                stage = omni.usd.get_context().get_stage()
            prim = stage.GetPrimAtPath(prim_path)
        if prim is None:
            return False
        if prim.IsValid() and prim.IsActive():
            return True
        return False

    @staticmethod
    def is_a_valid_xform(prim: Usd.Prim) -> bool:
        """Check if a prim is a valid xform"""
        if not USDUtil.is_valid_prim(prim):
            return False
        if not prim.IsA(UsdGeom.Xform):
            return False
        return True

    def get_prim_pos_and_rot(prim=None, stage=None, prim_path=None):
        # if valid and active prim is provided, use prim
        if prim and prim.IsValid() and prim.IsActive():
            gf_transform = UsdGeom.XformCache().GetLocalToWorldTransform(prim)
            gf_transform.Orthonormalize()
            gf_translation = gf_transform.ExtractTranslation()
            gf_rot = gf_transform.ExtractRotation()
            return gf_translation, gf_rot
        # else, check if valid prim_path and stage are provided
        else:
            if stage is not None and prim_path is not None:
                prim = stage.GetPrimAtPath(prim_path)
                if prim and prim.IsValid() and prim.IsActive():
                    gf_transform = UsdGeom.XformCache().GetLocalToWorldTransform(prim)
                    gf_transform.Orthonormalize()
                    gf_translation = gf_transform.ExtractTranslation()
                    gf_rot = gf_transform.ExtractRotation()
                    return gf_translation, gf_rot
            carb.log_error("Invalid prim path or prim")
            return None

    def get_prim_pos_and_rot_as_quat(prim=None, stage=None, prim_path=None):
        # if valid and active prim is provided, use prim
        if prim and prim.IsValid() and prim.IsActive():
            gf_transform = UsdGeom.XformCache().GetLocalToWorldTransform(prim)
            gf_transform.Orthonormalize()
            gf_translation = gf_transform.ExtractTranslation()
            gf_rot_quat = gf_transform.ExtractRotation().GetQuat()
            return gf_translation, gf_rot_quat
        # else, check if valid prim_path and stage are provided
        else:
            if stage is not None and prim_path is not None:
                prim = stage.GetPrimAtPath(prim_path)
                if prim and prim.IsValid() and prim.IsActive():
                    gf_transform = UsdGeom.XformCache().GetLocalToWorldTransform(prim)
                    gf_transform.Orthonormalize()
                    gf_translation = gf_transform.ExtractTranslation()
                    gf_rot_quat = gf_transform.ExtractRotation().GetQuat()
                    return gf_translation, gf_rot_quat
            carb.log_error("Invalid prim path or prim")
            return None

    def get_prim_pos(prim=None, stage=None, prim_path=None):
        # if valid and active prim is provided, use prim
        if prim and prim.IsValid() and prim.IsActive():
            gf_translation = UsdGeom.XformCache().GetLocalToWorldTransform(prim).ExtractTranslation()
            return carb.Float3(gf_translation[0], gf_translation[1], gf_translation[2])
        # else, check if valid prim_path and stage are provided
        else:
            if stage is not None and prim_path is not None:
                prim = stage.GetPrimAtPath(prim_path)
                if prim and prim.IsValid() and prim.IsActive():
                    gf_translation = UsdGeom.XformCache().GetLocalToWorldTransform(prim).ExtractTranslation()
                    return carb.Float3(gf_translation[0], gf_translation[1], gf_translation[2])
            carb.log_error("Invalid prim path or prim")
            return None

    def get_prim_rot_as_quat(prim=None, stage=None, prim_path=None):
        # if valid and active prim is provided, use prim
        if prim and prim.IsValid() and prim.IsActive():
            gf_rotation = UsdGeom.XformCache().GetLocalToWorldTransform(prim).ExtractRotationQuat()
            return gf_rotation
        # else, check if valid prim_path and stage are provided
        else:
            if stage is not None and prim_path is not None:
                prim = stage.GetPrimAtPath(prim_path)
                if prim and prim.IsValid() and prim.IsActive():
                    gf_rotation = UsdGeom.XformCache().GetLocalToWorldTransform(prim).ExtractRotationQuat()
                    return gf_rotation
            carb.log_error("Invalid prim path or prim")
            return None

    def get_prim_scale(stage, prim_path, prim=None):
        # if valid and active prim is provided, use prim
        if prim and prim.IsValid() and prim.IsActive():
            # Determinant3 is the scale of a linear transformation
            gf_scale = UsdGeom.XformCache().GetLocalToWorldTransform(prim).GetDeterminant3()
            return gf_scale
        else:
            if stage is not None and prim_path is not None:
                prim = stage.GetPrimAtPath(prim_path)
                if prim and prim.IsValid() and prim.IsActive():
                    gf_scale = UsdGeom.XformCache().GetLocalToWorldTransform(prim).GetDeterminant3()
                    return gf_scale
            carb.log_error("Invalid prim path or prim")
            return None

    def set_prim_pos(prim, pos):
        if USDUtil.is_valid_prim(prim):
            prim.GetAttribute("xformOp:translate").Set(pos)
        else:
            carb.log_error("Invalid prim")

    def set_prim_orient(prim, orient):
        if USDUtil.is_valid_prim(prim):
            prim.GetAttribute("xformOp:orient").Set(orient)
        else:
            carb.log_error("Invalid prim")

    def set_prim_pivot(prim, pivot):
        if USDUtil.is_valid_prim(prim):
            prim.GetAttribute("xformOp:translate:pivot").Set(pivot)
        else:
            carb.log_error("Invalid prim")

    def set_prim_scale(prim, scale):
        if USDUtil.is_valid_prim(prim):
            prim.GetAttribute("xformOp:scale").Set(scale)
        else:
            carb.log_error("Invalid prim")

    def set_prim_pos_and_rot(prim, pos, rot):
        if USDUtil.is_valid_prim(prim):
            trans_mat = Gf.Matrix4d(Gf.Rotation(rot), pos)
            prim.GetAttribute("xformOp:transform").Set(trans_mat)
        else:
            carb.log_error("Invalid prim")

    def compute_orthonormal_basis(A, default_right=np.array([1.0, 0.0, 0.0])):
        """
        Given a unit vector A in 3D space, compute the right unit vector B (parallel to the ground plane z=0)
        and the up vector C to form an orthonormal basis (A, B, C).

        Parameters:
        - A: array-like of shape (3,), the input unit vector.
        - default_right: array-like of shape (3,), the default right vector when A is aligned with the z-axis.

        Returns:
        - tuple of three np.ndarray objects: (A, B, C)
        """
        A = np.array(A, dtype=float)

        # Ensure A is a unit vector
        norm_A = np.linalg.norm(A)
        if norm_A == 0:
            raise ValueError("Input vector A must be non-zero.")
        A = A / norm_A

        # Extract components
        Ax, Ay, Az = A

        # Compute the projection of A onto the ground plane (z=0)
        proj_A = np.array([Ax, Ay, 0.0])

        norm_proj_A = np.linalg.norm(proj_A)

        if norm_proj_A > 1e-8:
            # If the projection is non-zero, B is perpendicular to proj_A in the ground plane
            B = np.array([-Ay, Ax, 0.0]) / norm_proj_A
        else:
            # If A is parallel to the z-axis, use the default_right vector
            default_right = np.array(default_right, dtype=float)
            norm_default_right = np.linalg.norm(default_right)
            if norm_default_right < 1e-8:
                raise ValueError("Default right vector must be non-zero.")
            B = default_right / norm_default_right

        # Compute C as the cross product of A and B
        C = np.cross(A, B)

        # Ensure C is a unit vector (optional, since A and B are unit and orthogonal)
        C_norm = np.linalg.norm(C)
        if C_norm > 1e-8:
            C = C / C_norm
        else:
            raise ValueError("Computed up vector C has zero magnitude.")

        return (A, B, C)

    def get_prim_name(stage=None, prim_path=None, prim=None):
        if prim is None:
            if stage is None:
                stage = omni.usd.get_context().get_stage()
            prim = stage.GetPrimAtPath(prim_path)
        # get prim name and cast to str
        prim_name = str(prim.GetName())
        return prim_name

    def get_prim_transform(
        prim: Optional[Usd.Prim] = None, prim_path: Optional[Union[Sdf.Path, str]] = None, stage=None
    ):
        if prim is None:
            if stage is None:
                stage = omni.usd.get_context().get_stage()
            prim = stage.GetPrimAtPath(prim_path)
        gf_transform = UsdGeom.XformCache().GetLocalToWorldTransform(prim)
        # convert to the np.array.
        transform = np.reshape(gf_transform, (4, 4))
        return transform

    def filter_children_by_type(
        type_name: str, prim: Optional[Usd.Prim] = None, prim_path: Optional[Union[Sdf.Path, str]] = None, stage=None
    ) -> List[Usd.Prim]:
        """filter child prim with types as input"""
        if prim is None:
            if stage is None:
                stage = omni.usd.get_context().get_stage()
            prim = stage.GetPrimAtPath(prim_path)

        result = []
        if USDUtil.is_valid_prim(prim=prim):
            for child_prim in prim.GetChildren():
                if child_prim.GetTypeName() == type_name:
                    result.append(child_prim)
        return result

    @classmethod
    def update_prim_property(
        cls,
        property_name: str,
        property_value: Any,
        property_type: Optional[Any] = None,
        stage: Optional[Usd.Stage] = None,
        prim: Optional[Usd.Prim] = None,
        prim_path: Optional[Union[str, Sdf.Path]] = None,
    ):
        """add/update property on target prim with desired value"""
        # check whether the target prim is valid
        if not cls.is_valid_prim(stage=stage, prim=prim, prim_path=prim_path):
            carb.log_verbose("Fail to update prim property")
            return
        # if prim is not included in input, fetch the prim
        if prim is None:
            if stage is None:
                stage = omni.usd.get_context().get_stage()
            prim = stage.GetPrimAtPath(prim_path)
        # update the target property.
        prim_property = None
        # if target objet do not contain required property.
        if not prim.HasAttribute(property_name):
            # create a property with target name
            prim_property = prim.CreateAttribute(property_name, property_type)
        else:
            # get the value of target property
            prim_property = prim.GetAttribute(property_name)

        prim_property.Set(property_value)

    @staticmethod
    def get_prim_attribute(prim: Usd.Prim, attribute_name: str, default_value: Optional[Any] = None):
        """get prim with target atribute, return default value if prim do not have such attribute"""
        if prim.HasAttribute(attribute_name):
            prim_value = prim.GetAttribute(attribute_name).Get()
            return prim_value
        else:
            return default_value

    def remove_physics_attributes_or_joint_recursive(prim: Usd.Prim):
        """
        Recursively remove all physics-related attributes from a prim and its children,
        or if it is a physics joint, remove the prim itself.

        Args:
            prim (Usd.Prim): The USD prim to modify or remove.
        Note:
            Physics joint prims are not removed, but set to inactive to preserve the hierarchy while disabling physics.
        """
        # Define a list of all known physics joint schemas
        physics_joint_types = [
            UsdPhysics.PrismaticJoint,
            UsdPhysics.RevoluteJoint,
            UsdPhysics.SphericalJoint,
            UsdPhysics.DistanceJoint,
            UsdPhysics.FixedJoint,
        ]

        # Check if the prim is a physics join
        for joint_type in physics_joint_types:
            if prim.IsA(joint_type):
                prim.SetActive(False)
                carb.log_info(f"Removed physics joint prim at {prim.GetPath()}")
                return

        # Remove physics attributes from this prim
        physics_attributes = [
            "physics:mass",
            "physics:density",
            "physics:velocity",
            "physics:angularVelocity",
            "physics:kinematicEnabled",
            "physics:gravityEnabled",
            "physics:rigidBodyEnabled",
            "physics:collisionEnabled",
            "physics:velocityDamping",
            "physics:angularDamping",
        ]

        for attr_name in physics_attributes:
            if prim.HasAttribute(attr_name):
                prim.GetAttribute(attr_name).Block()

        # Additional clean-up for physics-related APIs
        if prim.HasAPI(UsdPhysics.RigidBodyAPI):
            prim.RemoveAPI(UsdPhysics.RigidBodyAPI)

        if prim.HasAPI(UsdPhysics.CollisionAPI):
            prim.RemoveAPI(UsdPhysics.CollisionAPI)

        # print(f"Removed physics attributes from prim at {prim.GetPath()}")
        carb.log_info(f"Removed physics attributes from prim at {prim.GetPath()}")

        # Recursively process child prims
        for child_prim in prim.GetChildren():
            USDUtil.remove_physics_attributes_or_joint_recursive(child_prim)

    @staticmethod
    def get_object_reference(prim: Optional[Usd.Prim] = None, prim_path: Optional[str] = None, stage=None):
        """check the object reference url, return true if it is from the target asset path"""

        def is_abs(path: str):
            """check whether the target path is an absolute path"""
            parts = omni.client.break_url(path)
            return Path(parts.path).is_absolute() and bool(parts.scheme)

        asset_path = None

        if prim is None:
            if stage is None:
                stage = omni.usd.get_context().get_stage()
            if not prim_path:
                return asset_path
            # get prim from prim path
            prim = stage.GetPrimAtPath(prim_path)

        # if the prim is a payload prim
        try:
            ref_and_layers = omni.usd.get_composed_payloads_from_prim(prim, False)
        except:
            return None
        if len(ref_and_layers) == 0:
            # else if the prim is a reference prim
            ref_and_layers = omni.usd.get_composed_references_from_prim(prim, False)
        if len(ref_and_layers) > 0:
            ref, layer = ref_and_layers[0]
            asset_path = ref.assetPath
        else:
            return asset_path

        # if asset path is still none, return
        if asset_path is None:
            return asset_path

        # ensure the output is an obsolute path
        if not is_abs(asset_path):
            # get current stage's url path:
            asset_info = layer.GetAssetInfo()
            if asset_info is None and os.path.isabs(asset_path):
                return asset_path
            elif asset_info is None:
                return None
            current_stage_url = asset_info["url"]
            # get full asset path:
            asset_path = omni.client.combine_urls(current_stage_url, asset_path)

        return asset_path


class CameraUSDUtil:
    def get_camera_frustum_corners(
        camera_prim: Optional[Usd.Prim] = None, camera_path: Optional[Union[Sdf.Path, str]] = None, stage=None
    ):
        """get an 3d position to look at"""
        # get camera's frustum information
        if camera_prim is None:
            if stage is None:
                stage = omni.usd.get_context().get_stage()
            camera_prim = stage.GetPrimAtPath(camera_path)

        camera_frustum = UsdGeom.Camera(camera_prim).GetCamera().frustum
        # extract eight corners on frustum clipping plane
        corners = camera_frustum.ComputeCorners()
        return corners

    def get_camera_focus_point(camera_prim: Usd.Prim, near_plane: Optional[bool] = False):
        """get an 3d position to look at"""
        # get camera's frustum information
        corners = CameraUSDUtil.get_camera_frustum_corners(camera_prim=camera_prim)
        # get the near clip panel
        if near_plane:
            clip_panel_corner = corners[:4]
        else:
            # else get the far clip plane
            clip_panel_corner = corners[-4:]
        # calculate the center of the far clip panel as the look at point
        return MathNumpyUtil.calculate_centroid(clip_panel_corner)

    def get_camera_forward_vector(camera_prim):
        """calculate camera's forward vector"""
        # get camera position
        camera_position = USDUtil.get_prim_pos(prim=camera_prim)
        camera_pos = np.array([camera_position[0], camera_position[1], camera_position[2]])
        # get camera focus point
        focus_pos = CameraUSDUtil.get_camera_focus_point(camera_prim)
        # get camera forward vector.
        normal_vec = MathNumpyUtil.normalize_vector(focus_pos - camera_pos)
        return normal_vec

    def get_camera_view_matrix(
        prim: Optional[Usd.Prim] = None, prim_path: Optional[Union[Sdf.Path, str]] = None, stage=None
    ):
        """calculate the camera view matrix"""
        # extract camera's view matrix from camera transform
        camera_transform = USDUtil.get_prim_transform(prim=prim, prim_path=prim_path, stage=stage)
        view_matrix = np.linalg.inv(camera_transform)
        return view_matrix
