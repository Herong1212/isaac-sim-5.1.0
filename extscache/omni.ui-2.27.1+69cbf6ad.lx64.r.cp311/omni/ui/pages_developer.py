import asyncio
import carb
import omni.ui as ui
import omni.kit.app
from omni.kit.window.preferences import PreferenceBuilder, SettingType, PERSISTENT_SETTINGS_PREFIX
from carb.eventdispatcher import get_eventdispatcher

ENABLE_MIPS_PATH = "/exts/omni.kit.renderer.core/imgui/enableMips"
GENERATE_MIPS_PATH = "/persistent/exts/omni.ui/Image/generateMips"


class DeveloperPreferences(PreferenceBuilder):

    def __init__(self):
        super().__init__("Developer")
        self.__hooks = []
        self._fail_dialog = None

        # add settings callbacks
        self.__hooks.append(omni.kit.app.SettingChangeSubscription(GENERATE_MIPS_PATH, self._on_developer_preference_generatemips_changed))

    def show_page(self) -> bool:
        return carb.settings.get_settings().get("/app/show_developer_preference_section")

    def build(self):
        with ui.VStack(height=0):
            """ ui.Image """
            with self.add_frame("Mip Mapping in ui.Image"):
                with ui.VStack():
                    # check settings as they can be overridden
                    self.create_setting_widget("Generate Mips", GENERATE_MIPS_PATH, SettingType.BOOL)

    def _show_restart_message(self):
        from omni.kit.window.popup_dialog import MessageDialog

        async def on_ok_clicked(dialog):
            import sys
            import carb.events
            import omni.kit.app

            dialog.hide()

            def on_event(_):
                from omni.kit.window.preferences import restart_kit

                restart_kit(sys.argv)

            self._shutdown_sub = get_eventdispatcher().observe_event(event_name=omni.kit.app.GLOBAL_EVENT_PRE_SHUTDOWN, on_event=on_event, observer_name="re-start kit", order=0)
            await omni.kit.app.get_app().next_update_async()
            omni.kit.app.get_app().post_quit()


        if omni.usd.get_context().has_pending_edit():
            dialog = MessageDialog(
                title= f"{ui.get_custom_glyph_code('${glyphs}/exclamation.svg')} Restart so changes can take effect",
                width=400,
                message=f"This application will restart for new setting to take effect.\n\nYou will be prompted to save any unsaved changes.",
                ok_handler=lambda dialog: asyncio.ensure_future(on_ok_clicked(dialog)),
                ok_label="Continue",
                cancel_label="Cancel",
            )
        else:
            dialog = MessageDialog(
                title= f"{ui.get_custom_glyph_code('${glyphs}/exclamation.svg')} Restart so changes can take effect",
                width=400,
                message=f"This application will restart for new setting to take effect.",
                ok_handler=lambda dialog: asyncio.ensure_future(on_ok_clicked(dialog)),
                ok_label="Restart",
                cancel_label="Cancel",
            )
        dialog.show()

    def _on_developer_preference_generatemips_changed(self, item, event_type):
        # this can get triggered by "/persistent/exts/omni.ui/Image/generateMips" having its default value set.
        # if page isn't visible, ignore
        if not self.show_page():
            return

        async def on_ok_clicked(dialog):
            dialog.hide()
            self._fail_dialog = None

        if event_type == carb.settings.ChangeEventType.CHANGED:
            # /exts/omni.kit.renderer.core/imgui/enableMips isn't enabled
            if not carb.settings.get_settings().get(ENABLE_MIPS_PATH):
                if carb.settings.get_settings().get(GENERATE_MIPS_PATH) and self._fail_dialog == None:
                    carb.settings.get_settings().set_bool(GENERATE_MIPS_PATH, False)
                    from omni.kit.window.popup_dialog import MessageDialog

                    dialog = MessageDialog(
                        title= f"{ui.get_custom_glyph_code('${glyphs}/exclamation.svg')} Cannot Enable",
                        width=500,
                        message=f"This will have no effect as \"{ENABLE_MIPS_PATH}\" isn't enabled.",
                        ok_handler=lambda dialog: asyncio.ensure_future(on_ok_clicked(dialog)),
                        ok_label="Ok",
                        disable_cancel_button=True
                    )
                    dialog.show()
                    self._fail_dialog = dialog
                return

            self._show_restart_message()
