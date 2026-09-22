# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.2.6] - 2025-07-25
### Fixed
- OMPE-56640: Fix type error by None value for casting in Python.

## [1.2.5] - 2025-07-21
### Fixed
- OMPE-56104: Keep explicit casting in Python to avoid unsupported casts from Python to C++

## [1.2.3] - 2025-04-15
### Fixed
- OMPE-43816: ensured some extension enable/disable hook objects are cleaned up.

## [1.2.2] - 2024-08-13
### Added
- OMPE-17373: Always set widget identifier

## [1.2.1] - 2024-08-08
### Added
- OMPE-17373: Don't change widget identifier

## [1.2.0] - 2024-05-04
### Added
- Forward possible omni.ui constructor (i.e. tooltip) arguments from createComboboxWidget

## [1.1.2] - 2024-04-25
### Fixed
- OM-122859: Fixed double slashes in file picker apply handler.

## [1.1.1] - 2024-03-20
### Changed
- OM-122539: Changed "forcing setting_is_index=False" warning to info

## [1.1.0] - 2024-03-19
### Changed
- OM-122343: Added documentation

## [1.0.16] - 2024-02-07
### Changed
- OM-118790: omni.kit.widget.searchable_combobox is optional

## [1.0.15] - 2024-02-06
### Changed
- OMPRW-616: Fixed combobox changing after reset

## [1.0.14] - 2024-01-16
### Changed
- OM-118226: Fixed warning caused by combobox changes when using dict and default arguments.

## [1.0.13] - 2024-01-11
### Changed
- OM-118226: Fixed combobox set labels as setting values issue.

## [1.0.12] - 2024-01-04
### Changed
- OM-117775: Fixed incorrect combobox init value issue

## [1.0.11] - 2023-12-14
### Changed
- OM-117224: Add support to pass through "labels" to via "additional_widget_kwargs"
- OM-117224: Add support for new SettingWidgetType.VECTOR3 in create_setting_widget()

## [1.0.10] - 2023-11-13
### Changed
- OM-114529: Replace print statement with carb.log*

## [1.0.9] - 2023-10-27
### Changed
- OM-110067: Make VectorFloatComponentModel support min/max range

## [1.0.8] - 2023-10-10
### Changed
- Set widget identifier to path when not set elsewhere

## [1.0.7] - 2023-10-26
### Added
- OMFP-1252: Increased code coverage
- OMFP-1252: Removed some deprecated code

## [1.0.6] - 2023-09-27
### Added
- OM-109069: Fix for None error when querying settings dictionary.

## [1.0.5] - 2023-09-05
### Added
- OM-107668: Support RadioButton and Combobox Menu in setting widgets

## [1.0.4] - 2023-08-17
### Changed
- OM-77258: Use new ChangeDraggableSettingCommand when changing the value of a draggable setting

## [1.0.3] - 2023-04-24
### Fixed
- OM-91518: Fixed ComboBox widget double slash in it's xpath as shown in inspector

## [1.0.2] - 2022-11-30
### Changed
- Fixed widgets showing value modified when it wasn't

## [1.0.1] - 2022-06-23
### Changed
- Added identifier to create_setting_widget_combo for easier testing

## [1.0.0] - 2021-03-25
### Created
- Created as updated omni.kit.settings
