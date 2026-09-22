import typing
import asyncio
import carb

from .exceptions import LauncherUnavailableError, StarfleetTokenExchangeError
from omni.services.transport.client.base import exceptions as _cli_exceptions
from omni.services.client import AsyncClient


async def get_starfleet_tokens() -> typing.Tuple[str, str]:
    settings = carb.settings.get_settings()
    launcher_url = settings.get("exts/omni.services.starfleet_auth/launcher_url")
    client = AsyncClient(launcher_url)

    try:
        data = await asyncio.wait_for(client.auth.get(), timeout=5)
    except _cli_exceptions.BaseServiceError as exc:
        raise LauncherUnavailableError from exc
    except asyncio.TimeoutError as exc:
        raise LauncherUnavailableError("Timed out") from exc

    id_token = data.get("idToken")
    access_token = data.get("accessToken")

    if id_token is None:
        raise StarfleetTokenExchangeError("Could not find id token in response from launcher")

    if access_token is None:
        raise StarfleetTokenExchangeError("Could not find access token in response from launcher")

    return id_token, access_token
