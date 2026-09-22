# CHANGELOG

This document records all notable changes to ``omni.mdl.neuraylib`` extension.
This project adheres to [Semantic Versioning](https://semver.org).

## [0.2.12] - 2025-02-21
### Changed
- Rename various functions to match snake case convention.
  The old names are deprecated now and will be removed with Kit-SDK 108.
- changed `unregister_extension_content` to `deregister_extension_content` to emphasize that the content has to
  registered before and that this is the opposed operation.
- Expose the functions from the utils sub-module. These include tools for temporary DB scopes and resource iteration. 

## [0.2.11] - 2025-01-08
### Changed
- Remove deprecated APIs from omni.mdl.neuraylib

## [0.2.10] - 2024-10-10
### Changed
- Move the MDL search path location used by `RegisterExtensionContent` to the `omni.mdl` extension. No impact on users expected. 

## [0.2.9] - 2024-08-20
### Added
- Functions `RegisterExtensionContent` and `UnregisterExtensionContent` to allow extensions to register MDL content 
  into the root of an MDL search path. These new functions are more flexible but require some careful thought about
  content organization by the extension developer. In case of questions, reach out the MDL team (authors of this extension).
- New tests for the functions above.
### Changed
- Cleanup of the folder structure of the extension.
- Deprecated `RegisterExtensionSearchPath` and `UnregisterExtensionSearchPath`
- Use junctions on windows by default instead of trying symlinks first when registering extension search paths.
- Add more logging to extension search path registration for tracking down potential issues.

## [0.2.8] - 2024-07-29
### Changed
- Fix the recursive listing of module dependencies for e.g. `GetModuleUris` and `GetGraphResourcesUriMasks`

## [0.2.7] - 2024-07-24
### Changed
- Updates for Neuray/MDL SDK 2024.0.1
- Listing of resources reported from a DB scope without resource resolving (default) now include body resources.
- Add a base class for rendering tests related to MDL features.

## [0.2.6] - 2024-05-30
### Fixed
- Possibility of std::string construction from nullptr

## Added
### [0.2.5] - 2024-05-24
- Function `create_mdl_module_async` to load MDL modules in a coroutine. Use this instead of the synchronous version when calling from the UI thread.

## [0.2.4] - 2024-04-04
### Added
- Markdown-based documentation.

## [0.2.3] - 2023-11-13
### Added
- Functions `RegisterExtensionSearchPath` and `UnregisterExtensionSearchPath` to allow extensions to register MDL content in an existing search path.
- Added tests that can serve as example.
- Function `EnsureRunning` to make sure that neuray is running and MDL resolution through USD is possible, which is useful for applications without full MDL support.

## [0.2.2] - 2023-12-01
### Added
- Test cases for improved structure handling in the native libraries.
- No API changes.

## [0.2.1] - 2023-11-09
### Changed
- Function to get the Neuray DB scope name based on the active renderer moved to the native library.
  If there is no active scope, a `default_scope` is created.

## [0.2.0] - 2023-04-19
### Added
- Function to get the Neuray DB scope name based on the active renderer.
- This function is used a default for  `createMdlModule`, `createMdlEntity`, `createReadingTransaction`, and `createEditingTransaction` now as well.
- Add unit tests.

## [0.1.0] - 2022-03-28
### Added
- Initial extension. Ported from non-extension bindings.
