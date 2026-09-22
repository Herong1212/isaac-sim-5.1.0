from omni.metropolis.utils.usd_util import USDUtil
from pxr import Usd, Sdf, Gf, UsdGeom
import math
from typing import Optional, Union, List, Callable
import numpy as np
from .settings import GeneralSetting
from omni.metropolis.utils.simulation_util import SimulationUtil
import omni
import carb


class CameraGeneralUtil:
    """Util function that shared by both camera calibration/placement pipeline"""

    # internal global constants
    _POLE_LIMIT = 1.0 - 1e-6

    # internal global constants
    _POLE_LIMIT = 1.0 - 1e-6

    @staticmethod
    def get_target_camera_prims_under_root(
        root_prim: Optional[Usd.Prim] = None, root_prim_path: Optional[Union[Sdf.Path, str]] = None, stage=None
    ) -> List[Usd.Prim]:
        """get all camera prims under the root path"""
        if root_prim is None and root_prim_path is None:
            root_prim_path = GeneralSetting.camera_parent_prim_path

        if not USDUtil.is_valid_prim(prim_path=root_prim_path):
            return []

        return USDUtil.filter_children_by_type(
            type_name="Camera", prim=root_prim, prim_path=root_prim_path, stage=stage
        )

    ##NOTE: function is copied to remove the dependency on the isaacsim utils
    @staticmethod
    def lookat_to_quatf(camera: Gf.Vec3f, target: Gf.Vec3f, up: Gf.Vec3f) -> Gf.Quatf:
        """[summary]

        Args:
            camera (Gf.Vec3f): [description]
            target (Gf.Vec3f): [description]
            up (Gf.Vec3f): [description]

        Returns:
            Gf.Quatf: Pxr quaternion object.
        """
        F = (target - camera).GetNormalized()
        R = Gf.Cross(up, F).GetNormalized()
        U = Gf.Cross(F, R)

        q = Gf.Quatf()
        trace = R[0] + U[1] + F[2]
        if trace > 0.0:
            s = 0.5 / math.sqrt(trace + 1.0)
            q = Gf.Quatf(0.25 / s, Gf.Vec3f((U[2] - F[1]) * s, (F[0] - R[2]) * s, (R[1] - U[0]) * s))
        else:
            if R[0] > U[1] and R[0] > F[2]:
                s = 2.0 * math.sqrt(1.0 + R[0] - U[1] - F[2])
                q = Gf.Quatf((U[2] - F[1]) / s, Gf.Vec3f(0.25 * s, (U[0] + R[1]) / s, (F[0] + R[2]) / s))
            elif U[1] > F[2]:
                s = 2.0 * math.sqrt(1.0 + U[1] - R[0] - F[2])
                q = Gf.Quatf((F[0] - R[2]) / s, Gf.Vec3f((U[0] + R[1]) / s, 0.25 * s, (F[1] + U[2]) / s))
            else:
                s = 2.0 * math.sqrt(1.0 + F[2] - R[0] - U[1])
                q = Gf.Quatf((R[1] - U[0]) / s, Gf.Vec3f((F[0] + R[2]) / s, (F[1] + U[2]) / s, 0.25 * s))
        return q

    ##NOTE: function is copied to remove the dependency on the isaacsim utils
    @classmethod
    def matrix_to_euler_angles(cls, mat: np.ndarray, degrees: bool = False, extrinsic: bool = True) -> np.ndarray:
        """Convert rotation matrix to Euler XYZ extrinsic or intrinsic angles.

        Args:
            mat (np.ndarray): A 3x3 rotation matrix.
            degrees (bool, optional): Whether returned angles should be in degrees.
            extrinsic (bool, optional): True if the rotation matrix follows the extrinsic matrix
                    convention (equivalent to ZYX ordering but returned in the reverse) and False if it follows
                    the intrinsic matrix conventions (equivalent to XYZ ordering).
                    Defaults to True.

        Returns:
            np.ndarray: Euler XYZ angles (intrinsic form) if extrinsic is False and Euler XYZ angles (extrinsic form) if extrinsic is True.
        """
        if extrinsic:
            if mat[2, 0] > cls._POLE_LIMIT:
                roll = np.arctan2(mat[0, 1], mat[0, 2])
                pitch = -np.pi / 2
                yaw = 0.0
                return np.array([roll, pitch, yaw])

            if mat[2, 0] < -cls._POLE_LIMIT:
                roll = np.arctan2(mat[0, 1], mat[0, 2])
                pitch = np.pi / 2
                yaw = 0.0
                return np.array([roll, pitch, yaw])

            roll = np.arctan2(mat[2, 1], mat[2, 2])
            pitch = -np.arcsin(mat[2, 0])
            yaw = np.arctan2(mat[1, 0], mat[0, 0])
            if degrees:
                roll = math.degrees(roll)
                pitch = math.degrees(pitch)
                yaw = math.degrees(yaw)
            return np.array([roll, pitch, yaw])
        else:
            if mat[0, 2] > cls._POLE_LIMIT:
                roll = np.arctan2(mat[1, 0], mat[1, 1])
                pitch = np.pi / 2
                yaw = 0.0
                return np.array([roll, pitch, yaw])

            if mat[0, 2] < -cls._POLE_LIMIT:
                roll = np.arctan2(mat[1, 0], mat[1, 1])
                pitch = -np.pi / 2
                yaw = 0.0
                return np.array([roll, pitch, yaw])
            roll = -math.atan2(mat[1, 2], mat[2, 2])
            pitch = math.asin(mat[0, 2])
            yaw = -math.atan2(mat[0, 1], mat[0, 0])

            if degrees:
                roll = math.degrees(roll)
                pitch = math.degrees(pitch)
                yaw = math.degrees(yaw)
            return np.array([roll, pitch, yaw])



    @classmethod
    def ensure_parent_prim_exists(cls, target_prim_path: str, filter_fn: Optional[Callable] = None, default_prim_type: Optional[str] = "Xform"):
        """ensure the camera parent prim exists"""
        stage = omni.usd.get_context().get_stage()
        # If the target prim already exists, ensure it is xformable
        if USDUtil.is_valid_prim(prim_path=target_prim_path):
            prim = stage.GetPrimAtPath(target_prim_path)
            if filter_fn is None or filter_fn(prim):
                return
            carb.log_error(f"The target prim {target_prim_path} is not a valid prim by the filter function")
            return

        # Validate the target path string
        target_path = Sdf.Path(target_prim_path)
        if target_path == Sdf.Path.absoluteRootPath:
            return
        # Find the nearest existing ancestor prim
        missing_paths = []
        current_path = target_path
        while current_path != Sdf.Path.absoluteRootPath:
            if USDUtil.is_valid_prim(prim_path=current_path):
                break
            missing_paths.append(current_path)
            current_path = current_path.GetParentPath()

        # Create missing prims from the nearest existing ancestor down to the target path
        for path_to_create in reversed(missing_paths):
            omni.kit.commands.execute(
                "CreatePrimCommand",
                prim_type=default_prim_type,
                prim_path=str(path_to_create),
                select_new_prim=False,
            )

        # Verify the final prim is xformable
        final_prim = stage.GetPrimAtPath(target_path)
        if not (USDUtil.is_valid_prim(prim=final_prim) and (filter_fn is None or filter_fn(final_prim))):
            carb.log_error(f"Failed to create xformable prim at {target_prim_path}")
            return


    ##NOTE: function is copied to remove the dependency on the iac
    @classmethod
    def spawn_camera(
        cls, spawn_path=None, spawn_location=None, spawn_rotation=None, focallength=None, focus_point=None
    ):
        # set xformOp order to Scale, Orient, Translate, and store the setting
        original_xform_order_setting = SimulationUtil.update_xformOp_type(target_xform_type="Scale, Orient, Translate")
        stage = omni.usd.get_context().get_stage()
        camera_path = None
        if spawn_path:
            camera_path = spawn_path
        else:
            camera_path = Sdf.Path(
                omni.usd.get_stage_next_free_path(stage, GeneralSetting.camera_parent_prim_path + "/Camera", False)
            )

        # fetch the parent path of the camera prim
        camera_parent_prim_path = Sdf.Path(camera_path).GetParentPath()
        # ensure the camera parent prim is a valid xformable prim
        cls.ensure_parent_prim_exists(target_prim_path=camera_parent_prim_path, filter_fn=lambda prim: prim.IsA(UsdGeom.Xformable), default_prim_type="Xform")

        omni.kit.commands.execute("CreatePrimCommand", prim_type="Camera", prim_path=camera_path, select_new_prim=False)
        camera_prim = stage.GetPrimAtPath(camera_path)
        cls.set_camera(
            camera_prim=camera_prim,
            translate=spawn_location,
            orient=spawn_rotation,
            focallength=focallength,
            focus_point_translate=focus_point,
        )

        # set the xform setting back to original value
        SimulationUtil.update_xformOp_type(original_xform_order_setting)
        return camera_prim

    ##NOTE: function is copied to remove the dependency on the iac, should we move the function to utils?
    @classmethod
    def set_camera(cls, camera_prim, translate=None, orient=None, focallength=None, focus_point_translate=None):
        """set the camera rotation, position and focal length"""
        if not USDUtil.is_valid_prim(camera_prim):
            return

        curr_camera_pos = USDUtil.get_prim_pos(camera_prim)
        gf_translate = Gf.Vec3d(curr_camera_pos[0], curr_camera_pos[1], curr_camera_pos[2])
        if translate is not None:
            gf_translate = Gf.Vec3d(float(translate[0]), float(translate[1]), float(translate[2]))
            camera_prim.GetAttribute("xformOp:translate").Set(gf_translate)

        if orient is None:
            if focus_point_translate is not None:
                gf_focus_point_translate = Gf.Vec3d(
                    float(focus_point_translate[0]), float(focus_point_translate[1]), float(focus_point_translate[2])
                )
                orient = cls.lookat_to_quatf(
                    gf_focus_point_translate,
                    gf_translate,
                    Gf.Vec3d(0, 0, 1),
                )

        if orient is not None:
            camera_prim.GetAttribute("xformOp:orient").Set(Gf.Quatd(orient))

        if focallength is not None:
            camera_prim.GetAttribute("focalLength").Set(focallength)
