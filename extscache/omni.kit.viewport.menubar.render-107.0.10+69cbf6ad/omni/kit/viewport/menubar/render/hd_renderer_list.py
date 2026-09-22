# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = []

import carb
from .hd_renderer_plugins import HdRendererPlugins

_log_issue = carb.log_warn


class HdRenderer:
    def __init__(self, *args):
        self.pluginID, self.displayName, self.usdPlugin = args

    def __repr__(self):
        return f'HdRenderer("{self.pluginID}", "{self.displayName}")'


class HdEngineRenderer:
    def __init__(self, *args):
        self.engineName, self.renderModePath = args
        self.renderers = []

    def __repr__(self):
        return f'HdEngineRenderer("{self.engineName}", "{self.renderModePath}", {self.renderers})'


class HdRendererList:
    RTX_RENDER_MODE_PATH = "/rtx/rendermode"
    IRY_RENDER_MODE_PATH = "/rtx/iray/rendermode"
    PXR_RENDER_MODE_PATH = "/pxr/rendermode"

    @classmethod
    def enabled_engines(cls):
        engines = carb.settings.get_settings().get("/renderer/enabled")
        if engines:
            # Return as an ordered list based on how renderers should display
            engines = [engine for engine in engines.split(",") if engine]
            for engine in ("rtx", "iray", "index", "pxr"):
                if engine in engines:
                    engines.remove(engine)
                    yield engine
        else:
            engines = ("rtx", "iray", "pxr")

        yield from engines

    def __init__(self, update_fn: callable = None, engines=None):
        # Use an OrderedDict to preserve incoming or app-default order when added
        from collections import OrderedDict
        self.__renderers = OrderedDict()
        self.__hd_plugins = None
        self.__updated_fn = update_fn

        if not engines:
            engines = self.enabled_engines()

        for hd_engine in engines:
            if hd_engine == "rtx":
                if carb.settings.get_settings().get("/rtx-transient/rtEnabled"):
                    self.__add_renderer(hd_engine, self.RTX_RENDER_MODE_PATH, "RaytracedLighting", "RTX - Real-Time")
                if carb.settings.get_settings().get("/rtx-transient/ptEnabled"):
                    self.__add_renderer(hd_engine, self.RTX_RENDER_MODE_PATH, "PathTracing", "RTX - Interactive (Path Tracing)")
                if carb.settings.get_settings().get("/rtx-transient/rt2Enabled"):
                    self.__add_renderer(hd_engine, self.RTX_RENDER_MODE_PATH, "RealTimePathTracing", "RTX - Real-Time 2.0")
                if carb.settings.get_settings().get("/rtx-transient/aperture/enabled"):
                    self.__add_renderer(
                        hd_engine, self.RTX_RENDER_MODE_PATH, "LightspeedAperture", "RTX - Aperture (Game Path Tracer)"
                    )
            elif hd_engine == "iray":
                self.__add_renderer(hd_engine, self.IRY_RENDER_MODE_PATH, "iray", "RTX - Accurate (Iray)")
                # No known setting to enable this.
                if False:  # noqa: PLW0125
                    self.__add_renderer(hd_engine, self.IRY_RENDER_MODE_PATH, "irt", "RTX - Accurate (Iray Interactive)")
            elif hd_engine == "index":
                self.__add_renderer(hd_engine, None, "index", "RTX - Scientific (IndeX)")
            elif hd_engine == "pxr":
                self.__hd_plugins = HdRendererPlugins(self.__add_pxr_renderers)
                self.__add_pxr_renderers(self.__hd_plugins)
            elif hd_engine:
                _log_issue(f"Unknown Hydra engine '{hd_engine}'.")

    def destroy(self):
        if self.__hd_plugins:
            self.__hd_plugins.destroy()
            self.__hd_plugins = None
        self.__renderers = {}
        self.__updated_fn = None

    def __del__(self):
        self.destroy()

    def __add_pxr_renderers(self, plugins):
        for renderer, desc in plugins.renderers:
            plugin_id = renderer.typeName
            display_name = desc.get("displayName")
            # Special case Storm's displayName which is still 'GL'
            if plugin_id == "HdStormRendererPlugin":
                display_name = "Pixar Storm"
            self.__add_renderer("pxr", self.PXR_RENDER_MODE_PATH, plugin_id, display_name, desc.get("plugin"))

    def __add_renderer(self, engine_name: str, render_mode_path: str, plugin_id: str, display_name=None, usd_plugin=None):
        if not display_name:
            display_name = plugin_id
        engine_renderers = self.__renderers.get(engine_name)
        if not engine_renderers:
            engine_renderers = HdEngineRenderer(engine_name, render_mode_path)
            self.__renderers[engine_name] = engine_renderers
        elif any(r.pluginID == plugin_id for r in engine_renderers.renderers):
            return
        engine_renderers.renderers.append(HdRenderer(plugin_id, display_name, usd_plugin))
        if self.__updated_fn:
            self.__updated_fn(self)

    @property
    def renderers(self):
        for k, v in self.__renderers.items():
            yield k, v
