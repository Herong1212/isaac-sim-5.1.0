# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [4.5.12] - 2025-09-02
### Changed
- OMPE-41028: Fix issue with payload/reference of local file in non-local layer doesn't resolve correctly.

## [4.5.11] - 2025-05-19
### Changed
- Fixed issue with reference prim path validation

## [4.5.8] - 2025-05-01
### Changed
- Prepare for Python-3.12

## [4.5.7] - 2025-04-28
### Changed
- OMPE-41450: Widget support for int properties with options

## [4.5.6] - 2025-04-28
### Changed
- OMPE-39146: Remove hard code for "omnverse".

## [4.5.5] - 2025-04-18
### Changed
- Renamed "Hide from camera" to "Invisible to Primary Ray"

## [4.5.4] - 2025-04-08
### Changed
- OMPE-41028: Fix automatically add Nucleus-prefix to the path to local files in Reference asset path.

## [4.5.3] - 2025-04-07
### Changed
- Updated to use omni.usd via eventdispatcher (Events 2.0) instead of EventStream (Events 1.0)

## [4.5.2] - 2025-03-31
### Changed
- OMPE-41453: Update token widget to display and highlight invalid values.

## [4.5.1] - 2025-02-21
### Changed
- OMPE-37362: Improved class/function documentation and other lint fixes

## [4.5.0] - 2025-02-21
### Added
- OMPE-31959: Add support for renaming prims with unicode NFC normalization.

## [4.4.0] - 2025-02-11
### Changed
- OMPE-33113: schema API update

## [4.3.1] - 2025-01-13
### Changed
- OMPE-27796, OMPE-27800: Updated public API.

## [4.3.0] - 2025-02-12
### Changed
- Default `ext."omni.kit.property.usd".enableAdapter` to false and requires explict opt-in for Fabric/Adapter related workflow. Propery Widget by default now only shows USD attributes.

## [4.2.22] - 2025-01-31
### Changed
- OMPE-35747: Re-added timeout of 600

## [4.2.21] - 2025-01-09
### Changed
- OMPE-27667: Code tweaks for the public API checking tool.

## [4.2.20] - 2024-12-30
### Changed
- OMPE-30922: Fixed time-sampled value

## [4.2.19] - 2024-12-20
### Changed
- OMPE-31903: Use omni.usd.make_valid_identifier instead of Tf.MakeValidIdentifier to support unicode characters, update test with unicode data.

## [4.2.18] - 2024-12-10
### Changed
- OMPE-26015: Removed warning info for optional dependency not fulfilled

## [4.2.17] - 2024-12-05
### Changed
- Fixed SdfPath widgets loosing 1st character typed

## [4.2.16] - 2024-11-27
### Changed
- Fix for colorspace, browse and goto URL widgets becoming un-clickable

## [4.2.15] - 2024-11-06
### Changed
- Fixed issue with renaming prim in UI callback

## [4.2.14] - 2024-10-10
### Changed
- Fixed copy prim path to clipboard

## [4.2.13] - 2024-10-09
### Fixed
- Fixed backward compatibility for custom models that do not have `get_layers_with_strongest_value_opinions` function.

## [4.2.12] - 2024-09-26
### Added
- Added support to locate relative file path for `string` attribute with `filePath` as `uiType`.
### Fixed
- Fixed path validation against incorrect layer.

## [4.2.11] - 2024-09-04
### Changed
- Updated validate_url to use resolvedPath as it was showing red error for core material paths

## [4.2.10] - 2024-08-07
### Fixed
- Fix for accessing value().path for non path types

## [4.2.9] - 2024-08-06
### Fixed
- Payload/Reference locate file icon disappears when not no file or file is missing
- Sdf Asset files show red when missing

## [4.2.8] - 2024-08-06
### Changed
- OMPE-16059: widgets refresh on layer deleted
- Added function `cleanup_payload` to `PrimSelectionPayload`. This removes any invalid prims from payload list.

## [4.2.7] - 2024-07-23
### Changed
- Fixed private class access (accessing functions/variables with _)

## [4.2.6] - 2024-07-30
### Fixed
- OMPE-15133: Fix for failing test due to dragging out of focus item from treeview.

## [4.2.5] - 2024-07-25
### Fixed
- OMPE-16060: Fixed to create_label and create_text_label to handle elided_text correctly.

## [4.2.4] - 2024-07-11
### Fixed
- Fixed tests to not focus on treeview items during drag & drop.

## [4.2.3] - 2024-07-05
### Changed
- Updated documentation with AI agent.

## [4.2.2] - 2024-07-04
### Fixed
- OMPE-12908: Fixed issue with some usd attribute models' `set_value` not triggering `_item_changed` properly, added test

## [4.2.1] - 2024-06-06
### Fixed
- OMPE-10813: Update UsdBase to include optional removal of properties if they are set to their default values.

## [4.2.0] - 2024-05-25
### Fixed
- OM-118687: Several tests re-factored due to the removal of the UsdMaterialWatcher from Kit.

## [4.1.14] - 2025-05-29
### Fixed
- Removed usage of omni.kit.ui

## [4.1.13] - 2024-05-17
### Fixed
- Fixed linting issues

## [4.1.12] - 2024-05-10
### Changes
- OM-123519: usdrt updated, revert the workaround

## [4.1.11] - 2024-05-07
### Changes
- OM-124694: Add support for both square and non-square matrices.

## [4.1.10] - 2024-04-29
### Changed
- OM-124251: Any duplicate items in a combobox will have "** DUPLICATE **" decorators and be unselectable

## [4.1.9] - 2024-04-17
### Fixed
- OM-123519: avoid slowly compare of big array data.

## [4.1.8] - 2024-04-10
### Fixed
- OM-123126: Removed visibleInPrimaryRay default value from `_get_default_value()` as not needed anymore and default can be True/False depending on type.

## [4.1.7] - 2024-04-03
### Fixed
- OM-96664: UnboundLocalError 'object' error

## [4.1.6] - 2024-03-27
### Fixed
- Fixed notice form fabric stage

## [4.1.5] - 2024-03-12
### Changes
- Add live session to tests dependencies.

## [4.1.4] - 2024-03-11
### Fixed
- OMPRW-901: Fixed default value of xformOp:scale

## [4.1.3] - 2024-02-27
### Changes
- OM-118469: RelationshipTargetPicker has modal_window parameter to create window as modal. Default is False
- Added /exts/omni.kit.property.usd/allow_rename_prims setting so renaming prims can be disabled. Default is True

## [4.1.2] - 2024-02-20
### Changed
- OMPRW-827: Workaround for PayloadReferenceWidget stalling when prim has large amount of references
- Added new setting /persistent/exts/omni.kit.property.usd/references_check_missing
-  This settings can be used to disable the reference file/prim check as could be slow on complex usd files (default is True)
- Added new setting /persistent/exts/omni.kit.property.usd/references_hide_max
-  This settings controls if the "Reference" frame is automatically closed if references count exceeds given value (default is 50)

## [4.1.1] - 2024-02-15
### Changes
- OM-118420: Added support for follow_connections in UsdBase read_value function

## [4.1.0] - 2024-02-08
### Changes
- OM-36400: Set change_on_edit_end default to True, though allowing dragging to always update every frame.
- Added update_value in begin_edit so tabbing between vector fields keeps values correctly.

## [4.0.4] - 2024-02-05
### Changes
- Update test searches for fallback identifier changes.

## [4.0.3] - 2024-02-02
### Changes
- OM-119931: Fix control states

## [4.0.2] - 2024-01-20
### Changes
- OM-118904: Quick fix relationship attribute test on usdrt

## [4.0.1] - 2024-01-18
### Changes
- OM-118699: Fix GetCustomDataByKey for usdrt attribute

## [4.0.0] - 2024-01-13
### Changes
- OM-96664: Update for adapter extensions

## [3.21.22] - 2024-01-11
### Changed
- OM-56756: Fixed bare except

## [3.21.21] - 2024-01-10
### Changed
OM-117601: fixed Sdf.UnregisteredValue handling in property window
OM-117601: is_readonly errors from non UsdBase models

## [3.21.20] - 2024-01-02
### Changed
- OM-56756: Users can rename prims from property panel field

## [3.21.19] - 2023-12-13
### Changed
- OMFP-3741: Unquote special characters for Asset Path Field.

## [3.21.19] - 2023-11-30
### Changed
- OM-118420: Added support for follow_connections in UsdBase read_value function

## [3.21.18] - 2023-11-30
### Changed
- OM-115814: Fixed material path not correctly converted to relative path.

## [3.21.17] - 2023-10-23
### Changed
- Fixed frame rebuild during prim drag

## [3.21.16] - 2023-11-07
### Changed
- Added setting to show/hide Property Widgets preference page.

## [3.21.15] - 2023-10-13
### Changed
- OMFP-2387: Show correct prim path for internal prim reference from references or payloads.

## [3.21.14] - 2023-09-21
### Changed
- Fixed relationship property widget to show "Mixed" when multiple prims are selected with non-matching values

## [3.21.13] - 2023-09-18
### Changed
- Fixed asset path assignment not converting path with  (file: or omniverse:) prefix to relative.

## [3.21.12] - 2023-08-31
### Changed
- Scrolled position after selecting a new actor of same type fix after using layer properties

## [3.21.11] - 2023-08-31
### Changed
- Reference asset path of "" is valid

## [3.21.10] - 2023-08-15
### Changed
- Add AllowedTokens support to string_builder

## [3.21.9] - 2023-08-03
### Changed
- Better handling of exceptions

## [3.21.8] - 2023-07-31
### Changed
- Fixed `SdfRelationshipArrayItemModel` to handle None item
- Fixed `SdfAssetPathArrayAttributeItemModel` to handle None item

## [3.21.7] - 2023-07-07
### Changed
- Property panel should retain its scrolled position after selecting a new actor of same type

## [3.21.6] - 2023-07-17
### Changed
- Handle test for `inputs:excludeFromWhiteMode` PlaceholderAttribute.

## [3.21.5] - 2023-07-05
### Changed
- Added `create_primspec_token`, `create_primspec_float`, `create_primspec_int`, `create_primspec_bool`, `create_primspec_string` helper functions
- Added `add_custom_schema_attribute`, `is_custom_schema_attribute_used`, `add_custom_schema_attributes_to_props` helper functions

## [3.21.4] - 2023-07-04
### Fixed
- Split up build_nested_group_frames so it can be sub-classed easier

## [3.21.3] - 2023-05-31
### Fixed
- Fix to prevent overlapped exception in tests

## [3.21.2] - 2023-05-29
### Changed
- OM-79996: Remove the prefix for HDR dragged from environment window

## [3.21.1] - 2023-05-26
### Changed
- Allowed `TfTokenAttributeModel` to override `_update_index`.

## [3.21.0] - 2023-05-25
### Changed
- Exposed UsdPropertiesWidgetBuilder functions as public.

## [3.20.5] - 2023-05-23
### Fixed
- Fixed issue with browsing payloads/references

## [3.20.4] - 2023-05-11
### Fixed
- Flexibility of asset property widgets

## [3.20.3] - 2023-04-28
### Changes
- Added support for global reload setting to affect the rest of UI.

## [3.20.2] - 2023-04-20
### Added
- "+Add" context menu uses delegate to avoid offscreen clipping

## [3.20.1] - 2023-04-28
### Changed
- Auto reload per prim and css live style for reference widget.

## [3.20.0] - 2023-04-26
### Added
- UsdPropertyUiEntry.override_doc_string

## [3.19.5] - 2023-04-24
### Fixed
- Disable remove/edit to references/payloads that are not authored in the local layer stack.

## [3.19.4] - 2023-04-21
### Fixed
- Improve live prims support and fix session refresh issue.

## [3.19.3] - 2023-04-06
### Fixed
- Handle %xx escapes characters in strings

## [3.19.2] - 2023-04-18
### Fixed
- Fixed selecting multiple prims with divergent relationships

## [3.19.1] - 2023-04-18
### Fixed
- Relationship property UI had a bug that was found while creating a unit test for it

## [3.19.0] - 2023-04-17
### Added
- Allow override of single entry model class in SdfRelationshipArrayItemModel
- Check for duplicate targets in SdfRelationshipArraySingleEntryModel

## [3.18.33] - 2023-04-14
### Changed
- Improved handling of outdated layers that are in a live session
- Made the UI more responsive and tweaked CSS

## [3.18.32] - 2023-04-12
### Added
- Allowed customize the edit target layer for usd property widget model.

## [3.18.31] - 2023-04-06
### Fixed
- Locate File button on SdfAssetPath widgets disabled based on full resolved path
  so it correctly greys out relative paths when the .usd is on http
- Locate File button disabled when pointing to an invalid path
- Ensuring Content window is open before locating an asset in SdfAssetPath widgets
### Changed
- Locate File button is greyed out when disabled rather than hidden
- SdfAssetPathDelegate class is now publicly available so you can derive from it
  and use it as a delegate_cls for SdfAssetPathArray widgets. Also has overridable
  methods like _build_additional() so you can add new buttons
- on_edit_fn kwarg can be supplied to SdfAssetPath widgets (both array and single
  component) by overriding UsdPropertiesWidget.get_additional_kwargs. This creates
  an edit button next to the path and calls the supplied function when the button
  is clicked.

## [3.18.30] - 2023-04-03
### Fixed
- Spurious errors when relationship widget has a malformed path
### Changed
- target_picker_cls to additional_widget_kwargs for SdfRelationshipArrayItemModel

## [3.18.29] - 2023-03-16
### Fixed
- payloads/reference reject invalid prim paths

## [3.18.28] - 2023-03-17
### Changed
- Added live sessions on primitives.

## [3.18.27] - 2023-03-11
### Fixed
- Fix test_l1_shader_material_subid_property test so that we collect the widget + model
  during each iteration of the loop.

## [3.18.26] - 2023-02-10
### Fixed
- Update to fix issue with floating_point_builder

## [3.18.25] - 2023-02-17
### Fixed
- Fix regression where add reference/payload/asset will reject invalid filepaths when apply is clicked

## [3.18.24] - 2023-02-10
### Fixed
- Fix issue with floating_point_builder, now hides "mixed" when editing starts

## [3.18.23] - 2023-02-27
### Added
- Move "item" models into separate module, usd_model_items.py as doing so seems to fix a PyBind11
  issue, which is documented in OM-64635.

## [3.18.22] - 2023-02-26
### Changed
- Replaced asyncio.ensure_future calls in references_widget.py and usd_property_widget.py with
  omni.kit.async_engine.run_coroutine function.

## [3.18.21] - 2023-02-05
### Added
- Add property filter support

## [3.18.20] - 2023-02-07
### Added
- Updated PrimPathWidget to use ToggleInstanceableCommand
- Added widget refresh to PrimPathWidget on usd changed

## [3.18.19] - 2023-02-08
### Fixed
- Fix issue that changes to built-in cameras will be authored into the current edit target instead of session layer.

## [3.18.18] - 2023-01-17
### Fixed
- Fixes property widget to call the right set value function if the model is not an SdfAssetPathAttributeModel

## [3.18.17] - 2023-01-17
### Added
- Updated UDIM support and updated tests
- `SdfAssetPathAttributeModel` sets builds SdfAssetPath with path/resolvedPath for UDIM paths

## [3.18.16] - 2023-01-06
### Fixed
- Fixes improper use of the file_importer that caused a race condition in the unittest `test_asset_array_widget`.

## [3.18.15] - 2022-12-16
### Added
- Fix issue that cannot undo properties of materials

## [3.18.14] - 2022-12-15
### Changed
- Allows any prim to set a `default` custom data for default value override.

## [3.18.13] - 2022-12-13
### Added
- Don't allow to edit instance proxies.

## [3.18.12] - 2022-12-05
### Added
- Added ability to pass arbitrary model_kwargs to model_cls and single_channel_model_cls specified in
  additional_widget_kwargs

## [3.18.11] - 2022-11-28
### Changed
- Now using platform-agnostic copy/paste rather than pyperclip.
- Removed context menu test and made its own extension.

## [3.18.10] - 2022-11-07
### Changed
- Added reset-user option for test.
- Update test_assert_array_widget to use grid view for file picker.

## [3.18.9] - 2022-10-18
### Fixed
- Fix change value on multi-select Variants

## [3.18.8] - 2022-11-02
### Added
- Added kwarg to hide the control state part of a widget

## [3.18.7] - 2022-09-21
### Added
- Added listener for `ADDITIONAL_CHANGED_PATH_EVENT_TYPE` event in message bus to trigger additional property invalidation.

## [3.18.6] - 2022-10-13
### Fixed
- Fixed browsing reference/payload path not resolving wildcard tokens in filepath
- Fixed browsing asset path/array attribute not navigating to the correct path
- Brought back detail options panel in filepicker when adding reference/payload
### Changed
- Use `omni.kit.window.file_importer` instead of wrapped version of file picker

## [3.18.5] - 2022-09-14
### Fixed
- Variants now support multiple selections & mixed

## [3.18.4] - 2022-09-06
### Fixed
- Fixed unittests.

## [3.18.3] - 2022-08-30
### Added
- Supported drag&drop and Filepicker to add multiple files to `SdfAssetPathArray`.
- Added `Copy Property Path` to property context menu.
### Changed
- If `SdfAssetPath` and `SdfAssetPathArray` has no `fileExts` customData, allow folder to be selected.

## [3.18.2] - 2022-08-19
### Fixed
- Fixed performance regression when building model for attribute whose value is a big array.

## [3.18.1] - 2022-08-16
### Changed
- Adjusted alignment for `SdfAssetPath` and `SdfAssetPathArray` widgets.

## [3.18.0] - 2022-08-08
### Added
- Added widget builder and models for SdfAssetArray.

## [3.17.20] - 2022-08-08
### Changes
- Added relationship widget identifiers

## [3.17.19] - 2022-08-03
### Changes
- OM-58170: Custom Layout Group that can have a condition

3.21.13

## [3.17.18] - 2022-08-02
### Changes
- Ensure relative path by default for texture path.

## [3.17.17] - 2022-07-25
### Changes
- Re-factored unittests to make use of content_browser test helpers

## [3.17.16] - 2022-07-15
- OM-55770: RGB/RGBA color swatches in property window

## [3.17.15] - 2022-07-13
- OM-55771: File browser button

## [3.17.14] - 2022-06-23
- Support Reset all attributes for the Property Widget

## [3.17.13] - 2022-06-22
### Added
- supported event type omni.timeline.TimelineEventType.TENTATIVE_TIME_CHANGED

## [3.17.12] - 2022-05-31
### Changes
- Changed create_control_state to use ImageWithProvider to prevent flicker

## [3.17.11] - 2022-05-26
### Changes
- added `reset_builder_coverage_table` function
- added `widget_builder_coverage_table` for converge testing

## [3.17.10] - 2022-05-13
### Changes
- Cleaned up ImageWithProvider vs Image usage

## [3.17.9] - 2022-05-17
### Changes
-  Support multi-file drag & drop

## [3.17.8] - 2022-05-03
### Changes
- Fixed manual input on float2/float3/float4 types
- Fixed soft range on float2/float3/float4 types
- Fixed hard range on float2/float3/float4 types

## [3.17.7] - 2022-05-05
### Changes
- Hide the Remove context menu for the transform property widget

## [3.17.6] - 2022-05-02
### Changes
- Goto URL supports UDIM wildcards

## [3.17.5] - 2022-04-22
### Changes
- No longer supported copy and group copy of properties when multiple prims are selected.

## [3.17.4] - 2022-04-07
### Changes
- Locate button not visible when not valid. Like http or empty

## [3.17.3] - 2022-04-14
### Added
- Supported copy partially mixed vector value in group copy.

## [3.17.2] - 2022-04-12
### Changes
- Fix issue with add_button_menu_entry and context menu submenu depth

## [3.17.1] - 2022-03-30
### Changes
- PlaceholderAttribute doesn't error if the metadata doesn't contain "customData.default" or "default"

## [3.17.0] - 2022-03-17
### Changes
- Changed builder function to a class member

## [3.16.0] - 2022-02-18
### Added
- Added Copy/Paste all properties to collapsible frame header.

## [3.15.2] - 2022-02-10
### Added
- Added `set_path_item_padding` and `get_path_item_padding` to `PrimPathWidget`

## [3.15.1] - 2022-02-09
### Added
- Don't fix window slashes in payload reference widget

## [3.15.0] - 2022-02-01
### Added
- Allow Raw Usd Properties Widget to show with multi-selection protection.

## [3.14.0] - 2021-12-08
### Added
- Add -> Attribute to create new attribute on selected prim.
- Right click to remove a Property. However, if Property belongs to a schema, remove is disabled.

## [3.13.1] - 2021-12-02
### Changes
- Softrange update/fixes for array types

## [3.13.0] - 2021-11-29
### Changes
- Added `_get_alignment` and `_create_text_label` UsdPropertiesWidgetBuilder functions

## [3.12.5] - 2021-11-10
### Changes
- `TfTokenAttributeModel` can have custom `AbstractItem` passed into `_update_allowed_token function` to display different values in combobox

## [3.12.4] - 2021-11-10
### Fixed
- Fixed property widget refresh when Usd.Property is removed from Prim.

## [3.12.3] - 2021-10-18
### Changes
- Hard ranges show draggable range in widgets
- Soft ranges can be overridden by user
- Added support for `Sdf.ValueTypeNames.UChar`

## [3.12.2] - 2021-10-27
### Changes
- Prevent crash in event callback

## [3.12.1] - 2021-09-16
### Changes
- Added widget identifiers

## [3.12.0] - 2021-09-29
### Added
- `UsdPropertiesWidget` subclasses can now register a custom subclass of `UsdAttributeModel` to create the widget's models using the `model_cls` key in additional_widget_kwargs, and `single_channel_model_cls` for vector attributes.

## [3.11.3] - 2021-09-07
### Changed
- Fixed mixed `TfTokenAttributeModel` and `MdlEnumAttributeModel` overwriting unchanged values on other prims when last selected prim's value changed by USD API.

## [3.11.2] - 2021-07-20
### Changed
- Added Sdf.Payload support

## [3.11.1] - 2021-07-20
### Changed
- Fixed jump to path icon to handle versioning info in URL

## [3.11.0] - 2021-07-06
### Added
- Added hook for property context menu to add custom context menu entry for property value field.
- Added `ControlStateManager` to allow adding external control state.
- Added `GfVecAttributeSingleChannelModel` which backs value widgets with single channel of a vector.
### Changed
- All vector builder now builds each channel separately and have separated control state.
### Fixed
- A few fixes on models.

## [3.10.1] - 2021-06-15
### Changed
- Fixed asset path refresh issue

## [3.10.0] - 2021-05-21
### Changed
- Added refresh layer to Reference prims

## [3.9.7] - 2021-05-18
### Changed
- Added reset button to asset path selector

## [3.9.6] - 2021-05-18
### Changed
- Added tooltip to asset path stringbox

## [3.9.5] - 2021-05-12
### Fixed
- The default value of NoneGraph

## [3.9.4] - 2021-05-10
### Added
- Updated Sdf.Reference creation so it doesn't use windows slash "\"

## [3.9.3] - 2021-05-06
### Changes
- Only show references checkpoints when server supports them

## [3.9.2] - 2021-04-21
### Changes
- Improvements for large selection of prims

## [3.9.1] - 2021-04-15
### Changed
- Connected attributes are not editable

## [3.9.0] - 2021-04-09
### Added
- Supported hard range and soft range in USD property widget builder/model.

## [3.8.1] - 2021-04-08
### Changed
- Fixed Search in `Add Target(s)` window of relationship widget.

## [3.8.0] - 2021-03-25
### Added
- Supported checkpoint in Reference Widget. Requires `omni.kit.widget.versioning extension` to be enabled.

## [3.7.0] - 2021-03-16
### Added
- Supported `SdfTimeCode` type.
- Added `_save_real_values_as_prev` function in `UsdBase`. It can be overridden to deep copy `self._real_values` to `self._prev_real_values`

## [3.6.0] - 2021-03-11
### Added
- Supported nested display group from both USD and CustomLayoutGroup.

## [3.5.3] - 2021-02-19
### Added
- Added PrimPathWidget API tests

## [3.5.2] - 2021-02-18
### Changed
- Updated UI tests to use new docked_test_window function

## [3.5.1] - 2021-02-17
### Changed
- Fixed References Widget not able to fix broken references.

## [3.5.0] - 2021-02-10
### Added
- Added `change_on_edit_end` to `UsdAttributeModel` and `UsdBase` 's constructor (default to False). When set to True, value will be written back to USD when EditEnd.

### Changed
- `SdfAssetPathAttributeModel` now only updates value to USD on EditEnd.

## [3.4.4] - 2021-02-10
### Changes
- Updated StyleUI handling

## [3.4.3] - 2021-01-22
### Changed
- Show schema default value on UI if the Attribute value is undefined in USD file.

## [3.4.2] - 2020-12-09
### Changes
- Added extension icon
- Added readme
- Updated preview image

## [3.4.1] - 2020-12-07
## Changed
- Don't show "Raw Usd Properties" frame when its empty

## [3.4.0] - 2020-12-03
## Added
- Supported `default` value for more attributes. It first checks for `PropertySpec.default`, if not found, falls back to `ValueTypeName.defaultValue` on the value type.

## [3.3.1] - 2020-11-20
## Changed
- Added get_allowed_tokens function to usd_attribute_model class.

## [3.3.0] - 2020-11-19
## Added
- Added `ReferencesWidget` with preliminary support for Reference, It supports add/remove/replace Reference on prim with no multi-prim editing support yet.

## [3.2.0] - 2020-11-17
## Added
- Added `VariantsWidget` with preliminary support for VariantSet(s). It only supports changing current variant selection, and no multi-prim editing support.

## [3.1.0] - 2020-11-16
## Added
- Added `target_picker_filter_lambda` to `RelationshipEditWidget`'s `additional_widget_kwargs`, giving access to a custom lambda filter for relationships when filtering by type is not enough.
- Exposed `stage_widget` on `RelationshipTargetPicker` for a more flexible access to the widget when needed.

### Changed
- Skip `displayName`, `displayGroup` and `documentation` (in addition to `customData`) when writing metadata for a `PlaceholderAttribute`.

## [3.0.0] - 2020-11-13
### Changed
- Renamed all occurrences of "Attribute", "attr" to "Property" and "prop" to properly reflect the widgets are built on Usd Property (Attribute and Relationship), not just Attribute. The change is backward compatible, so existing code will continue to work, but should be updated asap before old classes and functions become deprecated in future.
  - `UsdAttributesWidget` is now `UsdPropertiesWidget`.
  - `UsdAttributesWidgetBuilder` is now `UsdPropertiesWidgetBuilder`.
  - `UsdAttributeUiEntry` is now `UsdPropertyUiEntry`
  - `usd_attribute_widget` is now `usd_property_widget`
  - `usd_attribute_widget_builder` is now `usd_property_widget_builder`
  - On `UsdPropertiesWidget(prev UsdAttributesWidget)` class:
    - `build_attribute_item` is now `build_property_item`
    - `_filter_attrs_to_build` is now `_filter_props_to_build`
    - `_customize_attrs_layout` is now `_customize_props_layout`
    - `_get_shared_attributes_from_selected_prims` is now `_get_shared_attributes_from_selected_prims`

## [2.11.0] - 2020-11-06
### Added
- Added colorspace combobox to sdf path widget
- Added MetadataObjectModel classes

## [2.10.0] - 2020-11-05
## Added
- Added `no_mixed` flag to `additional_widget_kwargs`. If set to True, the value field will not display "Mixed" overlay, but display the value from last selected prim. Editing the value still applies to all attributes.

## [2.9.0] - 2020-11-04
### Added
- Supported showing and clicking to jump authored Connections on Attribute.

## [2.8.1] - 2020-11-03
### Changed
- Added context menu to path widget for copy to clipboard
- Added additional frame padding to borderless frames

## [2.8.0] - 2020-11-02
### Changed
- Improved support for multi-prim property editing (i.e. "mixed" value).
  - All field that has different values across selected prims will properly show blue "Mixed" text on the UI.
  - When dragging on a Mixed value, all properties snap to the value on the last selected prim.
  - On vector types, each component can be shown as Mixed and edited individually.

## [2.7.0] - 2020-10-30
### Added
- Added `multi_edit` to `UsdAttributesWidget`'s constructor. Set it to False if you want the widget to only work on the last selected prim. Set it to True to work on shared properties across all selected prims. Default is True.
- Added `prim_paths` to `UsdAttributeUiEntry` to allow overriding of what prim path(s) the properties are going to built upon.

## [2.6.0] - 2020-10-28
### Added
- Supported drag-and-drop, file picker and "jump to" button on SdfAssetPath widget.

## [2.5.0] - 2020-10-27
### Added
- Added `targets_limit` to `RelationshipEditWidget`'s `additional_widget_kwargs`, allowing limiting the maximum number of targets can be set on a relationship.

## [2.4.0] - 2020-10-23
### Added
- Added `MdlEnumAttributeModel` and supported building MDL enum type in `UsdAttributesWidgetBuilder`.

## [2.3.3] - 2020-10-22
### Added
- Added optional `collapsed` parameter to `CustomLayoutGroup`

## [2.3.2] - 2020-10-19
### Changed
- Removed `PrimPathSchemeDelegate` and `XformbalePrimSchemeDelegate` so now controlled by omni.kit.property.bundle

## [2.3.1] - 2020-10-19
### Changed
- Fixed USD widget not cleared after current scene is closed.
- Fixed instance parsing error in SchemaAttributesWidget.

## [2.3.0] - 2020-10-14
### Added
- Added optional parameters `additional_label_kwargs` and `additional_widget_kwargs` to `UsdAttributesWidgetBuilder` to allow supplying additional kwargs to builders.
- Added `get_additional_kwargs` function to `UsdAttributesWidget` class. Override it to supply `additional_label_kwargs` and `additional_widget_kwargs` for specific USD property.
- An special parameter to add type filtering to Relationship target picker. See example in `MeshWidget.get_additional_kwargs`.

## [2.2.0] - 2020-10-14
### Added
- Placeholder attribute.

## [2.1.0] - 2020-10-13
### Added
- Added custom_layout_helper module to help declaratively build customized USD property layout.
- ext."omni.kit.window.property".labelAlignment setting to globally control property label alignment.
- ext."omni.kit.window.property".checkboxAlignment setting to globally control bool checkbox alignment.
- UsdAttributesWidgetBuilder._create_label as separated function.

### Changed
- Fixed UI models not cleaned up on new payload.
- Fixed string/token being mistakenly treated as array and clipped for being too long.
- Fallback builder now creates StringField with disabled style.

## [2.0.0] - 2020-10-09
### Added
- Supported Usd.Relationship.

## [1.2.0] - 2020-10-02
### Changed
- Updated Style & Path widget display

## [1.1.0] - 2020-10-06
### Added
- UsdAttributesWidget._customize_attrs_layout to customize attribute display name/group/order, operating on UsdAttributeUiEntry.

### Changed
- UsdAttributesWidget._get_shared_attributes_from_selected_prims now returns list of UsdAttributeUiEntry.
- Removed is_api_schema parameter from SchemaAttributesWidget constructor.
- SchemaAttributesWidget now works on multiple applied schema.

## [1.0.0] - 2020-09-18
### Added
- USD Widgets Released.
