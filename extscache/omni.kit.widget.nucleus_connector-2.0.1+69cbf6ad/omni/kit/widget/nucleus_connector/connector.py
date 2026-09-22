# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides classes and functionality for connecting to, authenticating with, and managing connections to Nucleus servers within the Omniverse environment."""


import asyncio
import omni.client
import carb

from typing import Callable
from functools import partial
from .ui import ConnectorDialog, AlertPane


class NucleusConnector:
    """NucleusConnector object helps with connecting to Nucleus servers.

    This class facilitates the establishment, management, and authentication of connections to Nucleus servers. It provides methods to start and end authentication flows, connect to servers with optional callbacks, and handle server reconnections. Additionally, it manages server connection status updates.
    """

    def __init__(self):
        self._dialog = None
        self._stored_retries = None
        self._connection_status = {}
        self._connection_status_sub = omni.client.register_connection_status_callback(self._server_status_changed)
        self._canceled_urls = []

    def _server_status_changed(self, url: str, status: omni.client.ConnectionStatus) -> None:
        self._connection_status[url] = status

    def start_auth_flow(self, host_name, auth_handle: int):
        """
        Called at the start of the authentication cycle. Most importantly, prepares a cancel button
        so that the user can cancel out of the process if it hangs for any reason.

        Args:
            host_name (str): The server host name that the authentication is for
            auth_handle (int): An integer handle that should be passed to cancel authentication

        """
        # OM-76995: for authentication callback, it is okay to re-use dialogs created since it most often comes from
        #  connection operations already
        if not self._dialog:
            self._dialog = ConnectorDialog()
        # Set dialog fields only if they're empty
        name = self._dialog.get_value("name") or host_name
        # TODO: do we want to support other kind of url for nucleus connector   ?
        url = omni.client.make_url(scheme="omniverse", host=self._dialog.get_value("url") or host_name)
        self._dialog.show_authenticate(name=name, url=url)
        self._dialog.set_cancel_clicked_fn(partial(self.cancel_auth, auth_handle))

    def end_auth_flow(self, auth_handle: int):
        """Called at the end of the authentication cycle; hides the app dialog"""
        if self._dialog:
            self._dialog.hide()
            self._dialog = None

    def cancel_auth(self, auth_handle: int, dialog: ConnectorDialog):
        """
        This callback is attached to the dialog's cancel button. It cancels the authentication process.

        Args:
            auth_handle (int): An integer handle that should be passed to cancel authentication

        """
        # Cancel the dialog task
        if self._dialog:
            self._dialog.cancel_task()
            self._dialog.hide()
            self._dialog = None
        # Cancel the auth flow in the browser
        omni.client.authentication_cancel(auth_handle)

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
            if not name:
                name = dialog.get_value("name")
            if not url:
                url = dialog.get_value("url")

            # OMFP-2249: If no name/url is present, we do nothing (when "ok" button is clicked)
            if not url and not name:
                return

            if show_waiting:
                dialog.show_waiting()
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
            self._dialog.show_authenticate(name=name, url=url)
            # If server is explicitly specified, then proceed to connect rather than wait for user input.
            on_connect_server(on_success_fn, on_failed_fn, self._dialog, name=name, url=url)
            return

        self._dialog.show(name=name, url=url)
        self._dialog.set_okay_clicked_fn(partial(on_connect_server, on_success_fn, on_failed_fn))
        self._dialog.set_cancel_clicked_fn(on_cancel)

    def _reset_omni_client_retries(self):
        if self._stored_retries:
            omni.client.set_retries(*self._stored_retries)
            self._stored_retries = None

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
        if not dialog:
            dialog = ConnectorDialog()
        dialog.show_authenticate(name=name, url=url)

        result, stats = None, None
        try:
            if not self._stored_retries:
                # OM-122760: Should reduce the inner retry times for omni client.
                self._stored_retries = omni.client.set_retries(0, 0, 0)
            # This stat triggers the start of the authentication flow
            result, stats = await omni.client.stat_async(url)
        except asyncio.CancelledError:
            # If this task is cancelled, then sign out completely in order to clear the auth process
            omni.client.sign_out(url)
            self._canceled_urls.append(url)
            carb.log_warn(f"Cancelled attempted connection to '{url}'.")
            return
        finally:
            self._reset_omni_client_retries()

        # OM-122760: Only retry on signed out server to reduce connecting time to invalid server
        connect_status = self._connection_status.get(url, None)

        if result == omni.client.Result.OK:
            dialog.hide()
            dialog.destroy()
            if on_success_fn:
                on_success_fn(name, url)
        elif (
            result == omni.client.Result.ERROR_CONNECTION
            and not retry
            and (connect_status == omni.client.ConnectionStatus.SIGNED_OUT or url in self._canceled_urls)
        ):
            # Note: Strangely, omni.client returns error if the user has previously connected or disconnected from
            # this server. In this case, only a reconnect will succeed.
            if url in self._canceled_urls:
                self._canceled_urls.remove(url)
            omni.client.reconnect(url)
            await self.connect_server_async(
                name, url, on_success_fn=on_success_fn, on_failed_fn=on_failed_fn, retry=True, dialog=dialog
            )
        else:
            msg = f"Unable to connect server '{url}'. Please check your internet connection then try again."
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
        # OM-76995: Create the dialog on demand, so in detached window the dialog window shows up correctly
        self._dialog = ConnectorDialog()
        self._dialog.show_authenticate(name=name, url=url)

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
            if self._dialog:
                self._dialog.hide()
                self._dialog = None
            if on_success_fn:
                on_success_fn(name, url)
        else:
            msg = f"Unable to connect server '{url}'. Please check your internet connection then try again."
            if not self._dialog:
                self._dialog = ConnectorDialog()
            self._dialog.show_alert(msg, AlertPane.Warn)
            if on_failed_fn:
                on_failed_fn(name, url)

    def destroy(self):
        """Destructor."""
        if self._dialog:
            self._dialog.destroy()
            self._dialog = None
        self._connection_status_sub = None
