# Changelog

## 7.6.1 2024-10-09

### Changed
- Prepare for Python-3.12

## 7.6.0 2024-10-09

### Fixed
- USDRT - USDRT SdfPath less-than operator should behave the same as USD. [OMPE-18389]


### Improved
- USDRT - Many improvements to Fabric Hierarchy and Connectivity targeting robotics and physics use cases enabling thousands of changes per frame. [OMPE-20759]

## 7.5.1 2024-09-22

### Added
- USDRT - Add C++ api docs in kit-sdk documentation. Ensure linking docs from kit-manual works. [OMPE-13843]
- USDRT - USDRT VtArray python bindings refactor to use pybind trampoline class & ensure GIL safety. [OMPE-14425]
- USDRT - Add Semantics Schema support [OMPE-14569]
- USDRT - Add support for multiple apply api schema ::Apply [OM-119535]
- USDRT - Add validation to api schema apply functions [OM-119536]
- USDRT - add UsdPrim::GetAllChildren, GetChildrenNames, and GetAllChildrenNames [OM-80310]
- USDRT - OM-123836 add VtArray::cspan
- IFabricHierarchy for standardized transforms with Fabric [OM-96719]
- USDRT - usdrt UsdPrim::HasProperty and GetPropertyNames [OM-98778]


### Fixed
- USDRT - USDRT VtArray pybind cleanup to avoid expensive cast exception when using numpy [OMPE-18960]
- USDRT - Update Usd.AccessType type to int enum in python bindings [OM-104136]
- USDRT - fix GfRange default value to match USD [OM-105217]
- USDRT - Use C++17 inline variable for SdfValueTypeNames instance [OM-121248]
- USDRT - DefinePrim: use provided type in fabric for unregistered schemas [OM-103068]
- USDRT - fix crash creating fabric world matrix attr when it already exists [OM-122386]
- USDRT - fix population and schema apply tagging in fabric for multiple-apply schemas [OM-122248]
- USDRT - Skip prefetch valueless attributes in fabric [OM-117937]
- USDRT - sync schema tags to fabric in UsdNoticeHandler [OM-122248]


### Developer Updates
- USDRT - Move source code and documentation into kit repo. Documentation is now bundled in with kit-sdk (OM-121095, OM-123751)
- USDRT: Get usdGenSchema working in kit repo [OM-121176]

## 7.5.0 2024-02-01

- OM-103434: Add pybind args to SdfPath
- OM-99781: RtChangeTracker added prims
- OM-119110: Add apply to single apply api schemas
- OM-118962: usdGenSchema: Support custom includes, template format tweaks
- OM-118637: Schema custom declaration code

## 7.4.9 2024-01-18

- SceneGraph: Add TfToken::size
- SceneGraph: Add checks for result

## 7.4.8 2024-01-10

- Expose TfToken python conversion
- Added missing header include in Scenegraph API
- Report failure in `RtPath::getPrefixes`
- OM-117847: `Stage::GetAttributeAtPath`: check fabric for attributes not in usd

## 7.4.7 2024-01-04

- Added docstrings to C++ headers

## 7.4.6 2023-12-15

- No changes to USDRT Scenegraph API

## 7.4.5 2023-12-11

- Root prims fall back to USD for relational calls

## 7.4.4 2023-12-10

- Perf fix for IXformCache

## 7.4.3 2023-12-08

- Add pathC property to SdfPath in python bindings
- Use Fabric Connectivity to resolve scenegraph relational calls (GetChildren etc) when FSD is enabled
- Documentation updates
- Add IFabricHierarchy support to Rt schema

## 7.4.2 2023-11-13

- RtXformable will initialize default values for position orientation and scale
- UsdPrim::IsValid returns false if Fabric prim does not exist
- Moving constructor and operator for SdfPath and TfToken

## 7.4.1 2023-11-03

- Added UsdSkel to USDRT Scenegraph API

## 7.4.0 2023-10-16

- Fix includes in SdfPath
- Fix bug in Gf with Decompose
- Add Gf type traits
- Add GfBbox3d GfFrustum GfLine GfLineSeg GfPlane GfRay

## 7.3.6 2023-9-20

- Several fixes for SdfPath implementation

## 7.3.5 2023-9-14

- No changes to USDRT Scenegraph API

## 7.3.4 2023-9-12

- No changes to USDRT Scenegraph API

## 7.3.3 2023-9-6

- No changes to USDRT Scenegraph API

## 7.3.2 2023-8-28

- SdfPath bugfixes

## 7.3.1 2023-8-4

- Adds GfTransform class
- Adds GfMatrix Factor
- Fix GfRange default value in Python

## 7.3.0 2023-8-4

- Adds GfRotation support
- Adds RtSelection class and Stage selection support
- Minor bugfixes

## 7.2.15 2023-7-21

- Gf python string format match USD
- SdfPath prefix bugfix

## 7.2.14 2023-7-14

- Bugfix for UsdAttribute and UsdRelationship GetStage()
- Bugfix in IXformCache to avoid crash on exit

## 7.2.13 2023-7-11

- Improved safety around UsdStage interfaces
- Fixed bug with UsdPrim::GetStage
- Fixed bug with UsdSchemaRegistry::GetAliasFromName
- Fixed bugs with SdfPath APIs added in 7.2.11, made public interface C++14 compliant
- Stage queries can discover prims outside the USD schema registry

## 7.2.12 2023-7-5

- SdfPath now hashable in Python
- API schema calls now support complete name or alias

## 7.2.11 2023-7-3

- Schema class now have static Define method
- Added many SdfPath helper APIs

## 7.2.10 2023-6-23

- Fix hang in IXformCache on shutdown

## 7.2.8 2023-6-13

- Gf types and VtArray support implicit creation from sequences where USD equivalents do

## 7.2.7 2023-6-5

- Adds bool operators for schemas

## 7.2.6 2023-5-31

- Updated testing for invalid prim and attribute calls

## 7.2.5 2023-5-26

- Fix RemovePrim handling

## 7.2.4 2023-5-18

- SdfPathSet and SdfPath cpp tests

## 7.2.3 2023-5-15

- Ensure no crashes when invalid prim in scenegraph API

## 7.2.2 2023-5-11

- No functional changes

## 7.2.1 2023-5-10

- Fix crash on creating attribute on invalid prim

## 7.2.0 2023-5-9

- Add API schema methods on UsdPrim

## 7.1.1 2023-4-25

- Fixes for buffer protocol support

## 7.1.0 2023-4-18

- Validate boolean operator and IsValid for typeless prims
- Adds SchemaRegistry implementation and schema typing support
- DefinePrim always authors Fabric type using alias, and also adds ancestor tags
- Supporting more types when writing usd attributes to fabric
- Add SdfAssetPath support to usdrt
- Ensure that prototype proxies are represented by stage queries

## 7.0.5 2023-3-27

- Both aliases and complete types are now supported for stage queries
- Stage query optimization while Fabric Scene Delegate is active

## 7.0.4 2023-3-22

- No functional changes

## 7.0.3 2023-3-21

- No functional changes

## 7.0.1 2023-3-17

- No functional changes

## 7.0.0 2023-3-12

- Update to USD-22.11

## 6.0.14 2023-3-10

- UsdStage::StageWithHistoryExists pybindings accept long int instead of uint64_t
- GetPathElementCount added to SdfPath

## 6.0.12 2023-2-28

- support GPU interop for 1d warp arrays with VtArray
- add deprecated API support for Fabric rebrand in scenegraph stage
- Only prefetch single attribute for UsdStage::GetAttributeAtPath

## 6.0.11 2023-2-27

- Adds connection support for UsdAttribute
- Fix for flaky tests on Linux

## 6.0.9 2023-2-14

- Fix for warp-0.7.0+ interop with VtArray

## 6.0.8 2023-2-9

- Internal changes in support of Fabric improvements

## 6.0.7 2023-2-2

- Small bugfixes
- Additional documentation
- Improved developer workflow

## 6.0.6 2023-1-29

- Adds stage queries to Scenegraph API
- Adds PyBind bindings for UsdTimeCode in Scenegraph API
- Hide external libraries under usdrt_only subdir so they do not conflict in Kit
- Fixed potential race condition in IXformCache
- UsdStage::RemovePrim will also track the removed for FSD
- Added PruneChildren to Scenegraph API PrimRange iterator
- Fixed bug with UsdPrim::GetChildren Fabric population in Scenegraph API

## 6.0.5 2023-1-12

- Add documentation on authoring geometry with USDRT for FSD
- Add RtBoundable schema
- Fix crash when authoring new geo to Fabric without primvars
- Update documentation to use USDRT schema tokens
- Fix for GetPrimAtPath with Fabric-only prims
- Add RtChangeTracker API

## 6.0.4 2022-12-13

- Fix regression in multi-target Relationship support
- Adds support for API schemas (single and multiple apply)

## 6.0.1 2022-11-21

- Adds Relationship support to schema classes
- Adds multi-target Relationship support

## 6.0.0 2022-11-4

- Added first round of USDRT pin-compatible schema class support
- All Get/Create APIs for concrete schemas are implemented
- Tokens classes for schemas are implemented
- All schemas that ship with USD, and also UsdPhysics and PhysX schemas are represented
- Support for API schemas to follow in subsequent release
- Updated for Fabric rebrand
- Fixed crash with calling UsdStage::WriteToLayer multiple times
- Added CPU/GPU status queries for UsdAttribute

## 5.0.1 2022-10-17

- Changes from 4.0.2 through 4.0.6 (mostly unrelated to Scenegraph API)

## 5.0.0 2022-9-22

- Sync Fabric from Kit for multi-relationship support

## 4.0.3 2022-9-29

**The USDRT Scenegraph ABI is STABLE for Kit-104 with this release**

C++ extensions that are built with the USDRT Scenegraph C++ API using any
4.* extension version will be ABI-compatible with all future releases
of the USDRT Scenegraph extension. Kit-104 will not move beyond the
4.* version of the USDRT Scenegraph API.

- Adds GfRange and GfRect2i support
- `__repr__` for all pybind wrappers
- Sdf.Path can be implicitly created from Python strings to match USD
- Fix for potential crash-on-exit

## 4.0.0 2022-9-5

**The USDRT Scenegraph ABI is STABLE for Kit-104 with this release**

C++ extensions that are built with the USDRT Scenegraph C++ API using any
4.* extension version will be ABI-compatible with all future releases
of the USDRT Sccenegraph extension. Kit-104 will not move beyond the
4.* version of the USDRT Scenegraph API.

- Adds UsdStage::RemovePrim and UsdStage::HasPrimAtPath
- Uses read- and write-specific Fabric APIs for improved change tracking
- Improved error message with Usd.Attribute.Set and Get in Python for unsupported types
- Always prefetch into Fabric on UsdPrim creation
- Adds SdfValueTypeNames->Tag for creating Fabric tags on prims
- __str__ support on SdfPath
- Adds RtXformable schema and documentation
- Prepare for transition to multi-target relationships in Fabric

## 3.0.0 2022-7-13

**The USDRT Scenegraph ABI is NOT stable for this release.**

- Additional RT Scenegraph APIs
  -  UsdPrim::GetChildren
  -  SdfPath::GetAncestorsRange
- Added copy and deepcopy support to Gf Python bindings

## 2.0.0

**The USDRT Scenegraph ABI is NOT stable for this release.**

- Add missing APIs for Quat-related methods on usdrt.Gf.Matrix classes
- Internal cleanup to use Fabric C++ wrappers
- Add repr for VtArray python bindings
- Add GetPseudoRoot to usdrt::UsdStage
- Adds RT Scene Delegate
  - USD->Fabric population plugin
  - UJITSO mesh merging on load
  - Geometry streaming support
  - Viewer updates
  - New USDRT::GfRange3d and python bindings
- Item accessors for Quat and Matrix Pyhon bindings
- Adds vector-type methods for resizing VtArray

## 1.0.1

**The USDRT Scenegraph ABI is NOT stable for this release.**

- Added support for missing Attribute.Get/Set for Quat types in Python
  - Added tests to track remaining outstanding type support
- Fixed Fabric types for Matrix data
- Fixed GetStageReaderWriterId Python bindings
- Added Stage.SetAttributeValue API to Python to shortcut Python overhead
  when setting multiple attribute values

## 1.0.0

**The USDRT Scenegraph ABI is NOT stable for this release.**

- Several new features for `usdrt::VtArray`
  - Python bindings support buffer protocol
  - Python bindings support `__cuda_aray_interface__` for populating
    from GPU sources
  - Safer reads and writes from Fabric data
  - Renamed DetachFromFabric to DetachFromSource to reflect that VtArray may be referencing data
    from a buffer protocol input, a cuda array input, or a Fabric CPU or GPU memory input
- `usdrt::UsdStage::Attach` will create a SimStageWithHistory for a StageId if one does not exist
- Initial support for writeback to USD from USDRT from `usdrt::UsdStage`
  - `WriteToLayer` will write to an arbitrary external layer not in use on the underlying USD Stage
  - `WriteToStage` will write back to the underlying USD Stage
- Update to 1.0.0 version number following reports of issue with `0.*` versions, the
  RT Scenegraph ABI is still considered unstable and subject to breaking changes

## 0.5.1

**The USDRT Scenegraph ABI is NOT stable for this release.**

Initial release of USDRT Scenegraph API for Kit.

This is an early release for experimentation and initial
explorations with production integration.
