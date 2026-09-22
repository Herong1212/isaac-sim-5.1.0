## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
__all__ = ["VersioningHelper"]
import asyncio
import omni.client


class VersioningHelper:
    server_info_cache = {}

    @staticmethod
    def is_versioning_enabled():
        """Check if versioning is enabled. """
        try:
            import omni.kit.widget.versioning

            enable_versioning = True
        except:
            enable_versioning = False

        return enable_versioning


    @staticmethod
    def extract_server_from_url(url):
        """
         Extract server URL from URL. 
         
         Args:
              url: URL to extract server from
         
         Returns: 
              Server URL.
        """
        client_url = omni.client.break_url(url)
        server_url = omni.client.make_url(scheme=client_url.scheme, host=client_url.host, port=client_url.port)
        return server_url


    @staticmethod
    async def check_server_checkpoint_support_async(server: str):
        """
         Check if server supports checkpointing. 
         
         Args:
              server: Server to check support. Can be empty or " ".
         
         Returns: 
              True if support checkpoint False otherwise.
        """
        if not server:
            return False

        server_info = await VersioningHelper.get_server_info_async(server)
        support_checkpoint = server_info and server_info.checkpoints_enabled
        return support_checkpoint

    @staticmethod
    async def get_server_info_async(server: str):
        """
         Get information about server. 
         
         Args:
              server: The server to get information about.
         
         Returns: 
              A dict containing server information or None.
        """
        if not server:
            return None

        if server in VersioningHelper.server_info_cache:
            return VersioningHelper.server_info_cache[server]

        result, server_info = await omni.client.get_server_info_async(server)
        if result:
            VersioningHelper.server_info_cache[server] = server_info
            return server_info
        else:
            return None

    @staticmethod
    def menu_checkpoint_dialog(ok_fn: callable, cancel_fn: callable):
        """
         Create and show a dialog to ask for checkpoints.
         
         Args:
              ok_fn: The function to call when the user presses OK.
              cancel_fn: The function to call when the user presses cancel.
        """
        import omni.ui as ui
        import carb.input

        window = ui.Window(
            "Checkpoint Name",
            width=200,
            height=0,
            flags = (
                omni.ui.WINDOW_FLAGS_NO_COLLAPSE |
                omni.ui.WINDOW_FLAGS_NO_RESIZE |
                omni.ui.WINDOW_FLAGS_NO_SCROLLBAR |
                omni.ui.WINDOW_FLAGS_NO_RESIZE |
                omni.ui.WINDOW_FLAGS_MODAL
            )
        )
        with window.frame:
            with ui.VStack(
                height=0,
                spacing=5,
                name="top_level_stack",
                style={"VStack::top_level_stack": {"margin": 5}, "Button": {"margin": 0}},
            ):
                async def focus(field):
                    await omni.kit.app.get_app().next_update_async()
                    await omni.kit.app.get_app().next_update_async()
                    field.focus_keyboard()

                with omni.ui.ZStack():
                    new_name_widget = omni.ui.StringField(multiline=True, height=60)
                    new_name_widget_hint_label = omni.ui.StringField(alignment=omni.ui.Alignment.LEFT_TOP, style={"color": 0xFF3F3F3F})
                new_name_widget.model.set_value("")
                new_name_widget_hint_label.model.set_value("Description....")
                new_name_widget_hint_label.enabled=False

                ui.Spacer(width=5, height=5)
                with ui.HStack(spacing=5):
                    def ok_clicked():
                        window.visible = False
                        if ok_fn:
                            ok_fn(new_name_widget.model.get_value_as_string())

                    def cancel_clicked():
                        window.visible = False
                        if cancel_fn:
                            cancel_fn()

                    ui.Button("Ok", clicked_fn=ok_clicked)
                    ui.Button("Cancel", clicked_fn=cancel_clicked)

                    editing_started = False

                    def on_begin(model):
                        nonlocal editing_started
                        editing_started = True

                    def on_end(model):
                        nonlocal editing_started
                        editing_started = False

                    def window_pressed_key(key_index, key_flags, key_down):
                        nonlocal editing_started
                        new_name_widget_hint_label.visible = not bool(new_name_widget.model.get_value_as_string())
                        key_mod = key_flags & ~ui.Widget.FLAG_WANT_CAPTURE_KEYBOARD
                        if (
                            carb.input.KeyboardInput(key_index) in [carb.input.KeyboardInput.ENTER, carb.input.KeyboardInput.NUMPAD_ENTER]
                            and key_mod == 0 and key_down and editing_started
                        ):
                            on_end(None)
                            ok_clicked()

                    new_name_widget.model.add_begin_edit_fn(on_begin)
                    new_name_widget.model.add_end_edit_fn(on_end)
                    window.set_key_pressed_fn(window_pressed_key)
                    asyncio.ensure_future(focus(new_name_widget))
        return window
