# Changelog

## [master] - 2025-04-29
- Update MaterialX modules to be in sync with what is in 1.38.10.openpbr.mdl110

## [master] - 2024-12-13
- Fixed NaN in `triplanar_normalmap_texture`

## [master] - 2024-12-11
- Added support for `KHR_materials_iridescence` and `KHR_materials_anisotropy` in glTF material
- Fixed tangent rotation for normal map lookups in glTF material

## [master] - 2024-11-25
- Removes colorpsace in empty texture_2d calls

## [master] - 2024-11-21
- Fixes default colorspace for linear texture resources in new property panel.
## [master] - 2024-11-01
- Fixed normalmap rotation was not properly shaded with `triplanar_normalmap_texture` and `hextiling_normalmap_texture`

## [master] - 2024-10-16
- Added support `closest` texture lookup mode in MDL backend for MaterialX

## [master] - 2024-10-08
- Fixed some hextiles were static

## [master] - 2024-10-02
- Fixed OmniGlass roughness was not squared

## [master] - 2024-09-30
- Added `color_correct` and `random_value` from DHL omni-extended-materials to core

## [master] - 2024-09-10
- Added normal roughness filtering for `OmniGlass`

## [master] - 2024-08-15
- Fixed a warning about an unused parameter in GLTF materials, and added conditional support for vertex opacity with a boolean

## [master] - 2024-08-12
- Changed parameter display name `Albedo Desaturation` to `Albedo Map Desaturation`. The tooltip is also updated

## [master] - 2024-07-24
- Added texture validation and the default return value in `hextiling_file_texture` and `hextiling_normalmap_texture`

## [master] - 2024-07-23
- Fixed per map rotation was not working properly in `triplanar_normalmap_texture`

## [master] - 2024-07-22
- Added `hextiling_file_texture` and `hextiling_normalmap_texture`

## [master] - 2024-07-09
- Added parameter range annotations in `OmniPBRBase`
- Added `Dusty diffuse` material

## [master] - 2024-05-13
- add open_pbr_uber_surface and open_pbr_uber_surface_default

## [master] - 2024-05-08
- Update anno::in_groups for Material Editor 2.0

## [master] - 2024-05-08
- Fixed mx_image_*() did not return default value when texture file is not present

## [master] - 2024-04-17
- Removed GTL entries from `config.packman.xml`

## [master] - 2024-04-10
- Remove `ArkPBR material`

## [master] - 2024-04-01
- Added `add_round_edges`

## [master] - 2024-03-22
- Added `add_vector_displacement`

## [master] - 2024-03-13
- Synchronized MaterialX MDL modules with public repository as of commit `839b919` in `dev_1.39` branch

## [master] - 2024-03-11
- Added round edges support to `OmniPBR`, `OmniPBRBase`, `OmniPBR_Clearcoat` and `OmniSurface`

## [master] - 2024-02-26
- Fixed bump was not working with mx_generalized_schlick_bsdf()

## [master] - 2024-02-07
- Renamed `OmniTwoSided` to `twosided` and moved to core_definitions

## [master] - 2024-01-29
- Added `OmniTwoSided`

## [master] - 2024-01-23
- Enabled `multiscatter_tint` for MaterialX BSDFs

## [master] - 2023-11-21
- VRay templates: Updated MDL version to 1.8.
- VRay templates: Added anno::node_output_port_default() and anno::display_name() to all texture map nodes.

## [master] - 2023-10-16
- Include a version tag in git during the publishing pipeline

## [master] - 2023-10-06
- rotate_around_*() functions are now exposed
- Fixed rotation in compute_latitude_longitude_projection() was incorrect

## [master] - 2023-10-01
- Reorganize repository
- Add Gitlab pipeline setup for publishing

## [master] - 2023-08-28
- Fixed OmniEmissive was in wrong category in the context menu.

## [master] - 2023-08-07
- Update MaterialX support modules to include MDL 1.8 features including custom UV names and other vertex channels.
- There are new modules based on the MDL version for upcoming code generator features in MaterialXGenMdl.

## [master] - 2023-08-02
- Update Blender support shaders to use BSD-3 terms.

## [master] - 2023-07-31
- Added directory /Nonvisual containing a .json of the nonvisual material map which will be used in the sim-ready nonvisual spec

## [master] - 2023-07-28
- Opacity Amount is now varying type parameter in OmniPBR and OmniPBR_ClearCoat

## [master] - 2023-07-24
- Added ARK shaders

## [master] - 2023-07-17
- Added backface emission support to OmniEmissive.

## [master] - 2023-07-13
- Metal has now a parameter edge_color, and uses Gulbrandson and fresnel_factor. Makes it compatible with thin_film
- Blend Material now also blends geometry and volume.

## [master] - 2023-07-11
- Default struct unrolling to use node_port_value_and_fields in order to maintain backwards compatibility.

## [master] - 2023-06-26
- update SimPBR_Translucency to use MDL 1.6

## [master] - 2023-06-26
- enable struct unrolling for texture_return functions in core_definitions

## [105, master] - 2023-05-23
- Change OmniSurfaceBase multi-scattering sheen tint to color(1.0)

## [105, master] - 2023-05-11
- Added ColorRamp MDL to replicate Blender's ColorRamp shader for use by UMM2

## [105, master] - 2023-05-17
- add new unlit material (MDL 1.7) that takes a texture map as emissive color.
- if texture has alpha, the alpha is used as a cutout for the material
- supports emissive intensity scaling

## [105, master] - 2023-04-26
- update MaterialX support modules to version 1.38.7 with MDL 1.7 features,
- fixed MaterialX volume mixing functions for MDL 1.7,
- fixed the thin-film with thickness 0 behavior of the MaterialX conductor
- VRay-to-MDL/Tiles Node: Improved matching of grout, color and fade variance with respect to 3dsmax.

## [105, master] - 2023-04-14
- signal normalmaps are raw.
- align the default for flip_v for triplanar_normalmap,
- changes order of transformation in transform_st,
- fixed parameter ordering in triplanar,
- fixed tangent space so that flip_v works as intended and ogl style normalmaps work as expected.
- fixed flip_v in case a single map is used

## [105, master] - 2023-03-29
- Moved SimPBR from the SimReady folder to the Base folder

## [105, master] - 2023-03-27
- Removed round edges support from OmniPBR, OmniPBRBase, OmniPBR_Clearcoat and OmniSurface

## [105, master] - 2023-03-21
- Added axf support module
- Added triplanar_file_texture()
- Changed unifrom texture transformations to varying

## [105, master] - 2023-03-10
- Fixed bump did not appear in OmniPBR, OmniPBRBase and OmniPBR_Clearcoat

## [105, master] - 2023-03-09
- Added round edges support to OmniPBR, OmniPBRBase, OmniPBR_Clearcoat and OmniSurface

## [104, master] - 2023-01-12
- Changed display name Texture Scale to Texture Tiling for OmniPBR, OmniPBR_Clearcoat and OmniGlass

## [104, master] - 2023-01-09
- glTF/pbr.mdl uses string input to control vertex opacity and vertex color lookups. Default is displayColor and displayOpacity

## [104, master] - 2022-12-12
- Changed OmniPBR, OmniPBR_ClearCoat, OmniPBRBase Emissive_Intensity from uniform to varying
