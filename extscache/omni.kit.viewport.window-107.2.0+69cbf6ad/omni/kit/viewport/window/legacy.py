# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = []

from functools import partial
from typing import Any, Optional
import carb


def _resolve_viewport_setting(viewport_id: str, setting_name: str, isettings: carb.settings.ISettings,
                              legacy_key: Optional[str] = None, set_per_vp_value: bool = False,
                              default_if_not_found: Any = None,
                              usd_context_name: Optional[str] = None):
    # Resolve a default Viewport setting from the most specific to the most general
    #  /app/viewport/usd_context_name/setting => Global signal that overrides any other (for state dependent on stage)
    #  /persistent/app/viewport/Viewport/Viewport0/setting => Saved setting for this specific Viewport
    #  /app/viewport/Viewport/Viewport0/setting  => Startup value for this specific Viewport
    #  /app/viewport/defaults/setting  => Startup value targetting all Viewports
    setting_key = f"/app/viewport/{viewport_id}/{setting_name}"
    persistent_key = "/persistent" + setting_key

    # Return values may push the setting to persistent storage if not there already
    def maybe_set_persistent_and_return(value):
        # Set to persitent storage if requested
        if set_per_vp_value:
            isettings.set(persistent_key, value)
        # Set to global storage if requested
        if usd_context_name is not None:
            isettings.set(f"/app/viewport/usdcontext-{usd_context_name}/{setting_name}", value)
        return value

    # Initial check if the setting is actually global to all Viewports on a UsdContext
    if usd_context_name is not None:
        value = isettings.get(f"/app/viewport/usdcontext-{usd_context_name}/{setting_name}")
        if value is not None:
            usd_context_name = None  # No need to set back to the setting that was just read
            return maybe_set_persistent_and_return(value)

    # First check if there is a persistent value stored in the preferences
    value = isettings.get(persistent_key)
    if value is not None:
        return maybe_set_persistent_and_return(value)

    # Next check if a non-persitent viewport-specific default exists via toml / start-up settings
    value = isettings.get(setting_key)
    if value is not None:
        return maybe_set_persistent_and_return(value)

    # Next check if a non-persitent global default exists via toml / start-up settings
    value = isettings.get(f"/app/viewport/defaults/{setting_name}")
    if value is not None:
        return maybe_set_persistent_and_return(value)

    # Finally check if there exists a legacy key to specify the startup value
    if legacy_key:
        value = isettings.get(legacy_key)
    if value is not None:
        return maybe_set_persistent_and_return(value)

    if default_if_not_found is not None:
        value = maybe_set_persistent_and_return(default_if_not_found)

    return value


def _setup_viewport_options(viewport_id: str, usd_context_name: str, isettings: carb.settings.ISettings):
    legacy_display_options_key: str = "/persistent/app/viewport/displayOptions"
    # force_hide_fps_key: str = "/app/viewport/forceHideFps"
    # show_layer_menu_key: str = "/app/viewport/showLayerMenu"

    # Map legacy bitmask values to new per-viewport keys: new_key: (bitmask, legacy_setting, is_usd_global)
    persitent_to_legacy_map = {
        "hud/renderFPS/visible": (1 << 0, None, False),
        "guide/axis/visible": (1 << 1, None, False),
        "hud/renderResolution/visible": (1 << 3, None, False),
        "scene/cameras/visible": (1 << 5, "/app/viewport/show/camera", True),
        "guide/grid/visible": (1 << 6, "/app/viewport/grid/enabled", False),
        "guide/selection/visible": (1 << 7, "/app/viewport/outline/enabled", False),
        "scene/lights/visible": (1 << 8, "/app/viewport/show/lights", True),
        "scene/skeletons/visible": (1 << 9, None, True),
        "scene/meshes/visible": (1 << 10, None, True),
        "hud/renderProgress/visible": (1 << 11, None, False),
        "scene/audio/visible": (1 << 12, "/app/viewport/show/audio", True),
        "hud/deviceMemory/visible": (1 << 13, None, False),
        "hud/hostMemory/visible": (1 << 14, "{persistent_key}/hud/processMemory/visible", False),
    }

    # Build some handlers to keep legacy displayOptions in sync with the new per-viewport settings

    # Used as nonlocal/global in legacy_display_options_changed to check for bits toggled
    # When no legacy displayOptions exists, we do not want to create it as set_default would do
    legacy_display_options: int = isettings.get(legacy_display_options_key)
    if legacy_display_options is None:
        legacy_display_options = 32255

    def format_secondary_key(setting_key: str, secondary_key: str | None):
        vp_persistent = f"/persistent/app/viewport/{viewport_id}"
        if secondary_key:
            secondary_key = secondary_key.format(viewport_id=viewport_id, persistent_key=vp_persistent)
        return f"{vp_persistent}/{setting_key}", secondary_key

    # Handles changes to legacy displayOptions (which are global to all viewports) and push them to our single Viewport
    def legacy_display_options_changed(item: carb.dictionary.Item, event_type: carb.settings.ChangeEventType):
        if event_type != carb.settings.ChangeEventType.CHANGED:
            return

        nonlocal legacy_display_options
        isettings = carb.settings.get_settings()

        # Get the previous and current displayOptions
        prev_display_options, current_display_options = legacy_display_options, isettings.get(legacy_display_options_key) or 0
        # If they match, nothing has changed so just exit
        if prev_display_options == current_display_options:
            return
        # Save the current state for comparison on next change
        legacy_display_options = current_display_options

        # Check for any bit changes to toggle/store into the per-viepwort key
        def check_bit_toggled(legacy_bitmask: int):
            cur_vis = bool(current_display_options & legacy_bitmask)
            return bool(prev_display_options & legacy_bitmask) != cur_vis, cur_vis

        # Check if a legacy bit was flipped, and if so store it's current state into per-viewport and stage-global
        # state if they are not already set to the same value.
        def toggle_per_viewport_setting(legacy_bitmask: int, setting_key: str, secondary_key: Optional[str] = None):
            toggled, visible = check_bit_toggled(legacy_bitmask)
            if toggled:
                # legacy displayOption was toggled, if it is not already matching the viewport push it there
                vp_key, secondary_key = format_secondary_key(setting_key, secondary_key)
                if visible != bool(isettings.get(vp_key)):
                    isettings.set(vp_key, visible)
                if secondary_key and (visible != bool(isettings.get(secondary_key))):
                    isettings.set(secondary_key, visible)
            return visible

        for setting_key, legacy_obj in persitent_to_legacy_map.items():
            # Settings may have had a displayOptions bit that was serialzed, but controlled via another setting
            legacy_bitmask, secondary_key, is_usd_state = legacy_obj
            visible = toggle_per_viewport_setting(legacy_bitmask, setting_key, secondary_key)
            # Store to global are if the setting represent UsdStage that must be communicated across Viewports
            if is_usd_state:
                usd_key = f"/app/viewport/usdcontext-{usd_context_name}/{setting_key}"
                if visible != bool(isettings.get(usd_key)):
                    isettings.set(usd_key, visible)

    def legacy_value_changed(setting_key: str, item: carb.dictionary.Item, event_type: carb.settings.ChangeEventType):
        if event_type != carb.settings.ChangeEventType.CHANGED:
            return

        legacy_obj = persitent_to_legacy_map.get(setting_key)
        if not legacy_obj:
            carb.log_error("No mapping for '{setting_key}' into legacy setting")
            return

        isettings = carb.settings.get_settings()
        secondary_key, is_stage_global = legacy_obj[1], legacy_obj[2]
        per_viewport_key, secondary_key = format_secondary_key(setting_key, secondary_key)
        viewport_show = bool(isettings.get(per_viewport_key))
        legacy_show = bool(isettings.get(secondary_key))
        if legacy_show != viewport_show:
            isettings.set(per_viewport_key, legacy_show)
        if is_stage_global:
            usd_key = f"/app/viewport/usdcontext-{usd_context_name}/{setting_key}"
            if legacy_show != bool(isettings.get(usd_key)):
                isettings.set(usd_key, legacy_show)

    def subscribe_to_legacy_obj(setting_key: str, isettings):
        legacy_obj = persitent_to_legacy_map.get(setting_key)
        if legacy_obj and legacy_obj[1]:
            return isettings.subscribe_to_node_change_events(legacy_obj[1], partial(legacy_value_changed, setting_key))

        carb.log_error("No mapping for '{setting_key}' into legacy setting")
        return None

    def global_value_changed(setting_key: str, item: carb.dictionary.Item, event_type: carb.settings.ChangeEventType):
        if event_type != carb.settings.ChangeEventType.CHANGED:
            return

        legacy_obj = persitent_to_legacy_map.get(setting_key)
        if not legacy_obj:
            carb.log_error("No mapping for '{setting_key}' into legacy setting")
            return

        # Simply forwards the global setting to all Viewport instances attached to this UsdContext
        isettings = carb.settings.get_settings()
        global_visible = isettings.get(f"/app/viewport/usdcontext-{usd_context_name}/{setting_key}")
        per_viewport_key, secondary_key = format_secondary_key(setting_key, legacy_obj[1])
        # Push global stage state into legacy global key state (that may be watched by other consumers)
        if secondary_key:
            legacy_show = bool(isettings.get(secondary_key))
            if legacy_show != global_visible:
                isettings.set(secondary_key, global_visible)
        # Push global stage state into per-viewport state
        if global_visible != bool(isettings.get(per_viewport_key)):
            isettings.set(per_viewport_key, global_visible)
        # XXX: Special case skeletons because that is handled externally and still tied to displayOptions
        # if setting_key == "scene/skeletons/visible":
        #     display_options = isettings.get(legacy_display_options_key)
        #     # If legacy display options is None, then it is not set at all: assume application doesnt want them at all
        #     if display_options is not None:
        #         legacy_bitmask = (1 << 9)  # Avoid persitent_to_legacy_map.get(setting_key)[0], already know the bitmask
        #         if global_visible != bool(display_options & legacy_bitmask):
        #             display_options = display_options | (1 << 9)
        #             isettings.set(legacy_display_options_key, display_options)
        #     else:
        #         carb.log_warn(f"{legacy_display_options_key} is unset, assuming application does not want it")

    def subscribe_to_global_obj(setting_key: str, isettings):
        legacy_obj = persitent_to_legacy_map.get(setting_key)
        if legacy_obj and legacy_obj[2]:
            global_key = f"/app/viewport/usdcontext-{usd_context_name}/{setting_key}"
            return isettings.subscribe_to_node_change_events(global_key, partial(global_value_changed, setting_key))

        carb.log_error("No mapping for '{setting_key}' into global stage setting")
        return None

    for setting_key, legacy_obj in persitent_to_legacy_map.items():
        legacy_bitmask, secondary_key, is_usd_state = legacy_obj
        legacy_visible = bool(legacy_display_options & legacy_bitmask)
        visible = _resolve_viewport_setting(viewport_id, setting_key, isettings, secondary_key, True, legacy_visible,
                                            usd_context_name=usd_context_name if is_usd_state else None)
        _, secondary_key = format_secondary_key(setting_key, secondary_key)
        if secondary_key:
            legacy_value = isettings.get(secondary_key)
            if (legacy_value is None) or (legacy_value != visible):
                isettings.set(secondary_key, visible)

        # Now take the full resolved 'visible' value and push back into the cached legacy_display_options bitmask.
        # This is so that any errant extension that still sets to displayOptions will trigger a global toggle
        # of the setting for all Viewports
        if legacy_visible != visible:
            if visible:
                legacy_display_options = legacy_display_options | legacy_bitmask
            else:
                legacy_display_options = legacy_display_options & ~legacy_bitmask

    # Global HUD visibility: first resolve to based on new persitent per-viewport and its defaults
    _resolve_viewport_setting(viewport_id, "hud/visible", isettings, None, True, True)

    # Global bounding box visibility:
    # First resolve to based on new persitent per-viewport and its defaults
    # Second sync legacy setting since it is not in display options
    legacy_bounding_box_setting_name = "/app/viewport/boundingBoxes/enabled"
    current_value = _resolve_viewport_setting(viewport_id, "guide/boundingBox/visible", isettings, legacy_bounding_box_setting_name, True, True)
    legacy_value = isettings.get(legacy_bounding_box_setting_name)
    if legacy_value != current_value:
        isettings.set(legacy_bounding_box_setting_name, current_value)

    return (
        isettings.subscribe_to_node_change_events(legacy_display_options_key, legacy_display_options_changed),
        # Subscriptions to manage legacy drawing state across all Viewports
        subscribe_to_legacy_obj("guide/grid/visible", isettings),
        subscribe_to_legacy_obj("guide/selection/visible", isettings),
        subscribe_to_legacy_obj("scene/cameras/visible", isettings),
        subscribe_to_legacy_obj("scene/lights/visible", isettings),
        subscribe_to_legacy_obj("scene/audio/visible", isettings),
        # Subscriptions to manage UsdStage state across Viewports sharing a UsdContext
        subscribe_to_global_obj("scene/cameras/visible", isettings),
        subscribe_to_global_obj("scene/lights/visible", isettings),
        subscribe_to_global_obj("scene/skeletons/visible", isettings),
        subscribe_to_global_obj("scene/meshes/visible", isettings),
        subscribe_to_global_obj("scene/audio/visible", isettings),
    )
