# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["RendererMenuContainer"]

import asyncio
from functools import partial
import os
from typing import Any, Callable, Dict, List, Sequence, TYPE_CHECKING

import carb
from carb.eventdispatcher import get_eventdispatcher
from omni.kit.app import SettingChangeSubscription
from omni.kit.viewport.menubar.core import (
    IconMenuDelegate,
    ViewportMenuDelegate,
    SettingComboBoxModel,
    ViewportMenuContainer,
    RadioMenuCollection,
    SelectableMenuItem,
    MenuDisplayStatus,
)
import omni.ui as ui
import omni.usd

from .hd_renderer_list import HdRendererList
from .menu_item.single_render_menu_item import SingleRenderMenuItem
from .style import UI_STYLE
if TYPE_CHECKING:
    from .menu_item.single_render_menu_item import SingleRenderMenuItemBase

SHADING_MODE = "/exts/omni.kit.viewport.menubar.render/shadingMode"
LIGHTING_MODE = "/rtx/useViewLightingMode"
MATERIAL_MODE = "/exts/omni.kit.viewport.menubar.render/materialMode"
RENDER_ACTIONS_MAP = {
    "omni.kit.viewport.actions::set_renderer_rtx_realtime": "RTX - Real-Time",
    "omni.kit.viewport.actions::set_renderer_rtx_pathtracing": "RTX - Interactive (Path Tracing)" ,
    "omni.kit.viewport.actions::set_renderer_iray": "RTX - Accurate (Iray)",
    "omni.kit.viewport.actions::set_renderer_pxr_storm": "Pixar Storm",
    "omni.kit.viewport.actions::toggle_wireframe": "Wireframe",
}


class BoolStringModel(ui.SimpleBoolModel):
    def __init__(self, setting_path: str, *args, value_map: Sequence[str] = ("default", "disabled"), **kwargs):
        super().__init__(*args, **kwargs)
        self.__setting_path = setting_path
        self.__value_map = value_map
        self.__settings = carb.settings.get_settings()
        self.__setting_sub = SettingChangeSubscription(setting_path, self.__setting_changed)  # noqa: PLW0238

    def __del__(self):
        self.destroy()

    def destroy(self):
        self.__setting_sub = None  # noqa: PLW0238

    def __setting_changed(self, item: carb.dictionary._dictionary.Item, event_type: carb.settings.ChangeEventType):

        if event_type == carb.settings.ChangeEventType.CHANGED:
            self._value_changed()

    def get_value_as_string(self) -> bool:
        return self.__settings.get(self.__setting_path)

    def get_value_as_bool(self) -> bool:
        return self.__settings.get(self.__setting_path) == self.__value_map[1]

    def get_value(self) -> bool:
        return self.get_value_as_bool()

    def set_value(self, value: bool) -> bool:
        cur_value = self.__settings.get(self.__setting_path)
        str_value = self.__value_map[bool(value)]
        changed = cur_value != str_value
        if changed:
            self.__settings.set(self.__setting_path, str_value)
            return True
        return changed


class FlashLightModel(BoolStringModel):
    def __init__(self, setting_path: str, *args, **kwargs):
        super().__init__(setting_path, value_map=(False, True))


class DisableMaterialModel(BoolStringModel):
    def set_value(self, value: bool) -> bool:
        changed = super().set_value(value)
        if changed:
            dbg_type = 0 if value else -1
            settings = carb.settings.get_settings()
            settings.set("/rtx/debugMaterialType", dbg_type)
            wire_mode = settings.get("/rtx/wireframe/mode")
            if wire_mode:
                wire_mode = 2 if dbg_type == 0 else 1
                settings.set("/rtx/wireframe/mode", wire_mode)
        return changed


class ShadingModeModel(BoolStringModel):
    def set_value(self, value: bool) -> bool:
        changed = super().set_value(value)
        if changed:
            wire_mode = 0
            settings = carb.settings.get_settings()
            if value:
                settings.set("/rtx/debugView/target", "")
                if self.get_value_as_string() == "wireframe":
                    flat_shade = settings.get("/rtx/debugMaterialType") == 0
                    wire_mode = 2 if flat_shade else 1
            settings.set("/rtx/wireframe/mode", wire_mode)

        return changed


class DebugShadingModel(SettingComboBoxModel):
    def __init__(self, viewport_api):
        debug_view_items = {}

        hd_engine = viewport_api.hydra_engine
        if hd_engine == "rtx":
            debug_view_items.update({
                "Off": "",
                "3D Motion Vectors [WARNING: Flashing Colors]": "targetMotion",
                "3D Motion Vector Arrows [WARNING: Flashing Colors]": "targetMotionArrows",
                "3D Final Motion Vector Arrows [WARNING: Flashing Colors]": "finalMotion",
                "Barycentrics": "barycentrics",
                "Beauty After Tonemap": "beautyPostTonemap",
                "Beauty Before Tonemap": "beautyPreTonemap",
                "Depth": "depth",
                "Instance ID": "instanceId",
                "Interpolated Normal": "normal",
                "Heat Map: Any Hit": "anyHitCountHeatMap",
                "Heat Map: Intersection": "intersectionCountHeatMap",
                "Heat Map: Timing": "timingHeatMap",
                "SDG: Cross Correspondence": "sdgCrossCorrespondence",
                "SDG: Motion": "sdgMotion",
                "Semantic ID": "semanticId",
                "Stable ID": "stableId",
                "Non-Visual Material ID": "nonVisualMaterialId",
                "Tangent U": "tangentu",
                "Tangent V": "tangentv",
                "Texture Coordinates 0": "texcoord0",
                "Texture Coordinates 1": "texcoord1",
                "Triangle Normal": "triangleNormal",
                "Wireframe": "wire",
            })

            render_mode = viewport_api.render_mode
            if render_mode == "RaytracedLighting":
                debug_view_items.update({
                    "RT Ambient Occlusion": "ao",
                    "RT Caustics": "caustics",
                    "RT Diffuse GI": "indirectDiffuse",
                    "RT Diffuse GI (Not Accumulated)": "indirectDiffuseNonAccum",
                    "RT Diffuse Reflectance": "diffuseReflectance",
                    "RT Material Normal": "materialGeometryNormal",
                    "RT Matte Object Compositing Alpha": "matteObjectAlpha",
                    "RT Matte Object Mask": "matteObjectMask",
                    "RT Matte Object View Before Postprocessing": "matteBeforePostprocessing",
                    "RT Radiance": "radiance",
                    "RT Reflections": "reflections",
                    "RT Reflections (Not Accumulated)": "reflectionsNonAccum",
                    "RT Reflections 3D Motion Vectors [WARNING: Flashing Colors]": "reflectionsMotion",
                    "RT Roughness": "roughness",
                    "RT Specular Reflectance": "reflectance",
                    "RT Subsurface Radiance": "subsurface",
                    "RT Subsurface Transmission Radiance": "subsurfaceTransmission",
                    "RT Translucency": "translucency",
                    "RT World Position": "worldPosition",
                })
            elif render_mode == "PathTracing":
                debug_view_items.update({
                    "PT Adaptive Sampling Error [WARNING: Flashing Colors]": "PTAdaptiveSamplingError",
                    "PT Denoised Result": "pathTracerDenoised",
                    "PT Noisy Result": "pathTracerNoisy",
                    "PT AOV Pre-Denoised Result": "aov:ePtPreDenoisedResult",
                    "PT AOV Background": "aov:ePtBackground",
                    "PT AOV Diffuse Filter": "aov:ePtDiffuseFilter",
                    "PT AOV Direct Illumation": "aov:ePtDirectIllumation",
                    "PT AOV Global Illumination": "aov:ePtGlobalIllumination",
                    "PT AOV Illuminance": "aov:ePtIlluminance",
                    "PT AOV Luminance": "aov:ePtLuminance",
                    "PT AOV Motion Vectors": "aov:ePtMotion",
                    "PT AOV Reflections": "aov:ePtReflections",
                    "PT AOV Reflection Filter": "aov:ePtReflectionFilter",
                    "PT AOV Refractions": "aov:ePtRefractions",
                    "PT AOV Refraction Filter": "aov:ePtRefractionFilter",
                    "PT AOV Subsurface Scattering": "aov:ePtSubsurfaceScattering",
                    "PT AOV Subsurface Filter": "aov:ePtSubsurfaceFilter",
                    "PT AOV Self-Illumination": "aov:ePtSelfIllumination",
                    "PT AOV Volumes": "aov:ePtVolumes",
                    "PT AOV World Normal": "aov:ePtWorldNormal",
                    "PT AOV World Position": "aov:ePtWorldPos",
                    "PT AOV View Normal": "aov:ePtViewNormal",
                    "PT AOV Z-Depth": "aov:ePtZDepth",
                    "PT AOV Multimatte0": "PTAOVMultimatte0",
                    "PT AOV Multimatte1": "PTAOVMultimatte1",
                    "PT AOV Multimatte2": "PTAOVMultimatte2",
                    "PT AOV Multimatte3": "PTAOVMultimatte3",
                    "PT AOV Multimatte4": "PTAOVMultimatte4",
                    "PT AOV Multimatte5": "PTAOVMultimatte5",
                    "PT AOV Multimatte6": "PTAOVMultimatte6",
                    "PT AOV Multimatte7": "PTAOVMultimatte7",
                })

        # Sort the above alphabetically
        names, values = [], []
        if debug_view_items:
            for k, v in (debug_view_items.items()):
                names.append(k)
                values.append(v)
        else:
            names = []
            values = []

        super().__init__("/rtx/debugView/target", names, values=values)

    def _on_change(self, *args, **kwargs) -> None:
        super()._on_change(*args, **kwargs)
        current_value = self._settings.get(self._path)
        if current_value == '':
            if self._settings.get(SHADING_MODE).startswith("custom:"):
                self._settings.set(SHADING_MODE, "default")
        else:
            self._settings.set(SHADING_MODE, f"custom:{current_value}")
            self._settings.set("/rtx/wireframe/mode", 0)

    def _get_current_index_by_value(self, value: Any, default: int = 0) -> int:
        # OMPE-3099: When switching renderer or render mode, debug view target is not changed, but it may not be in current list,
        # Show current as none instead of first value
        return super()._get_current_index_by_value(value, default=-1)

    def on_current_changed(self):
        # Do not change debug view target settings when current debug view target may not in list
        current_index = self.current_index.as_int
        if current_index >= 0:
            super().on_current_changed()

    def empty(self):
        children = self.get_item_children(None)
        return len(children) == 0 if children else True

    def __del__(self):
        self.destroy()


class MenuContext():
    def __init__(self, root_menu: ui.Menu, viewport_api, renderer_changed_fn: Callable):
        super().__init__()
        self.__root_menu = root_menu
        self.__viewport_api = viewport_api
        self.__destroyable = {}
        self.__usd_context_sub = get_eventdispatcher().observe_event(
            observer_name="omni.kit.viewport.menubar.render:renderer_menu_container",
            event_name=viewport_api.usd_context.stage_event_name(omni.usd.StageEventType.SETTINGS_LOADED),
            on_event=lambda _: self.set_default_state()
        )
        self.__renderer_changed_fn = renderer_changed_fn
        self.__rs_changed_sub = viewport_api.subscribe_to_render_settings_change(self.__render_settings_changed)

    def __render_settings_changed(self, *args, **kwargs):
        self.__renderer_changed_fn(self, self.__viewport_api)

    def set_default_state(self):
        stage = self.__viewport_api.stage
        if stage:
            render_settings = stage.GetMetadata('customLayerData').get('renderSettings', {})

            dbg_mat_type = render_settings.get('rtx:debugMaterialType')
            wire_mode = render_settings.get('rtx:wireframe:mode')
            dbg_target = render_settings.get('rtx:debugView:target')

            settings = carb.settings.get_settings()

            settings.set(MATERIAL_MODE, "disabled" if dbg_mat_type == 0 else "default")
            if wire_mode:
                shade_mode = "wireframe"
            elif dbg_target:
                shade_mode = f"custom:{dbg_target}"
            else:
                shade_mode = "default"
            settings.set(SHADING_MODE, shade_mode)

    @property
    def root_menu(self) -> ui.Menu:
        return self.__root_menu

    @property
    def delegate(self) -> ui.MenuDelegate:
        return self.root_menu.delegate

    @property
    def viewport_api(self):
        return self.__viewport_api

    def add_destroyables(self, key: str, destroyables: Sequence):
        self.destroy(key)
        self.__destroyable[key] = destroyables

    def destroy(self, key: str = None):
        if key is not None:
            items = self.__destroyable.get(key)
            if items:
                for item in items:
                    item.destroy()
                del self.__destroyable[key]
            return

        if self.__usd_context_sub:
            self.__usd_context_sub = None

        if self.__rs_changed_sub:
            self.__rs_changed_sub = None

        if self.__destroyable:
            for items in self.__destroyable.values():
                for item in items:
                    item.destroy()
            self.__destroyable = {}

        if self.__root_menu:
            self.__root_menu.destroy()
            self.__root_menu = None


class RendererMenuContainer(ViewportMenuContainer):
    """The menu with the list of renderers"""

    PXR_IN_USE = "/app/viewport/omni_hydra_pxr_in_use"
    __enabled_engines = None

    def __init__(self):
        super().__init__(
            name="Renderer",
            delegate=None,
            visible_setting_path="/exts/omni.kit.viewport.menubar.render/visible",
            order_setting_path="/exts/omni.kit.viewport.menubar.render/order",
            style=UI_STYLE,
            actions_map=RENDER_ACTIONS_MAP,
        )
        self.__render_list = None
        self.__render_state_subs = None
        self._folder_exist_popup = None
        self.__menu_item_type = SingleRenderMenuItem
        self.__pending_render_change = False
        self.__menu_context: Dict[int, MenuContext] = {}
        self.__app_ready_sub = None  # noqa: PLW0238
        self.__ext_manager_hooks = None  # noqa: PLW0238
        self.dirty = False

        # FIXME: Grab this now (on startup) as OmniHydraEngineFactoryBase can mutate it on first activation
        if not RendererMenuContainer.__enabled_engines:
            RendererMenuContainer.__enabled_engines = HdRendererList.enabled_engines()

        # We can possibly drop these subscriptions when Viewport-1 is retired; but for now we have to watch for some
        # common events if both VP-1 and VP-2 are sharing a hydra engine instance.
        settings = carb.settings.get_settings()
        self.__render_state_subs = (
            settings.subscribe_to_node_change_events(self.PXR_IN_USE, self.__dirty_menu),
            settings.subscribe_to_node_change_events("/pxr/renderers", self.__dirty_menu),
            settings.subscribe_to_node_change_events(HdRendererList.PXR_RENDER_MODE_PATH, self.__dirty_menu),
            settings.subscribe_to_node_change_events(HdRendererList.RTX_RENDER_MODE_PATH, self.__dirty_menu),
            settings.subscribe_to_node_change_events(HdRendererList.IRY_RENDER_MODE_PATH, self.__dirty_menu),
            settings.subscribe_to_node_change_events("/renderer/enabled", self.__dirty_renderers),
        )

        # Watch for extension enable/disable to support background renderer loading
        self.__setup_extenion_watching()

    def __setup_extenion_watching(self):
        import omni.kit.app  # noqa PLW0621
        app = omni.kit.app.get_app()
        if not app:  # pragma: no cover
            return

        def setup_ext_hooks(*args, **kwargs):
            import omni.ext  # noqa PLW0621
            ext_manager = omni.kit.app.get_app().get_extension_manager()
            if ext_manager:
                self.__ext_manager_hooks = ext_manager.subscribe_to_extension_enable(  # noqa PLW0238
                    self.__ext_enabled, self.__ext_disabled,
                    # ext_name="omni.hydra.*",
                    hook_name="omni.kit.viewport.menubar.render.extension_change",
                )

        if not app.is_app_ready():
            self.__app_ready_sub = get_eventdispatcher().observe_event(  # noqa PLW0238
                event_name=omni.kit.app.GLOBAL_EVENT_APP_READY, on_event=setup_ext_hooks, observer_name="omni.kit.viewport.menubar.render.app_ready"
            )
        else:
            setup_ext_hooks()

    def set_menu_item_type(self, menu_item_type: Callable[..., "SingleRenderMenuItemBase"]):
        """
        Set the menu type for the default created renderer

        Args:
            menu_item_type: callable that will create the menu item
        """
        if menu_item_type is None:
            menu_item_type = SingleRenderMenuItem
        if self.__menu_item_type != menu_item_type:
            self.__menu_item_type = menu_item_type
            self.__dirty_menu()

    def __hide_on_click(self, viewport_context: Dict = None):
        return viewport_context.get("hide_on_click", False) if viewport_context else False

    def destroy(self):
        self.__app_ready_sub = None  # noqa PLW0238
        self.__ext_manager_hooks = None  # noqa PLW0238

        if self.__render_list:
            self.__render_list.destroy()
            self.__render_list = None

        if self.__render_state_subs:
            settings = carb.settings.get_settings()
            for sub in self.__render_state_subs:
                settings.unsubscribe_to_change_events(sub)
            self.__render_state_subs = None

        for context in self.__menu_context.values():
            context.destroy()
        self.__menu_context = {}

        super().destroy()

    @property
    def render_list(self):
        """Returns the list of available renderers"""
        if not self.__render_list:

            def set_dirty(*args):
                self.__dirty_menu()

            self.__render_list = HdRendererList(set_dirty, self.__enabled_engines)
        return self.__render_list

    def build_fn(self, viewport_context: Dict):
        """Entry point for the menu bar"""
        viewport_api = viewport_context.get('viewport_api')
        viewport_api_id = viewport_api.id

        menu_context = self.__menu_context.get(viewport_api_id)
        if menu_context:
            menu_context.destroy()

        root_menu = ui.Menu(self.name,
                            delegate=IconMenuDelegate("Renderer", text=True),
                            on_build_fn=partial(self._build_menu, viewport_context),
                            style=self._style,
                            hide_on_click=self.__hide_on_click(viewport_context)
                            )
        self.__menu_context[viewport_api_id] = MenuContext(root_menu, viewport_api, self.__set_menu_label)

        # It will set the renderer name
        self.__dirty_menu()

    def get_display_status(self, factory_args: dict) -> MenuDisplayStatus:
        viewport_api_id = factory_args['viewport_api'].id
        context = self.__menu_context[viewport_api_id]
        return MenuDisplayStatus.LABEL if context.delegate.text_visible else MenuDisplayStatus.MIN

    def get_require_size(self, factory_args: dict, expand: bool = False) -> float:
        display_status = self.get_display_status(factory_args)
        viewport_api_id = factory_args['viewport_api'].id
        context = self.__menu_context[viewport_api_id]
        if expand:
            return 0 if display_status == MenuDisplayStatus.LABEL else context.delegate.text_size
        return 0

    def expand(self, factory_args: dict) -> None:
        viewport_api_id = factory_args['viewport_api'].id
        context = self.__menu_context[viewport_api_id]
        if context.delegate.text_visible:
            return

        context.delegate.text_visible = True
        if context.root_menu:
            context.root_menu.invalidate()

    def can_contract(self, factory_args: dict) -> bool:
        display_status = self.get_display_status(factory_args)
        return display_status == MenuDisplayStatus.LABEL

    def contract(self, factory_args: dict) -> bool:
        viewport_api_id = factory_args['viewport_api'].id
        context = self.__menu_context[viewport_api_id]
        display_status = self.get_display_status(factory_args)
        if display_status == MenuDisplayStatus.LABEL:
            context.delegate.text_visible = False
            if context.root_menu:
                context.root_menu.invalidate()
            return True
        return False

    def __add_destroyables(self, viewport_api, key: str, destroyables: Sequence):
        menu_context = self.__menu_context.get(viewport_api.id)
        assert menu_context, f"No MenuContext for {viewport_api} (id: {viewport_api.id})"
        menu_context.add_destroyables(key, destroyables)

    def __build_renderers(self, viewport_context):
        """Build the menu with the list of the renderers"""
        viewport_api = viewport_context["viewport_api"]
        hide_on_click = self.__hide_on_click(viewport_context)

        settings = carb.settings.get_settings()

        # See if the omni.hydra.pxr engine is available for use in this Viewport
        pxr_eng_available = self.__pxr_available(settings, viewport_api)
        # Example: HdStormRendererPlugin:Storm
        pxr_rnd_available = settings.get("/pxr/renderers")

        # Example: rtx
        current_engine_name = viewport_api.hydra_engine
        self.__menu_items = []
        for engine_name, hd_engine_renderer in self.render_list.renderers:
            is_pxr = engine_name == "pxr"
            is_engine_current = engine_name == current_engine_name

            # Only sort renderers of the engine alphabetically for pxr renderers
            if is_pxr:
                renderers = sorted(
                    hd_engine_renderer.renderers, key=lambda hd_renderer: hd_renderer.displayName.lower()
                )
            else:
                renderers = hd_engine_renderer.renderers

            # Example: /rtx/rendermode
            render_mode_path = hd_engine_renderer.renderModePath
            # Get current from settings
            if is_engine_current:
                # Example: RaytracedLighting
                current_render_mode = settings.get(render_mode_path) if render_mode_path else None
            else:
                current_render_mode = None

            # Show hotkey placeholder for menuitems if hotkey in any menuitem
            show_hotkey_placeholder = any(self._get_menu_item_hotkey_text(hd_renderer.displayName) for hd_renderer in renderers)

            for hd_renderer in renderers:
                # Example: RaytracedLighting
                render_mode = hd_renderer.pluginID

                enabled = True
                if is_pxr:  # noqa SIM102
                    # Check the renderer hasn't actually de-registered itself
                    # And only enable these menu items if omni.hydra.pxr engine is available for this Viewport instance
                    if not pxr_eng_available or (pxr_rnd_available and pxr_rnd_available.find(render_mode) == -1):
                        enabled = False

                checked = is_engine_current and (render_mode == current_render_mode if render_mode_path else True)

                def apply(viewport_api, engine_name, render_mode_path, render_mode):
                    """Switch the current renderer"""
                    settings = carb.settings.get_settings()
                    # Set the legacy /renderer/active change for anyone that may be watching for it
                    settings.set('/renderer/active', engine_name)
                    # Now set the render-mode on that engine too
                    if render_mode_path:
                        settings.set(render_mode_path, render_mode)
                    # Finally apply it to the backing texture
                    viewport_api.set_hd_engine(engine_name, render_mode)

                menu_item = self.__menu_item_type(
                    hd_renderer.displayName,
                    engine_name,
                    hd_engine_renderer,
                    hd_renderer,
                    viewport_api,
                    enabled=enabled,
                    checked=checked,
                    hide_on_click=hide_on_click,
                    triggered_fn=partial(apply, viewport_api, engine_name, render_mode_path, render_mode),
                    hotkey_text=self._get_menu_item_hotkey_text(hd_renderer.displayName),
                    show_hotkey_placeholder=show_hotkey_placeholder,
                )
                self.__menu_items.append(menu_item)

    def __build_shading_modes(self, viewport_context):
        """Build the shading modes"""
        hide_on_click = self.__hide_on_click(viewport_context)

        viewport_api = viewport_context.get("viewport_api")
        engine_name = viewport_api.hydra_engine
        is_rtx_or_pxr = engine_name in ("rtx", "pxr")

        show_hotkey_placeholder = any(self._get_menu_item_hotkey_text(item) for item in ["Default", "Wireframe"])

        default_shade_mode = SelectableMenuItem(
            "Default",
            model=ShadingModeModel(SHADING_MODE, value_map=("wireframe", "default")),
            delegate=ViewportMenuDelegate(force_checked=True, show_hotkey_placeholder=show_hotkey_placeholder),
            hide_on_click=hide_on_click,
            toggle=False,
            enabled=is_rtx_or_pxr,
            hotkey_text=self._get_menu_item_hotkey_text("Default"),
        )

        wireframe_mode = SelectableMenuItem(
            "Wireframe",
            model=ShadingModeModel(SHADING_MODE, value_map=("default", "wireframe")),
            delegate=ViewportMenuDelegate(force_checked=True, show_hotkey_placeholder=show_hotkey_placeholder),
            hide_on_click=hide_on_click,
            toggle=False,
            enabled=is_rtx_or_pxr,
            hotkey_text=self._get_menu_item_hotkey_text("Wireframe"),
        )

        debug_mode = RadioMenuCollection(
            "Debug View",
            DebugShadingModel(viewport_api),
            hide_on_click=hide_on_click,
        )
        debug_mode.enabled = not debug_mode._model.empty()  # noqa: PLW0212

        self.__add_destroyables(viewport_api, 'omni.kit.viewport.menubar.render.shading_modes', [default_shade_mode, wireframe_mode, debug_mode])

        if not debug_mode.enabled:
            carb.settings.get_settings().set("/rtx/debugView/target", "")

        async def toggle_states():
            import omni.kit.app  # noqa: PLW0621
            await omni.kit.app.get_app().next_update_async()
            if default_shade_mode.model:
                default_shade_mode.delegate.checked = default_shade_mode.model.as_bool
            if wireframe_mode.model:
                wireframe_mode.delegate.checked = wireframe_mode.model.as_bool

        asyncio.ensure_future(toggle_states())

    def __build_render_options(self, viewport_context):
        # Get the useViewLightingMode and turn on/off shadows based on it
        viewport_api = viewport_context["viewport_api"]
        engine_name = viewport_api.hydra_engine
        is_iray = engine_name == "iray"
        is_rtx_or_pxr = engine_name in ["rtx", "pxr"]

        flash_light = SelectableMenuItem("Camera Light",
                                         model=FlashLightModel(LIGHTING_MODE),
                                         enabled=is_rtx_or_pxr)

        disable_mat = SelectableMenuItem("Disable Materials (White Mode)",
                                         model=DisableMaterialModel(MATERIAL_MODE),
                                         enabled=is_rtx_or_pxr or is_iray)

        self.__add_destroyables(viewport_api, 'omni.kit.viewport.menubar.render.render_options', [flash_light, disable_mat])

    def __build_rendering_settings(self, viewport_context):
        """Build the rendering settings presets"""
        # loading settings with menu open results in weird refresh problems, so disabled
        hide_on_click = True

        # get presets
        preset_dict = carb.settings.get_settings().get_settings_dictionary("exts/omni.kit.viewport.menubar.render/presets").get_dict()
        # remove any unused presets
        for preset in preset_dict.copy():
            if not preset_dict[preset]:
                del preset_dict[preset]

        if preset_dict:
            def get_title(name):
                return name.replace("_", " ").title()

            ui.Separator(text="Rendering Settings")
            with ui.Menu("Load from Preset", hide_on_click=hide_on_click):
                for preset in preset_dict:
                    ui.MenuItem(f"{get_title(preset)}", triggered_fn=lambda p=preset_dict[preset]: asyncio.ensure_future(self.__load_setting_file(carb.tokens.get_tokens_interface().resolve(p))), hide_on_click=hide_on_click)
                ui.Separator()
                ui.MenuItem("Load Preset From File", triggered_fn=lambda v=viewport_context: self.__load_settings(v), hide_on_click=hide_on_click)

            ui.MenuItem("Save Current as Preset", triggered_fn=lambda v=viewport_context: self.__save_settings(v), hide_on_click=hide_on_click)
            ui.MenuItem("Reset to Defaults", triggered_fn=self.__reset_settings, hide_on_click=hide_on_click)

    def __reset_settings(self):
        omni.kit.commands.execute("RestoreDefaultRenderSettingSection", path="/rtx")

    def __save_settings(self, viewport_context):
        try:
            from omni.kit.window.file_exporter import get_file_exporter

            def show_file_exist_popup(usd_path, save_file):  # pragma: no cover
                try:
                    from omni.kit.widget.prompt import Prompt

                    def on_confirm(usd_path):
                        on_cancel()
                        save_file(usd_path)

                    def on_cancel():
                        self._folder_exist_popup.hide()
                        self._folder_exist_popup = None

                    if not self._folder_exist_popup:
                        self._folder_exist_popup = Prompt(
                            title="Overwrite",
                            text="The file already exists, are you sure you want to overwrite it?",
                            ok_button_text="Overwrite",
                            cancel_button_text="Cancel",
                            ok_button_fn=lambda: on_confirm(usd_path),
                            cancel_button_fn=on_cancel,
                        )
                        self._folder_exist_popup.show()
                except ModuleNotFoundError:
                    carb.log_error("omni.kit.widget.prompt not enabled!")
                except Exception as exc:  # noqa: PLW0718
                    carb.log_error(f"__save_settings.show_file_exist_popup error {exc}")

            def save_handler(filename: str, dirname: str, extension: str, selections: List[str]):
                try:
                    from omni.rtx.window.settings.usd_serializer import USDSettingsSerialiser

                    def save_file(usd_path):
                        serialiser = USDSettingsSerialiser()
                        serialiser.save_to_usd(usd_path)

                    final_path = f"{dirname}{filename}{extension}"
                    if os.path.exists(final_path):  # pragma: no cover
                        show_file_exist_popup(final_path, save_file)
                    else:
                        save_file(final_path)
                except ModuleNotFoundError:  # pragma: no cover
                    carb.log_error("omni.rtx.window.settings not enabled!")
                except Exception as exc:  # pragma: no cover # noqa: PLW0718
                    carb.log_error(f"__save_settings.save_handler error {exc}")

            file_exporter = get_file_exporter()
            if file_exporter:
                file_exporter.show_window(
                    title="Save Settings File",
                    export_button_label="Save",
                    export_handler=save_handler,
                    filename_url=carb.tokens.get_tokens_interface().resolve("${cache}/"),
                    file_postfix_options=["settings"])
        except ModuleNotFoundError:  # pragma: no cover
            carb.log_error("omni.kit.window.file_exporter not enabled!")
        except Exception as exc:  # pragma: no cover # noqa: PLW0718
            carb.log_error(f"__save_settings error {exc}")

    def __load_settings(self, viewport_context):
        try:
            from omni.kit.window.file_importer import get_file_importer

            def load_handler(filename: str, dirname: str, selections: List[str]):
                from omni.rtx.window.settings.usd_serializer import USDSettingsSerialiser

                final_path = f"{dirname}{filename}"
                try:
                    serialiser = USDSettingsSerialiser()
                    serialiser.load_from_usd(final_path)
                except ModuleNotFoundError:  # pragma: no cover
                    carb.log_error("omni.rtx.window.settings not enabled!")
                except Exception as exc:  # pragma: no cover # noqa: PLW0718
                    carb.log_error(f"__save_settings.save_handler error {exc}")

            file_importer = get_file_importer()
            if file_importer:
                file_importer.show_window(
                    title="Load Settings File",
                    import_button_label="Load",
                    import_handler=load_handler,
                    filename_url=carb.tokens.get_tokens_interface().resolve("${cache}/"),
                    file_postfix_options=["settings"])
        except ModuleNotFoundError:  # pragma: no cover
            carb.log_error("omni.kit.window.file_importer not enabled!")
        except Exception as exc:  # pragma: no cover # noqa: PLW0718
            carb.log_error(f"__load_settings error {exc}")

    async def __load_setting_file(self, preset_name):
        await omni.kit.app.get_app().next_update_async()

        try:
            from omni.rtx.window.settings.usd_serializer import USDSettingsSerialiser

            serialiser = USDSettingsSerialiser()
            serialiser.load_from_usd(preset_name)
        except ModuleNotFoundError:  # pragma: no cover
            carb.log_error("omni.rtx.window.settings not enabled!")
        except Exception as exc:  # pragma: no cover # noqa: PLW0718
            carb.log_error(f"__load_setting_file error {exc}")

    def _build_menu(self, viewport_context):
        """Build the first level menu"""
        hide_on_click = self.__hide_on_click(viewport_context)
        viewport_api = viewport_context.get("viewport_api")
        if not viewport_api:  # pragma: no cover
            return

        menu_context = self.__menu_context.get(viewport_api.id)

        self.__menu_context[viewport_api.id].root_menu.clear()

        ui.MenuItemCollection(on_build_fn=lambda *args: self.__build_renderers(viewport_context))

        # Rendering Settings
        self.__build_rendering_settings(viewport_context)

        # Rendering Mode
        ui.Separator(text="Rendering Mode")

        self.__build_shading_modes(viewport_context)

        ui.Separator()

        self.__build_render_options(viewport_context)

        ui.Separator()

        # This opens a new Window or goes to an existing preference-pane, so close the Menu
        ui.MenuItem("Preferences", triggered_fn=self.__show_render_preferences, hide_on_click=hide_on_click)

        # The rest of the menu on the case someone wants to put custom stuff
        children = self._children

        if children:
            ui.Separator()

        for child in children:
            child.build_fn(viewport_context)

        if not menu_context:
            return

        self.__set_menu_label(menu_context, viewport_api)

    def __dirty_menu(self, *args, **kwargs):
        """Rebuild everything"""
        for context in self.__menu_context.values():
            if context.root_menu:
                context.root_menu.invalidate()
        self.dirty = True

    def __dirty_renderers(self, *args, **kwargs):
        # On 105.0, changes to /renderer/enabled can/will be recursive
        if self.__pending_render_change:
            return

        self.__pending_render_change = True

        async def update_render_list():
            self.__pending_render_change = False
            RendererMenuContainer.__enabled_engines = HdRendererList.enabled_engines()
            self.__render_list = None
            self.__dirty_menu()

        from omni.kit.async_engine import run_coroutine
        run_coroutine(update_render_list())

    def __ext_changed(self, ext_name: str, enabled: bool):
        engine_name, engine_idx = None, 0
        if ext_name.startswith("omni.kit.viewport."):
            engine_idx = 3
        elif ext_name.startswith("omni.hydra."):
            engine_idx = 2
        elif ext_name.startswith("omni.iray.settings.core."):
            # Iray does not follow "omni.hydra.renderer.settings" convention
            engine_name = "iray"
        else:
            return

        if (not engine_name) and (not engine_idx):
            return

        settings = carb.settings.get_settings()
        managed_hd_exts = settings.get("/exts/omni.kit.viewport.menubar.render/autoManage/enabledList")
        if not managed_hd_exts:
            return

        managed_hd_exts = [ext.lstrip().rstrip() for ext in managed_hd_exts.split(",")]

        if not engine_name:
            engine_split = ext_name.split(".")
            if len(engine_split) >= (engine_idx + 1):
                engine_name = engine_split[engine_idx].split("-")[0]

        # Test is this extension is "managed"
        if engine_name in managed_hd_exts:
            rnd_enabled = settings.get("/renderer/enabled") or ""
            rnd_loc = rnd_enabled.find(engine_name)
            if enabled:
                if rnd_loc == -1:
                    # Here rnd_enabled may be empty when running omni.app.editor.base.kit
                    # Where omni.hydra.* are enabled later and this setting is cleared in __auto_enable_renderers
                    # For OM-121568, do not add empty engine string here
                    rnd_enabled_dst = ",".join([rnd_enabled, engine_name]) if rnd_enabled else engine_name
                    settings.set("/renderer/enabled", rnd_enabled_dst)
            elif rnd_loc != -1 and settings.get("/exts/omni.kit.viewport.menubar.render/autoManage/canRemove"):
                rnd_enabled = rnd_enabled.split(",")
                rnd_enabled.remove(engine_name)
                settings.set("/renderer/enabled", ",".join(rnd_enabled))
            else:
                engine_name = None

            if engine_name:
                self.__dirty_renderers()

    def __ext_enabled(self, ext_name: str, *args, **kwargs):
        self.__ext_changed(ext_name, True)

    def __ext_disabled(self, ext_name: str, *args, **kwargs):
        self.__ext_changed(ext_name, False)

    def __pxr_available(self, settings, viewport_api):
        # return True
        # See if the omni.hydra.pxr engine is available for use in this Viewport
        try:
            usd_context_key = f"'{viewport_api.usd_context_name}':"
            setting_path = viewport_api._settings_path  # noqa: PLW0212

            pxr_eng_in_use = settings.get(self.PXR_IN_USE)
            if not pxr_eng_in_use:
                return True

            # Iterate the list of UsdContext.name => ViewportKey
            usd_context_key_len = len(usd_context_key)
            for in_use in pxr_eng_in_use:
                # Is a hydra.pxr engine instance running fo this UsdContext?
                if in_use.startswith(usd_context_key):
                    # Yes, so the menu must be in the Viewport that claims
                    if in_use.find(setting_path) == usd_context_key_len:
                        return True
                    # Otherwise this Viewport cannot use hydra.pxr
                    return False
            # hydra.pxr is not in use for this USdContext, so it is available
            return True
        except Exception:  # noqa: PLW0718
            pass
        return False

    def __get_current_name(self, viewport_api):
        """Returns display name of the current renderer"""
        engine_name = viewport_api.hydra_engine
        engine_name, hd_engine_renderer = next(
            (i for i in self.render_list.renderers if i[0] == engine_name), (None, None)
        )
        if not hd_engine_renderer or not hd_engine_renderer.renderers:
            return self.name

        # Example: /rtx/rendermode
        render_mode_path = hd_engine_renderer.renderModePath
        if not render_mode_path:  # pragma: no cover
            return hd_engine_renderer.renderers[0].displayName
        # Example: RaytracedLighting
        current_render_mode = carb.settings.get_settings().get(render_mode_path)
        return next((i.displayName for i in hd_engine_renderer.renderers if i.pluginID == current_render_mode), None)

    def __set_menu_label(self, menu_context: MenuContext, viewport_api):
        if menu_context is None:  # pragma: no cover
            menu_context = self.__menu_context.get(viewport_api.id)
            if menu_context is None:
                carb.log_error("No MenuContext for this menubar-item")
                return

        current_renderer_name = self.__get_current_name(viewport_api)
        menu_context.root_menu.text = {
            "RTX - Interactive (Path Tracing)": "RTX - Interactive",
            "RTX - Accurate (Iray)": "RTX - Accurate",
            "RTX - Scientific (IndeX)": "RTX - Scientific",
        }.get(current_renderer_name, str(current_renderer_name)) if current_renderer_name else self.name

    def __show_render_preferences(self, *args, **kwargs) -> None:
        try:
            import omni.kit.window.preferences as preferences

            async def focus_async():
                pref_window = ui.Workspace.get_window("Preferences")
                if pref_window:
                    pref_window.focus()

            page_title = "Rendering"
            inst = preferences.get_instance()
            if not inst:  # pragma: no cover
                carb.log_error("Preferences extension is not loaded yet")
                return None

            pages = preferences.get_page_list()
            for page in pages:
                if page.get_title() == page_title:
                    inst.select_page(page)
                    # Show the Window
                    inst.show_preferences_window()
                    # Force the tab to be the active/focused tab (this currently needs to be done in async)
                    asyncio.ensure_future(focus_async())
                    return page
            carb.log_error("Render Preferences page not found!")  # pragma: no cover
            return None
        except ImportError:  # pragma: no cover
            carb.log_error("omni.kit.window.preferences not enabled!")
            return None
