# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["ViewportCameraState"]


from pxr import Gf, Sdf, Usd, UsdGeom


class ViewportCameraState:
    """A class that encapsulates the state of a camera within a viewport.

    It provides methods to query and manipulate the camera's position, target, and other properties, taking into account the stage's up axis and other USD-specific details.

    Args:
        camera_path: str
            The path to the camera in USD.
        viewport: The viewport associated with the camera state.
        time: Usd.TimeCode
            The time code for sampling the camera data."""

    def __init__(
        self, camera_path: str = None, viewport=None, time: Usd.TimeCode = None, **kwargs
    ):
        """Initializes the viewport camera state with a given camera path, viewport, and time

        Args:
            camera_path (str, optional): The path to the camera in USD. Defaults to the active viewport camera path if not provided.
            viewport (optional): The viewport to associate with the camera state. Defaults to the active viewport if not provided.
            time (Usd.TimeCode, optional): The time code for sampling the camera data. Defaults to Usd.TimeCode.Default() if not provided.

        Raises:
            RuntimeError: If no default or provided viewport is found."""
        if kwargs.get("force_legacy_api", None) != None:
            carb.log_error("force_legacy_api is deprecated arg to ViewportCameraState")

        if viewport is None:
            from omni.kit.viewport.utility import get_active_viewport

            viewport = get_active_viewport()
            if viewport is None:
                raise RuntimeError("No default or provided Viewport")

        self.__viewport_api = viewport
        self.__camera_path = str(camera_path if camera_path else viewport.camera_path)
        self.__time = Usd.TimeCode.Default() if time is None else time

    def get_world_camera_up(self, stage) -> Gf.Vec3d:
        """Returns the world space up direction for the camera based on the stage's up axis.

        Args:
            stage (Usd.Stage): The stage from which to retrieve the up axis information.

        Returns:
            Gf.Vec3d: The world space up direction vector for the camera."""
        up_axis = UsdGeom.GetStageUpAxis(stage) if stage else UsdGeom.Tokens.y
        if up_axis == UsdGeom.Tokens.y:
            return Gf.Vec3d(0, 1, 0)
        if up_axis == UsdGeom.Tokens.z:
            return Gf.Vec3d(0, 0, 1)
        if up_axis == UsdGeom.Tokens.x:
            return Gf.Vec3d(1, 0, 0)
        return Gf.Vec3d(0, 1, 0)

    @property
    def usd_camera(self) -> Usd.Prim:
        """Retrieves the USD camera primitive associated with the camera path.

        Returns:
            Usd.Prim: The USD camera primitive.

        Raises:
            RuntimeError: If the camera path does not correspond to a valid Usd.Prim or UsdGeom.Camera."""
        camera_prim = self.__viewport_api.stage.GetPrimAtPath(self.__camera_path)
        usd_camera = UsdGeom.Camera(camera_prim) if camera_prim else None
        if usd_camera:
            return usd_camera
        raise RuntimeError(f'"{self.__camera_path}" is not a valid Usd.Prim or UsdGeom.Camera')

    @property
    def position_world(self):
        """Gets the world position of the camera.

        Returns:
            Gf.Vec3d: The world position of the camera as a Gf.Vec3d vector."""
        return self.usd_camera.ComputeLocalToWorldTransform(self.__time).Transform(Gf.Vec3d(0, 0, 0))

    @property
    def target_world(self):
        """Gets the world space target position of the camera.

        Returns:
            Gf.Vec3d: The world space target position of the camera as a Gf.Vec3d vector."""
        local_coi = self.usd_camera.GetPrim().GetAttribute("omni:kit:centerOfInterest").Get(self.__time)
        return self.usd_camera.ComputeLocalToWorldTransform(self.__time).Transform(local_coi)

    def set_position_world(self, world_position: Gf.Vec3d, rotate: bool):
        """Sets the world position of the camera, with an option to rotate it to maintain its current orientation.

        Args:
            world_position (Gf.Vec3d): The new world position for the camera.
            rotate (bool): If True, the camera will be rotated to maintain its current orientation towards the center of interest.
        """
        usd_camera = self.usd_camera
        world_xform = usd_camera.ComputeLocalToWorldTransform(self.__time)
        parent_xform = usd_camera.ComputeParentToWorldTransform(self.__time)
        iparent_xform = parent_xform.GetInverse()
        initial_local_xform = world_xform * iparent_xform
        pos_in_parent = iparent_xform.Transform(world_position)
        if rotate:
            cam_prim = usd_camera.GetPrim()
            coi_attr = cam_prim.GetAttribute("omni:kit:centerOfInterest")
            prev_local_coi = coi_attr.Get(self.__time)
            coi_in_parent = iparent_xform.Transform(world_xform.Transform(prev_local_coi))
            cam_up = self.get_world_camera_up(cam_prim.GetStage())
            new_local_transform = Gf.Matrix4d(1).SetLookAt(pos_in_parent, coi_in_parent, cam_up).GetInverse()
        else:
            coi_attr, prev_local_coi = None, None
            new_local_transform = Gf.Matrix4d(initial_local_xform)

        new_local_transform = new_local_transform.SetTranslateOnly(pos_in_parent)

        import omni.kit.commands

        omni.kit.commands.create(
            "TransformPrimCommand",
            path=self.__camera_path,
            new_transform_matrix=new_local_transform,
            old_transform_matrix=initial_local_xform,
            time_code=self.__time,
            usd_context_name=self.__viewport_api.usd_context_name,
        ).do()
        if coi_attr and prev_local_coi:
            prev_world_coi = world_xform.Transform(prev_local_coi)
            new_local_coi = (new_local_transform * parent_xform).GetInverse().Transform(prev_world_coi)
            omni.kit.commands.create(
                "ChangePropertyCommand",
                prop_path=coi_attr.GetPath(),
                value=new_local_coi,
                prev=prev_local_coi,
                timecode=self.__time,
                usd_context_name=self.__viewport_api.usd_context_name,
                type_to_create_if_not_exist=Sdf.ValueTypeNames.Vector3d,
            ).do()

    def set_target_world(self, world_target: Gf.Vec3d, rotate: bool):
        """Sets the world target of the camera, with an option to rotate it. This can either move the camera to keep the same orientation and distance or just rotate the camera to look at the new target.

        Args:
            world_target (Gf.Vec3d): The new world target position for the camera.
            rotate (bool): If True, the camera will rotate to look at the new target. If False, the camera will move to maintain its orientation and distance relative to the target.
        """
        usd_camera = self.usd_camera
        world_xform = usd_camera.ComputeLocalToWorldTransform(self.__time)
        parent_xform = usd_camera.ComputeParentToWorldTransform(self.__time)
        iparent_xform = parent_xform.GetInverse()
        initial_local_xform = world_xform * iparent_xform

        cam_prim = usd_camera.GetPrim()
        coi_attr = cam_prim.GetAttribute("omni:kit:centerOfInterest")
        prev_local_coi = coi_attr.Get(self.__time)

        pos_in_parent = iparent_xform.Transform(initial_local_xform.Transform(Gf.Vec3d(0, 0, 0)))
        if rotate:
            # Rotate camera to look at new target, leaving it where it is
            cam_up = self.get_world_camera_up(cam_prim.GetStage())
            coi_in_parent = iparent_xform.Transform(world_target)
            new_local_transform = Gf.Matrix4d(1).SetLookAt(pos_in_parent, coi_in_parent, cam_up).GetInverse()
            new_local_coi = (new_local_transform * parent_xform).GetInverse().Transform(world_target)
        else:
            # Camera keeps orientation and distance relative to target
            # Calculate movement of center-of-interest in parent's space
            target_move = iparent_xform.Transform(world_target) - iparent_xform.Transform(
                world_xform.Transform(prev_local_coi)
            )
            # Copy the camera's local transform
            new_local_transform = Gf.Matrix4d(initial_local_xform)
            # And move it by the delta
            new_local_transform.SetTranslateOnly(pos_in_parent + target_move)

        import omni.kit.commands

        if rotate:
            omni.kit.commands.create(
                "ChangePropertyCommand",
                prop_path=coi_attr.GetPath(),
                value=new_local_coi,
                prev=prev_local_coi,
                timecode=self.__time,
                usd_context_name=self.__viewport_api.usd_context_name,
                type_to_create_if_not_exist=Sdf.ValueTypeNames.Vector3d,
            ).do()
        omni.kit.commands.create(
            "TransformPrimCommand",
            path=self.__camera_path,
            new_transform_matrix=new_local_transform,
            old_transform_matrix=initial_local_xform,
            time_code=self.__time,
            usd_context_name=self.__viewport_api.usd_context_name,
        ).do()
