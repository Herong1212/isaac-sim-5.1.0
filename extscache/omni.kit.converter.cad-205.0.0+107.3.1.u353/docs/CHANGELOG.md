# Changelog

## [205.0.0] - 2025-08-21
- [DGN Converter] Add support for `MergedAttributeStyle.ePrimvar` in `Parameters.mergedAttributeStyle`.
- [DGN Converter] Exposed the name of Element ID primvar as `omni.converter.dgn.tokens.elementIdPrimvar`.
- [DGN Converter] Triangulation of Meshes is now optional based on `Parameters.triangulate`. The default value is `true`.
- [DGN Converter] Validate transform scale of 2D objects.
- [DGN Converter] Display name metadata is authored for metadata `UsdGeomSubsets`.
- [DGN Converter] Graphics Elements are sorted by Element ID before conversion to make results more consistent.
- [DGN Converter] Display name metadata is authored for all Prims that could not use the prefered name.
- [DGN Converter] The element type is transcoded with the rest of the Prim name rather than added as a suffix.
- [DGN Converter] Prims representing merged Graphics Elements no longer have an element Id in their name.
- [DGN Converter] Support basis curve width and expose `fallbackCurveWidth`.
- [DGN Converter] Add `mergeCurves` option to control curve merging.
- [HOOPS Converter] Set display name for material prims
- [HOOPS Converter] Author widths primvar for USD Basis Curves
- [HOOPS Converter] Update to HOOPS Exchange 2025.6
- [HOOPS Converter] Only specialize Materials when the instancing style requires it
- [JT Converter] Apply translation to geometry Prims to place them at the centroid of the Part

## [204.0.4] - 2025-08-18
- [DGN Converter] Respect Level based color override flag.

## [204.0.3] - 2025-08-07
- [DGN Converter] Skip extrusion solids that do not have valid extents

## [204.0.2] - 2025-08-01
- Fix publishing issue

## [204.0.1] - 2025-07-15
- [JT Converter] Fixed layer filtering
- [HOOPS Converter] Deduplicate Materials
- [HOOPS Converter] Author primvar display colors and opacities when materials are disabled
- [HOOPS Converter] Added instancing style parameter
- [HOOPS Converter] Move Looks scope to child of default prim
- [HOOPS Converter] Update to HOOPS Exchange 2025.5
- [DGN Converter] Update ODA Kernel and Drawings SDKs to version 26.6
- [CAD Converter] Fixed convert options mapping

## [204.0.0] - 2025-06-30
- Update to Kit 108 / USD 25.02 / Python 3.12

## [203.2.2] - 2025-06-16
- [DGN Converter] Mirror transformations are translated correctly
- [DGN Converter] Rotations are correctly translated
- [DGN Converter] Element names are stored in USD

## [203.2.1] - 2025-06-11
- [CAD Converter] Include core extension and backend converter versions in output creator metadata

## [203.2.0] - 2025-06-10
- [CAD Converter] Conversion failures are correctly handled and logged
- [CAD Converter] Conversion arguments and `Parameters` are logged at the start of conversion

- [DGN Converter] A transform is applied to `Mesh` prims to place them at the centroid of their combined Graphics Elements

- [HOOPS Converter] The `Prototypes` Prim is a `Scope` rather than having an undefined type name
- [HOOPS Converter] Addressed memory leak vulnerabilities
- [HOOPS Converter] Fixed conversion failures due to `UnicodeDecodeError` on Linux
- [HOOPS Converter] BIM relationships are translated to `UsdRelationships` for IFC models

- [JT Converter] Update to JT Toolkit version `11.7.1`
- [JT Converter] Empty `UsdGeomPointBased` Prims are not defined if no `points` were generated
- [JT Converter] Line strips where the end vertex of one line is collocated with the first vertex of the next will be joined together
- [JT Converter] Constant display color primvars based on Material parameters are only authored in the absence of per vertex colors
- [JT Converter] Per vertex normals are translated for `UsdGeomBasisCurves` and `UsdGeomPoints` prims
- [JT Converter] Per vertex colors are translated for `UsdGeomMesh`, `UsdGeomBasisCurves` and `UsdGeomPoints` prims
- [JT Converter] Constant widths are translated for `UsdGeomBasisCurves` prims

## [203.1.4] 2025-05-21
### Changed
- [CAD Converter] Added .usdz export feature from UI.
- [DGN Converter] Updated to ODA Kernel and Drawings SDKs to 26.3
- [DGN Converter] Changed default surface tolerance from 0.0 to 0.2 for batch conversion mode
- [DGN Converter] The element type attribute is now a Tf.Token rather than a String.
- [DGN Converter] Custom attributes holding the color and fill color of Graphics Elements are authored.
- [DGN Converter] Per object metadata for merged Element Meshes will only be created as UsdGeomSubset Prims if there are less than 1000 input Elements as a measure to limit conversion hangs.
- [DGN Converter] Improved conversion time for DGN files with vast numbers of sibling Elements.
- [HOOPS Converter] Updated HOOPS Exchange SDK to 2025.3.0
- [HOOPS Converter] Include BIM relationships in IFC model metadata conversion

### Fixed
- [CAD Converter] Fixed .SAT and .DAE format support in omni.services.convert.cad extension by using file regex filters from core extensions.
- [CAD Converter] Fix conversion failure when writing to Nucleus
- [DGN Converter] Removed SQLite and DWF dependencies.
- [DGN Converter] Package tokens python module.
- [DGN Converter] Fill color is the default color for Materials; color will be used in its absence.
- [HOOPS Converter] Removed Direct X library.
- [HOOPS Converter] Package tokens python module.
- [HOOPS Converter] Fixed missing metadata in converted usd output.
- [HOOPS Converter] Attributes 'No value' is authored in USD for Attributes that do not have a defined value in the source file.
- [HOOPS Converter] Only read attributes when metadata is being converted.
- [JT Converter] Fix bug where the converter exports hidden geometry as visible

## [203.1.3] 2025-05-09

- Fix dependency version constraints to properly handle minor and patch version updates

## [203.1.2] 2025-04-28

- Updated backend converter versions

## [203.1.1] 2025-04-23

- Expose option to choose between USD Preview Surface and OmniPBR materials (OmniPBR includes USD Preview Surface support)

## [203.1.0] 2025-04-09

- Update DGN and HOOPS backend converter dependencies

## [203.0.1] 2025-02-18

- Lock to USD target.

## [203.0.0] 2025-02-14

- Update to Kit 107, USD 24, and Python311
- ABI upgrade
- Update progress logging
- [JT Converter] Avoid Crash on Conversion Failure
- [JT Converter] Exclude plmxml
- [HOOPS Converter] Update to hoops exchange sdk 2025.1
- [HOOPS Converter] Empty metadata conversion fix
- [DGN Converter] Update to ODA Drawings SDK 25.12
- [DGN Converter] Skip converting DGN element with invalid mesh vertices
- [DGN Converter] Fix invalid merged mesh topology
- [DGN Converter] Add option to skip merging meshes
- [DGN Converter] Remove libxl.dll
- [DGN Converter] Remove unused libraries with vulnerabilities
- [DGN Converter] Fix smart solids level names

## [202.1.0] 2024-11-26

- Merge release 202.0.0 updates into master
- Update to Hoops Exchange SDK 2024.8
- Update DGN Converter to ODA SDK 25.8
- Fixed incorrect value for double type metadata conversion.
- Fixed crash caused by invalid attributes.
- Update dependencies for security

## [202.0.0] 2024-10-22

- Add option to override up-axis and meters per unit USD stage metrics with Scene Optimizer with helpful quick links.
- Add Scene Optimizer string config option
- Merge release 201.1.0 updates into master
- [HOOPS Converter] add bConvertMetadata option
- Update documentation
- Update extension versions in toml and documentation
- Add version constraints in toml and bump hoops/hoops_core major semver
- Update kit-kernel to 106.2
- Updated HECC dependency containg 2024.6.0 Hoops SDK to address security vulnerability
- Link hoops extension import options to the backend converter's settings for metadata and hidden object handling.
- Add option to specify USD output file format.
- Add option to specify USD output file name.
- [Asset Converter Service] Add new entrypoint to handle asset management on NVCF.
- Migrate Hoops converter from CSDK to USD Exchange.
- Migrate JT Converter from CSDK to USD Exchange.
- Revert DGN Converter ODA library to version 25.4 to avoid version mismatch with HOOPS Converter
- Update documentation for 202.0 release.
- Update dependencies from release branch

## [201.2.1] 2024-09-19

- Remove omni.usd as the extensions do not have a GPU dependency
- Update kit-kernel to 106.1.0; Update Scene Optimizer; Remove Asset Validator as it is unused
- Remove test data from build package
- Update Scene Optimizer version dependency to maintain compatibility across Kit Kernel 106.0.x and 106.1.x
- Create release branch with 201.2.0 hot fix updates
- Resolve ETM issues by setting range on extension version dependencies
- Republish without pre-release tags with kit-kernel 106.1

## [201.1.0] 2024-07-22

- Audited documentation and updated based on changes for release 201.1.
- Update pre-release tag to release candidate
- Consolidate changelog pre-release entries
- Bump semantic version for resolving versions in ETM tests.
- Use converters' packages built against Ubuntu 20.04
- Use semantic versioning for extensions. Use external/marketing version in CHANGELOG.md
- Add test waiver to extension to avoid OV Apps from failing test pipeline
- Skip test for codeless omni.kit.converter.cad extension
- Moved ui delegates and registration to separate extensions: .hoops, .dgn, .jt. Moved service registration to .hoops_core, .dgn_core, .jt_core. Moved more common functionality to .common. Renamed .cad_core to .hoops_core, removed .cad since all delegates / registration are in the new separate extensions.
- Renamed cad_core to hoops_core
- Updated set_app_data to include client name / version
- Run scene optimizer as post-conversion task
- Update extension.toml to lock extension to Kit SDK version being used
- Update to 201.1.0, move connect-sdk and scene optimizer to omni.kit.converter.common
- Update to Kit 106.0.1
- Update converter_options payload from str to dict
- Remove pre-release tag from public-facing release version

## [201.0.0] - 2024-03-04

- Remove Nucleus test case from unreliable test cases
- Update to kit-kernel 106.0
- Add tessellation options subsection to UI.
- Update metadata tests.
- Update CATIA filters
- Surface tolerance fix to have surface tolerance field present and hide LOD drop down when selecting a DGN file and vice versa when selecting other files for import.
- JT Connect SDK branch integration.
- Support for Surface Tolerance setting and UI field
- [DGN Converter] add bConvertHidden option
- Fix USD output path of DGN converter
- Use same kit-kernel version as Connect SDK
- Updated keywords for improving searchability for CAD Converters
- Update to DGN converter that uses Connect SDK
- Update passing of arguments to DGN subprocess
- Update Connect SDK to release 0.6.0
- fix etm - use explicit pre-release
- etm-failure-fix and merge release to master
- Update Overview.md documentation

## [200.1.1] - 2023-11-28

- Fixed Overview.md doc for NX related files
- Updated Overview.md doc for NX related files
- Handle scenario when get_local_file_async() is not able to pull down nucleus file to local OV cached folder
- Updated dependency version in extension.toml
- Updated to OMFP-3756\. Supports CAD file with a version suffix greater than 9\. (i.e., car_bumper.prt.42)
- Resolves issue saving files with valid characters in filename (i.e., periods)
- Updated CAD Converter deps. Bump all extension versions

## [200.1.0] - 2023-10-26

- Fixed typos in UI
- Error handling when failing to write to Nucleus.
- Changed version lock on all exact deps.
- Removed .CATDrawing, .CATShape, NEU, XAS, and XPR supports
- Fixed empty tessellation box
- Show all conversion options when using multi-select
- Fixed overwrite confirmation dialog text
- Fixed Progress Window Cut Off
- Spelling corrections; cutoff handled with OMFP-2051 fixes
- OMFP-2051 - [CAD Converter][DGN] DGN progress needs better info
- Added callback functions for dgn_core call through omni.kit.cad.converter UI
- Added CAD Converter options to UI.
- OM-86344 - [CAD Converter] Add import to current stage option
- OM-99536 - [CAD Converter] Cannot overwrite existing files.
- Fixed missing _.STP/_.IGS file extension support.

## [200.0.0] - 2023-05-11

- Split UI and Core CAD Converter

## [104.1.5] - 2022-12-19

- Added new endpoint for services

## [104.1.4] - 2022-12-01

### Changed

- Official HOOPS Exchnge update to HE2022SP2U2
- This include support for SolidWorks 2022

## [104.1.3] - 2022-12-01

### Changed

- testing

## [104.1.2] - 2022-12-01

### Changed

- testing HOOPS update HE2022SP2U2

## [104.1.1] - 2022-11-10

### Changed

- preparing for kit 104.1
- fixes for model visibility issues while instancing
- converting hidden items as hidden

## [104.0.2] - 2022-10-13

### Changed

- fixes to sub-part representation item transform stack

## [104.0.1] - 2022-10-06

### Changed

- initial 104 build
- initial 2022.3 with instancing

## [103.5.5] - 2022-08-02

### Changed

- hoops license update permanent

## [103.5.4] - 2022-08-01

### Changed

- rfind fix for converted asset path basename
- that is where the converter writes the USD file during import

## [103.5.3] - 2022-07-26

### Changed

- wait lock fix for python binding

## [103.5.1] - 2022-07-22

### Changed

- bringing 103.1 hotfix items to 103.5 for View 2022.2

## [1.0.14] - 2022-07-18

### Changed

- update license key for hoops sdk with permanent key
- picking up hoops sdk direct from packman
- additional CAD file format suffixes

## [1.0.13] - 2022-07-07

### Changed

- update license key for hoops sdk with permanent key
- test

## [1.0.12] - 2022-07-07

### Changed

- added more file suffixes for Parasolid files

## [1.0.11] - 2022-07-04

### Changed

- update license key for hoops sdk thru 20220731

## [1.0.9] - 2022-06-23

### Changed

- Migration to HOOPS Viewer Sample
- test

## [1.0.8] - 2022-05-17

### Changed

- Representation Item Sets

## [1.0.7] - 2022-05-03

### Changed

- update license key for hoops sdk up thru 20220630

## [1.0.6] - 2022-05-03

### Changed

- full coverage of HOOPS triangle mesh formats including textures, and model structure info command line output

## [1.0.5] - 2022-04-28

### Changed

- updated texture normals and format handling

## [1.0.4] - 2022-04-25

### Changed

- fix for non USD safe names

  ## [1.0.3] - 2022-04-20

  ### Changed

- update hoops version

## [1.0.2] - 2022-04-19

### Changed

- add support for unsaved stage

## [1.0.1] - 2022-04-04

### Changed

- disabled output file picker until filepicker bugfix: OM-47383

## [1.0.0] - 2022-03-24

### Changed

- Initial extension from original omni.kit.converter.cad.
