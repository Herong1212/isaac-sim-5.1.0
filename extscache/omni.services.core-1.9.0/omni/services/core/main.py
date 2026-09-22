# Copyright (c) 2020-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

"""Omniverse microservices framework."""
import os

from typing import Any, Callable, Dict, List, Optional, Set

import starlette

from fastapi.routing import APIWebSocketRoute
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.types import ASGIApp

import carb
import omni.ext
import omni.kit
import omni.services.facilities.base as facilities

from . import _app
from . import _encoding
from . import routers

_singleton = None


def register_endpoint(verb: str, url: str, func: Callable[..., Any], **kwargs: Optional[Any]) -> None:
    """
    Register an endpoint with the Services framework.

    Args:
        verb (str): HTTP verb the endpoint should respond to (e.g. "get", "post", "put", etc.).
        url (str): URL of the endpoint.
        func (Callable[..., Any]): Callback to execute upon reaching the endpoint.
        **kwargs: Optional additional parameters to forward to FastAPI.

    Returns:
        None

    """
    _singleton.register_endpoint(verb, url, func, **kwargs)


def register_websocket_endpoint(url: str, func: Callable[..., Any], **kwargs) -> None:
    """
    Register an endpoint with the Services framework accessible via websockets.

    Args:
        url (str): URL of the endpoint.
        func (Callable[..., Any]): Callback to execute upon reaching the endpoint.
        **kwargs: Optional additional parameters to forward to FastAPI.

    Returns:
        None

    """
    _singleton.register_websocket_endpoint(url, func, **kwargs)


def register_asyncapi_app(app, app_name: str, **kwargs):
    """
    Register an AsyncAPI Application with the services framework

    Args:
        app: Instance of the AsyncAPI Application
        app_id (str): Machine friendly name for the application
        **kwargs: Optional additional parameters
    """
    _singleton.register_asyncapi_app(app, app_name, **kwargs)


def register_mount(path: str, app: ASGIApp, **kwargs: Optional[Any]) -> None:
    """
    Register a mount point with the Services framework.

    Args:
        path (str): URL of the endpoint.
        app (ASGIApp): An ASGI-compatible mount point to forward to FastAPI.
        **kwargs: Optional additional parameters to forward to FastAPI.

    Returns:
        None

    """
    _singleton.register_mount(path, app, **kwargs)


def register_facility(facility: facilities.Facility) -> None:
    """
    Register a facility with the Services framework.

    Args:
        facility (facilities.Facility): Facility to register to the Services framework.

    Returns:
        None
    """
    _singleton.facilities.append(facility)


def register_router(router: routers.ServiceAPIRouter, **kwargs: Optional[Any]) -> None:
    """
    Register a router with the Services framework.

    Args:
        router (routers.ServiceAPIRouter): Router to register to the Services framework.
        **kwargs: Optional additional parameters to forward to FastAPI.

    Returns:
        None

    """
    _singleton.register_router(router, **kwargs)


def register_middleware(cls: type, **kwargs: Optional[Any]) -> None:
    """
    Register a middleware with Services framework.

    Args:
        cls (type): Middleware to register to the Services framework.
        **kwargs: Optional additional parameters to forward to FastAPI.

    Returns:
        None

    """
    _singleton.app.add_middleware(cls, **kwargs)


def deregister_endpoint(verb: str, url: str) -> None:
    """
    Deregister an endpoint from the Services framework.

    Args:
        verb (str): HTTP verb of the endpoint to deregister (e.g. "get", "post", "put", etc.).
        url (str): URL of the endpoint to deregister.

    Returns:
        None

    """
    _singleton.deregister_endpoint(verb, url)


def deregister_mount(path: str) -> None:
    """
    Deregister a mount point from the Services framework.

    Args:
        path (str): Path of the mount point to deregister.

    Returns:
        None

    """
    _singleton.deregister_mount(path)


def deregister_router(router: routers.ServiceAPIRouter, prefix: str = None) -> None:
    """
    Deregister a router from the Services framework.

    Args:
        router (routers.ServiceAPIRouter): Router to deregister.
        prefix (str): Prefix of the Router to deregister.

    Returns:
        None

    """
    _singleton.deregister_router(router, prefix=prefix)


def deregister_asyncapi_app(app_name: str):
    """
    Deregister an AsyncAPI Application with the services framework

    Args:
        app_name (str): Name of the application
    """
    _singleton.deregister_asyncapi_app(app_name=app_name)


def register_encoder(name: str, encoder: Any) -> None:
    """
    Register a data encoder.

    The encoder is expected to have both a `compress` and `decompress` function.

    Args:
        name (str): Name of the encoder to register.
        encoder (Any): Encoder to register.

    Returns:
        None

    """
    _encoding.register_encoder(name, encoder)


def set_metadata(title: str, description: str, version: str, tags_metadata: List[Dict[str, str]] = None, root_path: Optional[str] = None) -> None:
    """
    Set service metadata

    Args:
        title (str): Title of the service
        description (str): Description of the service
        version (str): Version of the service

    Kwargs:
        tags_metadata List[Dict[str, str]]: List of definitions for tags in the format: [{"name": "<name of tag>"}, "description": "<tag description>"}, {"name": "<name of tag>"}, "description": "<tag description>"}]
        root_path (Optional[str]): Root path to use in case of a service being behind a proxy (see the `Fast API documentation <https://fastapi.tiangolo.com/advanced/behind-a-proxy>`_ for reference).

    Returns:
        None

    """
    _singleton.set_description(title, description, version)

    if root_path:
        _singleton.set_root_path(root_path)

    if tags_metadata:
        get_app().openapi_tags.extend(tags_metadata)


def get_app():
    return _singleton.app


async def _status():
    """ Returns the current status of the service.
    """
    return "OK"


class ServicesCoreExtension(omni.ext.IExt):
    """
    Core Services extension

    The Core of Kit's microservices framework.

    Services can be registered using the `controlport`.
    When paired with one (or multiple) of the transport extensions the services can be served to be accessed over
    various protocols such as HTTP, HTTPS, etc.

    """

    _title = "Kit services core"
    _description = "Drive Kit with microservices"
    _version = "0.1"

    def __init__(self, *args, **kwargs):
        super(ServicesCoreExtension, self).__init__(*args, **kwargs)

        _settings = carb.settings.get_settings_interface()
        root_path = _settings.get_as_string("/exts/omni.services.core/root_path") or ""

        self._app = _app.OmniverseService(
            title=self._title,
            description=self._description,
            version=self._version,
            openapi_tags=[],
            root_path=root_path
        )
        self._facilities: List[facilities.Facility] = []

        # Register FastAPI middlewares to assist with configuration of the Services framework:
        self._register_middlewares()

        self._async_apps = {}

    def _register_middlewares(self) -> None:
        """
        Register FastAPI middlewares to assist with configuration of the Services framework.

        Args:
            None

        Return:
            None

        """
        settings = carb.settings.get_settings_interface()
        CORRELATION_ID_SETTING_PREFIX = "/exts/omni.services.core/correlation_id"

        use_default_correlation_id_middleware = settings.get_as_bool(f"{CORRELATION_ID_SETTING_PREFIX}/use_default_middleware")
        if use_default_correlation_id_middleware:
            header_name = settings.get_as_string(f"{CORRELATION_ID_SETTING_PREFIX}/header_name")
            update_request_header = settings.get_as_bool(f"{CORRELATION_ID_SETTING_PREFIX}/update_request_header")

            try:
                from asgi_correlation_id import CorrelationIdMiddleware

                self._app.add_middleware(
                    middleware_class=CorrelationIdMiddleware,
                    header_name=header_name,
                    update_request_header=update_request_header,
                )
            except ImportError as exc:
                carb.log_verbose(f"`asgi_correlation_id` middleware not imported: {str(exc)}")

    @property
    def app(self) -> _app.OmniverseService :
        """
        Return a reference to the FastAPI app.

        Returns:
            (OmniverseApp): A reference to the OmniverseService app.

        """
        return self._app

    def set_description(self, title: str, description: str, version: str) -> None:
        """
        Set the description of the microservices framework.

        Args:
            title (str): Title of the microservices framework.
            description (str): Description of the microservices framework.
            version (str): String representing the semantic versioning scheme of the microservices framework.

        Returns:
            None

        """
        self._app.title = title
        self._app.description = description
        self._app.version = version
        self._reset_openapi_schema()

    def set_root_path(self, root_path: str) -> None:
        """
        Set the root path of the service (e.g.: `/api/v1`).

        Args:
            root_path (str): Root path to use in case of a service being behind a proxy (https://fastapi.tiangolo.com/advanced/behind-a-proxy/)

        Returns:
            None

        """
        self._app.root_path = root_path
        self._reset_openapi_schema()

    @property
    def facilities(self) -> List[facilities.Facility]:
        """
        Return the list of Facilities currently registered with the microservices framework.

        Returns:
            List[facilities.Facility]: The list of Facilities currently registered.

        """
        return self._facilities

    def on_startup(self) -> None:
        global _singleton
        _singleton = self

        show_status_endpoint = carb.settings.get_settings_interface().get_as_bool("exts/omni.services.core/show_status_endpoint")
        self.register_endpoint("get", "/status", _status, include_in_schema=show_status_endpoint, summary="Returns the current status of the service")
        self.register_endpoint("get", "/health", _status, include_in_schema=show_status_endpoint, summary="Health probe")
        self.register_endpoint("get", "/ready", _status, include_in_schema=show_status_endpoint, summary="Readiness probe")
        self.register_endpoint("get", "/startup", _status, include_in_schema=show_status_endpoint, summary="Startup probe")

        manager = omni.kit.app.get_app().get_extension_manager()
        self._data_path = os.path.join(manager.get_extension_path_by_module(__name__), "data")

        # Used by some of the connectors but should eventually be removed.
        self.register_endpoint("get", "/controlport/status", _status, include_in_schema=False)

        self.register_endpoint("get", "/asyncapi/docs", self._async_app_docs_endpoint)
        self.register_endpoint("get", "/asyncapi/schema", self._async_app_schema_endpoint)

    async def _async_app_schema_endpoint(self, app_name: str):
        if app_name not in self._async_apps:
            return JSONResponse(status_code=404, content={"message": "Not Found"},)

        return self._async_apps[app_name].spec()

    async def _async_app_docs_endpoint(self, app_name: str):
        if app_name not in self._async_apps:
            # TODO: return a nice HTMLResponse instead.
            return JSONResponse(status_code=404, content={"message": "Not Found"})

        template_path = os.path.join(self._data_path, "templates", "asyncapi_browser.html")
        with open(template_path, "r") as file:
            html_content = file.read()

        # Replace the placeholder with the schema_url
        html_content = html_content.replace('{{ schema_url }}', f"/asyncapi/schema?app_name={app_name}")

        return HTMLResponse(content=html_content)

    def register_endpoint(self, verb: str, url: str, func: Callable[..., Any], **kwargs: Optional[Any]) -> None:
        """
        Register an endpoint with the Services framework.

        Args:
            verb (str): HTTP verb the endpoint should respond to (e.g. "get", "post", "put", etc.).
            url (str): URL of the endpoint.
            func (Callable[..., Any]): Callback to execute upon reaching the endpoint.
            **kwargs: Optional additional parameters to forward to FastAPI.

        Returns:
            None

        """
        verb_func = getattr(self._app, verb)
        verb_func(url, **kwargs)(func)
        self._reset_openapi_schema()

    def register_websocket_endpoint(self, url: str, func: Callable[..., Any], **kwargs: Optional[Any]) -> None:
        """
        Register an endpoint with the Services framework accessible via websockets.

        Args:
            url (str): URL of the endpoint.
            func (Callable[..., Any]): Callback to execute upon reaching the endpoint.
            **kwargs: Optional additional parameters to forward to FastAPI.

        Returns:
            None

        """
        self._app.add_api_websocket_route(url, func, **kwargs)
        self._reset_openapi_schema()

    def register_mount(self, path: str, app: ASGIApp, **kwargs: Optional[Any]) -> None:
        """
        Register a mount point with the Services framework.

        Args:
            path (str): URL of the endpoint.
            app (ASGIApp): An ASGI-compatible mount point to forward to FastAPI.
            **kwargs: Optional additional parameters to forward to FastAPI.

        Returns:
            None

        """
        self._app.mount(path, app, **kwargs)
        self._reset_openapi_schema()

    def register_router(self, router: routers.ServiceAPIRouter, **kwargs: Optional[Any]) -> None:
        """
        Register a router with the Services framework.

        Args:
            router (routers.ServiceAPIRouter): Router to register to the Services framework.
            **kwargs: Optional additional parameters to forward to FastAPI.

        Returns:
            None

        """
        if "prefix" in kwargs and kwargs["prefix"]:
            prefix = kwargs["prefix"].replace(".", "/")
            if not prefix.startswith("/"):
                prefix = f"/{prefix}"
            kwargs["prefix"] = prefix

            if hasattr(router, "_bypassed_paths"):
                # NOTE: update _bypassed_paths with the prefix,
                # which is otherwise unknown to the AuthorizedServiceAPIRouter, since the router is being registered at the app level
                prefixed_bypassed_paths: Set[str] = set()
                for path in router._bypassed_paths:
                    prefixed_path = f'{kwargs["prefix"].rstrip("/")}{path}'
                    prefixed_bypassed_paths.add(prefixed_path)
                router._bypassed_paths = prefixed_bypassed_paths

        self._app.include_router(router, **kwargs)
        self._reset_openapi_schema()

    def register_asyncapi_app(self, app, app_name: str, **kwargs):
        """
        Register an AsyncAPI Application with the services framework

        Args:
            app: Instance of the AsyncAPI Application
            app_name (str): Machine friendly name for the application
            **kwargs: Optional additional parameters
        """
        self._async_apps[app_name] = app

    def deregister_endpoint(self, verb: str, url: str) -> None:
        """
        Deregister an endpoint from the Services framework.

        Args:
            verb (str): HTTP verb of the endpoint to deregister (e.g. "get", "post", "put", etc.).
            url (str): URL of the endpoint to deregister.

        Returns:
            None

        """
        to_remove = []
        for route in self._app.routes:
            if route.path == url:
                if isinstance(route, starlette.routing.Mount) or verb.upper() in route.methods:
                    to_remove.append(route)

        for route in to_remove:
            self._app.routes.remove(route)

        self._reset_openapi_schema()

    def deregister_mount(self, path: str) -> None:
        """
        Deregister the given service mount point.

        Args:
            path (str): Path of the mount point to deregister.

        Returns:
            None

        """
        mounts_to_remove = []
        for route in self._app.routes:
            if isinstance(route, starlette.routing.Mount) and route.path == path:
                mounts_to_remove.append(route)

        for mount_to_remove in mounts_to_remove:
            self._app.routes.remove(mount_to_remove)

        self._reset_openapi_schema()

    def deregister_router(self, router: routers.ServiceAPIRouter, prefix: str = None) -> None:
        """
        Deregister a router from the Services framework.

        Args:
            router (routers.ServiceAPIRouter): Router to deregister.
            prefix (str): Prefix of the Router to deregister.

        Returns:
            None

        """
        if prefix:
            prefix = prefix.replace(".", "/")
            if not prefix.startswith("/"):
                prefix = f"/{prefix}"

        for route in router.routes:
            if hasattr(route, "methods"):
                methods = sorted(route.methods)
                path = f"{prefix}{route.path}" if prefix else route.path
                for method in methods:
                    self.deregister_endpoint(method, path)
            elif issubclass(route.__class__, APIWebSocketRoute) and route in self._app.routes:
                # WebSocket routes do not feature `methods` properties, as opposed to HTTP-based routers:
                self._app.routes.remove(route)

        self._reset_openapi_schema()

    def deregister_asyncapi_app(self, app_name: str) -> None:
        """
        Deregister an AsyncAPI application

        Args:
            app_name (str): Name of the AsyncAPI application that was previously registered.
        """
        if app_name not in self._async_apps:
            carb.log_warn(f"{app_name} is not a registered AsyncAPI application")
            return

        self._async_apps.pop(app_name)

    def _reset_openapi_schema(self) -> None:
        """Reset the OpenAPI schema of the microservices framework."""
        self._app.openapi_schema = None

    def on_shutdown(self) -> None: # pragma: no cover
        global _singleton
        _singleton = None

        for facility in self._facilities:
            facility.stop()

        if self._app:
            self.deregister_endpoint("get", "/status")
            self.deregister_endpoint("get", "/health")
            self.deregister_endpoint("get", "/ready")
            self.deregister_endpoint("get", "/startup")
            self.deregister_endpoint("get", "/controlport/status")
            self.deregister_endpoint("get", "/asyncapi/docs")
            self.deregister_endpoint("get", "/asyncapi/schema")
