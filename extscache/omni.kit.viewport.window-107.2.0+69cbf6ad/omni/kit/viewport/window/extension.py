# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['ViewportWindowExtension']

import contextlib
from typing import Dict, List, Optional

import carb
import omni.ext
from .menu_entry import create_viewport_window_menu
from .dragdrop.usd_file_drop_delegate import UsdFileDropDelegate
from .dragdrop.usd_prim_drop_delegate import UsdShadeDropDelegate
from .dragdrop.material_file_drop_delegate import MaterialFileDropDelegate
from .dragdrop.audio_file_drop_delegate import AudioFileDropDelegate


class ViewportWindowExtension(omni.ext.IExt):
    """The Entry Point for Viewport Window"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__registered = None
        self.__vp_items = None
        self.__extension_enabled_hooks = []
        self.__extension_dependent_scenes = {}
        self.__default_drag_handlers = None

    def on_startup(self, extension_id: str):
        # Register the top-level application Window/Viewport/Viewport xxx menu items
        self.__vp_items = create_viewport_window_menu()
        # Register the default scenes to apply into the ViewportWindow
        self.__registered = self.__register_scenes()
        # Register the default drop-delegates for the ViewportWindow
        self.__default_drag_handlers = (
            UsdFileDropDelegate('/persistent/app/viewport/previewOnPeek'),
            UsdShadeDropDelegate(),
            MaterialFileDropDelegate(),
            AudioFileDropDelegate()
        )

    def on_shutdown(self):
        self.__extension_enabled_hooks = []
        self.__default_drag_handlers = None

        # Remove all instance variables and run their destruction
        vp_entries, self.__vp_items = self.__vp_items, None
        ext_dep_scenes, self.__extension_dependent_scenes = self.__extension_dependent_scenes, None
        reg_scenes, self.__registered = self.__registered, None

        if vp_entries:
            for vp_entry in vp_entries:
                vp_entry.destroy()

        if ext_dep_scenes:
            self.__unregister_scenes(ext_dep_scenes.values())

        if reg_scenes:
            self.__unregister_scenes(reg_scenes)

        from .events import set_ui_delegate
        set_ui_delegate(None)

    def __register_ext_dependent_scene(self, ext_name: str, loaded_exts: List[Dict], ext_manager: omni.ext.ExtensionManager,
                                       factory_dict: Dict, other_factories: Optional[Dict] = None):
        def is_extension_loaded(ext_name: str) -> bool:
            for ext in loaded_exts:
                if ext_name == omni.ext.get_extension_name(ext['id']):
                    return ext['enabled']
            return False

        def extension_loaded(ext_id: str, log_msg_str: str = "Removing"):
            nonlocal ext_name
            # UnRegister existing first
            if other_factories:
                carb.log_info(f'{log_msg_str} embedded ui.scenes fallbacks for "{ext_name}"')
                for factory_id, _ in other_factories.items():
                    self.__extension_dependent_scenes[factory_id] = None

            # Register new scene types second
            carb.log_info(f'Adding ui.scenes dependent on "{ext_name}"')
            from omni.kit.viewport.registry import RegisterScene
            self.__extension_dependent_scenes[ext_name] = [
                RegisterScene(factory, factory_id) for factory_id, factory in factory_dict.items()
            ]

        def extension_unloaded(ext_id: str):
            nonlocal ext_name
            # UnRegister scenes dependeing on extension first
            if self.__extension_dependent_scenes.get(ext_name):
                carb.log_info(f'Removing ui.scenes dependent on "{ext_name}"')
                self.__extension_dependent_scenes[ext_name] = None

            # Register replacement scene types second
            if other_factories:
                carb.log_info(f'Adding embedded ui.scenes fallbacks for "{ext_name}"')
                from omni.kit.viewport.registry import RegisterScene
                for factory_id, factory in other_factories.items():
                    self.__extension_dependent_scenes[factory_id] = RegisterScene(factory, factory_id)

        if not is_extension_loaded(ext_name):
            carb.log_info(f'{ext_name} is not loaded, adding extension enabled hooks')
            self.__extension_enabled_hooks += [
                ext_manager.subscribe_to_extension_enable(
                    extension_loaded,
                    extension_unloaded,
                    ext_name=ext_name,
                    hook_name="omni.kit.viewport.window-ext_name"
                )
            ]
            if other_factories:
                extension_unloaded(ext_name)
        else:
            extension_loaded(ext_name, "Ignoring")

    def __register_scenes(self):
        # Register all of the items that use omni.ui.scene to add functionality
        from omni.kit.viewport.registry import RegisterScene, RegisterViewportLayer

        app = omni.kit.app.get_app_interface()
        ext_mgr = app.get_extension_manager()
        exts_loaded = ext_mgr.get_extensions()
        registered = []

        # Register the Camera manipulator (if available)
        def delay_load_cam_manip(*args, **kwargs):
            from .manipulator.camera import ViewportCameraManiulatorFactory
            return ViewportCameraManiulatorFactory(*args, **kwargs)

        self.__register_ext_dependent_scene('omni.kit.manipulator.camera', exts_loaded, ext_mgr, {
            'omni.kit.viewport.window.manipulator.Camera': delay_load_cam_manip,
        })

        # Register the Selection manipulator (if available)
        def delay_load_selection_manip(*args, **kwargs):
            from .manipulator.selection import SelectionManipulatorItem
            return SelectionManipulatorItem(*args, **kwargs)

        self.__register_ext_dependent_scene('omni.kit.manipulator.selection', exts_loaded, ext_mgr, {
            'omni.kit.viewport.window.manipulator.Selection': delay_load_selection_manip,
        })

        # Register the legacy Gizmo drawing (if available) or the omni.ui.scene version when not
        from .scene.legacy import LegacyGridScene, LegacyLightScene, LegacyAudioScene
        from .scene.scenes import SimpleGrid
        self.__register_ext_dependent_scene("omni.kit.viewport.legacy_gizmos", exts_loaded, ext_mgr, {
            'omni.kit.viewport.window.scene.LegacyGrid': LegacyGridScene,
            'omni.kit.viewport.window.scene.LegacyLight': LegacyLightScene,
            'omni.kit.viewport.window.scene.LegacyAudio': LegacyAudioScene,
        }, {
            'omni.kit.viewport.window.scene.SimpleGrid': SimpleGrid
        })

        # Register other omni.scene.ui elements
        from .scene.scenes import SimpleGrid, SimpleOrigin, CameraAxisLayer
        registered = [
            RegisterScene(SimpleOrigin, 'omni.kit.viewport.window.scene.SimpleOrigin'),
            RegisterViewportLayer(CameraAxisLayer, 'omni.kit.viewport.window.CameraAxisLayer')
        ]

        # Register the context click menu
        from .manipulator.context_menu import ViewportClickFactory
        registered += [
            RegisterScene(ViewportClickFactory, 'omni.kit.viewport.window.manipulator.ContextMenu')
        ]

        # Register the Object click manipulator
        from .manipulator.object_click import ObjectClickFactory
        registered += [
            RegisterScene(ObjectClickFactory, 'omni.kit.viewport.window.manipulator.ObjectClick')
        ]

        # Register the HUD stats
        from .stats import ViewportStatsLayer
        registered.append(RegisterViewportLayer(ViewportStatsLayer, 'omni.kit.viewport.window.ViewportStats'))

        # Finally register the ViewportSceneLayer
        from .scene.layer import ViewportSceneLayer
        registered.append(RegisterViewportLayer(ViewportSceneLayer, 'omni.kit.viewport.window.SceneLayer'))
        return registered

    def __unregister_scenes(self, registered):
        for item in registered:
            with contextlib.suppress(Exception):
                item.destroy()
