# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.9.0] - 2024-01-27
### Update
- Update health and status endpoints to be inline with UCS guidelines.

## [1.8.0] - 2023-11-28
### Added
- Add support for registering AsyncAPI Applications.

## [1.7.0] - 2023-10-23
### Changed
- Make /metrics endpoint visibility configurable

## [1.6.4] - 2023-10-05
### Added
- Added unit tests to increase code coverage of Core features.
- Added code documentation.

## [1.6.3] - 2023-09-01
### Changed
- Temporarily muted imports of `asgi_correlation_id` to work around mixed imports of `starlette` between `kit-services` and `kit` components.

## [1.6.2] - 2023-08-31
### Fixed
- Fixed issue where discrepancies between various various of the `starlette` dependency of FastAPI may cause crashes due to the `self._debug` attribute of `starlette` application (inherited from `starlette`) was renamed to `self.debug`.

## [1.6.1] - 2023-08-25
### Added
- Added ability to convert FastAPI Request Headers to a Python dictionary, suitable for the Service framework's `AsyncClient`.

## [1.6.0] - 2023-08-09
### Added
- Added ability to generate unique Correlation IDs to requests issued against the Services framework.

## [1.5.6] - 2023-08-08
### Fixed
- Fixed bug preventing supplying a different `route_class` than the default `omni.services.core._route.CompressedRoute`.

## [1.5.5] - 2023-07-14
### Changed
- Added filter for de-registering websocket endpoint.

## [1.5.4] - 2023-07-03
### Added
- Added support for de-registering WebSocket routes for Service API endpoints.

## [1.5.3] - 2023-06-26
### Changed
- Include router prefix if specified and update `_bypassed_paths` on the router (used by `AuthorizedServiceAPIRouter`).

## [1.5.2] - 2023-06-04
### Changed
- Added dependency on `omni.kit.async_engine` given the async nature of the library. This is to assure clean shutdowns

## [1.5.1] - 2023-05-27
### Changed
- Hide deprecated /controlport/status endpoint from OpenAPI schema.

## [1.5.0] - 2023-05-19
### Changed
- Custom App class
- Expose option for root_path

## [1.4.5] - 2023-04-27
### Changed
- Update unit tests for `omni.services.core`.

## [1.4.4] - 2023-04-27
### Changed
- Update unit tests for `omni.services.core`.

## [1.4.3] - 2023-04-24
### Changed
- Update unit tests for `omni.services.core`.

## [1.4.2] - 2023-02-28
### Changed
- Update unit tests to use `omni.kit.test.AsyncTestCase` class.

## [1.4.1] - 2023-02-01
### Added
- Add query_params to _get_request_async method of base test class

## [1.4.0] - 2023-01-22
### Added
- Add support for declaring prefixes and tags in the ServiceAPIRouter directly
- Add support for setting metadata directly on the app
- Auto-initialize openapi_tags to avoid needing checks on empty lists
- Add support for dotted prefixes

## [1.3.0] - 2022-11-09
### Remove
- Remove dependency on omni.kit.tests

## [1.2.0] - 2021-12-06
### Added
- Add /status and /controlport/status (for backwards compatibility) to indicate if the services are up.

## [1.1.1] - 2021-05-14
### Added
- Added option to register and deregister mount points for static assets.
- Enhanced documentation.
- Improved test coverage.

## [1.1.0] - 2020-11-27
### Added
- Added option to deregister endpoints and routers.

## [1.0.0] - 2020-09-17
### Added
- Initial commit of `omni.services.core` after porting it over from omni.kit.controlport.
