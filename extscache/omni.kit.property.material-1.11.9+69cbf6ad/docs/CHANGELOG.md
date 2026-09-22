# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.11.9] - 2025-05-01
### Changed
- OMPE-45212: ensure extension test data is local to this extension.

## [1.11.8] - 2025-04-07
### Changed
- Updated to use omni.usd via eventdispatcher (Events 2.0) instead of EventStream (Events 1.0)

## [1.11.7] - 2025-03-26
### Changed
- OMPE-41459: ensure MaterialX hard and soft range metadata is typed correctly.

## [1.11.6] - 2025-02-28
### Changed
- OMPE-38466: refactor delayed rebuild widget logic that is called as a result of the UsdMdl.Notice.[ModuleLoaded|ModuleReloaded] callbacks being triggered.

## [1.11.5] - 2025-02-21
### Changed
- OMPE-29401: Add support for /app/properties/material/mdlForceRawForUsage setting.
- OMPE-35155: Add support for decoupled texture colorspace parameters.

## [1.11.4] - 2025-01-13
### Changed
- OMPE-27796, OMPE-27800: Updated public API.

## [1.11.3] - 2025-01-22
### Changed
- OMPE-33662: Add support for Material parameter sdr metadata hints

## [1.11.2] - 2024-12-20
### Changed
- OMPE-31903: Use omni.usd.make_valid_identifier instead of Tf.MakeValidIdentifier to support unicode characters.

## [1.11.1] - 2024-12-16
### Added
- OMPE-28754 - update utils.get_sdr_shader_property_default_value to add support for case where an enumerated value is mapped to a Token or String value.

## [1.11.0] - 2024-10-01
### Changed
- Update verion for OpenUsd-24.0.5

## [1.10.17] - 2024-10-28
### Added
- OMPE-26146: MDL reloading causing widget to hang.

## [1.10.16] - 2024-10-10
### Added
- OMPE-24805: special handling of UsdShade.Material outputs in ShaderInfoAPI.
- Add getter convenience functions to UsdShadePropertyPlaceholder.

## [1.10.15] - 2024-10-01
### Added
- replace UsdMdl with omni.UsdMdl

## [1.10.14] - 2024-09-24
### Fixed
- OMPE-22434 - Remove invalid attributes and connections upon subidentifier change + relevant tests.

## [1.10.13] - 2024-09-18
### Fixed
- OMPE-21559 - Update colorspace gamma comparison to use math.is_close w/ relative tolerance to account for floating-point imprecision.

## [1.10.12] - 2024-09-05
### Fixed
- OMPE-20845 - Fix iteration bug in MdlMatrixAttributeModel.update_value().
- Remove irrevelant info:* properties on info:implementationSource change.
- Ensure pending_rebuild_task is None in reload callback.

## [1.10.11] - 2024-09-04
### Fixed
- OMPE-19544: Add support for incompatible subidentifiers.

## [1.10.10] - 2024-09-01
### Added
- OMPE-20378: correctly remove attributes and/or connections when UsdShade prims definition has changed.
- Extend ShaderInfoAPI to handle UsdShade.NodeGraph prims.

## [1.10.9] - 2024-08-12
### Added
- OMPE-16191: replace usd.mdl with UsdMdl.

## [1.10.8] - 2024-06-28
### Changed
- Updated documentation with AI agent.

## [1.10.7] - 2024-06-27
### Added
- OMPE-13639: materialx uimin/max range annotations ignored.

## [1.10.6] - 2024-06-27
### Added
- OMPE-13564: material inputs not displayed if their name conflicts with a shader parameter of the same name.

## [1.10.5] - 2024-06-25
### Added
- OMPE-12904: disable removal of material attributes whose values have been reverted to their default state.

## [1.10.4] - 2024-06-15
### Added
- OMPE-12271: fix bad attribute reference in usd_attribute_widget

## [1.10.3] - 2024-06-13
### Added
- Assertion that resolved extension path is not None

## [1.10.2] - 2024-06-07
### Fixed
- OMPE-11130: Add compatibility layer/stub modules for scripts.material_utils and usd_binding_widget to maintain backwards compatibility.

## [1.10.1] - 2024-06-06
### Fixed
- OMPE-10813: Remove material properties if they have been set to their default values.
- Fix path to renderContexts persistant setting.

## [1.10.0] - 2024-05-29
### Fixed
- OM-118687: Complete rewrite of the UsdShade widgets due to the removal of the UsdMaterialWatcher from Kit.

## [1.9.4] - 2024-05-29
### Changes
- OMPE-5051: Profile and Improve test times of omni.kit.property.material in Kit 107

## [1.9.3] - 2021-05-17
### Fixed
- Fixed linting issues

## [1.9.2] - 2024-04-16
### Changes
- OM-123596: Fix handling of empty shaders.

## [1.9.1] - 2024-04-15
### Changes
- OM-123482: Fixed changing material binding on inherited material

## [1.9.0] - 2024-03-01
### Changes
- OM-121330: Updated to use omni.kit.widget.context_menu

## [1.8.39] - 2024-01-30
### Changes
- OM-119226: Add settings and disable fabric adapter

## [1.8.38] - 2023-12-18
### Changes
- Update for fabric adapter

## [1.9.0] - 2024-01-24
### Changes
- OM-118420: Fixed material connections so they show in property window correctly

## [1.8.37] - 2023-12-04
### Changes
- OM-92919: Refactor code to enable derivation

## [1.8.36] - 2023-10-20
### Changes
- OM-112502: Fix UsdShade.Nodegraph parameters not displaying.

## [1.8.35] - 2023-10-12
### Changes
- OM-104254: Synchronize material loading and compilation in extension tests.

## [1.8.34] - 2023-08-29
### Changes
- Material subid's' don't show really long "::Z73file_*" paths

## [1.8.32] - 2023-08-16
### Changes
- Material "X" hidden on None texture
- Missing bound textures are shown in red

## [1.8.31] - 2023-08-08
### Changes
- Fixed material group names

## [1.8.30] - 2023-07-19
### Changes
- Changed `inputs:excludeFromWhiteMode` on shader prim into a PlaceholderAttribute.

## [1.8.29] - 2023-07-19
### Changes
- Fix material properties without shader

## [1.8.28] - 2023-07-04
### Changes
- Material properties can show values before groups

## [1.8.27] - 2023-05-22
### Changes
- OM-95750: MaterailX shaders not displayed in info:id dropdown

## [1.8.26] - 2023-04-04
### Changes
- Add paused property to material prims

## [1.8.25] - 2023-04-02
### Changes
- Only use enumeration widget for integer parameters that have enumeration metadata.

## [1.8.24] - 2023-03-27
### Changes
- Move enumeration code into separate file + cleanup
- Cleanup build_property_item method
- Remap int to bool if widgetType metadata is set.

## [1.8.23] - 2023-03-15
### Changes
- Update UsdShade.Shader schema attributes

## [1.8.22] - 2023-03-09
### Changes
- Fix sub-identifier drop down list population.

## [1.8.21] - 2023-02-24
### Changes
- Hide/show info: properties based on value of info:id
- Remove all hardcoded UsdPreviewSurface parameter hints
- Remove adding of sourceColorSpace parameter for UsdUVTexture
- General cleanup and commenting

## [1.8.21] - 2023-02-26
### Changes
- Replaced asyncio.ensure_future calls in usd_binding_widget.py with omni.kit.async_engine.run_coroutine function.

## [1.8.21] - 2023-02-16
### Changes
- Support material display_name enums

## [1.8.20] - 2023-02-05
### Changes
- Support property filter

## [1.8.18] - 2023-01-11
### Changes
- Material property widget parameters - don't override displayName and/or displayGroup if already set.

## [1.8.17] - 2023-01-10
### Changes
- Fix ui refresh issue when modifying material prim.

## [1.8.17] - 2022-12-20
### Changes
- Add arrange_windows to fix some tests when run in random order.

## [1.8.16] - 2022-11-25
### Changes
- Use notification instead of popup to avoid hang.

## [1.8.15] - 2022-11-16
### Changes
- Fixed widget rebuilding w/ any property change.

## [1.8.15] - 2022-11-09
### Changes
- added add_context_menu to UsdBindingAttributeWidget to prevent multiple menu additions

## [1.8.14] - 2022-11-04
### Changes
- Clean up material property UI by removing info:, inputs: and outputs: prefixes from properties that don't have explicit display name metadata

## [1.8.13] - 2022-08-17
### Changes
- Updated "material:binding" widget refreshing

## [1.8.12] - 2022-08-17
### Changes
- Fixed clicking on thumbnail to goto material. Now works with inherited materials & multiple selections

## [1.8.11] - 2022-08-09
### Changes
- Updated golden images for TreeView.

## [1.8.10] - 2022-07-25
### Changes
- Refactored unittests to make use of content_browser test helpers

## [1.8.9] - 2022-05-30
### Changes
- Update material thumbnail image to prevent multiple images being overlayed

## [1.8.8] - 2022-05-24
### Changes
- Material thumbnail context menu update
- Copy and Paste material groups

## [1.8.7] - 2022-05-23
### Changes
- Support legacy and new Viewport API
- Add dependency on omni.kit.viewport.utility

## [1.8.6] - 2022-05-11
### Changes
- Support material browser drag/drop

## [1.8.5] - 2022-05-17
### Changes
- Support multi-file drag & drop

## [1.8.4] - 2022-05-12
### Changes
- Show shader description on material

## [1.8.3] - 2022-05-03
### Changes
- Fixed unittest stemming from content browser changes

## [1.8.2] - 2022-01-11
### Changes
- Improved info:mdl:sourceAsset:subidentifier match with combobox list from material library

## [1.8.1] - 2021-12-02
### Changes
- Exception fixes and shader preload stall fix

## [1.8.0] - 2021-11-29
### Changes
- Added material annotations "description" property

## [1.7.5] - 2021-11-12
### Changes
- Updated to new omni.kit.material.library with new neuraylib

## [1.7.4] - 2021-11-02
### Changes
- Fixed refresh on binding

## [1.7.3] - 2021-10-27
### Changes
- Prevent crash in event callback

## [1.7.2] - 2021-09-10
### Changes
- Dragging a multi-material .mdl file onto preview icon shows material dialog
- Added widget identifiers

## [1.7.1] - 2021-08-11
### Changes
- Fixed Sdf.Path warning due to string <-> Sdf.Path compare

## [1.7.0] - 2021-06-30
### Changes
- Updated material list handling to use async Treeview and prevent stalls on large scenes
- Moved `MaterialUtils`, `MaterialListBoxWidget`, `SearchWidget`, `ThumbnailLoader`, `MaterialListModel` & `MaterialListDelegate` into omni.kit.material.library

## [1.6.5] - 2021-05-31
### Changes
- Changed "Material & Shader" to "Material and Shader"

## [1.6.4] - 2021-05-20
### Changes
- Material search resets scroll position when typing to prevent user not seeing results

## [1.6.3] - 2021-05-11
### Changes
- Updated material info so Outputs, UI Properties and Material Flags are closed by default

## [1.6.2] - 2021-04-15
### Changes
- Changed how material input is populated.

## [1.6.1] - 2021-03-17
### Changes
- Add material thumnail context menu

## [1.6.0] - 2021-03-16
### Changes
- Add support for UsdShade.NodeGraph prims
- Add support for UsdUI.Backdrop prims

## [1.5.0] - 2021-03-09
### Changes
- Updated material search dialog
- Added current materials to quicksearch

## [1.4.3] - 2021-02-25
### Changes
- Fixed issue with materials with Relationship

## [1.4.2] - 2021-02-10
### Changes
- Updated StyleUI handling

## [1.4.1] - 2021-02-03
### Changes
- Fixed text issue with long lists in material name search dialog

## [1.4.0] - 2021-01-28
### Changes
- Added material name search dialog

## [1.3.8] - 2020-12-16
### Changes
- Fixed material shader preloading

## [1.3.7] - 2020-12-10
### Changes
-  fixed button leak

## [1.3.6] - 2020-12-09
### Changes
- Added extension icon
- Added readme
- Updated preview image

## [1.3.5] - 2020-12-01
### Updated
- When property in both material and shader don't show shader properties in material

## [1.3.5] - 2020-11-20
### Updated
- Added Sub-Identifier support

## [1.3.4] - 2020-11-19
### Updated
- Fixed issue with newly created materials not refreshing when loaded

## [1.3.3] - 2020-11-18
### Added
- Updates thumbnail loading to use async and quiet error messages

## [1.3.2] - 2020-11-13
### Added
- Improved material group/name & added PreviewSurface values

## [1.3.1] - 2020-11-12
### Added
- Fixed issue where bound material didn't show sometimes
- Added refresh on bound material when material created/modified to update material list

## [1.3.0] - 2020-11-06
### Added
- Materials now show Materials & Shader values

## [1.2.1] - 2020-10-21
### Added
- Moved schema into bundle

## [1.2.0] - 2020-10-16
### Added
- Added thumbnail preview
- Added click to goto material on thumbnail

## [1.1.0] - 2020-10-02
### Added
- Added material binding UI

## [1.0.0] - 2020-09-17
### Added
- Created
