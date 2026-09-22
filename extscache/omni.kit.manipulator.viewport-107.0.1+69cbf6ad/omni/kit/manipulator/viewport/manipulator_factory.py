# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from typing import List, Type

import carb.events
import omni.kit.app
import omni.ui as ui
from omni.ui import scene as sc

from .viewport_manipulator import ViewportManipulator

DRAW_ON_VP1 = True
SUPPORT_MULTI_VP1 = True


class ManipulatorPool:
    """
    A ManipulatorPool allows omni.ui.scene items in released Manipulator to be reused for a newly created Manipulator,
    instead having to rebuild them in the scene view.
    """

    def __init__(self, manipulator_class, scene_view: sc.SceneView):
        self._manipulator_class = manipulator_class
        self._scene_view = scene_view
        self._pool = []

    def create(self):
        if self._pool:
            manipulator = self._pool.pop()
        else:
            with self._scene_view.scene:
                manipulator = self._manipulator_class()

        return manipulator

    def release(self, manipulator):
        manipulator.enabled = False
        manipulator.model = None

        # Put the released manipulator back into the pool
        self._pool.append(manipulator)


class _ViewportWindowObject:
    def __init__(self, ui_window, ui_scene_view, draw_sub):
        self.window = ui_window
        self.scene_view = ui_scene_view
        self.draw_sub = draw_sub

    def __del__(self):
        self.draw_sub = None
        self.scene_view.destroy()
        self.window.destroy()


class ManipulatorFactory:
    _instance = None

    @classmethod
    def create_manipulator(cls, manipulator_class: Type, **kwargs):
        """
        Creates a ViewportManipulator object.
        Args: Arguments need to match manipulator_type's constructor
        """
        return cls._instance._create_manipulator(manipulator_class, **kwargs)

    @classmethod
    def destroy_manipulator(cls, *args, **kwargs):
        """
        Destroys a ViewportManipulator object.
        Args @see `_destroy_manipulator`
        """
        cls._instance._destroy_manipulator(*args, **kwargs)

    def startup(self):
        self._instances = dict()
        self._manipulators = set()
        self._pools = {}  # Each manipulator type needs a pool for each viewport.
        self._vp1_overlay_windows = {}
        self._viewport = None
        ManipulatorFactory._instance = self

        global DRAW_ON_VP1, SUPPORT_MULTI_VP1
        try:
            import omni.kit.viewport_legacy
            self._viewport = omni.kit.viewport_legacy.acquire_viewport_interface()
        except ImportError:
            DRAW_ON_VP1, SUPPORT_MULTI_VP1 = False, False

        if not DRAW_ON_VP1:
            return

        self._dead_vp1_overlay_windows = []
        self._vp1_instances = []

        from carb.eventdispatcher import get_eventdispatcher
        self._update_sub = get_eventdispatcher().observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_UPDATE,
            on_event=self._on_update,
            observer_name="omni.kit.manipulator.viewport manipulator_factory"
        )

    def shutdown(self):
        if DRAW_ON_VP1:
            self._vp1_overlay_windows.clear()
            self._dead_vp1_overlay_windows.clear()
            self._update_sub = None

        ManipulatorFactory._instance = None

    def _create_vp1_scene_view(self, instance):
        name = self._viewport.get_viewport_window_name(instance)
        window = self._viewport.get_viewport_window(instance)

        vp1_scene_window = ui.Window(name, visible=window.is_visible(), detachable=False)
        with vp1_scene_window.frame:
            vp1_scene_view = sc.SceneView(aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT)

        draw_event_stream = window.get_ui_draw_event_stream()
        draw_sub = draw_event_stream.create_subscription_to_pop(
            lambda event, instance=instance: self._on_vp_draw(event, instance)
        )

        self._vp1_overlay_windows[instance] = _ViewportWindowObject(vp1_scene_window, vp1_scene_view, draw_sub)
        return vp1_scene_view

    def _create_manipulator(self, manipulator_class: Type, **kwargs) -> ViewportManipulator:
        """
        This function creates a TransformManipulator object that has instances in ALL existing viewports and future created viewports.

        Args: Arguments need to match manipulator_type's constructor

        Return:
            ViewportManipulator object.
        """

        manipulator = ViewportManipulator(manipulator_class, **kwargs)

        pools = self._get_or_create_pools_for_manipulator_class(manipulator_class)
        for pool in pools:
            instance = pool.create()
            self._instances[instance] = pool
            manipulator.add_instance(instance)

        self._manipulators.add(manipulator)
        return manipulator

    def _destroy_manipulator(self, manipulator: ViewportManipulator):
        """
        Destroy the TransformManipulator and all its instances.
        """
        instances = manipulator.get_all_instances()
        for instance in instances:
            self._instances.pop(instance).release(instance)

        manipulator.clear_all_instances()
        self._manipulators.remove(manipulator)

    def _get_or_create_pools_for_manipulator_class(self, manipulator_class: Type) -> List[ManipulatorPool]:
        if manipulator_class not in self._pools:
            self._pools[manipulator_class] = [
                ManipulatorPool(manipulator_class, vp_obj.scene_view) for vp_obj in self._vp1_overlay_windows.values()
            ]

        return self._pools[manipulator_class]

    def _on_update(self, _):
        if DRAW_ON_VP1:
            # The visible state between vp 1.0 and the dummy ui.scene overlay window needs to be in sync.
            vp_instances_to_remove = []
            for vp_instance, vp_obj in self._vp1_overlay_windows.items():
                vp_window = self._viewport.get_viewport_window(vp_instance)
                if vp_window:
                    visible = vp_window.is_visible()
                    if visible != vp_obj.window.visible:
                        vp_obj.window.visible = visible
                        vp_obj.scene_view.visible = visible
                else:
                    # Destroy the draw_sub not, its what's caling this method
                    vp_obj.draw_sub = None
                    # Hide all ui as well
                    vp_obj.window.visible = False
                    vp_obj.scene_view.visible = False
                    vp_instances_to_remove.append(vp_instance)

            # Clear any pending dead Windows and Scenes
            self._dead_vp1_overlay_windows.clear()

            # Gather all the newly dead Windows and stash them for destruction later
            for vp_instance in vp_instances_to_remove:
                self._dead_vp1_overlay_windows.append(self._vp1_overlay_windows[vp_instance])
                del self._vp1_overlay_windows[vp_instance]
                self._vp1_instances.remove(vp_instance)

            # Since there's no callback for new VP1 creation, we check for change in update
            if SUPPORT_MULTI_VP1:
                vp1_instances = self._viewport.get_instance_list()
                if vp1_instances != self._vp1_instances:
                    # assuming Kit can only add viewport.
                    diff = list(set(vp1_instances) - set(self._vp1_instances))

                    for instance in diff:
                        scene_view = self._create_vp1_scene_view(instance)

                        # make a new pool for the manipulators
                        for manipulator_class, pools in self._pools.items():
                            pools.append(ManipulatorPool(manipulator_class, scene_view))

                        # create a new instance in the new viewport for each existing manipulators
                        for manipulator in self._manipulators:
                            manipulator_class = manipulator.manipulator_class
                            pools = self._get_or_create_pools_for_manipulator_class(manipulator_class)
                            pool = pools[-1]
                            instance = pool.create()
                            self._instances[instance] = pool
                            manipulator.add_instance(instance)

                    self._vp1_instances = vp1_instances

    def _on_vp_draw(self, event: carb.events.IEvent, vp_instance):
        vp_obj = self._vp1_overlay_windows.get(vp_instance)
        if not vp_obj:
            return

        vm = event.payload["viewMatrix"]
        pm = event.payload["projMatrix"]

        if pm[15] == 0.0:
            # perspective matrix matrix
            proj_matrix = sc.Matrix44(pm[0], pm[1], pm[2], pm[3], pm[4], pm[5], pm[6], pm[7], pm[8], pm[9], pm[10], pm[11], pm[12], pm[13], pm[14], pm[15])
            compensation = sc.Matrix44(1.0, 0.0, -0.0, 0.0, 0.0, 1.0, 0.0, -0.0, -0.0, 0.0, 1.0, -1.0, 0.0, -0.0, 0.0, -2.0)
            proj_matrix = proj_matrix * compensation
            # Flatten into list for model
            pm = [proj_matrix[0], proj_matrix[1], proj_matrix[2], proj_matrix[3],
                  proj_matrix[4], proj_matrix[5], proj_matrix[6], proj_matrix[7],
                  proj_matrix[8], proj_matrix[9], proj_matrix[10], proj_matrix[11],
                  proj_matrix[12], proj_matrix[13], proj_matrix[14], proj_matrix[15]]

        scene_view = vp_obj.scene_view
        scene_view.model.set_floats("projection", pm)
        scene_view.model.set_floats("view", vm)
