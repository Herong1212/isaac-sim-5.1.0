# Copyright (c) 2023-2025, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["SceneViewUtils", "SceneViewAttachMode"]

import weakref
from enum import Enum, auto
from typing import Any, ClassVar, Dict, Generic, Protocol, Type, TypeGuard, TypeVar

import carb
import carb.events
import omni.kit.app
import omni.ui
from omni.kit.viewport.utility import get_active_viewport_window

from .custom_types import _TSceneView


# Enum for whether or not a scene view should be attached to the main viewport
class SceneViewAttachMode(Enum):
    """
    Enum for whether or not a scene view should be attached to the main viewport

    Options:
        ATTACH_TO_MAIN_VIEWPORT:
            The scene view will be attached to the main viewport. This is the default behavior,
            and should be expected to work correctly for normal SceneView usage.
        DO_NOT_ATTACH_TO_MAIN_VIEWPORT:
            The scene view will not be attached to the main viewport. Most normal interaction will
            still work from XR tools, however currently custom gesture subclasses and gesture managers
            are known to not work correctly with this option.
    """

    ATTACH_TO_MAIN_VIEWPORT = auto()
    DO_NOT_ATTACH_TO_MAIN_VIEWPORT = auto()


# Custom type checking for objects with a system_path attribute
# Functions like `hasattr` don't actually tend to narrow the type using type checkers,
# and I'm reluctant to rely on `isinstance` as that's not very future-proof. Apparently
# the "accepted" way to do this is with a custom `TypeGuard` function, which is returns
# a bool, but is annotated to return a `TypeGuard[NarrowedType]`, and which the type
# checkers can use to know what you're trying to do.
class HasSystemPath(Protocol):
    system_path: str


def _has_system_path(obj: Any) -> TypeGuard[HasSystemPath]:
    try:
        system_path = getattr(obj, "system_path")
        return isinstance(system_path, str)
    except:
        return False


class SceneViewUtils(Generic[_TSceneView]):
    """
    A utility class to help create and manage UI scene views for your extension.
    """

    __id: str
    __viewport_window: Any = None
    __scene_view_stack: omni.ui.ZStack | None = None
    __viewport_views: ClassVar[Dict[str, Any]] = {}
    __non_viewport_views: ClassVar[Dict[str, Any]] = {}
    __delete_later_queue: list[Any] = []
    __delete_later_subscription: carb.events.ISubscription | None = None
    __update_scene_views_sub: carb.events.ISubscription | None = None
    __update_scene_view_transforms_sub: carb.events.ISubscription | None = None

    @classmethod
    def _set_extension_id(cls, ext_id: str) -> None:
        """
        Initialize the class with data needed to function correctly.

        The extension ID is needed for creating supporting UI layers.

        Args:
            ext_id (str): The string name/id of the extension this comes from
        """

        from omni.kit.xr.core import XRCore, XRCoreEventType

        cls.__id = ext_id
        cls.__delete_later_subscription = (
            XRCore.get_singleton()
            .get_message_bus()
            .create_subscription_to_pop_by_type(
                XRCoreEventType.pre_sync_update,
                cls.__do_delete_later,
                name="SceneViewUtils Delete Later",
            )
        )

        # pre_sync_update
        cls.__update_scene_views_sub = (
            XRCore.get_singleton()
            .get_message_bus()
            .create_subscription_to_pop_by_type(XRCoreEventType.pre_sync_update, cls.update_scene_views)
        )

        # post_layer_update
        cls.__update_scene_view_transforms_sub = (
            XRCore.get_singleton()
            .get_message_bus()
            .create_subscription_to_pop_by_type(XRCoreEventType.post_layer_update, cls.update_scene_view_transforms)
        )

    @classmethod
    def _shutdown_extension(cls) -> None:
        """
        Clean up all created scene views and release them.

        Do not call this function except when the whole extension is shutting down.
        """

        # Remove any frames created by this class
        if cls.__viewport_window is not None:
            frames_attr_name = f"_{cls.__viewport_window.__class__.__name__}__added_frames"  # type: ignore
            if hasattr(cls.__viewport_window, frames_attr_name):  # type: ignore
                getattr(cls.__viewport_window, frames_attr_name).pop(cls.__id).clear()  # type: ignore
            else:
                carb.log_warn(f"[XR] No attribute found: {frames_attr_name}")

        # Unsubscribe from all subscriptions
        if cls.__update_scene_views_sub is not None:
            cls.__update_scene_views_sub.unsubscribe()
            cls.__update_scene_views_sub = None

        if cls.__update_scene_view_transforms_sub is not None:
            cls.__update_scene_view_transforms_sub.unsubscribe()
            cls.__update_scene_view_transforms_sub = None

        if cls.__delete_later_subscription is not None:
            cls.__delete_later_subscription.unsubscribe()
            cls.__delete_later_subscription = None

        # Process any remaining items in the delete later queue
        cls.__do_delete_later(None)

    @classmethod
    def find_scene_view(cls, element_path: str) -> _TSceneView | None:
        """
        Find a scene view by its element path.

        Args:
            element_path (str): The USD path (string) to the desired element.

        Returns:
            _TSceneView | None: The scene view if found, otherwise None.
        """

        def __check_for_view(source, element_path) -> _TSceneView | None:
            found = [(key, val) for key, val in source.items() if element_path.startswith(key)]
            if found:
                found_key, found_scene = found[0]
                result = found_scene()
                if result is not None:
                    return result

                # This view has somehow been dropped, so remove it from the list
                carb.log_warn(f"[XR] Removing tracked scene_view that was dropped: {found_key}")
                del source[found_key]
            return None

        # Grab known views which are parents of the supplied element path
        result = __check_for_view(cls.__viewport_views, element_path)
        if result is not None:
            return result

        return __check_for_view(cls.__non_viewport_views, element_path)

    @classmethod
    def update_scene_views(cls, event: carb.events.IEvent) -> None:
        """
        Update all scene views, including input events, etc. This shouldn't be called during the XR sync loop,
        as that should only be updating transforms.
        """
        try:
            for _, val in cls.__non_viewport_views.items():
                scene_view = val()
                if scene_view is not None:
                    scene_view.run_update()
        except Exception as e:
            carb.log_warn(f"[XR] Error updating scene views: {e}")

    @classmethod
    def update_scene_view_transforms(cls, event: carb.events.IEvent) -> None:
        """
        Update only scene view transforms to ensure they are up-to-date and synced with (especially) XR transforms.
        This gets called during the XR sync loop.
        """
        try:
            layer_path = event.payload["layerName"]

            for system_path, val in cls.__non_viewport_views.items():
                if system_path.startswith(layer_path):
                    scene_view = val()
                    if scene_view is not None:
                        scene_view.update_transforms()
        except Exception as e:
            carb.log_warn(f"[XR] Error updating scene view transforms: {e}")

    def __init__(
        self,
        scene_view_type: Type[_TSceneView],
        scene_view_args: dict = {},
        attach_mode: SceneViewAttachMode = SceneViewAttachMode.ATTACH_TO_MAIN_VIEWPORT,
    ) -> None:
        """
        Create a new instance of the utility class.

        This is a lightweight container around a singleton dictionary of SceneView types, and will automatically create
        up to one SceneView of each SceneView-descended class.

        Deleting or allowing this object to be deleted has no real affect on the overall system, so feel free to create
        and remove them as needed, or to hold on to one.

        When the utility extension is unloaded, all associated scene views will be cleaned up and removed.

        Args:
            scene_view_type (Type[_TSceneView]):
                Class / type of omni.ui.scene.SceneView or child to create using this utility. Each utility instance
                can only manage one type of SceneView, so if you need multiple for some reason (likely not), you would
                need multiple instances.
        """

        self.__scene_view: _TSceneView
        self.__scene_view_type = scene_view_type
        self.__workaround_container: omni.ui.Frame | None = None

        # Create the scene view, choosing whether to attach it to the viewport or now
        match attach_mode:
            case SceneViewAttachMode.ATTACH_TO_MAIN_VIEWPORT:
                self.__scene_view = self.__create_scene_view_in_viewport(**scene_view_args)
            case SceneViewAttachMode.DO_NOT_ATTACH_TO_MAIN_VIEWPORT:
                self.__scene_view = self.__create_scene_view_without_viewport(**scene_view_args)

    def __create_scene_view_without_viewport(self, **scene_view_args) -> _TSceneView:
        scene_view = self.__scene_view_type(**scene_view_args)

        system_path = ""
        if _has_system_path(scene_view):
            system_path = scene_view.system_path

        SceneViewUtils.__non_viewport_views[system_path] = weakref.ref(scene_view)

        return scene_view

    def __create_scene_view_in_viewport(self, **scene_view_args) -> _TSceneView:
        scene_view: _TSceneView

        if SceneViewUtils.__viewport_window is None:
            SceneViewUtils.__viewport_window = get_active_viewport_window()
        if SceneViewUtils.__scene_view_stack is None:
            with SceneViewUtils.__viewport_window.get_frame(SceneViewUtils.__id):
                SceneViewUtils.__scene_view_stack = omni.ui.ZStack()
        with SceneViewUtils.__scene_view_stack:
            # NOTE: There's not really a way to remove elements from this stack. It's a minor "leak", but it's
            # known. The workaround of course is for all users to never destroy and re-make the same scene view;
            # but we can't rely on end users knowing that. We will look for a better solution, but for now we
            # accept the "leak" and potential performance hit.

            # NOTE: The "leak" is small -- the real concern is the accumulation of objects that need to be
            # processed every frame. It wouldn't take too many iterations of re-creating the same views before
            # we would expect to see a noticeable performance hit.

            # NOTE: omni.ui.Frame is probably the most lightweight, basic type we can leak.
            self.__workaround_container = omni.ui.Frame()
            with self.__workaround_container:
                scene_view = self.__scene_view_type(**scene_view_args)

        if SceneViewUtils.__viewport_window.viewport_api is not None:
            SceneViewUtils.__viewport_window.viewport_api.add_scene_view(scene_view)

        if _has_system_path(scene_view):
            carb.log_info(f"[XR] adding viewport scene_view {scene_view.system_path}")
            SceneViewUtils.__viewport_views[scene_view.system_path] = weakref.ref(scene_view)
            carb.log_info(f"[XR] tracked viewport scene_view count: {len(SceneViewUtils.__viewport_views)}")
        assert scene_view is not None

        return scene_view

    def __del__(self):
        if _has_system_path(self.__scene_view):
            carb.log_info(f"[XR] removing known scene_view {self.__scene_view.system_path}")
            if self.__scene_view.system_path in SceneViewUtils.__viewport_views:
                del SceneViewUtils.__viewport_views[self.__scene_view.system_path]
            if self.__scene_view.system_path in SceneViewUtils.__non_viewport_views:
                del SceneViewUtils.__non_viewport_views[self.__scene_view.system_path]
            carb.log_info(
                f"[XR] tracked scene_views"
                f"(viewport: {len(SceneViewUtils.__viewport_views)}, "
                f"non-viewport: {len(SceneViewUtils.__non_viewport_views)}"
            )

        if SceneViewUtils.__viewport_window is not None:
            if SceneViewUtils.__viewport_window.viewport_api is not None:  # type: ignore
                if SceneViewUtils.__viewport_window.viewport_api is not None:  # type: ignore
                    SceneViewUtils.__viewport_window.viewport_api.remove_scene_view(self.__scene_view)  # type: ignore

        # NOTE: __workaround_container is a workaround. It's leaked for the moment.
        if self.__workaround_container is not None:
            self.__workaround_container.clear()

    @classmethod
    def delete_later(cls, item: Any):
        """
        Queue this instance for deletion at a later time.

        This is useful when you want to delete an instance, but you are currently in a state where it is unsafe to do so.
        """
        cls.__delete_later_queue.append(item)

    @classmethod
    def __do_delete_later(cls, _: carb.events.IEvent | None) -> None:
        """
        Process the delete later queue.
        """
        if len(cls.__delete_later_queue) > 0:
            carb.log_info(f"[XR] Late-deleting {len(cls.__delete_later_queue)} XR UI objects")
            cls.__delete_later_queue.clear()

    @property
    def scene_view(self) -> _TSceneView:
        """
        Get the SceneView instance associated with the class specified when this instance was created

        Returns:
            scene_view (_TSceneView): the scene view associated with the class specified at creation time

        """
        return self.__scene_view
