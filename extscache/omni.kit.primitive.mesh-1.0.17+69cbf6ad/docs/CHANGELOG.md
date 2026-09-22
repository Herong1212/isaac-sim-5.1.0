# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.17] - 2024-07-16
### Changed
- Updated documentation with AI agent.

## [1.0.16] - 2023-11-06
### Changes
- Fix issue that CreateMeshPrimWithDefaultXformCommand does not accept type Gf.Vec for object_position param.
- Fix issue that creating primitives from context menu does not put meshes above ground.

## [1.0.15] - 2023-10-31
### Changes
- Add more tests to increase code coverage.

## [1.0.14] - 2023-08-24
### Changes
- Fix issue that creates meshes offset them by 50m instead of 0.5m in meter units.

## [1.0.13] - 2023-04-26
### Changes
- Revert behavior to not create meshes above ground by default, and use param to control the behavior.

## [1.0.12] - 2023-04-03
### Changes
- Fix UV mapping.
- Ensure all meshes created above ground.

## [1.0.11] - 2023-03-23
### Changes
- Use texCoord2f[] for primvars:st type.

## [1.0.10] - 2023-03-15
### Changes
- Use texCoord2d[] for primvars:st type.

## [1.0.9] - 2023-01-06
### Changes
- Fix test_tessellation_params test by creating a new stage

## [1.0.8] - 2022-11-25
### Changes
- Improve mesh primitives for physx needs.
- Make sure cone and cylinder are watertight.
- Fix normal issues at the tip of Cone.
- Add more tessellation settings for caps of cone and cylinder.
- Add more tessellation settings for cube to tesselate cube with axis.

## [1.0.7] - 2022-11-22
### Changes
- Fix to avoid crash at shutdown when loading optional slice

## [1.0.6] - 2022-11-22
### Changes
- Make UI dpendency optional

## [1.0.5] - 2022-11-12
### Changes
- Export extent attr for mesh.

## [1.0.4] - 2022-11-11
### Changes
- Clean up dependencies.
## [1.0.3] - 2022-10-25
### Changes
- Added prepend_default_prim parameters to CreateMeshPrimWithDefaultXformCommand

## [1.0.2] - 2022-08-12
### Changes
- Added select_new_prim & prim_path parameters to CreateMeshPrimWithDefaultXformCommand

## [1.0.1] - 2022-06-08
### Changes
- Updated menus to use actions.

## [1.0.0] - 2020-09-09
### Changes
- Supports cube, cone, cylinder, disk, plane, sphere, torus generation.
- Supports subdivision of meshes.
