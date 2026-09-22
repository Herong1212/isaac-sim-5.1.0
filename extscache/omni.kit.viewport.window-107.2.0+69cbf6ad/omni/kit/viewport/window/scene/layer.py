# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['ViewportSceneLayer']

import traceback
from typing import Sequence
import weakref

import carb
import omni.ui as ui
from omni.ui import scene as sc

from omni.kit.viewport.registry import RegisterScene
from .scenes import _flatten_matrix
from ..events import add_event_delegation, remove_event_delegation


class _SceneItem():
    def __init__(self, transform, instance, factory):
        self.__transform = transform
        self.__instance = instance
        self.__transform.visible = self.__instance.visible

    def __repr__(self) -> str:
        return f'<class {self.__class__.__name__} {self.__instance}>'

    @property
    def name(self) -> str:
        return self.__instance.name

    @property
    def visible(self) -> bool:
        return self.__transform.visible

    @visible.setter
    def visible(self, value: bool):
        self.__transform.visible = bool(value)
        self.__instance.visible = bool(value)

    @property
    def layers(self) -> Sequence:
        return ()

    @property
    def categories(self) -> Sequence:
        return self.__instance.categories

    @property
    def layer(self) -> Sequence:
        return self.__instance

    def destroy(self):
        instance, self.__instance = self.__instance, None
        xform, self.__transform = self.__transform, None
        if xform and callable(getattr(xform, "clear", None)):
            xform.clear()
        if instance and callable(getattr(instance, "destroy", None)):
            instance.destroy()


class ViewportSceneLayer:
    """Viewport Scene Overlay"""

    def __init__(self, factory_args, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__scene_view = None
        self.__dd_handler = None
        self.__view_change_sub = None
        self.__scene_items = {}
        self.__factory_args = factory_args
        self.__ui_frame = ui.Frame()
        RegisterScene.add_notifier(self.___scene_type_notification)

    def __del__(self):
        self.destroy()

    @property
    def layers(self):
        return self.__scene_items.values()

    def __view_changed(self, viewport_api):
        self.__scene_view.view = _flatten_matrix(viewport_api.view)
        self.__scene_view.projection = _flatten_matrix(viewport_api.projection)

    def ___scene_type_added(self, factory):
        # Push both our scopes onto the stack, to capture anything that's created
        if not self.__scene_view:
            viewport_api = self.__factory_args.get('viewport_api')
            if not viewport_api:
                raise RuntimeError('Cannot create a ViewportSceneLayer without a viewport')

            with self.__ui_frame:
                self.__scene_view = sc.SceneView(aspect_ratio_policy=sc.AspectRatioPolicy.STRETCH)
                add_event_delegation(weakref.proxy(self.__scene_view), viewport_api)

            # 1030 Tell the ViewportAPI that we have a SceneView we want it to be updating
            if hasattr(viewport_api, 'add_scene_view'):
                viewport_api.add_scene_view(self.__scene_view)
                self.__view_change_sub = None
            else:
                self.__view_change_sub = viewport_api.subscribe_to_view_change(self.__view_changed)

            # 1030 Fixes menu issue triggering selection (should remove hasattr pre 103-final)
            if hasattr(self.__scene_view, 'child_windows_input'):
                self.__scene_view.child_windows_input = False

        with self.__scene_view.scene:
            transform = sc.Transform()
            with transform:
                try:
                    # Shallow copy, but should help keeping any errant extensions from messing with one-another
                    instance = factory(self.__factory_args.copy())
                    if instance:
                        self.__scene_items[factory] = _SceneItem(transform, instance, factory)
                except Exception:  # noqa PLW0718
                    carb.log_error(f"Error loading {factory}. Traceback:\n{traceback.format_exc()}")

    def ___scene_type_removed(self, factory):
        scene = self.__scene_items.get(factory)
        if not scene:
            return

        scene.destroy()
        del self.__scene_items[factory]

        # Cleanup if we know we're empty
        if not self.__scene_items and self.__scene_view:
            self.__scene_view.destroy()
            self.__scene_view = None
            self.__dd_handler = None

    def ___scene_type_notification(self, factory, loading):
        if loading:
            self.___scene_type_added(factory)
        else:
            self.___scene_type_removed(factory)

    def destroy(self):
        remove_event_delegation(self.__scene_view)
        RegisterScene.remove_notifier(self.___scene_type_notification)
        self.__dd_handler = None
        for factory, instance in self.__scene_items.items():
            try:
                if hasattr(instance, 'destroy'):
                    instance.destroy()
            except Exception:  # noqa PLW0718
                carb.log_error(f"Error destroying {instance} from {factory}. Traceback:\n{traceback.format_exc()}")
        if self.__scene_view:
            scene_view, self.__scene_view = self.__scene_view, None
            scene_view.destroy()
            viewport_api = self.__factory_args.get('viewport_api')
            if viewport_api:
                if hasattr(viewport_api, 'remove_scene_view'):
                    viewport_api.remove_scene_view(scene_view)
                else:
                    self.__view_change_sub = None
        if self.__ui_frame:
            self.__ui_frame.destroy()
            self.__ui_frame = None
        self.__scene_items = {}
        self.__factory_args = None
