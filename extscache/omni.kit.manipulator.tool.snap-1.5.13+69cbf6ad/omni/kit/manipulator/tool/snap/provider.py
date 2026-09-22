# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from abc import ABC, abstractmethod
from typing import Callable, List, Sequence, Tuple, Type, Union

from omni.ui import scene as sc
from pxr import Gf, Sdf


class SnapProvider(ABC):
    """An abstract base class for snap providers in a manipulator tool.

    This class defines the interface for snap operations in manipulators. Implementors should provide functionality for snapping objects in 3D space based on the given parameters.

    Args:
        viewport_api: The API for interacting with the viewport in which snapping occurs.
    """

    def __init__(self, viewport_api):
        """Initializes the SnapProvider with the given viewport API.

        Args:
            viewport_api: The API for interacting with the viewport in which snapping occurs."""
        self._viewport_api = viewport_api

    def __del__(self):
        self.destroy()

    def destroy(self):
        """Cleans up any resources or state held by the provider."""
        ...

    def on_began(self, excluded_paths: List[Union[str, Sdf.Path]], **kwargs):
        """Initializes the snap operation with a list of paths to exclude from snapping.

        Args:
            excluded_paths: A list of paths that should be excluded from snapping calculations."""
        self._excluded_path = list(excluded_paths)

    def on_ended(self, **kwargs):
        """Resets the state of the provider when the snap operation ends."""
        self._excluded_path = []

    @abstractmethod
    def on_snap(
        self,
        xform: Gf.Matrix4d,
        ndc_location: Sequence[float],
        scene_view: sc.SceneView,
        want_orient: bool,
        want_keep_spacing: bool,
        on_snapped: Callable,
        conform_up_axis: str,
        enabled_providers: List["SnapProvider"],
        *args,
        **kwargs,
    ) -> bool:
        """Called when manipulator wants to perform a snap operation. Only the current selected snap provider will be called.

        Args:
            xform: Transformation of the current manipulator object.
            ndc_location: Location of the cursor in NDC space.
            scene_view: SceneView of the manipulator that triggers this snap request.
            want_orient: If the snap provider can change the orientation of the object to be snapped (e.g., conform to normal),
                         it should supply 'orient' to 'on_snapped' when 'want_orient' is True.
            want_keep_spacing: When multiple objects are selected, indicates if the original spacing between them should be maintained.
            on_snapped: A callback function receiving '**kwargs'. Depending on if the snap is successful and settings,
                        'position', 'path', 'orient' may be provided to it.
            conform_up_axis: The up axis to be used to conform to the target orientation.
            enabled_providers: All enabled providers for hint purposes. Do NOT modify the content.

        Returns:
            bool: True if the snap is successful. If the snap is an asynchronous operation, return True if the request of snapping is successful.
                  False if the snap failed or cannot be requested."""
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def get_name() -> str:
        """Returns the name/id of the provider. This is the internal name used for the snap manager.

        Returns:
            str: The name/id of the snap provider."""
        raise NotImplementedError()

    @classmethod
    def get_display_name(cls) -> str:
        """Returns the display name of the provider. It will be used on the menu. If not overridden, it falls back to get_name() instead.

        Returns:
            str: The display name of the snap provider."""
        return cls.get_name()

    @staticmethod
    @abstractmethod
    def can_orient() -> bool:
        """Returns if the provider may change the orientation of the object during a snap.

        Returns:
            bool: True if the snap provider can change orientation, False otherwise."""
        raise NotImplementedError()

    @classmethod
    def can_show_menu(cls, object: dict) -> bool:
        """Returns if the provider can appear in the menu list of all providers.

        Args:
            object: A dictionary containing context information about the object.

        Returns:
            bool: True if the provider can be shown in the menu, False otherwise."""
        if not cls.require_viewport_api():
            return True

        # While we can port Viewport 1.0 manipulator/snap to support legacy viewport_api, it is currently not requested,
        # so we still rely on Viewport 2.0 to provide viewport_api interface.
        if object.get("viewport_api", None):
            return True

        if object.get("main_toolbar", False):
            return True

        return False

    @staticmethod
    def can_enable_menu(object: dict) -> bool:
        """Returns if the provider can be enabled on the menu.

        Args:
            object: A dictionary containing context information about the object.

        Returns:
            bool: True if the provider can be enabled, False otherwise."""
        return True

    @staticmethod
    def require_viewport_api() -> bool:
        """Returns if the provider requires viewport_api to work.

        Returns:
            bool: True if viewport_api is required, False otherwise."""
        return True

    @staticmethod
    def get_order() -> float:
        """Returns the priority order of the snap provider. If more than one provider is enabled at the same time and both
        are able to provide snap results, the one with the lower order wins.

        Returns:
            float: The priority order of the provider."""
        return 0.0

    def _generate_picking_ray(self, ndc_location: Sequence[float]) -> Tuple[Gf.Vec3d, Gf.Vec3d, float]:
        """
        A helper function to generate picking ray from ndc cursor location.
        Only call it if self._viewport_api is not None.
        """
        ndc_near = (ndc_location[0], ndc_location[1], -1)
        ndc_far = (ndc_location[0], ndc_location[1], 1)
        view = self._viewport_api.view
        proj = self._viewport_api.projection
        view_proj_inv = (view * proj).GetInverse()

        origin = view_proj_inv.Transform(ndc_near)
        dir = view_proj_inv.Transform(ndc_far) - origin
        dist = dir.Normalize()

        return (origin, dir, dist)

    def _get_ndc_to_screen_matrix(self, scene_view: sc.SceneView) -> Gf.Matrix4d:
        if scene_view:
            width = scene_view.computed_width
            height = scene_view.computed_height
        else:
            # fallback to resolution if scene_view is not available
            # Note, self._viewport_api.resolution may not map 1:1 to the actual viewport size
            width = self._viewport_api.resolution[0]
            height = self._viewport_api.resolution[1]

        ndc_to_screen = Gf.Matrix4d()
        ndc_to_screen.SetScale(Gf.Vec3d(width * 0.5, height * 0.5, 0.5))
        ndc_to_screen.SetTranslateOnly(Gf.Vec3d(width * 0.5, height * 0.5, 0.5))

        return ndc_to_screen

    def _get_gf_type(self, xform: "Gf.Matrix4d") -> Type:
        import importlib

        # To handle pxr.Gf and usdrt.Gf uniformly based on input type
        gf_name = type(xform).__module__

        # in case xform type is not Gf type (e.g. None)
        # fallback to pxr
        if not gf_name.endswith("Gf"):
            gf_name = "pxr.Gf"

        return importlib.import_module(gf_name)
