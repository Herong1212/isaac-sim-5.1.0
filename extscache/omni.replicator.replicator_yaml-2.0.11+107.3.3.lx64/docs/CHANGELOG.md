# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [2.0.11] - 2025-02-07
### FIXED
- Support Kit 107

## [2.0.10] - 2024-11-26
### CHANGED
- Added 'ticked' to window menu layout

## [2.0.9] - 2024-10-31
### FIXED
- Error handling in parser now supports outputting line number in yaml file. (OMPE-16930)

## [2.0.8] - 2024-09-17
### CHANGED
- Skip tutorial test to address issue with ETM

## [2.0.7] - 2024-09-05
### FIXED
- Update for Kit 106.1

## [2.0.6] - 2024-07-30
### FIXED
- Replaced depreciated omni.kit.ui.get_editor_menu()
- Shutdown app if YAML processing fails
- Ensure stage is loaded before processing YAML

## [2.0.5] - 2023-12-13
### CHANGED
- Upgrade writers to new replicator backend system

## [2.0.4] - 2023-10-06
### FIXED
- Fix incorrect path

## [2.0.3] - 2023-09-26
### ADDED
- Raise an error when multi-item dict is provided a function in yaml.
### CHANGED
- Change YAML's Isaac Sim USD paths to the correct version.
## [2.0.2] - 2023-09-22
### CHANGED
- Yaml scripts can now also be specified through the `--/omni/replicator/script` flag just like python scripts

## [2.0.1] - 2023-08-29
### FIXED
- Fixed `ReplicatorYAMLWriter` when stereo camera render products are provided.

## [2.0.0] - 2023-08-12
### CHANGED
- Release of ReplicatorYAML which replaces Replicator Composer
- New syntax enables compatibility with all existing Replicator components and supports custom components including custom randomizers, annotators and writers

## [1.2.13] - 2023-07-28
### CHANGED
- Remove some pip bunlde dependencies to use pip bundle from `omni.pip.compute` and `omni.kit.pip_archive` instead.

## [1.2.12] - 2023-05-02
### FIXED
- Fix composer visualizer to use absolute path. (OM-89391)

## [1.2.11] - 2023-03-22
### FIXED
- Fix saving stereo camera output because of render product name change. (OM-86634)

## [1.2.10] - 2023-03-09
### ADDED
- Add another check for existence of an asset in nucleus, as the first check might fail if the asset is not cached. (OM-83289)
## [1.2.9] - 2023-02-28
### CHANGED
- Change object instantiation to use references rather than scene instances by default

## [1.2.8] - 2023-02-16
### FIXED
- Fix composer visualize models with inherited group. (OM-60415)

## [1.2.7] - 2023-02-13
### ADDED
- Add UI for omni.replicator.composer. (OM-64511)

## [1.2.6] - 2023-02-06
### CHANGED
- Change the directory structure to support `omni.graph` nodes for composer.
### ADDED
- Add `visualize_models` mode to visualize the assets that the yaml file wants to load. (OM-60415)

## [1.2.5] - 2023-02-06
### ADDED
- Add occlusion output for composer. (OM-74481)

## [1.2.4] - 2023-02-01
### FIXED
- Set ignore on saved exit to true so that composer test don't time out.
- Fix `wall/ceiling/floor_color` not working before. (OM-76559)
## [1.2.3] - 2022-12-16
### FIXED
- Remove `omni.kit.window.viewport` dependency that causes crash.

## [1.2.2] - 2022-12-14
### FIXED
- Fix when `overwrite` is set to False, `on_time` trigger does not output the correct file paths. (OM-76376)
- Fix `light_temp` argument not working. (OM-76557)
- Fix creating walls, floors and ceiling not working for scenario room. (OM-76559)
- Fix `ComposerWriter` to use up-to-date annotators. (OM-76317)

### ADDED
- Add support for sky light parameters. (OM-76561)

## [1.2.1] - 2022-12-06
### FIXED
- Fix `parser.py` where check for wrong file type.
- Fix `overwrite` args on empty directory.

## [1.2.0] - 2022-11-21
### ADDED
- Add support for `walk` distribution
### FIXED
- Fix `group` in composer.py for generating scenario scene.
- Fix `overwrite` argument behavior in `composer_writer`.
- Fix directory structure when `groundtruth_stereo` is set to true.
- parser will raise error when input file is with incorrect file type.

## [1.1.3] - 2022-08-22
### FIXED
- Fix `bounding_box_2d` for left stereo camera.

## [1.1.2] - 2022-08-19
### FIXED
- Fix `composer_writer`'s directory to bounding box data
- Fix the behaviour of `overwrite` args. Now if it set to `False`, it will not overwrite the old data, but will still write the new data.

## [1.1.1] - 2022-08-17
### ADDED
- Add Composer Writer that has specific output directory structure.

## [1.1.0] - 2022-08-16
### CHANGE
- Make sure that all the examples are running fine.

## [1.0.2] - 2022-08-08
### CHANGE
- Change the way that composer handles relative path.
- Bug fixes.

## [1.0.1] - 2022-08-04
### CHANGED
- Change that extension will build separately for windows and linux.

## [1.0.0] - 2022-08-02
### Added
- Initial release.
