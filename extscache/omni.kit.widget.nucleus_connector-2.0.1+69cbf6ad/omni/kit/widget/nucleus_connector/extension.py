# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides an extension for connecting to Nucleus servers, supporting authentication flows and connection management."""


import carb.settings
import omni.ext
import omni.kit.app
import omni.client
import asyncio

from typing import Callable
from functools import partial
from .connector import NucleusConnector
from .device_auth import DeviceAuthConnector
from . import NUCLEUS_CONNECTION_SUCCEEDED_GLOBAL_EVENT

g_singleton = None


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class NucleusConnectorExtension(omni.ext.IExt):
    """Helper extension for connecting to Nucleus servers.

    This extension serves as a utility for managing connections to Nucleus servers, handling both authentication flows and connection management tasks. It provides a convenient interface for initiating and terminating server connections, as well as managing authentication processes through both standard and device auth flows.
    """

    def __init__(self):
        """Initializes the NucleusConnectorExtension class."""
        super().__init__()
        self._connector = None

    def on_startup(self, ext_id):
        """Build connector and register/set auth callback on extension startup.

        Args:
            ext_id (str): The extension identifier.
        """
        # Save away this instance as singleton
        global g_singleton
        g_singleton = self

        # OM-98449: Register device auth flow callback if device auth flow is turned on in settings
        self._device_auth_sub = None
        settings = carb.settings.get_settings()
        device_auth = settings.get_as_bool("exts/omni.kit.widget.nucleus_connector/device_auth_flow")
        if device_auth:
            try:
                import qrcode
            except ModuleNotFoundError:
                carb.log_warn("Package qrcode not installed. Not using device_auth_flow.")
                device_auth = False
        if device_auth:  # pragma: no cover
            self._connector = DeviceAuthConnector()
            self._device_auth_sub = omni.client.register_device_flow_auth_callback(self._on_device_auth)
        else:
            self._connector = NucleusConnector()
            # Set the callback to invoke when authentication requires opening a web browser to complete sign-in.
            omni.client.set_authentication_message_box_callback(self._on_authenticate)

    def _on_device_auth(self, auth_handle: int, params: omni.client.AuthDeviceFlowParams):
        """
        This callback is invoked when authentication for device auth flow, instead of auth in the web browser.

        Args:
            auth_handle (int): The auth handle that could be used for canceling.
            params (omni.client.AuthDeviceFlowParams): An object containing info to display to user to complete the auth.
                if it is None, it means the auth attempt is finished.
        """
        if self._connector:
            if not params:
                # Auth is done, either succeeded or failed, result needed to be determined from status callback;
                # Here we just close out the dialog.
                self._connector.end_auth_flow(auth_handle)
                return

            self._connector.start_auth_flow(auth_handle, params)

    def _on_authenticate(self, show_alert: bool, host_name: str, auth_handle: int):
        """
        This callback is invoked when the application should show a dialog box letting the user know that a
        browser window has opened and to complete signing in using the web browser.

        Args:
            show_alert (bool): True means to start the authentication cycle and False means to end it
            host_name (str): The server host name that the authentication is for
            auth_handle (int): An integer handle that should be passed to cancel authentication

        """
        if self._connector:
            if show_alert:
                self._connector.start_auth_flow(host_name, auth_handle)
            else:
                self._connector.end_auth_flow(auth_handle)

    def _on_connect_succeeded(self, callback: Callable, name: str, url: str):
        """Called when connection is made successfully; invokes the given callback"""
        # Emit event on successful connection
        omni.kit.app.queue_event(NUCLEUS_CONNECTION_SUCCEEDED_GLOBAL_EVENT, {"url": url})
        if callback:
            callback(name, url)

    def _on_connect_failed(self, callback: Callable, name: str, url: str):
        """Called when connection fails; invokes the given callback"""
        if callback:
            callback(name, url)

    @omni.kit.app.deprecated(
        "omni.kit.widget.nucleus_connector.NucleusConnectorExtension.connect_with_dialog() is deprecated. Please use omni.kit.widget.nucleus_connector.connect_with_dialog() instead."
    )
    def connect_with_dialog(self, on_success_fn: Callable = None, on_failed_fn: Callable = None):
        """
        Prompts for server name and Url and proceeds to connect to it.

        Args:
            on_success_fn (Callable): Invoked when successful, on_success_fn(name: str, url: str)
            on_faild_fn (Callable): Invoked when failed, on_faild_fn(name: str, url: str)

        """
        if self._connector:
            self._connector.connect_with_callback(
                on_success_fn=partial(self._on_connect_succeeded, on_success_fn),
                on_failed_fn=partial(self._on_connect_failed, on_failed_fn),
            )

    @omni.kit.app.deprecated(
        "omni.kit.widget.nucleus_connector.NucleusConnectorExtension.connect() is deprecated. Please use omni.kit.widget.nucleus_connector.connect() instead."
    )
    def connect(self, name: str, url: str, on_success_fn: Callable = None, on_failed_fn: Callable = None):
        """
        Connects to the named server.

        Args:
            name (str): Name of server
            url (str): Url of server
            on_success_fn (Callable): Invoked when successful, on_success_fn(name: str, url: str)
            on_faild_fn (Callable): Invoked when failed, on_faild_fn(name: str, url: str)

        """
        if self._connector:
            self._connector.connect_with_callback(
                name=name,
                url=url,
                on_success_fn=partial(self._on_connect_succeeded, on_success_fn),
                on_failed_fn=partial(self._on_connect_failed, on_failed_fn),
            )

    @omni.kit.app.deprecated(
        "omni.kit.widget.nucleus_connector.NucleusConnectorExtension.reconnect() is deprecated. Please use omni.kit.widget.nucleus_connector.reconnect() instead."
    )
    def reconnect(self, url: str, on_success_fn: Callable = None, on_failed_fn: Callable = None):
        """
        Reconnects to the named server.

        Args:
            url (str): Url of server
            on_success_fn (Callable): Invoked when successful, on_success_fn(url: str)
            on_faild_fn (Callable): Invoked when failed, on_faild_fn(url: str)

        """
        if self._connector:
            asyncio.ensure_future(
                self._connector.reconnect_server_async(
                    url,
                    partial(self._on_connect_succeeded, on_success_fn),
                    partial(self._on_connect_failed, on_failed_fn),
                )
            )

    @omni.kit.app.deprecated(
        "omni.kit.widget.nucleus_connector.NucleusConnectorExtension.disconnect() is deprecated. Please use omni.kit.widget.nucleus_connector.disconnect() instead."
    )
    def disconnect(self, url: str):
        """
        Disconnects from the server.

        Args:
            url (str): Url of server

        """
        omni.client.sign_out(url)

    def on_shutdown(self):
        """Clears the auth callback and destroy on extension shutdown."""
        # Clears the auth callback
        omni.client.set_authentication_message_box_callback(None)

        # OM-98449: Clears device auth flow connector and callback
        self._device_auth_sub = None

        # Clean up the connector
        if self._connector:
            self._connector.destroy()
            self._connector = None

        global g_singleton
        g_singleton = None


def get_instance():
    """Returns the singleton instance of NucleusConnectorExtension.

    Returns:
        The singleton instance of NucleusConnectorExtension if it exists, otherwise None."""
    return g_singleton


def connect_with_dialog(on_success_fn: Callable = None, on_failed_fn: Callable = None):
    """Prompts for server name and Url and proceeds to connect to it.

    Args:
        on_success_fn (Callable): Invoked when successful, on_success_fn(name: str, url: str)
        on_failed_fn (Callable): Invoked when failed, on_failed_fn(name: str, url: str)
    """
    ext_inst = get_instance()
    if ext_inst._connector:
        ext_inst._connector.connect_with_callback(
            on_success_fn=partial(ext_inst._on_connect_succeeded, on_success_fn),
            on_failed_fn=partial(ext_inst._on_connect_failed, on_failed_fn),
        )


def connect(name: str, url: str, on_success_fn: Callable = None, on_failed_fn: Callable = None):
    """Connects to the named server.

    Args:
        name (str): Name of server
        url (str): Url of server
        on_success_fn (Callable): Invoked when successful, on_success_fn(name: str, url: str)
        on_failed_fn (Callable): Invoked when failed, on_failed_fn(name: str, url: str)
    """
    ext_inst = get_instance()
    if ext_inst._connector:
        ext_inst._connector.connect_with_callback(
            name=name,
            url=url,
            on_success_fn=partial(ext_inst._on_connect_succeeded, on_success_fn),
            on_failed_fn=partial(ext_inst._on_connect_failed, on_failed_fn),
        )


def reconnect(url: str, on_success_fn: Callable = None, on_failed_fn: Callable = None):
    """Reconnects to the named server.

    Args:
        url (str): Url of server
        on_success_fn (Callable): Invoked when successful, on_success_fn(url: str)
        on_failed_fn (Callable): Invoked when failed, on_failed_fn(url: str)
    """
    ext_inst = get_instance()
    if ext_inst._connector:
        asyncio.ensure_future(
            ext_inst._connector.reconnect_server_async(
                url,
                partial(ext_inst._on_connect_succeeded, on_success_fn),
                partial(ext_inst._on_connect_failed, on_failed_fn),
            )
        )


def disconnect(url: str):
    """Disconnects from the server.

    Args:
        url (str): Url of server
    """
    omni.client.sign_out(url)
