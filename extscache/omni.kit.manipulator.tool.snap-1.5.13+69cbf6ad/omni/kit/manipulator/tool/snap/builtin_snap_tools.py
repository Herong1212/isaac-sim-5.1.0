# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["PrimSnap", "DepthBufferBasedSnap", "GridSnap", "PRIM_SNAP_NAME", "SURFACE_SNAP_NAME", "GRID_SNAP_NAME"]

from typing import Callable, List, Sequence, Union

import carb
import carb.settings
import omni.kit.raycast.query
import omni.usd
from omni.kit.viewport.utility import get_ground_plane_info
from omni.ui import scene as sc
from pxr import Sdf, UsdGeom

from .provider import SnapProvider

PRIM_SNAP_NAME = "Prim (Framebuffer Based)"
PRIM_SNAP_DISPLAY_NAME = "Prim"
SURFACE_SNAP_NAME = "Surface (Framebuffer Based)"
SURFACE_SNAP_DISPLAY_NAME = "Surface"
GRID_SNAP_NAME = "Grid"

GRID_ENABLED_SETTING_PATH = "/app/viewport/grid/enabled"


class PrimSnap(SnapProvider):  # pragma: no cover
    """A snap provider that allows snapping objects to the closest primitive based on provided NDC position.

    This provider is initialized with an optional list of excluded paths that should not be considered during the snapping process. It uses previous snap results to determine if a valid snap result can be provided, introducing a delay but solving multi-snap conflicts.

    Args:
        *args: Variable length argument list which will be forwarded to execute.
        **kwargs: Arbitrary keyword arguments that will be forwarded to execute.
    """

    def __init__(self, *args, **kwargs):
        """Initializes the PrimSnap provider.
        Args:
            *args: Variable length argument list which will be forwarded to execute.
            **kwargs: Arbitrary keyword arguments that will be forwarded to execute.
        """
        super().__init__(*args, **kwargs)
        self._previous_hit_prim_path = None

    def on_began(self, excluded_paths: List[Union[str, Sdf.Path]], **kwargs):
        """Called when the snap operation begins.

        Args:
            excluded_paths (List[Union[str, Sdf.Path]]): The list of paths to be excluded from picking.
        """
        super().on_began(excluded_paths)

        for path in self._excluded_path:
            self._viewport_api.usd_context.set_pickable(path.pathString, False)

        self._previous_hit_prim_path = None

    def on_ended(self, **kwargs):
        """Called when the snap operation ends."""
        self._previous_hit_prim_path = None

        for path in self._excluded_path:
            self._viewport_api.usd_context.set_pickable(path.pathString, True)

        super().on_ended()

    def on_snap(
        self,
        xform: "Gf.Matrix4d",
        ndc_location: Sequence[float],
        scene_view: sc.SceneView,
        want_orient: bool,
        want_keep_spacing: bool,
        on_snapped: Callable,
        enabled_providers: List[SnapProvider],
        *args,
        **kwargs,
    ) -> bool:
        """Attempts to snap to the closest prim based on the framebuffer.

        Args:
            xform (Gf.Matrix4d): The current transform of the object being snapped.
            ndc_location (Sequence[float]): The location in normalized device coordinates where the snap is being queried.
            scene_view (sc.SceneView): The scene view in which the snap is occurring.
            want_orient (bool): Indicates if the object needs to be oriented based on the snap result.
            want_keep_spacing (bool): When multiple objects are selected, indicates if the original spacing between them should be maintained.
            on_snapped (Callable): The callback function to be called once the snap result is available.
            enabled_providers (List[SnapProvider]): A list of enabled snap providers.

        Returns:
            bool: True if the snap can potentially provide a result, False otherwise.
        """
        Gf = self._get_gf_type(xform)

        def on_query_complete(path, pos, vp, *args):
            payload = {}
            payload["keep_spacing"] = want_keep_spacing
            payload["path"] = path
            if path:
                transform = vp.usd_context.compute_path_world_transform(path)
                payload["position"] = (transform[12], transform[13], transform[14])
                if want_orient:
                    rotation = Gf.Matrix3d(
                        transform[0],
                        transform[1],
                        transform[2],
                        transform[4],
                        transform[5],
                        transform[6],
                        transform[8],
                        transform[9],
                        transform[10],
                    )
                    rotation.Orthonormalize()
                    payload["orient"] = rotation.ExtractRotation()

            self._previous_hit_prim_path = path
            if self.__can_provide_result(enabled_providers):
                on_snapped(**payload)

        pixel_loc, vp2_api = self._viewport_api.map_ndc_to_texture_pixel(ndc_location)
        if vp2_api:
            vp2_api.request_query(
                pixel_loc,
                lambda path, pos, *args, vp=vp2_api: on_query_complete(path, pos, vp, *args),
                query_name="omni.kit.manipulator.prim.snap_tool.DepthBufferBasedSnap",
            )

            return self.__can_provide_result(enabled_providers)

        return False

    # Because the picking query is async, we cannot know yet in `on_snap` if it can find a valid result yet. This
    # would cause trouble when we have multiple snap options enabled. For example, if "grid" and "prim" are enabled,
    # during "prim" snap we cannot immediately know if it hits a prim and should skip "gird" snap.
    #
    # Thus we use self._previous_hit_prim_path as a hint from PREVIOUS snap. This is not perfect and introduced delay
    # for "prim" snap option, but somewhat solved the multi-snap problem.
    def __can_provide_result(self, enabled_providers: List[SnapProvider]) -> bool:
        """Determines if this snap provider can provide a result based on previous hits.

        Args:
            enabled_providers (List[SnapProvider]): A list of currently enabled snap providers.

        Returns:
            bool: True if this provider can provide a snap result, False otherwise.
        """
        # If self is the last entry in the enabled_providers, there's no more provider to fallback to, so we can safely
        # say it can provide a snap result without masking out other providers
        return enabled_providers[-1] == self or bool(self._previous_hit_prim_path)

    @staticmethod
    def get_name() -> str:
        """Returns the unique name of this snap provider.

        Returns:
            str: The name of the provider.
        """
        return PRIM_SNAP_NAME

    @classmethod
    def get_display_name(cls) -> str:
        """Returns the display name of this snap provider.

        Returns:
            str: The display name of the provider.
        """
        return PRIM_SNAP_DISPLAY_NAME

    @staticmethod
    def can_orient() -> bool:
        """Indicates if this snap provider can orient objects.

        Returns:
            bool: True if the provider can orient objects, False otherwise.
        """
        return True


class DepthBufferBasedSnap(SnapProvider):  # pragma: no cover
    """A snap provider assists in snapping objects within a 3D viewport.

    This snap provider utilizes raycasting or viewport picking queries to determine the snap location based on the depth buffer information. It is designed to work with viewport APIs that support 'rtx' engine or similar technologies for precise snapping to surfaces within the viewport.

    Args:
        viewport_api: The API used to interact with the viewport, enabling operations such as raycasting."""

    def __init__(self, viewport_api):
        """Initializes the DepthBufferBasedSnap snap provider.

        Args:
            viewport_api: The API used to interact with the viewport, enabling operations such as raycasting."""
        super().__init__(viewport_api)
        self._raycast_query = omni.kit.raycast.query.acquire_raycast_query_interface()
        self._previous_hit_prim_path = None

    def on_began(self, excluded_paths: List[Union[str, Sdf.Path]], **kwargs):
        """Called when the snap operation begins by setting up the excluded paths and preparing the USD context.

        Args:
            excluded_paths (List[Union[str, Sdf.Path]]): The list of paths to be excluded from picking."""
        super().on_began(excluded_paths)

        self._usd_context = None

        # TODO No need for gesture when VP1 has viewport_api
        self._gesture = kwargs.get("gesture", None)

        if self._viewport_api:
            self._usd_context = self._viewport_api.usd_context
        elif self._gesture._vp1_window_state:
            self._usd_context = omni.usd.get_context(self._gesture._vp1_window_state.get_usd_context_name())

        if self._usd_context:
            for path in self._excluded_path:
                self._usd_context.set_pickable(path.pathString, False)

        self._previous_hit_prim_path = None

    def on_ended(self, **kwargs):
        """Called when the snap operation ends by resetting the previous hit prim path and restoring pickability to the previously excluded paths."""
        self._previous_hit_prim_path = None

        if self._usd_context:
            for path in self._excluded_path:
                self._usd_context.set_pickable(path.pathString, True)

        super().on_ended()

    def on_snap(
        self,
        xform: "Gf.Matrix4d",
        ndc_location: Sequence[float],
        scene_view: sc.SceneView,
        want_orient: bool,
        want_keep_spacing: bool,
        on_snapped: Callable,
        conform_up_axis: str,
        enabled_providers: List[SnapProvider],
        *args,
        **kwargs,
    ) -> bool:
        """Attempts to snap an object to a surface within the viewport using either raycast or picking queries.

        Args:
            xform (Gf.Matrix4d): The current transform of the object being snapped.
            ndc_location (Sequence[float]): The location in normalized device coordinates where the snap is initiated.
            scene_view (sc.SceneView): The scene view in which the snap is occurring.
            want_orient (bool): Indicates if the object needs to be oriented based on the snap result.
            want_keep_spacing (bool): When multiple objects are selected, indicates if the original spacing between them should be maintained.
            on_snapped (Callable): The callback function to be called once the snap result is available.
            conform_up_axis (str): The axis to which the object should conform when oriented.
            enabled_providers (List[SnapProvider]): A list of enabled snap providers.

        Returns:
            bool: True if the snap can potentially provide a result, False otherwise."""
        # We only do this because viewport picking query doesn't return normal. However the underlying code it uses
        # is able to get normal information. It's not exposed due to VP1 compatibility.
        # TODO Remove the need for _snap_by_raycast_query when viewport picking query can return normal info.
        if self._viewport_api and self._viewport_api.hydra_engine == "rtx":
            return self._snap_by_raycast_query(
                xform, ndc_location, want_orient, want_keep_spacing, on_snapped, conform_up_axis, enabled_providers
            )

        else:
            return self._snap_by_picking_query(xform, ndc_location, want_keep_spacing, on_snapped, enabled_providers)

    def _snap_by_picking_query(
        self,
        xform: "Gf.Matrix4d",
        ndc_location: Sequence[float],
        want_keep_spacing: bool,
        on_snapped: Callable,
        enabled_providers: List[SnapProvider],
    ) -> bool:
        """Performs the snap operation using a viewport picking query.

        Args:
            xform (Gf.Matrix4d): The current transform of the object being snapped.
            ndc_location (Sequence[float]): The location in normalized device coordinates where the snap is initiated.
            want_keep_spacing (bool): When multiple objects are selected, indicates if the original spacing between them should be maintained.
            on_snapped (Callable): The callback function to be called once the snap result is available.
            enabled_providers (List[SnapProvider]): A list of enabled snap providers.

        Returns:
            bool: True if the snap can potentially provide a result, False otherwise."""
        Gf = self._get_gf_type(xform)

        if self._viewport_api:

            def on_query_complete(path, pos, *args):
                payload = {}
                # always keep spacing if nothing picked
                payload["keep_spacing"] = want_keep_spacing if path else True
                payload["path"] = path
                if path:
                    payload["position"] = Gf.Vec3d(pos[0], pos[1], pos[2])

                self._previous_hit_prim_path = path
                if self.__can_provide_result(enabled_providers):
                    on_snapped(**payload)

            pixel_loc, vp2_api = self._viewport_api.map_ndc_to_texture_pixel(ndc_location)
            if vp2_api:
                vp2_api.request_query(
                    pixel_loc,
                    on_query_complete,
                    query_name="omni.kit.manipulator.prim.snap_tool.DepthBufferBasedSnap",
                )
                return self.__can_provide_result(enabled_providers)

        # no need for this when VP1 has viewport_api
        elif self._gesture._vp1_window_state is not None:
            picked_world_pos = self._gesture._vp1_window_state.get_picked_world_pos()
            if picked_world_pos is not None:
                payload = {}
                payload["keep_spacing"] = want_keep_spacing
                payload["position"] = Gf.Vec3d(picked_world_pos[0], picked_world_pos[1], picked_world_pos[2])
                on_snapped(**payload)
                return self.__can_provide_result(enabled_providers)

        return False

    def _snap_by_raycast_query(
        self,
        xform: "Gf.Matrix4d",
        ndc_location: Sequence[float],
        want_orient: bool,
        want_keep_spacing: bool,
        on_snapped: Callable,
        conform_up_axis: str,
        enabled_providers: List[SnapProvider],
    ):
        """Performs the snap operation using a raycast query when the viewport API is using the 'rtx' engine.

        Args:
            xform (Gf.Matrix4d): The current transform of the object being snapped.
            ndc_location (Sequence[float]): The location in normalized device coordinates where the snap is initiated.
            want_orient (bool): Indicates if the object needs to be oriented based on the snap result.
            want_keep_spacing (bool): When multiple objects are selected, indicates if the original spacing between them should be maintained.
            on_snapped (Callable): The callback function to be called once the snap result is available.
            conform_up_axis (str): The axis to which the object should conform when oriented.
            enabled_providers (List[SnapProvider]): A list of enabled snap providers."""

        @carb.profiler.profile
        def query(ray, result: omni.kit.raycast.query.RayQueryResult, *args, **kwargs):
            nonlocal conform_up_axis, xform

            Gf = self._get_gf_type(xform)

            payload = {}
            # always keep spacing if nothing picked
            payload["keep_spacing"] = True

            if result.valid:
                path = result.get_target_usd_path()
                payload["path"] = path
                payload["keep_spacing"] = want_keep_spacing if path else True
                payload["position"] = Gf.Vec3d(result.hit_position[0], result.hit_position[1], result.hit_position[2])

                if want_orient:
                    stage = self._viewport_api.stage
                    stage_up_axis = UsdGeom.GetStageUpAxis(stage)

                    normal = Gf.Vec3d(result.normal[0], result.normal[1], result.normal[2])
                    normal.Normalize()

                    if conform_up_axis == "Stage":
                        conform_up_axis = stage_up_axis

                    if conform_up_axis == "X":
                        index = 0
                    elif conform_up_axis == "Y":
                        index = 1
                    else:
                        index = 2

                    if not xform:
                        xform = Gf.Matrix4d(1.0)

                    axis_to_align = xform.GetRow3(index).GetNormalized()
                    # in case xform is a usdrt matrix
                    axis_to_align = Gf.Vec3d(axis_to_align[0], axis_to_align[1], axis_to_align[2])
                    diff_rotation = Gf.Rotation(axis_to_align, normal)

                    # only set new normal and orient if anything needs to change
                    if diff_rotation.GetAngle() != 0:
                        curr_rotation = xform.GetOrthonormalized().ExtractRotation()
                        new_rotation = curr_rotation * diff_rotation

                        payload["normal"] = result.normal
                        payload["orient"] = new_rotation

                self._previous_hit_prim_path = path
            else:
                self._previous_hit_prim_path = None

            if self.__can_provide_result(enabled_providers):
                on_snapped(**payload)

        (origin, dir, dist) = self._generate_picking_ray(ndc_location)
        ray = omni.kit.raycast.query.Ray(origin, dir)
        self._raycast_query.submit_raycast_query(ray, query)

        return self.__can_provide_result(enabled_providers)

    # Because the picking query is async, we cannot know yet in `on_snap` if it can find a valid result yet. This
    # would cause trouble when we have multiple snap options enabled. For example, if "grid" and "prim" are enabled,
    # during "prim" snap we cannot immediately know if it hits a prim and should skip "gird" snap.
    #
    # Thus we use self._previous_hit_prim_path as a hint from PREVIOUS snap. This is not perfect and introduced delay
    # for "prim" snap option, but somewhat solved the multi-snap problem.
    def __can_provide_result(self, enabled_providers: List[SnapProvider]) -> bool:
        """Determines if this snap provider can provide a result based on previous hits.

        Args:
            enabled_providers (List[SnapProvider]): A list of currently enabled snap providers.

        Returns:
            bool: True if this provider can provide a snap result, False otherwise."""
        # If self is the last entry in the enabled_providers, there's no more provider to fallback to, so we can safely
        # say it can provide a snap result without masking out other providers. This can also prevent the delay
        # introduced by rejecting the first few frames before the first snap result comes back.
        return enabled_providers[-1] == self or bool(self._previous_hit_prim_path)

    @staticmethod
    def get_name() -> str:
        """Returns the unique name of this snap provider.

        Returns:
            str: The name of the provider."""
        return SURFACE_SNAP_NAME

    @classmethod
    def get_display_name(cls) -> str:
        """Returns the display name of this snap provider.

        Returns:
            str: The display name of the provider."""
        return SURFACE_SNAP_DISPLAY_NAME

    @staticmethod
    def can_orient() -> bool:
        """Indicates if this snap provider can orient objects.

        Returns:
            bool: True if the provider can orient objects, False otherwise."""
        return True

    @staticmethod
    def require_viewport_api() -> bool:
        """Indicates if this snap provider requires the viewport API to function.

        Returns:
            bool: False, as this provider does not require the viewport API."""
        return False

    @staticmethod
    def get_order() -> float:
        """Returns the order value for this snap provider, which can affect the priority of snapping operations.

        Returns:
            float: The order value, which is -1.0 indicating a high priority."""
        return -1.0


class GridSnap(SnapProvider):
    """A snap provider for snapping objects to grid intersections in a 3D scene.

    This class is used to align objects to a virtual grid within the scene. It calculates the closest grid intersection point to the desired snapping location and moves the object to that point. Grid snapping does not orient the object; it only affects its position.

    Args:
        *args: Variable length argument list which will be forwarded to execute.
        **kwargs: Arbitrary keyword arguments that will be forwarded to execute.
    """

    def __init__(self, *args, **kwargs):
        """Initializes the GridSnap provider.
        Args:
            *args: Variable length argument list which will be forwarded to execute.
            **kwargs: Arbitrary keyword arguments that will be forwarded to execute.
        """
        super().__init__(*args, **kwargs)
        self._settings = carb.settings.get_settings()

    def on_snap(
        self,
        xform: "Gf.Matrix4d",
        ndc_location: Sequence[float],
        scene_view: sc.SceneView,
        want_orient: bool,
        want_keep_spacing: bool,
        on_snapped: Callable,
        *args,
        **kwargs,
    ) -> bool:
        """Attempts to snap an object to the closest grid intersection point.

        Args:
            xform (Gf.Matrix4d): The current transform of the object being snapped.
            ndc_location (Sequence[float]): The location in normalized device coordinates where the snap is initiated.
            scene_view (sc.SceneView): The scene view in which the snap is occurring.
            want_orient (bool): Indicates if the object needs to be oriented based on the snap result.
            want_keep_spacing (bool): When multiple objects are selected, indicates if the original spacing between them should be maintained.
            on_snapped (Callable): The callback function to be called once the snap result is available.

        Returns:
            bool: True if a snap point is found, False otherwise."""
        if not self._settings.get(GRID_ENABLED_SETTING_PATH):
            return False

        from pxr import Gf

        OutGf = self._get_gf_type(xform)

        size = self._settings.get("/persistent/app/viewport/grid/scale")

        normal, planes = get_ground_plane_info(self._viewport_api)

        (origin, dir, dist) = self._generate_picking_ray(ndc_location)
        center = Gf.Vec3d(0)
        denom = Gf.Dot(normal, dir)
        if abs(denom) > 1e-6:
            t = Gf.Dot(center - origin, normal) / denom
            if t > 0:
                position = origin + dir * t

                if "x" in planes:
                    position[0] = round(position[0] / size) * size

                if "y" in planes:
                    position[1] = round(position[1] / size) * size

                if "z" in planes:
                    position[2] = round(position[2] / size) * size

                payload = {
                    "position": OutGf.Vec3d(position[0], position[1], position[2]),
                    "keep_spacing": want_keep_spacing,
                }
                on_snapped(**payload)
                return True

        return False

    @staticmethod
    def get_name() -> str:
        """Returns the unique name of the GridSnap provider.

        Returns:
            str: The name of the provider."""
        return GRID_SNAP_NAME

    @staticmethod
    def can_orient() -> bool:
        """Indicates if the GridSnap provider can orient objects.

        Returns:
            bool: False, as the GridSnap provider does not orient objects."""
        return False

    @staticmethod
    def can_enable_menu(object: dict) -> bool:
        """Determines if the snap to grid option should be available in the menu.

        Args:
            object (dict): The object to be considered for snapping.

        Returns:
            bool: True if the grid is enabled and snap to grid should be available, False otherwise."""
        # Do not allow snap to grid if grid is off
        return carb.settings.get_settings().get(GRID_ENABLED_SETTING_PATH)

    @staticmethod
    def get_order() -> float:
        """Returns the order value for the GridSnap provider, affecting the priority in snapping operations.

        Returns:
            float: The order value which is 1.0."""
        return 1.0
