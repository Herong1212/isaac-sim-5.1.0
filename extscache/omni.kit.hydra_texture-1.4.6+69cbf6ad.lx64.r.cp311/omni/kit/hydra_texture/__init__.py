# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# Mark the interfaces that are public and documented
__all__ = [
    "create_hydra_texture",
    "IHydraTexture",
    "EVENT_TYPE_DRAWABLE_CHANGED",
    "EVENT_TYPE_HYDRA_ENGINE_CHANGED",
    "EVENT_TYPE_RENDER_SETTINGS_CHANGED"
]

from omni.kit.app import deprecated as _deprecated
import omni.ext


# Import the interfaces that are exposed publicly
from omni.hydratexture._hydra_texture import (
    acquire_hydra_texture_factory_interface,
    IHydraTexture,
    IHydraTextureFactory,
    EVENT_TYPE_DRAWABLE_CHANGED,
    EVENT_TYPE_HYDRA_ENGINE_CHANGED,
    EVENT_TYPE_RENDER_SETTINGS_CHANGED
)
from omni.hydratexture._hydra_texture import acquire_hydra_texture_factory_interface as _acquire_hydra_texture_factory_interface


@_deprecated("")
def _get_imgui_reference(self, *args, **kwargs):
    return self._get_imgui_reference(*args, **kwargs)

@_deprecated("")
def _get_drawable_ldr_resource(self, *args, **kwargs):
    return self._get_drawable_ldr_resource(*args, **kwargs)

setattr(IHydraTexture, "get_imgui_reference", _get_imgui_reference)
setattr(IHydraTexture, "get_drawable_ldr_resource", _get_drawable_ldr_resource)


@_deprecated("")
def acquire_hydra_texture_factory_interface():
    return _acquire_hydra_texture_factory_interface()


def create_hydra_texture(name: str,
                         width: int,
                         height: int,
                         usd_context_name: str = '',
                         usd_camera_path: str = '/OmniverseKit_Persp',
                         hydra_engine_name: str = 'rtx',
                         is_async: bool = True,
                         is_async_low_latency: bool = False,
                         hydra_tick_rate: int = 0,
                         engine_creation_flags: int = 0,
                         device_mask: int = 0,
                         *args, **kwargs):
    deprecated_arg = kwargs.get('is_asyncLowLatency', None)
    if deprecated_arg is not None:
        import carb
        carb.log_warn("is_asyncLowLatency is deprecated, please use is_async_low_latency")
        if is_async_low_latency is None:
            is_async_low_latency = deprecated_arg

    deprecated_arg = kwargs.get('hydraTickRate', None)
    if deprecated_arg is not None:
        import carb
        carb.log_warn("hydraTickRate is deprecated, please use hydra_tick_rate")
        if hydra_tick_rate is None:
            hydra_tick_rate = deprecated_arg

    return Extension._Extension__iface.create_hydra_texture(name, width, height, usd_context_name, usd_camera_path,
                                                            hydra_engine_name, is_async, is_async_low_latency, hydra_tick_rate,
                                                            engine_creation_flags, device_mask)

class Extension(omni.ext.IExt):
    __iface = None

    def on_startup(self):
        import omni.hydratexture
        Extension.__iface = _acquire_hydra_texture_factory_interface()
        Extension.__iface.startup()

    def on_shutdown(self):
        Extension.__iface.shutdown()
        Extension.__iface = None
