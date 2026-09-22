import asyncio
import os
import carb.settings
import omni.kit.app
from carb.eventdispatcher import get_eventdispatcher
import omni.ui as ui
from ..preferences_window import PreferenceBuilder

class GlobalPreferences(PreferenceBuilder): # pragma: no cover
    def __init__(self):
        super().__init__("")

    def build(self):
        async def on_ok_clicked(dialog):
            import sys
            import carb.events
            import omni.kit.app

            dialog.hide()

            def on_event(_):
                from omni.kit.window.preferences import restart_kit

                restart_kit(sys.argv + ["--reset-user"])

            self._shutdown_sub = get_eventdispatcher().observe_event(event_name=omni.kit.app.GLOBAL_EVENT_PRE_SHUTDOWN, on_event=on_event, observer_name="preferences re-start", order=0)
            await omni.kit.app.get_app().next_update_async()
            omni.kit.app.get_app().post_quit()

        def reset_clicked():
            from omni.kit.window.popup_dialog import MessageDialog

            try:
                import omni.usd

                if omni.usd.get_context().has_pending_edit():
                    dialog = MessageDialog(
                        title= f"{ui.get_custom_glyph_code('${glyphs}/exclamation.svg')} Reset to Default Settings",
                        width=400,
                        message=f"This application will restart to remove all custom settings and restore the application to the installed state.\n\nYou will be prompted to save any unsaved changes.",
                        ok_handler=lambda dialog: asyncio.ensure_future(on_ok_clicked(dialog)),
                        ok_label="Continue",
                        cancel_label="Cancel",
                    )
                else:
                    dialog = MessageDialog(
                        title= f"{ui.get_custom_glyph_code('${glyphs}/exclamation.svg')} Reset to Default Settings",
                        width=400,
                        message=f"This application will restart to remove all custom settings and restore the application to the installed state.",
                        ok_handler=lambda dialog: asyncio.ensure_future(on_ok_clicked(dialog)),
                        ok_label="Restart",
                        cancel_label="Cancel",
                    )
            except ImportError:
                dialog = MessageDialog(
                    title= f"{ui.get_custom_glyph_code('${glyphs}/exclamation.svg')} Reset to Default Settings",
                    width=400,
                    message=f"This application will restart to remove all custom settings and restore the application to the installed state.",
                    ok_handler=lambda dialog: asyncio.ensure_future(on_ok_clicked(dialog)),
                    ok_label="Restart",
                    cancel_label="Cancel",
                )
            dialog.show()

        ui.Button("Reset to Default", clicked_fn=reset_clicked, name="global", tooltip="This will reset all settings back to the installed state after the application is restarted")

    def __del__(self): # pragma: no cover
        super().__del__()
