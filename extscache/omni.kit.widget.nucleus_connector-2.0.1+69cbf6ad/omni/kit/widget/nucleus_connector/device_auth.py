# Copyright (c) 2018-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides functionality for device authentication flow with Nucleus servers, including QR code display, user cancellation handling, and maintaining connection status."""


import asyncio
import omni.client
import carb

from typing import Callable
from functools import partial
from .ui import DeviceAuthFlowDialog, ConnectorDialog, AlertPane


class DeviceAuthConnector:
    """DeviceAuthConnector facilitates the connection to Nucleus servers using the device authentication flow.

    It manages the authentication process by displaying QR codes, handling user cancellations, and maintaining the connection status.
    """

    def __init__(self):
        self._conn_status_sub = omni.client.register_connection_status_callback(self._connection_status_changed)
        self._pending_results = {}  # url: (auth_handle, dialog instance)

    def start_auth_flow(self, auth_handle: int, params: omni.client.AuthDeviceFlowParams):
        """
        Called at the start of the authentication cycle. Shows the user a qrcode of auth url and code that needs to be
        entered in the auth page. User can cancel the process by clicking the cancel button.

        Args:
            auth_handle (int): An integer handle that should be passed to cancel authentication

        """
        dialog = DeviceAuthFlowDialog(params)
        self._pending_results[params.server] = (auth_handle, dialog)
        dialog.set_cancel_clicked_fn(partial(self.cancel_auth, auth_handle, params.server))

    def end_auth_flow(self, auth_handle: int):
        """Called at the end of the authentication cycle; hides the app dialog"""
        # find server from auth handle
        server = None
        for server_name, (handle, _) in self._pending_results.items():
            if handle == auth_handle:
                server = server_name
                break
        if not server:
            return

        _, dialog = self._pending_results.pop(server)
        if dialog:
            dialog.hide()
            dialog = None

    def cancel_auth(self, auth_handle: int, server: str, dialog: DeviceAuthFlowDialog):
        """
        This callback is attached to the dialog's cancel button. It cancels the authentication process.

        Args:
            auth_handle (int): An integer handle that should be passed to cancel authentication
            server (str): The server url that the auth handle is binding to

        """
        if dialog:
            dialog.hide()
            dialog = None
            if server in self._pending_results:
                self._pending_results.pop(server)
        # Cancel the auth flow
        omni.client.authentication_cancel(auth_handle)

    def _connection_status_changed(self, server: str, status: omni.client.ConnectionStatus) -> None:
        """Collect signed in server's service information based upon server status changed."""
        # need to strip off the omniverse:// here from the server
        if server.startswith("omniverse://"):
            server = server[12:]
        if server not in self._pending_results:
            return
        if status == omni.client.ConnectionStatus.CONNECTED:
            _, dialog = self._pending_results.pop(server)
            if dialog:
                dialog.hide()
                dialog = None

    def connect_with_callback(
        self, name: str = None, url: str = None, on_success_fn: Callable = None, on_failed_fn: Callable = None
    ):
        """
        Unless specified, prompts for server name and Url and proceeds to connect to it.

        Args:
            name (str): Name of server
            url (str): Url of server
            on_success_fn (Callable): Invoked when successful, on_success_fn(name: str, url: str)
            on_faild_fn (Callable): Invoked when failed, on_faild_fn(name: str, url: str)

        """

        def on_connect_server(
            on_success_fn: Callable,
            on_failed_fn: Callable,
            dialog: ConnectorDialog,
            name: str = None,
            url: str = None,
            show_waiting: bool = True,
        ):
            if show_waiting:
                dialog.show_waiting()
            if not name:
                name = dialog.get_value("name")
            if not url:
                url = dialog.get_value("url")
            # Give dialog ownership of the task so that it can cancel at will.
            asyncio.ensure_future(
                dialog.run_cancellable_task(
                    self.connect_server_async(name, url, on_success_fn, on_failed_fn, dialog=dialog)
                )
            )

        def on_cancel(dialog):
            dialog.cancel_task()
            dialog.hide()

        # OM-76995: Create the dialog on demand, so in detached window the dialog window shows up correctly
        self._dialog = ConnectorDialog()

        if url:
            # If server is explicitly specified, then proceed to connect rather than wait for user input.
            on_connect_server(on_success_fn, on_failed_fn, self._dialog, name=name, url=url)
            return

        self._dialog.show(name=name, url=url)
        self._dialog.set_okay_clicked_fn(partial(on_connect_server, on_success_fn, on_failed_fn))
        self._dialog.set_cancel_clicked_fn(on_cancel)

    async def connect_server_async(
        self,
        name: str,
        url: str,
        on_success_fn: Callable = None,
        on_failed_fn: Callable = None,
        retry: bool = False,
        dialog: ConnectorDialog = None,
    ):
        """
        Connects to the named server.

        Args:
            name (str): Name of server
            url (str): Url of server
            on_success_fn (Callable): Invoked when successful, on_success_fn(name: str, url: str)
            on_faild_fn (Callable): Invoked when failed, on_faild_fn(name: str, url: str)
            retry (bool): True if re-trying for second time.
            dialog (ConnectorDialog): A dialog instance to re-use from parent operation.

        """
        if not url:
            carb.log_warn(f"Error connecting server, missing Url.")
            return
        elif not url.startswith("omniverse://"):
            url = f"omniverse://{url}"

        if not name:
            # If no name specified, then use name of child directory
            name = list(filter(None, url.split("/")))[-1]

        result, stats = None, None
        try:
            # This stat triggers the start of the authentication flow
            result, stats = await omni.client.stat_async(url)
        except asyncio.CancelledError:
            # If this task is cancelled, then sign out completely in order to clear the auth process
            omni.client.sign_out(url)
            carb.log_warn(f"Cancelled attempted connection to '{url}'.")
            return

        if result == omni.client.Result.OK:
            if dialog:
                dialog.hide()
            if on_success_fn:
                on_success_fn(name, url)
        elif result == omni.client.Result.ERROR_CONNECTION and not retry:
            # Note: Strangely, omni.client returns error if the user has previously connected or disconnected from
            # this server. In this case, only a reconnect will succeed.
            omni.client.reconnect(url)
            await self.connect_server_async(
                name, url, on_success_fn=on_success_fn, on_failed_fn=on_failed_fn, retry=True, dialog=dialog
            )
        else:
            msg = f"Unable to connect server '{url}'. Please check your internet connection then try again."
            if not dialog:
                dialog = ConnectorDialog()
            dialog.show_alert(msg, AlertPane.Warn)
            if on_failed_fn:
                on_failed_fn(name, url)

    async def reconnect_server_async(self, url: str, on_success_fn: Callable = None, on_failed_fn: Callable = None):
        """
        Re-connects to the named server.

        Args:
            url (str): Url of server
            on_success_fn (Callable): Invoked when successful, on_success_fn(name: str, url: str)
            on_faild_fn (Callable): Invoked when failed, on_faild_fn(name: str, url: str)

        """
        if not url:
            carb.log_warn(f"Error reconnecting server, missing Url.")
            return
        name = list(filter(None, url.split("/")))[-1]

        # Do the reconnect
        omni.client.reconnect(url)

        result, stats = None, None
        try:
            result, stats = await omni.client.stat_async(url)
        except asyncio.CancelledError:
            # If this task is cancelled, then sign out completely in order to clear the auth process
            omni.client.sign_out(url)
            carb.log_warn(f"Cancelled attempted connection to '{url}'.")
            return

        if result == omni.client.Result.OK:
            if on_success_fn:
                on_success_fn(name, url)
        else:
            if on_failed_fn:
                on_failed_fn(name, url)

    def destroy(self):
        """Destructor."""
        if self._pending_results:
            self._pending_results.clear()
        self._conn_status_sub = None

        # Cleanup temp img files created for qrcode
        import os

        if os.path.exists(DeviceAuthFlowDialog.TEMP_DIR):
            try:
                import shutil

                shutil.rmtree(DeviceAuthFlowDialog.TEMP_DIR)
            except OSError as e:
                carb.log_warn(
                    f"Failed to clean up temp directory {DeviceAuthFlowDialog.TEMP_DIR}, error encountered: {str(e)}"
                )
