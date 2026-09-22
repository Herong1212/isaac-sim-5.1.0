
__all__ = ["register_actions", "deregister_actions"]

import omni.kit.actions.core
import omni.kit.viewport.utility
import carb
import carb.settings

from pxr import Sdf, UsdGeom

from functools import partial
from typing import List, Optional, Sequence, Tuple


PERSP_CAM = "perspective_camera"
TOP_CAM = "top_camera"
FRONT_CAM = "front_camera"
RIGHT_CAM = "right_camera"

SHOW_ALL_PURPOSE = "toggle_show_by_purpose_all"
SHOW_GUIDE = "toggle_show_by_purpose_guide"
SHOW_PROXY = "toggle_show_by_purpose_proxy"
SHOW_RENDER = "toggle_show_by_purpose_render"

INERTIA_TOGGLE = "toggle_camera_inertia_enabled"
FILL_VIEWPORT_TOGGLE = "toggle_fill_viewport"

RENDERER_RTX_REALTIME = "set_renderer_rtx_realtime"
RENDERER_RTX_PT = "set_renderer_rtx_pathtracing"
RENDERER_RTX_TOGGLE = "toggle_rtx_rendermode"
RENDERER_IRAY = "set_renderer_iray"
RENDERER_PXR_STORM = "set_renderer_pxr_storm"
RENDERER_WIREFRAME = "toggle_wireframe"

PERSISTENT_SETTINGS_PREFIX = "/persistent"
INERTIA_ENABLE_SETTING = PERSISTENT_SETTINGS_PREFIX + "/app/viewport/camInertiaEnabled"
FILL_VIEWPORT_SETTING  = PERSISTENT_SETTINGS_PREFIX + "/app/viewport/{viewport_api_id}/fillViewport"
DISPLAY_GUIDE_SETTING  = PERSISTENT_SETTINGS_PREFIX + "/app/hydra/displayPurpose/guide"
DISPLAY_PROXY_SETTING  = PERSISTENT_SETTINGS_PREFIX + "/app/hydra/displayPurpose/proxy"
DISPLAY_RENDER_SETTING = PERSISTENT_SETTINGS_PREFIX + "/app/hydra/displayPurpose/render"
SECTION_VISIBILE_SETTING = PERSISTENT_SETTINGS_PREFIX + "/app/viewport/{viewport_api_id}/{section}/visible"
SHADING_MODE_SETTING = "/exts/omni.kit.viewport.menubar.render/shadingMode"

workspace_data = []

def register_actions(extension_id: str):

    action_registry = omni.kit.actions.core.get_action_registry()
    actions_tag = "Viewport Camera Menu Actions"

    action_registry.register_action(
        extension_id,
        PERSP_CAM,
        partial(set_camera, "/OmniverseKit_Persp"),
        display_name="Perspective Camera",
        description="Switch to Perspective Camera",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        TOP_CAM,
        partial(set_camera, "/OmniverseKit_Top"),
        display_name="Top Camera",
        description="Switch to Top Camera",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        FRONT_CAM,
        partial(set_camera, "/OmniverseKit_Front"),
        display_name="Front Camera",
        description="Switch to Front Camera",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        RIGHT_CAM,
        partial(set_camera, "/OmniverseKit_Right"),
        display_name="Right Camera",
        description="Switch to Right Camera",
        tag=actions_tag,
    )

    actions_tag = "Viewport Display Menu Actions"

    action_registry.register_action(
        extension_id,
        SHOW_ALL_PURPOSE,
        partial(
            toggle_category_settings,
            DISPLAY_GUIDE_SETTING,
            DISPLAY_PROXY_SETTING,
            DISPLAY_RENDER_SETTING,
        ),
        display_name="Toggle Show All Purpose",
        description="Toggle Show By Purpose - All",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        SHOW_GUIDE,
        partial(_toggle_setting, DISPLAY_GUIDE_SETTING),
        display_name="Toggle Show Guide Purpose",
        description="Toggle Show By Purpose - Guide",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        SHOW_PROXY,
        partial(_toggle_setting, DISPLAY_PROXY_SETTING),
        display_name="Toggle Show Proxy Purpose",
        description="Toggle Show By Purpose - Proxy",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        SHOW_RENDER,
        partial(_toggle_setting, DISPLAY_RENDER_SETTING),
        display_name="Toggle Show Render Purpose",
        description="Toggle Show By Purpose - Render",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "toggle_camera_visibility",
        toggle_camera_visibility,
        display_name="Toggle Show Cameras",
        description="Toggle Show By Type - Cameras",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "toggle_light_visibility",
        toggle_light_visibility,
        display_name="Toggle Show Lights",
        description="Toggle Show By Type - Lights",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "toggle_skeleton_visibility",
        toggle_skeleton_visibility,
        display_name="Toggle Show Skeletons",
        description="Toggle Show By Type - Skeletons",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "toggle_audio_visibility",
        toggle_audio_visibility,
        display_name="Toggle Show Audio",
        description="Toggle Show By Type - Audio",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "toggle_mesh_visibility",
        toggle_mesh_visibility,
        display_name="Toggle Show Meshes",
        description="Toggle Show By Type - Meshes",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "toggle_show_by_type_visibility",
        toggle_show_by_type_visibility,
        display_name="Toggle Show By Type",
        description="Toggle Show By Type - All Type Toggle",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "toggle_grid_visibility",
        toggle_grid_visibility,
        display_name="Toggle Grid",
        description="Toggle drawing of grid",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "toggle_axis_visibility",
        toggle_axis_visibility,
        display_name="Toggle Camera Axis",
        description="Toggle drawing of camera axis",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "toggle_selection_hilight_visibility",
        toggle_selection_hilight_visibility,
        display_name="Toggle Selection Outline",
        description="Toggle drawing of selection hilight",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "toggle_bounding_box_visibility",
        toggle_bounding_box_visibility,
        display_name="Toggle Bounding Box",
        description="Toggle drawing of bounding box",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "toggle_global_visibility",
        toggle_global_visibility,
        display_name="Toggle Global Visibility",
        description="Toggle drawing of grid, HUD, audio, light, camera, and skeleton gizmos",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "toggle_viewport_visibility",
        toggle_viewport_visibility,
        display_name="Toggle Viewport item visibility",
        description="Toggle drawing of Viewport items by key.",
        tag=actions_tag,
    )

    actions_tag = "Viewport Settings Menu Actions"

    action_registry.register_action(
        extension_id,
        INERTIA_TOGGLE,
        partial(_toggle_setting, INERTIA_ENABLE_SETTING),
        display_name="Toggle Camera Inertia Enabled",
        description="Toggle Camera Inertia Mode Enabled",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        FILL_VIEWPORT_TOGGLE,
        partial(_toggle_setting, FILL_VIEWPORT_SETTING),
        display_name="Toggle Fill Viewport",
        description="Toggle Fill Viewport Setting",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "toggle_lock_navigation_height",
        partial(_toggle_setting, "/persistent/exts/omni.kit.manipulator.camera/flyViewLock"),
        display_name="Toggle Lock Navigation Height",
        description="Toggle whether fly-mode forward/backward and up/down uses ore ignores the camera orientation.",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "set_viewport_resolution",
        set_viewport_resolution,
        display_name="Set Viewport Resolution",
        description="Set a Viewport's resolution with a tuple or named constant.",
        tag=actions_tag,
    )

    actions_tag = "Viewport Render Menu Actions"

    # TODO: these should maybe register dynamically as renderers are loaded/unloaded?
    settings = carb.settings.get_settings()
    available_engines = (settings.get('/renderer/enabled') or '').split(',')
    ignore_loaded_engined = True
    if ignore_loaded_engined or ('rtx' in available_engines):

        action_registry.register_action(
            extension_id,
            RENDERER_RTX_REALTIME,
            partial(set_renderer, "rtx", "RaytracedLighting"),
            display_name="Set Renderer to RTX Realtime",
            description="Set Renderer Engine to RTX Realtime",
            tag=actions_tag,
        )

        action_registry.register_action(
            extension_id,
            RENDERER_RTX_PT,
            partial(set_renderer, "rtx", "PathTracing"),
            display_name="Set Renderer to RTX Pathtracing",
            description="Set Renderer Engine to RTX Pathtracing",
            tag=actions_tag,
        )

        action_registry.register_action(
            extension_id,
            RENDERER_RTX_TOGGLE,
            toggle_rtx_rendermode,
            display_name="Toggle RTX render-mode",
            description="Toggle RTX render-mode between Realtime and Pathtracing",
            tag=actions_tag,
        )


    if ignore_loaded_engined or ('iray' in available_engines):

        action_registry.register_action(
            extension_id,
            RENDERER_IRAY,
            partial(set_renderer, "iray", "iray"),
            display_name="Set Renderer to RTX Accurate (Iray)",
            description="Set Renderer Engine to RTX Accurate (Iray)",
            tag=actions_tag,
        )

    if ignore_loaded_engined or ('pxr' in available_engines):
        action_registry.register_action(
            extension_id,
            RENDERER_PXR_STORM,
            partial(set_renderer, "pxr", "HdStormRendererPlugin"),
            display_name="Set Renderer to Pixar Storm",
            description="Set Renderer Engine to Pixar Storm",
            tag=actions_tag,
        )

    action_registry.register_action(
        extension_id,
        RENDERER_WIREFRAME,
        toggle_wireframe,
        display_name="Toggle wireframe",
        description="Toggle wireframe",
        tag=actions_tag,
    )

    # HUD visibility actions
    actions_tag = "Viewport HUD Visibility Actions"

    action_registry.register_action(
        extension_id,
        "toggle_hud_fps_visibility",
        partial(_toggle_viewport_visibility, visible=None, setting_keys=["hud/renderFPS"], action="toggle_hud_fps_visibility"),
        display_name="Toggle Render FPS HUD visibility",
        description="Toggle whether render fps item is visible in HUD or not.",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "toggle_hud_resolution_visibility",
        partial(_toggle_viewport_visibility, visible=None, setting_keys=["hud/renderResolution"], action="toggle_hud_resolution_visibility"),
        display_name="Toggle Render Resolution HUD visibility",
        description="Toggle whether render resolution item is visible in HUD or not.",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "toggle_hud_progress_visibility",
        partial(_toggle_viewport_visibility, visible=None, setting_keys=["hud/renderProgress"], action="toggle_hud_progress_visibility"),
        display_name="Toggle Render Progress HUD visibility",
        description="Toggle whether render progress item is visible in HUD or not.",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "toggle_hud_camera_speed_visibility",
        partial(_toggle_viewport_visibility, visible=None, setting_keys=["hud/cameraSpeed"], action="toggle_hud_camera_speed_visibility"),
        display_name="Toggle Camera Speed HUD visibility",
        description="Toggle whether camera speed HUD item is visible in HUD or not.",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "toggle_hud_memory_visibility",
        toggle_hud_memory_visibility,
        display_name="Toggle Memory Item HUD visibility",
        description="Toggle whether HUD memory items HUD are visible in HUD or not.",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "toggle_hud_visibility",
        toggle_hud_visibility,
        display_name="Toggle Global HUD visibility",
        description="Toggle whether any HUD items are visible or not.",
        tag=actions_tag,
    )


def deregister_actions(extension_id):
    action_registry = omni.kit.actions.core.get_action_registry()
    if action_registry:
        action_registry.deregister_all_actions_for_extension(extension_id)


def _get_viewport_argument(viewport_api, action: str):
    if not viewport_api:
        viewport_api = omni.kit.viewport.utility.get_active_viewport()
        if not viewport_api:
            carb.log_warn(f"There was no provided or active Viewport - not able to run viewport-specific action: {action}.")
            return None
    return viewport_api


def set_camera(camera_str: str, viewport_api=None) -> bool:
    """Switch the camera in the active viewport based on the camera path.

    Args:
        camera_str (str): Camera Path in string form.  ie "/OmniverseKit_Persp"
        viewport_api (viewport): Optional viewport in order to set the camera
                                 in a specific viewport.
    Returns:
        bool: True if successful, False if not.
    """
    viewport = _get_viewport_argument(viewport_api, "set_camera")
    if not viewport:
        return False

    stage = viewport.stage
    if not stage:
        carb.log_warn("Viewport Stage does not exist, to switch cameras.")
        return False

    camera_path = Sdf.Path(camera_str)
    prim = stage.GetPrimAtPath(camera_path)
    if not prim:
        carb.log_warn(f"Prim for camera path: {camera_path} does not exist in the stage.")
        return False

    if not UsdGeom.Camera(prim):
        carb.log_warn(f"Camera: {camera_path} does not exist in the stage.")
        return False

    viewport.camera_path = camera_path
    return True


def set_renderer(engine_name, render_mode, viewport_api=None) -> bool:
    viewport = _get_viewport_argument(viewport_api, "set_renderer")
    if not viewport:
        return False

    viewport.set_hd_engine(engine_name, render_mode)
    return True


def toggle_rtx_rendermode(viewport_api=None) -> bool:
    viewport = _get_viewport_argument(viewport_api, "toggle_rtx_rendermode")
    if not viewport:
        return False

    # Toggle to PathTracing when already on RTX and using RaytracedLighting
    if viewport.hydra_engine == "rtx" and viewport.render_mode == "RaytracedLighting":
        render_mode = "PathTracing"
    else:
        render_mode = "RaytracedLighting"

    viewport.set_hd_engine("rtx", render_mode)
    return True


def toggle_wireframe() -> str:
    settings = carb.settings.get_settings()
    mode = settings.get(SHADING_MODE_SETTING)
    if mode == "wireframe":
        # Set to default
        settings.set(SHADING_MODE_SETTING, "default")
        settings.set("/rtx/wireframe/mode", 0)
        return "default"
    else:
        # Set to wireframe
        settings.set(SHADING_MODE_SETTING, "wireframe")
        settings.set("/rtx/debugView/target", "")
        flat_shade = settings.get("/rtx/debugMaterialType") == 0
        wire_mode = 2 if flat_shade else 1
        settings.set("/rtx/wireframe/mode", wire_mode)
        return "wireframe"


def toggle_category_settings(*setting_names):
    settings = carb.settings.get_settings()
    vals = [settings.get(setting_name) for setting_name in setting_names]

    value_for_all = False if all(vals) else True
    for setting_name in setting_names:
        settings.set(setting_name, value_for_all)


def _toggle_setting(setting_name: str, viewport_api: Optional["ViewportAPI"] = None, visible: bool | None = None):
    viewport_api = _get_viewport_argument(viewport_api, "_toggle_setting")
    if not viewport_api:
        return

    setting_path = setting_name.format(viewport_api_id=viewport_api.id)
    settings = carb.settings.get_settings()
    if visible is None:
        visible = not bool(settings.get(setting_path))

    settings.set(setting_path, visible)
    return visible


_k_setting_to_prim_type = {
    "scene/cameras": {"Camera"},
    "scene/skeletons": {"Skeleton"},
    "scene/audio": {"Sound", "Listener"},
    "scene/meshes": {"Mesh", "Cone", "Cube", "Cylinder", "Sphere", "Capsule"},
    # "scene/lights"
}


def _stage_opened(usd_context_name: str, stage):
    if not stage:
        return

    settings = carb.settings.get_settings()
    reset_on_open = settings.get("/exts/omni.kit.viewport.actions/resetVisibilityOnOpen")

    def get_display_option_and_off(setting_key: str):
        vis_key = f"/app/viewport/usdcontext-{usd_context_name}/{setting_key}/visible"
        return (vis_key, not bool(settings.get(vis_key)))

    def is_display_option_off(setting_key: str):
        return get_display_option_and_off(setting_key)[1]

    types_to_hide = set()
    for setting_key, prim_types in _k_setting_to_prim_type.items():
        vis_key, is_off = get_display_option_and_off(setting_key)
        if reset_on_open and setting_key in reset_on_open:
            if is_off:
                settings.set(vis_key, True)
        elif is_off:
            types_to_hide.update(prim_types)

    if not types_to_hide:
        return

    from omni.kit.viewport.actions.visibility import VisibilityEdit
    VisibilityEdit(stage, types_to_show=None, types_to_hide=types_to_hide).run()


def _get_visible(visible: bool | Sequence[bool], index: int):
    """Utility function to get visibilty as a bool or from a bool or a list with index"""
    getitem = getattr(visible, "__getitem__", None)
    if getitem:
        return bool(getitem(index))
    return bool(visible)


def _toggle_legacy_display_visibility(viewport_api,
                                      visible: bool | Sequence[bool],
                                      setting_keys: Sequence[str],
                                      reduce_sequence: bool) -> List[str]:
    persitent_to_legacy_map = {
        "hud/renderFPS": (1 << 0, None),
        "guide/axis": (1 << 1, None),
        "hud/renderResolution": (1 << 3, None),
        "scene/cameras": (1 << 5, "/app/viewport/show/camera"),
        "guide/grid": (1 << 6, "/app/viewport/grid/enabled"),
        "guide/selection": (1 << 7, "/app/viewport/outline/enabled"),
        "scene/lights": (1 << 8, "/app/viewport/show/lights"),
        "scene/skeletons": (1 << 9, None),
        "scene/meshes": (1 << 10, None),
        "hud/renderProgress": (1 << 11, None),
        "scene/audio": (1 << 12, "/app/viewport/show/audio"),
        "hud/deviceMemory": (1 << 13, None),
        "hud/processMemory": (1 << 14, "{persistent_key}/hud/hostMemory"),
    }

    settings = carb.settings.get_settings()
    display_options = settings.get("/persistent/app/viewport/displayOptions") or 0
    empty_tuple = (None, None)
    result = []

    for i in range(len(setting_keys)):
        section, new_visible = setting_keys[i], _get_visible(visible, i)
        section_mask, section_key = persitent_to_legacy_map.get(section, empty_tuple)
        if section_mask is None:
            continue

        was_visible = bool(display_options & section_mask)
        if new_visible is None:
            display_options ^= section_mask
            # Make new_visible != was_visible comparison below correct for state transition
            new_visible = bool(display_options & section_mask)
        elif new_visible != was_visible:
            if new_visible:
                display_options |= section_mask
            else:
                display_options &= ~section_mask

        if new_visible != was_visible:
            result.append(section)
            if section_key:
                viewport_api_id = str(viewport_api.id)
                vp_persistent = f"/persistent/app/viewport/{viewport_api_id}"
                settings.set(section_key.format(viewport_api_id=viewport_api_id, persistent_key=vp_persistent), new_visible)

    settings.set("/persistent/app/viewport/displayOptions", display_options)

    # Reduce the case of a single item sequence to the item or None if requested
    if reduce_sequence:
        result = result[0] if result else None
    return result


def _toggle_viewport_visibility(viewport_api,
                                visible: bool | Sequence[bool] | None,
                                setting_keys: Sequence[str],
                                action: str,
                                reduce_sequence: bool = True) -> List[str] | str | None:
    viewport_api = _get_viewport_argument(viewport_api, action)
    if not viewport_api:
        return []

    settings = carb.settings.get_settings()
    usd_context_name = viewport_api.usd_context_name

    def get_visibility(setting_key: str) -> Tuple[bool, str]:
        # Currently settings in "scene" correspond to a state change in the Usd stage
        if setting_key.startswith("scene"):
            setting_key = f"/app/viewport/usdcontext-{usd_context_name}/{setting_key}/visible"
        else:
            setting_key = f"/persistent/app/viewport/{viewport_api.id}/{setting_key}/visible"
        return bool(settings.get(setting_key)), setting_key

    if visible is None:
        # No explicit visibility given, figure out what things to flip
        all_visible, any_visible = True, False
        for setting_key in setting_keys:
            # Get the current visibility
            cur_visibility, _ = get_visibility(setting_key)
            # If this any item is not visible, then the toggle is a transition to all items visible; early exit
            if not cur_visibility:
                all_visible = False
            else:
                any_visible = True

        # Transition to hidden if all were visible, otherwise transition to visible
        # All were visible => Nothing visible
        # Nothing was visible => All visible
        # Anything was visible => All visible
        if any_visible and not all_visible:
            visible = True
        else:
            visible = not all_visible

    stage = viewport_api.stage
    types_to_show, types_to_hide = set(), set()
    # Apply any visibility UsdAttribute changes to the types requested
    setting_to_prim_types = _k_setting_to_prim_type if stage else {}
    result = []

    # Find all the objects that need to be toggled
    for i in range(len(setting_keys)):
        setting_key, new_visible = setting_keys[i], _get_visible(visible, i)
        cur_visibility, pref_key = get_visibility(setting_key)
        cur_visibility = bool(cur_visibility)
        if cur_visibility != new_visible:
            settings.set(pref_key, new_visible)
            prim_types = setting_to_prim_types.get(setting_key)
            if prim_types:
                if new_visible:
                    types_to_show.update(prim_types)
                else:
                    types_to_hide.update(prim_types)
            elif setting_key == "guide/selection":
                # Still need to special case this to forward correctly (its global)
                settings.set("/app/viewport/outline/enabled", new_visible)
            elif setting_key == "guide/boundingBox":
                # Still need to special case this to forward correctly (its global)
                settings.set("/app/viewport/boundingBoxes/enabled", new_visible)
        # If visibility was toggled, add to the key to the return value
        if new_visible != cur_visibility:
            result.append(setting_key)

    if settings.get("/exts/omni.kit.viewport.actions/visibilityToggle/removeCameraMeshes"):
        if "Camera" in types_to_show:
            settings.set("/app/viewport/createCameraModelRep", True)
            types_to_show.remove("Camera")
        elif "Camera" in types_to_hide:
            settings.set("/app/viewport/createCameraModelRep", False)
            types_to_hide.remove("Camera")

    # Apply any visibility UsdAttribute changes to the types requested
    if types_to_show or types_to_hide:
        from .visibility import VisibilityEdit
        VisibilityEdit(stage, types_to_show=types_to_show, types_to_hide=types_to_hide).run()

        # The action is a toggle of state that is sticky across new stage's, so need to apply state to any new stage
        from omni.kit.viewport.actions.extension import get_instance
        get_instance()._watch_stage_open(usd_context_name, _stage_opened)

    # Reduce the case of a single item sequence to the item or None if requested
    if reduce_sequence:
        result = result[0] if result else None
    return result


def toggle_grid_visibility(viewport_api=None, visible: bool | Sequence[bool] | None = None) -> str | None:
    return _toggle_viewport_visibility(viewport_api, visible, ["guide/grid"], "toggle_grid_visibility")


def toggle_axis_visibility(viewport_api=None, visible: bool | Sequence[bool] | None = None) -> str | None:
    return _toggle_viewport_visibility(viewport_api, visible, ["guide/axis"], "toggle_axis_visibility")


def toggle_selection_hilight_visibility(viewport_api=None, visible: bool | Sequence[bool] | None = None) -> str | None:
    return _toggle_viewport_visibility(viewport_api, visible, ["guide/selection"], "toggle_selection_hilight_visibility")


def toggle_bounding_box_visibility(viewport_api=None, visible: bool | Sequence[bool] | None = None) -> str | None:
    return _toggle_viewport_visibility(viewport_api, visible, ["guide/boundingBox"], "toggle_bounding_box_visibility")


def toggle_camera_visibility(viewport_api=None, visible: bool | Sequence[bool] | None = None) -> str | None:
    return _toggle_viewport_visibility(viewport_api, visible, ["scene/cameras"], "toggle_camera_visibility")


def toggle_light_visibility(viewport_api=None, visible: bool | Sequence[bool] | None = None) -> str | None:
    return _toggle_viewport_visibility(viewport_api, visible, ["scene/lights"], "toggle_light_visibility")


def toggle_skeleton_visibility(viewport_api=None, visible: bool | Sequence[bool] | None = None) -> str | None:
    return _toggle_viewport_visibility(viewport_api, visible, ["scene/skeletons"], "toggle_skeleton_visibility")


def toggle_audio_visibility(viewport_api=None, visible: bool | Sequence[bool] | None = None) -> str | None:
    return _toggle_viewport_visibility(viewport_api, visible, ["scene/audio"], "toggle_audio_visibility")


def toggle_mesh_visibility(viewport_api=None, visible: bool | Sequence[bool] | None = None) -> str | None:
    return _toggle_viewport_visibility(viewport_api, visible, ["scene/meshes"], "toggle_mesh_visibility")


def toggle_show_by_type_visibility(viewport_api=None, visible: bool | Sequence[bool] | None = None) -> List[str]:
    # OMPE-24967: Remove toggle types from exclusion list from viewport menubar display settings, otherwise this would
    # cause the initial settings to be incorrect because the excluded types could have a default that is different from
    # the other visible settings, this would result in error when calculating the result for visibility.
    settings = carb.settings.get_settings()
    exclude_types = settings.get("/exts/omni.kit.viewport.menubar.display/showByType/exclude_list") or []
    exclude_types = [t.casefold() for t in exclude_types]
    all_types = ('cameras', 'lights', 'skeletons', 'audio')
    toggle_types = [f"scene/{t}" for t in all_types if t not in exclude_types]
    return _toggle_viewport_visibility(viewport_api, visible, toggle_types, "toggle_show_by_type_visibility", False)


def _get_toggle_types(settings, setting_path: str) -> List[str]:
    toggle_types = settings.get(setting_path)
    if toggle_types is None:
        return []
    if isinstance(toggle_types, str):
        return toggle_types.split(",")
    return toggle_types


def toggle_global_visibility(viewport_api=None, visible: bool | Sequence[bool] | None = None) -> List[str]:
    viewport_api = _get_viewport_argument(viewport_api, "toggle_global_visibility")
    # Get the list of what to hide (defaulting to what legacy Viewport and toggle_global_visibility_settings did)
    settings = carb.settings.get_settings()
    toggle_types = _get_toggle_types(settings, "/exts/omni.kit.viewport.actions/visibilityToggle/globalTypes")
    toggle_types += _get_toggle_types(settings, "/exts/omni.kit.viewport.actions/visibilityToggle/hudTypes")

    return _toggle_viewport_visibility(viewport_api, visible, toggle_types, "toggle_global_visibility", False)


def toggle_viewport_visibility(keys: Sequence[str], viewport_api=None, visible: bool | Sequence[bool] | None = None) -> List[str]:
    return _toggle_viewport_visibility(viewport_api, visible, keys, "toggle_viewport_visibility", False)


def toggle_hud_memory_visibility(viewport_api=None, visible: bool | Sequence[bool] | None = None,
                                 process: bool = True,
                                 device: bool = True,
                                 host: bool = True) -> str | None:
    items = []
    if process:
        items.append("hud/processMemory")
    if device:
        items.append("hud/deviceMemory")
    if host:
        items.append("hud/hostMemory")
    if items:
        return _toggle_viewport_visibility(viewport_api, visible, items, "toggle_hud_memory_visibility")
    return []


def toggle_hud_visibility(viewport_api=None, visible: bool | None = None, use_setting: bool = False):
    viewport = _get_viewport_argument(viewport_api, "toggle_hud_visibility")
    if not viewport:
        return
    # as_menu works around a defect in Viewport-menu modeling of settings, where top-level item will enable
    # or disable all child items only in the first grouping, but toggle_hud_visibility action should really mean
    # all HUD items, (the ui-layer that contains any "hud/children" items).
    if use_setting:
        settings = carb.settings.get_settings()
        toggle_types = _get_toggle_types(settings, "/exts/omni.kit.viewport.actions/visibilityToggle/hudTypes")
        toggled = _toggle_viewport_visibility(viewport, visible, toggle_types, "toggle_hud_visibility", reduce_sequence=False)

        any_vis = bool(visible)
        if not any_vis:
            for key in toggle_types:
                any_vis = settings.get(f"/persistent/app/viewport/{viewport.id}/{key}/visible")
                if any_vis:
                    break
        # If any of the children are now visible, make sure the top-level parent is also visible
        if any_vis:
            _toggle_setting("/persistent/app/viewport/{viewport_api_id}/hud/visible", viewport, visible=True)
        return toggled

    return _toggle_setting("/persistent/app/viewport/{viewport_api_id}/hud/visible", viewport)


def set_viewport_resolution(resolution, viewport_api=None):
    viewport_api = _get_viewport_argument(viewport_api, "set_viewport_resolution")
    if not viewport_api:
        return

    # Accept resolution as a named constant (str) as well as a tuple
    if isinstance(resolution, str):
        resolution_tuple = NAME_RESOLUTIONS = {
            "Icon": (512, 512),
            "Square": (1024, 1024),
            "SD": (1280, 960),
            "HD720P": (1280, 720),
            "HD1080P": (1920, 1080),
            "2K": (2048, 1080),
            "1440P": (2560, 1440),
            "UHD": (3840, 2160),
            "Ultra Wide": (3440, 1440),
            "Super Ultra Wide": (3840, 1440),
            "5K Wide": (5120, 2880),
        }.get(resolution)

        if resolution_tuple is None:
            carb.log_error("Resolution named {resolution} is not known.")
            return

        resolution = resolution_tuple

    viewport_api.resolution = resolution
