# CHANGELOG

This document records all notable changes to ``omni.mdl`` extension.
This project adheres to [Semantic Versioning](https://semver.org).

## [56.0.3] - 2025-04-26
### Changed
- OMPE-39146: Remove hard code for "omnverse".

## [56.0.2] - 2025-01-13
- Expose omni.mdl.pymdl as public module

## [56.0.0] - 2024-12-12
- Updated Neuray/MDL SDK to version 2024.1.0 beta, 381500.1577 (MDL ABI version 56)

## [55.0.1] - 2024-07-24
- Updated Neuray/MDL SDK to version 2024.0.1, 377400.2109 (MDL ABI version 55)

## [51.0.1] - 2024-04-04
### Added
- Markdown-based documentation.

## [51.0.0] - 2023-12-08
### Changed
- Extension major version now corresponds to the ABI version of neuray to have semantic versioning.
- Requires Iray/Neuray 2023.1.0
- Applied changes in the bindings for handling enums and defines as well as some functions with ReturnCode parameters.

## [0.1.4] - 2023-10-25
### Added
- Extension tests.
### Changed
- Requires Iray/Neuray 2023.0.6
- Fixed the binding for the ITile::get_pixel() and set_pixel() functions (OM-112741).
- Mapped mi::Size to signed integers in python to allow for comparing against -1.
- Deprecated the tuple return of functions that have an float* out parameter in C++. Now a ReturnCode object is passed in and out as Python parameter.
- Removed unused classes and functions from the bindings.

## [0.1.3] - 2023-10-10
### Changed
- Extend the wrapper around MDL type (Type)
- Give access to vectors and arrays size and element type.
- Give access to matrices size.
- Converts low level IValues to python friendly data types:
- Extend to give access to file path for textures, light profiles and BSDF measurements.

## [0.1.2] - 2023-01-09
### Changed
- Update code in Type__printName method to use the pymdlsdk.IType_texture.Shape enumerations vs int

## [0.1.1] - 2023-01-04
### Changed
- Extension publishing: fix extensions that contain only bindings to be published per platform

## [0.1.0] - 2022-03-28
### Added
- Initial extension. Ported fom non-extension bindings.
