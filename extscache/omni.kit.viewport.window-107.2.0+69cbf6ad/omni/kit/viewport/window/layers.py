# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['ViewportLayers']

import traceback
from typing import Callable, Optional, Sequence
import weakref

from pxr import Usd, Sdf

import carb
import omni.ui as ui
import omni.timeline
import omni.usd

from omni.kit.viewport.registry import RegisterViewportLayer
from omni.kit.widget.viewport import ViewportWidget
from omni.kit.widget.viewport.api import ViewportAPI

from .legacy import _resolve_viewport_setting


DEFAULT_LAYER_ORDER = [
    'omni.kit.viewport.window.ViewportLayer',
    'omni.kit.viewport.window.SceneLayer',
    'omni.kit.viewport.menubar.MenuBarLayer'
]


# Class to wrap the underlying omni.kit.widget.viewport.ViewportWidget into the layer-system
class _ViewportLayerItem:
    def __init__(self, viewport):
        self.__viewport = viewport

    @property
    def visible(self) -> bool:
        return bool(self.__viewport.visible)

    @visible.setter
    def visible(self, value: bool):
        self.__viewport.visible = bool(value)

    # TODO: Would be nice to express AOV's as more controllable items
    @property
    def name(self) -> str:
        return 'Render (color)'

    @property
    def layers(self) -> Sequence:
        return ()

    @property
    def categories(self) -> Sequence:
        return ('viewport',)

    def destroy(self):
        # Respond to destroy, but since this doesn't own the underlying viewport, don't forward to it
        pass

    # Since we're exposing ourself in the 'viewport' category expose the .viewport_api getter
    @property
    def viewport_api(self):
        return self.__viewport.viewport_api


class ViewportLayers:
    """The Viewport Layers Widget
       Holds a single viewport and manages the order of layers within a ui.ZStack
    """

    # For convenience and access, promote the underlying viewport api to this widget
    @property
    def viewport_api(self) -> "ViewportAPI":
        return self.__viewport.viewport_api if self.__viewport else None

    @property
    def viewport_widget(self) -> "ViewportAPI":
        return weakref.proxy(self.__viewport)

    @property
    def layers(self) -> Sequence:
        yield from self.__viewport_layers.values()

    def get_frame(self, name: str) -> None:  # noqa PLE0202
        carb.log_error("ViewportLayers.get_frame called but parent has not provided an implementation.")

    def __init__(self,
                 viewport_id: str,
                 usd_context_name: str = '',
                 get_frame_parent: Optional[Callable] = None,
                 hydra_engine_options: Optional[dict] = None,
                 **ui_kwargs):
        self.__viewport_layers = {}
        self.__ui_frame = None
        self.__viewport = None
        self.__zstack = None
        self.__timeline = omni.timeline.get_timeline_interface()
        self.__timeline_sub = self.__timeline.get_timeline_event_stream().create_subscription_to_pop_by_type(
            omni.timeline.TimelineEventType.CURRENT_TIME_TICKED,
            self.__on_timeline_event)
        if get_frame_parent:
            self.get_frame = get_frame_parent

        isettings = carb.settings.get_settings()
        # If no resolution specified, see if a knnown setting exists to use as an initial value
        # This is a little complicated due to serialization but also preservation of legacy global defaults
        resolution = _resolve_viewport_setting(viewport_id, 'resolution', isettings)
        # If no -new- resolution setting was resolved, check against legacy setting
        if resolution is None:
            width = isettings.get('/app/renderer/resolution/width')
            height = isettings.get('/app/renderer/resolution/height')
            # Both need to be set and valid to be used
            if (width is not None) and (height is not None):
                # When either width or height is 0 or less, Viewport will be set to use UI size
                if (width > 0) and (height > 0):
                    resolution = (width, height)
                else:
                    resolution = 'fill_frame'

        # Also resolve any resolution scaling to use for the Viewport
        res_scale = _resolve_viewport_setting(viewport_id, 'resolutionScale', isettings,
                                              '/app/renderer/resolution/multiplier')

        # Our 'frame' is really a Z-Stack so that we can push another z-stack on top of the render
        self.__ui_frame = ui.ZStack(**ui_kwargs)
        with self.__ui_frame:
            ui.Rectangle(style_type_name_override='ViewportBackgroundColor')
            self.__viewport = ViewportWidget(usd_context_name, resolution=resolution,
                                             viewport_api=ViewportAPI(usd_context_name, viewport_id,
                                                                      self.__viewport_updated),
                                             hydra_engine_options=hydra_engine_options)

            # Apply the resolution scaling now that the Viewport exists
            if res_scale is not None:
                self.__viewport.viewport_api.resolution_scale = res_scale

        # Expose the viewport itself into the layer system (factory is the key, so use the contructor)
        self.__viewport_layers[_ViewportLayerItem] = _ViewportLayerItem(weakref.proxy(self.__viewport))
        # Now add the notification which will be called for all layers already registered and any future ones.
        RegisterViewportLayer.add_notifier(self.__viewport_layer_event)

    def __viewport_updated(self, camera_path: Sdf.Path, stage: Usd.Stage):
        if not self.__viewport:
            return
        # Get the current time-line time and push that to the Viewport
        if stage:
            time = self.__timeline.get_current_time()
            time = Usd.TimeCode(omni.usd.get_frame_time_code(time, stage.GetTimeCodesPerSecond()))
        else:
            time = Usd.TimeCode.Default()
        # Push the time, and let the Viewport handle any view-changed notifications
        self.__viewport._viewport_changed(camera_path, stage, time)  # noqa PLW0212

    def __on_timeline_event(self, e: carb.events.IEvent):
        if self.__viewport:
            assert e.type == int(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED)
            viewport_api = self.__viewport.viewport_api
            self.__viewport_updated(viewport_api.camera_path, viewport_api.stage)

    def __viewport_layer_event(self, loaded_factory, loading):
        if loading:
            # A layer was registered
            # Preserve the 'ViewportLayer' in our dictionary
            vp_layer = self.__viewport_layers[_ViewportLayerItem]
            del self.__viewport_layers[_ViewportLayerItem]
            for instance in self.__viewport_layers.values():
                instance.destroy()
            self.__viewport_layers = {_ViewportLayerItem: vp_layer}
            # Create the factory argument
            factory_args = {
                'usd_context_name': self.viewport_api.usd_context_name,
                'layer_provider': weakref.proxy(self),
                'viewport_api': self.viewport_api
            }

            # Clear out the old stack
            if self.__zstack:
                self.__zstack.destroy()
                self.__zstack.clear()
            with self.__ui_frame:
                self.__zstack = ui.ZStack()
                # Rebuild all the other layers according to our order
                for factory_id, factory in RegisterViewportLayer.ordered_factories(DEFAULT_LAYER_ORDER):  # noqa B007
                    # Skip over things that weren't found (they may have not been registered or enabled yet)
                    if not factory:
                        continue
                    with self.__zstack:
                        try:
                            self.__viewport_layers[factory] = factory(factory_args.copy())
                        except Exception:  # noqa PLW0718
                            carb.log_error(f"Error creating layer {factory}. Traceback:\n{traceback.format_exc()}")
        else:
            if loaded_factory in self.__viewport_layers:
                self.__viewport_layers[loaded_factory].destroy()
                del self.__viewport_layers[loaded_factory]
            else:
                carb.log_error(f'Removing {loaded_factory} which was never instantiated')

    def __del__(self):
        self.destroy()

    def destroy(self):
        self.__timeline_sub = None
        RegisterViewportLayer.remove_notifier(self.__viewport_layer_event)
        for factory, instance in self.__viewport_layers.items():  # noqa PLW0612
            instance.destroy()
        self.__viewport_layers = {}
        if self.__zstack:
            self.__zstack.destroy()
            self.__zstack = None
        if self.__viewport:
            self.__viewport.destroy()
            self.__viewport = None
        if self.__ui_frame:
            self.__ui_frame.destroy()
            self.__ui_frame = None
        self.get_frame = None
        self.__timeline = None
