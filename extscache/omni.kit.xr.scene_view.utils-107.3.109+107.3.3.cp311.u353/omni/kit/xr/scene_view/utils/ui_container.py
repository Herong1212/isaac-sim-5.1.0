# Copyright (c) 2023-2025, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["UiContainer", "UiInput", "UiInputMotion", "UiInputToggle"]

import contextlib
from abc import ABC, abstractmethod

import omni.ui.scene
from carb.events import IEventStream
from omni.kit.xr.scene_view.core import InputButtonMap, InputType, XRSceneView

from .composable_manipulator import ManipulatorComponent
from .sceneview_utils import SceneViewAttachMode, SceneViewUtils
from .spatial_source import SpatialSource
from .transformable_manipulator import TransformableManipulator


class UiInput(ABC):
    @abstractmethod
    def push_input(self, scene_view: omni.ui.scene.SceneView): ...


class UiInputMotion(UiInput):
    def __init__(self, origin: list[float], direction: list[float]):
        assert len(origin) == 3
        assert len(direction) == 3

        self.__origin = origin
        self.__direction = direction

    def push_input(self, scene_view: omni.ui.scene.SceneView):
        if type(scene_view) is not XRSceneView:
            return

        input_stream: IEventStream = scene_view.input_event_stream
        input_stream.push(
            InputType.WorldSpaceMovement.value, payload={"origin": self.__origin, "direction": self.__direction}
        )


class UiInputToggle(UiInput):
    def __init__(self, input_map: InputButtonMap, pressed: bool):
        self.__input_map = input_map
        self.__state = pressed

    def push_input(self, scene_view: omni.ui.scene.SceneView):
        if type(scene_view) is not XRSceneView:
            return

        input_stream: IEventStream = scene_view.input_event_stream
        if self.__state is True:
            input_stream.push(InputType.ToggleActivated.value, payload={"input_map": self.__input_map.value})
        else:
            input_stream.push(InputType.ToggleDeactivated.value, payload={"input_map": self.__input_map.value})


class UiContainer:
    def __init__(
        self,
        initial_component: ManipulatorComponent | None = None,
        space_stack: SpatialSource | list[SpatialSource] | None = None,
        scene_view_type: type[omni.ui.scene.SceneView] = XRSceneView,
        scene_view_args: dict = {},
        attach_mode: SceneViewAttachMode = SceneViewAttachMode.ATTACH_TO_MAIN_VIEWPORT,
    ):
        """Construct a container for scene UI widgets.

        Contain and manages a UI Widget in 3D space. Construction of a view_class instance will
        be handled automatically, passing any kwargs to the view_class's constructor.

        In order to avoid performance hazards, you should avoid destroying and re-creating instances of this class.
        Instead, use the show() and hide() methods to control visibility.

        Args:
            initial_widget_component:
                The initial WidgetComponent you want contained and managed.
            space_stack:
                Either a single, or a list of, SpatialSource instance(s). Will be applied in-order; used to customize
                placement of the UI in world space.
            scene_view_type:
                The type of SceneView to use. Defaults to XRSceneView.
            attach_mode:
                The attach mode to use for the SceneView. Defaults to ATTACH_TO_MAIN_VIEWPORT.
        """
        # Construction args -> members
        self.__space_stack: list[SpatialSource] = []
        match space_stack:
            case SpatialSource():
                self.__space_stack.append(space_stack)
            case [*_]:
                self.__space_stack.extend(space_stack)

        # Member defaults
        self.__visible: bool = True

        # Create the initial scene hierarch along with a Manipulator for dealing with gestures
        # and models and rebuilding invalidated hierarchies
        self.__utils = SceneViewUtils(scene_view_type, scene_view_args, attach_mode)
        with self.__utils.scene_view.scene:
            with contextlib.ExitStack() as stack:
                # Because removing individual children from omni.ui.scene.Scene is explicitly forbidden, create
                # a root transform to be the a lightweight container that can "leak" without using up too much
                # memory. We will clear this to remove the more memory-intensive components when destroyed.
                self.__root = omni.ui.scene.Transform()
                self.__root.visible = self.__visible
                stack.enter_context(self.__root)

                for space in self.__space_stack:
                    stack.enter_context(space)

                self.__manipulator = TransformableManipulator()

        if initial_component is not None:
            self.__manipulator.add_component(initial_component)

    def __del__(self):
        SceneViewUtils.delete_later(self.__utils)
        SceneViewUtils.delete_later(self.__space_stack)
        SceneViewUtils.delete_later(self.__manipulator)

    def show(self):
        self.__visible = True
        if self.__root is not None:
            self.__root.visible = self.__visible

    def hide(self):
        self.__visible = False
        if self.__root is not None:
            self.__root.visible = self.__visible

    @property
    def root(self) -> omni.ui.scene.AbstractContainer:
        """WORKAROUND: Get a reference to the root container so you can clear its children."""
        # NOTE: This will be going away. This only exists to work around OM-112334.
        return self.__root

    @property
    def manipulator(self) -> TransformableManipulator:
        return self.__manipulator

    @property
    def visible(self):
        return self.__visible

    @visible.setter
    def visible(self, should_be_visible: bool):
        self.__visible = should_be_visible
        if self.__root is not None:
            self.__root.visible = self.__visible

    @property
    def scene_view(self) -> omni.ui.scene.SceneView:
        return self.__utils.scene_view
