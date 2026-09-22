# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import carb
import omni.kit.actions.core
import omni.ui as ui

esc_key_binding = None

SHOW_DPI_SCALE_MENU_SETTING = "/app/window/showDpiScaleMenu"
DPI_SCALE_OVERRIDE_SETTING = "/app/window/dpiScaleOverride"
DPI_SCALE_OVERRIDE_DEFAULT = -1.0
DPI_SCALE_OVERRIDE_MIN = 0.5
DPI_SCALE_OVERRIDE_MAX = 5.0
DPI_SCALE_OVERRIDE_STEP = 0.5

def register_actions(extension_id: str):
    carb.settings.get_settings().set_default_bool(SHOW_DPI_SCALE_MENU_SETTING, False)
    actions_tag = "UI Actions"

    # add UI hotkeys
    toggle_ui_hotkey = None
    toggle_fullscreen_hotkey = None
    dpi_scale_increase_hotkey = None
    dpi_scale_decrease_hotkey = None
    action_registry = omni.kit.actions.core.get_action_registry()

    if carb.settings.get_settings().get("exts/omni.kit.ui.actions/ui_hotkeys"):
        toggle_ui_hotkey = "F7"
        # check if IAppWindowImplOs has already registered F11
        if not carb.settings.get_settings().get("/exts/omni.appwindow/listenF11"):
            toggle_fullscreen_hotkey = "F11"

        if carb.settings.get_settings().get_as_bool( "/app/window/showDpiScaleMenu"):
            dpi_scale_increase_hotkey = "EQUAL"
            dpi_scale_decrease_hotkey = "MINUS"
    
    action_registry.register_action(
		extension_id,
		"toggle_ui",
		on_toggle_ui,
		display_name="Toggle Viewport UI Overlay",
		description="Toggle Viewport UI Overlay",
		tag=actions_tag
	)

    action_registry.register_action(
		extension_id,
		"toggle_fullscreen",
		on_fullscreen,
		display_name="Toggle Viewport Fullscreen",
		description="Toggle Viewport Fullscreen",
		tag=actions_tag
	)

    action_registry.register_action(
		extension_id,
		"dpi_scale_increase",
		on_dpi_scale_increase,
		display_name="DPI Scale Increase",
		description="DPI Scale Increase",
		tag=actions_tag
	)

    action_registry.register_action(
		extension_id,
		"dpi_scale_decrease",
		on_dpi_scale_decrease,
		display_name="DPI Scale Decrease",
		description="DPI Scale Decrease",
		tag=actions_tag
	)

    action_registry.register_action(
		extension_id,
		"dpi_scale_reset",
		on_dpi_scale_reset,
		display_name="DPI Scale Reset",
		description="DPI scale reset to default",
		tag=actions_tag
	)

    action_registry.register_action(
		extension_id,
		"cancel_fullscreen_ui",
		lambda: on_fullscreen(False),
		display_name="Cancel fullscreen and/or no-UI",
		description="Cancel fullscreen and/or no-UI",
		tag=actions_tag
	)

def deregister_actions(extension_id):
    action_registry = omni.kit.actions.core.get_action_registry()
    if action_registry:
        action_registry.deregister_all_actions_for_extension(extension_id)

__workspace_data = None

def set_ui_hidden(hide: bool, save_ui: bool):
    if hide:
        # hide context_menu
        try:
            import omni.kit.context.menu
            omni.kit.context_menu.close_menu()
        except:
            pass

        # windows are going to be hidden. Save workspace 1st
        if save_ui:
            toggle_windowed(True)

        carb.settings.get_settings().set("/app/window/hideUi", hide)
    else:
        carb.settings.get_settings().set("/app/window/hideUi", hide)
        # windows are going to be restored from hidden. Re-load workspace
        #   ui.Workspace.restore_workspace is async so it don't need to
        #   wait for initial unhide of the window here
        if save_ui:
            toggle_windowed(False)

def is_ui_hidden():
    return carb.settings.get_settings().get("/app/window/hideUi")

def toggle_windowed(save: bool):
    global __workspace_data

    if save:
        __workspace_data = ui.Workspace.dump_workspace()
    elif __workspace_data:
        ui.Workspace.restore_workspace(__workspace_data, False)
        __workspace_data = None

def on_toggle_ui(new_state=None):
    import omni.appwindow

    if new_state is None:
        new_state = not is_ui_hidden()
    is_fullscreen = omni.appwindow.get_default_app_window().is_fullscreen()
    set_ui_hidden(new_state, not is_fullscreen)
    if not is_fullscreen:
        update_cancel_hotkey(new_state)

def on_fullscreen(new_state=None):
    display_mode_lock = carb.settings.get_settings().get(f"/app/window/displayModeLock")
    if display_mode_lock:
        # Always stay in fullscreen_mode, only hide or show UI.
        set_ui_hidden(new_state if new_state is None else not is_ui_hidden(), True)
    else:
        import omni.appwindow

        # Only toggle fullscreen on/off when not display_mode_lock
        was_fullscreen = omni.appwindow.get_default_app_window().is_fullscreen()
        if new_state is None:
            new_state = not was_fullscreen

        if new_state != was_fullscreen:
            # save window state when not fullscreen and not ui_hidden
            if not was_fullscreen and not is_ui_hidden():
                toggle_windowed(True)
            omni.appwindow.get_default_app_window().set_fullscreen(new_state)

            # Always hide UI in fullscreen
            set_ui_hidden(new_state, False)

            # restore window state when not fullscreen anymore (ui_hidden hidden has been canceled)
            if was_fullscreen:
                toggle_windowed(False)
            update_cancel_hotkey(new_state)
        # not fullscreen and not display_mode_lock. Still may need to change ui
        elif new_state != is_ui_hidden():
            # save window state when not fullscreen and not ui_hidden
            if new_state and not is_ui_hidden():
                toggle_windowed(True)
            set_ui_hidden(new_state, False)
            # restore window state when ui_hidden has been canceled
            if not new_state:
                toggle_windowed(False)
            update_cancel_hotkey(new_state)

def update_cancel_hotkey(new_state):
    # register ESCAPE to cancel fullscreen/no-UI (F11/F7)
    #  this is special case as omni.kit.menu.edit also registers this key from clear selection
    #  so add hotkey_filter to prevent duplicate hotkey spam
    if carb.settings.get_settings().get("exts/omni.kit.ui.actions/ui_hotkey_escape"):
        import omni.kit.hotkeys.core as hotkeys
        global esc_key_binding

        hotkey_registry = hotkeys.get_hotkey_registry()
        if new_state:
            if not esc_key_binding:
                esc_key_binding = hotkey_registry.register_hotkey(
                    hotkey_ext_id="omni.kit.ui.actions",
                    key="ESCAPE",
                    action_ext_id="omni.kit.ui.actions",
                    action_id="cancel_fullscreen_ui",
                    filter=hotkeys.HotkeyFilter(windows=["Viewport"]),
                )
        else:
            hotkey_registry.deregister_hotkey(esc_key_binding)
            esc_key_binding = None

def step_and_clamp_dpi_scale_override(increase):
    import omni.ui as ui

    # Get the current value.
    dpi_scale = carb.settings.get_settings().get_as_float(DPI_SCALE_OVERRIDE_SETTING)
    if dpi_scale == DPI_SCALE_OVERRIDE_DEFAULT:
        dpi_scale = ui.Workspace.get_dpi_scale()

    # Increase or decrease the current value by the step value.
    if increase:
        dpi_scale += DPI_SCALE_OVERRIDE_STEP
    else:
        dpi_scale -= DPI_SCALE_OVERRIDE_STEP

    # Clamp the new value between the min/max values.
    dpi_scale = max(min(dpi_scale, DPI_SCALE_OVERRIDE_MAX), DPI_SCALE_OVERRIDE_MIN)

    # Set the new value.
    carb.settings.get_settings().set(DPI_SCALE_OVERRIDE_SETTING, dpi_scale)

def on_dpi_scale_increase():
    step_and_clamp_dpi_scale_override(True)

def on_dpi_scale_decrease():
    step_and_clamp_dpi_scale_override(False)

def on_dpi_scale_reset():
    carb.settings.get_settings().set(DPI_SCALE_OVERRIDE_SETTING, DPI_SCALE_OVERRIDE_DEFAULT)
