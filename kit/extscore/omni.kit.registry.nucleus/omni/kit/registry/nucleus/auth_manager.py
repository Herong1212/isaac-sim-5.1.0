import omni.client

import logging
from typing import Tuple

from .utils.common import _get_setting, mask_password

logger = logging.getLogger(__name__)


class OmniAuthManager:
    """Manager to help with auth per host. We can't have it per registry as they can share the same server and that won't work from nucleus perspective."""

    def __init__(self, host: str, url: str):
        def to_user_pass(auth):
            parts = auth.split(":", maxsplit=1)
            return (parts[0], parts[1]) if len(parts) > 1 else (auth, None)

        read_account, write_account = self._get_accounts_from_settings(host)
        self._read_user, self._read_pass = to_user_pass(read_account)
        self._write_user, self._write_pass = to_user_pass(write_account)

        self._host = host
        self._url = url
        self._switch_auth(self._read_user, self._read_pass)
        self._signed_for_write = False

    def _get_accounts_from_settings(self, host) -> Tuple[str, str]:
        # Search in accounts by host first
        accounts = _get_setting("/exts/omni.kit.registry.nucleus/accounts", [])
        for account in accounts:
            url = account.get("url", "")
            if not url or omni.client.break_url(url).host == host:
                return account.get("read", ""), account.get("write", "")

        # Fall back to global accounts (old way)
        return _get_setting("/exts/omni.kit.registry.nucleus/omniReadAuth", ""), _get_setting(
            "/exts/omni.kit.registry.nucleus/omniWriteAuth", ""
        )

    def shutdown(self):
        self._switch_auth(None)

    def sign_in_for_write_auth(self) -> bool:
        # Already signed in?
        if self._signed_for_write:
            return True

        result, info = omni.client.get_server_info(self._url)
        if result == omni.client.Result.ERROR_NOT_SUPPORTED:
            return True
        if result != omni.client.Result.OK:
            logger.error(f"Failed get server info for '{self._url}'. Result: '{result}'")
            return False

        # Switch to write account if any, otherwise will just switch off read account
        self._switch_auth(self._write_user, self._write_pass)

        # Force relogin if we are on read user or we have write user set
        if info.username == self._read_user or (self._write_user and info.username != self._write_user):
            omni.client.sign_out(self._url)
            omni.client.reconnect(self._url)

        # Only sign in for write once and forever
        self._signed_for_write = True

        return True

    def _switch_auth(self, user=None, password=None):
        logger.info(f"switch auth for host: {self._host}, account: {user}:{mask_password(password)}")
        if not user or not password:
            self._auth_cb = None
            return

        def auth_cb(prefix):
            if omni.client.break_url(prefix).host != self._host:
                return None
            logger.info(
                f"auth callback matches the host, prefix: {prefix}, host: {self._host}, account: {user}:{mask_password(password)}"
            )
            return (user, password)

        self._auth_cb = omni.client.register_authorize_callback(auth_cb)
