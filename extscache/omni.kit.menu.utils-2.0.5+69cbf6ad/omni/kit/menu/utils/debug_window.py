"""
Menu debug window. Press "SHIFT+CONTROL+ALT+M" to open.
"""

__all__ = ["MenuUtilsDebugExtension"]

# pylint: disable=redefined-outer-name, protected-access
import asyncio
import json

import carb
import carb.settings
import omni.ext
from omni import ui


class MenuUtilsDebugExtension(omni.ext.IExt):
    """
    Menu debug window. Press "SHIFT+CONTROL+ALT+M" to open.
    """

    def __init__(self):
        super().__init__()
        self._extension_name = None
        self._debug_window = None
        self._registered_hotkey = None
        self._hooks = []

    def on_startup(self):
        manager = omni.kit.app.get_app().get_extension_manager()
        self._extension_name = omni.ext.get_extension_name(manager.get_extension_id_by_module(__name__))
        self._hooks = []
        self._debug_window = None

        self._hooks.append(
            manager.subscribe_to_extension_enable(
                on_enable_fn=lambda _: self._register_actions(),
                ext_name="omni.kit.actions.core",
                hook_name="omni.kit.menu.utils debug omni.kit.actions.core listener",
            )
        )

        self._hooks.append(
            manager.subscribe_to_extension_enable(
                on_enable_fn=lambda _: self._register_hotkeys(),
                ext_name="omni.kit.hotkeys.core",
                hook_name="omni.kit.menu.utils debug omni.kit.hotkeys.core listener",
            )
        )

    def on_shutdown(self):
        omni.kit.actions.core.get_action_registry().deregister_action(
            self._extension_name, "show_menu_debug_debug_window"
        )

        self._hooks = []

        if self._debug_window:
            del self._debug_window
            self._debug_window = None

        try:
            from omni.kit.hotkeys.core import get_hotkey_registry

            hotkey_registry = get_hotkey_registry()
            hotkey_registry.deregister_hotkey(self._registered_hotkey)
        except (ModuleNotFoundError, AttributeError):
            pass

    def _register_actions(self):
        import omni.kit.actions.core

        omni.kit.actions.core.get_action_registry().register_action(
            self._extension_name,
            "show_menu_debug_debug_window",
            self.show_menu_debug_debug_window,
            display_name="Show Menu Debug Window",
            description="Show Menu Debug Window",
            tag="Menu Debug Actions",
        )

    def _register_hotkeys(self):
        from omni.kit.hotkeys.core import KeyCombination, get_hotkey_registry

        hotkey_combo = KeyCombination(
            carb.input.KeyboardInput.M,
            modifiers=carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL
            + carb.input.KEYBOARD_MODIFIER_FLAG_ALT
            + carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT,
        )
        hotkey_registry = get_hotkey_registry()
        self._registered_hotkey = hotkey_registry.register_hotkey(
            self._extension_name, hotkey_combo, self._extension_name, "show_menu_debug_debug_window"
        )

    def show_menu_debug_debug_window(self):
        import omni.kit.ui
        from omni.ui import color as cl

        collapsable_frame_style = {
            "CollapsableFrame": {
                "background_color": 0xFF343432,
                "secondary_color": 0xFF343432,
                "color": 0xFFAAAAAA,
                "border_radius": 4.0,
                "border_color": 0x0,
                "border_width": 0,
                "font_size": 14,
                "padding": 0,
            },
            "HStack::header": {"margin": 5},
            "CollapsableFrame:hovered": {"secondary_color": 0xFF3A3A3A},
            "CollapsableFrame:pressed": {"secondary_color": 0xFF343432},
        }

        def show_dict_data(legend, value):
            if value:
                ui.Button(
                    f"Save {legend}",
                    clicked_fn=lambda b=None: save_dict(legend, value),
                    height=24,
                    identifier=f"save_{legend.lower().replace(' ', '_')}",
                )
            else:
                ui.Button(
                    f"Save {legend}",
                    clicked_fn=lambda b=None: save_dict(legend, value),
                    height=24,
                    identifier=f"save_{legend.lower().replace(' ', '_')}",
                    enabled=False,
                )

        async def refresh_debug_window(rebuild_menus):
            await omni.kit.app.get_app().next_update_async()
            self._debug_window.frame.clear()
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()
            del self._debug_window
            self._debug_window = None
            if rebuild_menus:
                omni.kit.menu.utils.rebuild_menus()
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()
            self.show_menu_debug_debug_window()

        def save_dict(legend, value):
            from omni.kit.window.file_exporter import get_file_exporter

            def on_click_save(filename: str, dirname: str, extension: str, value: dict):
                dirname = dirname.strip()
                if dirname and not dirname.endswith("/"):
                    dirname += "/"
                fullpath = f"{dirname}{filename}{extension}"

                def serialize(obj):
                    if hasattr(obj, "json_enc"):
                        return obj.json_enc()
                    if hasattr(obj, "__dict__"):
                        return obj.__dict__

                    return {"unknown": f"{obj}"}

                with open(fullpath, "w", encoding="utf-8") as file:
                    file.write(json.dumps(value, default=serialize))

            file_exporter = get_file_exporter()
            if file_exporter:
                file_exporter.show_window(
                    title=f"Save {legend} as json",
                    export_button_label="Save",
                    export_handler=lambda filename, dirname, extension, selections: on_click_save(
                        filename, dirname, extension.replace(".usd", ""), value
                    ),
                    file_postfix_options=["json"],
                )

        self._debug_window = ui.Window("omni.kit.menu.utils debug", width=600)
        with self._debug_window.frame:
            with ui.VStack():
                # header
                menu_instance = omni.kit.menu.utils.get_instance()
                menu_creator = None
                if menu_instance:
                    ui.Label("omni.kit.menu.utils - Alive", height=20)
                    menu_creator = menu_instance._menu_creator
                else:
                    ui.Label("omni.kit.menu.utils - Shut Down", height=20)

                legacy_mode = omni.kit.ui.using_legacy_mode()
                ui.Label(f"omni.kit.ui.get_editor_menu() -> omni.kit.menu.utils: {not legacy_mode}", height=20)

                if menu_creator:
                    ui.Label(f"omni.kit.menu.utils - Creator: {menu_creator.__class__.__name__}", height=20)
                else:
                    ui.Label("omni.kit.menu.utils - Creator: Not Found", height=20)

                ui.Spacer(height=8)

                with ui.ScrollingFrame():
                    with ui.VStack():
                        # debug stats
                        open_stat_frame = False
                        stat_frame = ui.CollapsableFrame(
                            title="Debug Stats",
                            collapsed=True,
                            style=collapsable_frame_style,
                            height=16,
                            identifier="stats_frame",
                        )
                        with stat_frame:
                            with ui.VStack():
                                debug_stats = omni.kit.menu.utils.get_debug_stats()
                                for stat in debug_stats.keys():
                                    name = stat.replace("_", " ").title()
                                    if isinstance(debug_stats[stat], dict):
                                        with ui.CollapsableFrame(
                                            title=stat, collapsed=True, style=collapsable_frame_style
                                        ):
                                            with ui.VStack():
                                                refreshed_items = debug_stats[stat].keys()
                                                if refreshed_items:
                                                    for refreshed in refreshed_items:
                                                        ui.Label(
                                                            f"           {refreshed}: {debug_stats[stat][refreshed]}",
                                                            height=18,
                                                            style={"color": cl.white},
                                                        )
                                                else:
                                                    ui.Label("           Nothing", height=18, style={"color": cl.white})

                                    elif stat == "extension_loaded_count":
                                        if debug_stats[stat] != 1:
                                            open_stat_frame = True
                                        ui.Label(
                                            f"        {name}: {debug_stats[stat]}",
                                            height=18,
                                            style={"color": cl.red if open_stat_frame else cl.white},
                                        )
                                    else:
                                        ui.Label(
                                            f"        {name}: {debug_stats[stat]}", height=18, style={"color": cl.white}
                                        )

                        open_menu_frame = False
                        if menu_creator:
                            # ui.Menu frame
                            if menu_creator.__class__.__name__ == "AppMenu":
                                menu_frame = ui.CollapsableFrame(
                                    title="ui.Menu",
                                    collapsed=True,
                                    style=collapsable_frame_style,
                                    height=16,
                                    identifier="ui_frame",
                                )
                                with menu_frame:
                                    with ui.VStack():
                                        menu_chain = menu_creator._main_menus
                                        if not menu_chain or not all(
                                            k in menu_chain for k in ["File", "Edit", "Window", "Help"]
                                        ):
                                            ui.Label("        ERROR MISSING MENUS", height=20, style={"color": cl.red})
                                            open_menu_frame = True

                                        for key in menu_chain.keys():
                                            if not menu_chain[key].visible:
                                                open_menu_frame = True
                                            ui.Label(
                                                f"        {key} visible:{menu_chain[key].visible}",
                                                height=20,
                                                style={"color": cl.white if menu_chain[key].visible else cl.red},
                                            )

                            # empty frame to force 2 other frames to top
                            ui.Frame()

                ui.Spacer(height=8)

                menu_layout = omni.kit.menu.utils.get_menu_layout()
                merged_menus = omni.kit.menu.utils.get_merged_menus()

                show_dict_data("Menu Layout", menu_layout)
                show_dict_data("Menus", merged_menus)

                ui.Button(
                    "Refresh Debug Window",
                    clicked_fn=lambda: asyncio.ensure_future(refresh_debug_window(False)),
                    height=24,
                    identifier="refresh_window",
                )
                ui.Button(
                    "Rebuild Menus",
                    clicked_fn=lambda: asyncio.ensure_future(refresh_debug_window(True)),
                    height=24,
                    identifier="rebuild_menus",
                )

                ui.Spacer(height=30)

                if open_stat_frame:
                    stat_frame.collapsed = False
                if open_menu_frame:
                    menu_frame.collapsed = False
