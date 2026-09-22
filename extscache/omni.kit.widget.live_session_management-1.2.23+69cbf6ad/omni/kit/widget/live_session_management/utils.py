# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = [
    "build_live_session_user_layout",
    "is_viewer_only_mode",
    "VIEWER_ONLY_MODE_SETTING",
    "reload_outdated_layers",
]

import asyncio
import os
from typing import Union, List, Callable

import carb
import omni.kit.app
from omni.kit.async_engine import run_coroutine
import omni.kit.usd.layers as layers
from omni.kit.widget.prompt import PromptManager, PromptButtonInfo
import omni.ui as ui
import omni.usd
from pxr import Sdf


VIEWER_ONLY_MODE_SETTING = "/exts/omni.kit.widget.live_session_management/viewer_only_mode"

# When this setting is True, it will show the Join/Create Session dialog wqhen the quick live button is pressed.
# When this setting if False, it will auto Create Session or Join with no dialog shown.
QUICK_JOIN_ENABLED = "/exts/omni.kit.widget.live_session_management/quick_join_enabled"

SESSION_LIST_SELECT = "/exts/omni.kit.widget.live_session_management/session_list_select"

SESSION_LIST_SELECT_DEFAULT_SESSION = "DefaultSession"
SESSION_LIST_SELECT_LAST_SESSION = "LastSession"


def is_viewer_only_mode():
    """Return True if viewer only mode is enabled based on settings.

    When it returns True, it will follow rules:
        * When joining a live session, if the user has unsaved changes, skip the dialog and automatically reload the stage, then join the session.
        * When creating a live session, if the user has unsaved changes, skip the dialog and automatically reload the stage, then create the session.
        * When leaving a live session, do not offer to merge changes, instead reload the stage to its original state.

    This mode can be controlled by setting omni.kit.widget.live_session_management.VIEWER_ONLY_MODE_SETTING.

    Returns:
        bool: True if viewer only mode is enabled; otherwise False.
    """

    return carb.settings.get_settings().get(VIEWER_ONLY_MODE_SETTING) or False


def is_quick_join_enabled():
    return carb.settings.get_settings().get(QUICK_JOIN_ENABLED) or False


def get_session_list_select():
    return carb.settings.get_settings().get(SESSION_LIST_SELECT)


def join_live_session(layers_interface, layer_identifier, current_session, prim_path=None, force_reload=False):
    layers_state = layers_interface.get_layers_state()
    live_syncing = layers_interface.get_live_syncing()
    layer_handle = Sdf.Find(layer_identifier)

    def fetch_and_join(layer_identifier):
        with Sdf.ChangeBlock():
            layer = Sdf.Find(layer_identifier)
            if layer:
                layer.Reload(True)

            if layers_state.is_auto_reload_layer(layer_identifier):
                layers_state.remove_auto_reload_layer(layer_identifier)
            return live_syncing.join_live_session(current_session, prim_path)

    async def post_simple_prompt(title, text, ok_button_info, cancel_button_info):
        await omni.kit.app.get_app().next_update_async()
        PromptManager.post_simple_prompt(
            title, text, ok_button_info=ok_button_info, cancel_button_info=cancel_button_info
        )

    is_outdated = layers_state.is_layer_outdated(layer_identifier)
    if force_reload and (is_outdated or layer_handle.dirty):
        fetch_and_join(layer_identifier)
    elif is_outdated:
        asyncio.ensure_future(
            post_simple_prompt(
                "Join Session",
                "The file you would like to go live on is not up to date, "
                "a newer version must be fetched for joining a live session. "
                "Press Fetch to get the most recent version or use Cancel "
                "if you would like to save a copy first.",
                ok_button_info=PromptButtonInfo("Fetch", lambda: fetch_and_join(layer_identifier)),
                cancel_button_info=PromptButtonInfo("Cancel"),
            )
        )
    elif layer_handle.dirty:
        asyncio.ensure_future(
            post_simple_prompt(
                "Join Session",
                "There are unsaved changes to your file. Joining this live session will discard any unsaved changes.",
                ok_button_info=PromptButtonInfo("Join", lambda: fetch_and_join(layer_identifier)),
                cancel_button_info=PromptButtonInfo("Cancel"),
            )
        )
    else:
        if layers_state.is_auto_reload_layer(layer_identifier):
            layers_state.remove_auto_reload_layer(layer_identifier)
        return live_syncing.join_live_session(current_session, prim_path)

    return True


def is_extension_loaded(extansion_name: str) -> bool:
    """
    Returns True if the extension with the given name is loaded.
    """

    def is_ext(id: str, extension_name: str) -> bool:
        id_name = id.split("-")[0]
        return id_name == extension_name

    app = omni.kit.app.get_app_interface()
    ext_manager = app.get_extension_manager()
    extensions = ext_manager.get_extensions()

    loaded = next((ext for ext in extensions if is_ext(ext["id"], extansion_name) and ext["enabled"]), None)

    return not not loaded


def build_live_session_user_layout(
    user_info: layers.LiveSessionUser,
    size=16,
    tooltip="",
    on_double_click_fn: Callable[[float, float, int, int, layers.LiveSessionUser], None] = None,
    on_mouse_click_fn: Callable[[float, float, int, int, layers.LiveSessionUser], None] = None,
) -> ui.ZStack:
    """Utility function to build an user icon widget with user information.

    Args:
        user_info (layers.LiveSessionUser): User information.
        size (int): Icon size; default is 16.
        tooltip (str): Tooltip of the widget.
        on_double_click_fn (Callable[[float, float, int, int, layers.LiveSessionUser], None]): Callback when the widget is double clicked. The first two parameters are the mouse x and y positions. The third parameter indicates the mouse button (0 for LMB, 1 for RMB). The fourth parameter is the keyboard modifier; see carb.input.KEYBOARD_MODIFIER_FLAG_* for details.
        on_mouse_click_fn (Callable[[float, float, int, int, layers.LiveSessionUser], None]): Callback when the widget is single clicked.

    Returns:
        ui.ZStack: The widget containing the user icon.
    """

    user_layout = ui.ZStack(width=size, height=size)
    with user_layout:
        circle = ui.Circle(style={"background_color": ui.color(*user_info.user_color)})

        if on_double_click_fn:
            circle.set_mouse_double_clicked_fn(
                lambda x, y, b, m, user_info_t=user_info: on_double_click_fn(x, y, b, m, user_info_t)
            )

        if on_mouse_click_fn:
            circle.set_mouse_pressed_fn(
                lambda x, y, b, m, user_info_t=user_info: on_mouse_click_fn(x, y, b, m, user_info_t)
            )

        ui.Label(
            layers.get_short_user_name(user_info.user_name),
            style={"font_size": size - 5, "color": 0xFFFFFFFF},
            alignment=ui.Alignment.CENTER,
        )

    if tooltip:
        user_layout.set_tooltip(tooltip)

    return user_layout


def reload_outdated_layers(
    layer_identifiers: Union[str, List[str]], usd_context_name_or_instance: Union[str, omni.usd.UsdContext] = None
) -> None:
    """Reloads outdated layer. It will show a prompt to the user if the layer is in a Live Session.

    Args:
        layer_identifiers (Union[str, List[str]]): Layer identifier(s) to reload if outdated.
        usd_context_name_or_instance (Union[str, omni.usd.UsdContext]): The USD context name or instance; if not provided, uses the current context.
    """

    if isinstance(usd_context_name_or_instance, str):
        usd_context = omni.usd.get_context(usd_context_name_or_instance)
    elif isinstance(usd_context_name_or_instance, omni.usd.UsdContext):
        usd_context = usd_context_name_or_instance
    elif not usd_context_name_or_instance:
        usd_context = omni.usd.get_context()

    if not usd_context:
        carb.log_error("Failed to reload layer as usd context is not invalid.")
        return

    if isinstance(layer_identifiers, str):
        layer_identifiers = [layer_identifiers]

    live_syncing = layers.get_live_syncing(usd_context)
    layers_state = layers.get_layers_state(usd_context)

    all_layer_ids = layers_state.get_all_outdated_layer_identifiers()
    if not all_layer_ids:
        return

    layer_identifiers = [layer_id for layer_id in layer_identifiers if layer_id in all_layer_ids]
    if not layer_identifiers:
        return

    count = 0
    for layer_identifier in layer_identifiers:
        if live_syncing.is_layer_in_live_session(layer_identifier):
            count += 1

    if count == 1:
        title = f"{os.path.basename(layer_identifier)} is in a Live Session"
    else:
        title = "Reload Layers In Live Session"

    def reload_layers(layer_identifiers):
        async def reload(layer_identifiers):
            layers.LayerUtils.reload_all_layers(layer_identifiers)

        run_coroutine(reload(layer_identifiers))

    if count != 0:
        PromptManager.post_simple_prompt(
            title,
            "Reloading live layers has performance implications and some live edits may be lost - OK to proceed?",
            PromptButtonInfo("YES", lambda: reload_layers(layer_identifiers)),
            PromptButtonInfo("NO"),
        )
    else:
        reload_layers(layer_identifiers)
