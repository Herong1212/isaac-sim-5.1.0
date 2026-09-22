# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["build_reload_widget"]

from functools import partial
from typing import Union
import weakref

import carb
import omni.kit.app
from omni.kit.async_engine import run_coroutine
import omni.kit.usd.layers as layers
import omni.ui as ui
import omni.usd

from .live_style import Styles
from .layer_icons import LayerIcons
from .utils import reload_outdated_layers



class ReloadWidgetWrapper(ui.ZStack):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.auto_reload_menu = None

    def __del__(self):
        if self.auto_reload_menu:
            self.auto_reload_menu.hide()
            self.auto_reload_menu = None


def show_reload_menu(layer_identifier, usd_context, widget, button, global_auto):
    """Creates and shows a reload menu relative to widget position"""

    layers_state = layers.get_layers_state(usd_context)
    live_syncing = layers.get_live_syncing()
    is_outdated = layers_state.is_layer_outdated(layer_identifier)
    in_session = live_syncing.is_layer_in_live_session(layer_identifier)

    def toggle_auto_reload(layer_identifier, widget):
        async def toggle(layer_identifier):
            is_auto = layers_state.is_auto_reload_layer(layer_identifier)
            if not is_auto:
                layers_state.add_auto_reload_layer(layer_identifier)
                widget.set_style(Styles.RELOAD_AUTO)
                button.tooltip = "Auto Reload Enabled"
            else:
                layers_state.remove_auto_reload_layer(layer_identifier)
                widget.set_style(Styles.RELOAD_BTN)
                button.tooltip = "Reload"

        run_coroutine(toggle(layer_identifier))

    def reload_layer(layer_identifier):
        reload_outdated_layers(layer_identifier, layers_state._usd_context)

    auto_reload_menu = ui.Menu("auto_reload_menu")
    with auto_reload_menu:
        ui.MenuItem(
            "Reload Layer",
            triggered_fn=lambda *args: reload_layer(layer_identifier),
            enabled=is_outdated,
            visible=not global_auto
        )
        ui.MenuItem(
            "Auto Reload",
            triggered_fn=lambda *args: toggle_auto_reload(layer_identifier, widget),
            checkable=True,
            checked=layers_state.is_auto_reload_layer(layer_identifier),
            visible=not global_auto,
            enabled=not in_session
        )

    _x = widget.screen_position_x
    _y = widget.screen_position_y
    _h = widget.computed_height

    auto_reload_menu.show_at(_x - 95, _y + _h / 2 + 2)

    return auto_reload_menu


def build_reload_widget(
    layer_identifier: str,
    usd_context_name_or_instance: Union[str, omni.usd.UsdContext] = None,
    is_outdated=False,
    is_auto=False,
    global_auto=False
) -> None:
    """Builds reload widget."""

    if isinstance(usd_context_name_or_instance, str):
        usd_context = omni.usd.get_context(usd_context_name_or_instance)
    elif isinstance(usd_context_name_or_instance, omni.usd.UsdContext):
        usd_context = usd_context_name_or_instance
    elif not usd_context_name_or_instance:
        usd_context = omni.usd.get_context()

    if not usd_context:
        carb.log_error("Failed to reload layer as usd context is not invalid.")
        return

    reload_stack = ReloadWidgetWrapper(width=0, height=0)

    if global_auto:
        is_auto = global_auto

    reload_stack.name = "reload-auto" if is_auto else "reload-outd" if is_outdated else "reload"
    reload_stack.set_style(Styles.RELOAD_AUTO if is_auto and not is_outdated else Styles.RELOAD_OTD if is_outdated else Styles.RELOAD_BTN)
    with reload_stack:
        with ui.VStack(width=0, height=0):
            ui.Spacer(width=22, height=12)
            with ui.HStack(width=0):
                ui.Spacer(width=16)
                ui.Image(
                    LayerIcons.get("drop_down"),
                    width=6, height=6, alignment=ui.Alignment.RIGHT_BOTTOM,
                    name="drop_down"
                )
        ui.Image(LayerIcons.get("reload"), width=20, name="reload", identifier="reload_button")

        tooltip = "Auto Reload All Enabled" if global_auto else "Auto Reload Enabled" if is_auto else "Reload"
        if is_outdated:
            tooltip = "Reload Outdated"
        reload_button = ui.InvisibleButton(width=20, tooltip=tooltip)

    def on_reload_clicked(layout_weakref, x, y, b, m):
        if (b == 0):
            reload_outdated_layers(layer_identifier, usd_context)
            return

        auto_reload_menu = show_reload_menu(layer_identifier, usd_context, reload_stack, reload_button, global_auto)

        if layout_weakref():
            # Hold the menu handle to release it along with the stack.
            layout_weakref().auto_reload_menu = auto_reload_menu

    layout_weakref = weakref.ref(reload_stack)
    reload_button.set_mouse_pressed_fn(partial(on_reload_clicked, layout_weakref))

    return reload_stack
