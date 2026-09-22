# Changelog
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## 1.12.27 - 2025-10-02
### CHANGED
- Made COCOWriter's output labels respect case-sensitivity.
- Change error in `OgnCameraParamsOpenCV.cpp` to warning to prevent replicator from stopping when renderer is initializing.
- Warn when using `orchestrator.step` or `orchestrator.step_async` in combination with a `GenericModelOutput` annotator (NVBug-5542453)

### FIXED
- Allow sequences to be specified per-prim by providing 2d value arrays (NVBug-5549579)

## 1.12.26 - 2025-09-29
### CHANGED
- Change colorization algorithm in instance, instance id and semantic segmentation annotators to avoid color collision when mapping from id to color.

## 1.12.25 - 2025-09-26
### ADDED
- Add support to correctly output 2D Annotator size when `/rtx/dataWindowNDC` is set. (NVBug-5489669)
- Add `openCVFx` and `openCVFy` camera params support for openCV cameras. (NVBug-5521074)
- Add functional.create lights (distant, sphere, rect, disk, cylinder)

### CHANGED
- Add missing `shaping_cone_softness` argument to functional.create.sphere_light
- Fix extraneous arguments assigned to dome light: remove light shaping, remove pivot

### FIXED
- Fix hang that occurs with Kit 107.3.3 after detaching writers and restoring AsyncRendering
- Fix issue causing semantic filter nodes that failed to detach together with their annotator (NVBug-5508385)
- Fix semantic segmentation returning incorrect results when number of visible instance IDs is constant but the IDs change

## 1.12.24 - 2025-09-08
### FIXED
- Fix Graph node leak when using SemanticFilter on Bounding Box

## 1.12.23 - 2025-09-05
### FIXED
- Fix MDL config type mismatch when using omni.extended.materials, convert tuple config to list
- Improve Semantic class parsing robustess by limitting the params output

## 1.12.22 - 2025-09-05
### FIXED
- Fix error on annotator detach if annotator was previously detached (NVBug-5493371)
- Fix issue where a Writer appending an annotator could mutate annotator lists of another writer (NVBug-5383689)
- Fix `on_final_frame` not called on writers when running in standalone mode (NVBug-5446727)

### ADDED
- Add `OgnSelectSwitch` flow control node that enables selection of inputs node based on condition possible. (NVBug-5429474)

## 1.12.21 - 2025-08-29
### FIXED
- Fix skeleton frame offset issue by moving reading of joint data to post-renderer node. (OMPE-58809)
- Fix issue creating new semantic annotators after destroying a render product (NVBug-5482420)


## 1.12.20 - 2025-08-25
### FIXED
- Fix error raised when calling `scatter_2d` with multiple surfaces with different numbers of polygons
- Fix error calling `functional.modify.visibility` with a list of bools as values
- Fix error in scatter_3d when using extents as bounds where created volume prim is visible
- Fix `io_function` import error observed in some applications

### ADDED
- Enable per-annotator semantic filtering for segmentation annotators (OMPE-28827)

## 1.12.19 - 2025-08-13
### FIXED
- Update `settings.carb_settings` docstring references to point to latest rendering documentation
- Fix bug causing other schemas to be overwritten when adding semantics

### CHANGED
- Change bind material node to use functional implementation

### ADDED
- Add `functional.modify.material`
- Add `material` argument to `functional.create.<cone/plane/sphere/torus/cube>` functions

## 1.12.18 - 2025-08-06
### ADDED
- Add `OgnReadRpFabricTime` that reads render product's fabric time.

### CHANGED
- Change set visibility node to use functional implementation
- Can now write 2 channel exr with channel names are R,G. Previously, only 1 (Y), 3 (RGB), or 4 (RGBA) channels were supported. (DRIVE-24393)
- `functional.randomizer.scatter_2d/scatter_3d` now accept `numpy.random.default_rng()` random number generator as its `rng` argument, and default to a new numpy RNG when not explicitly defined.

## 1.12.17 - 2025-07-17
### FIXED
- Fix bug when applying physics mass and density to multiple prims at the same time.
- Fix bug in `functional.get.prim_at_paths` preventing correct output
- Fix unexpected delta on Root layer on `DispatchSync` node when running Replicator (NVBug-5373106)
- Fix bug when trying to modify float2 and float4 attributes

### ADDED
- Expose SRTX AOVs as annotators (NVBug-5247167)

## 1.12.16 - 2025-07-03
### FIXED
- Fix bug where timeline plays when a writer is attached and timeline is paused (NVBug-5373123)
- Address performance regression where segmentation annotators blocked CPU thread (NVBug-5359615)

## 1.12.15 - 2025-06-26
### FIXED
- Fix bug handling writer annotators defined as NodeConnectionTemplate (NVBug-5359267)

## 1.12.14 - 2025-06-19
### FIXED
- Fix hang when calling `orchestrator.wait_until_complete()` when replicator is already stopped.

## 1.12.13 - 2025-06-18
### FIXED
- Fix error when wait_for_complete() called after all writers detached (NVBug-5347243)
- Fix scatter error when `rng=None`

### CHANGED
- `functional.io_functions.write_exr` now uses a more efficient implementation

## 1.12.12 - 2025-06-16
### FIXED
- Fix menu creation bug causing startup issues in IsaacSim (NVBug-5344576)
- Fix system memory leak that occurred when attaching and detaching writers (NVBug-5319074)

## 1.12.11 - 2025-06-10
### FIXED
- Fix skeleton data inView logic, when one joint is outside the view inView is False
- Fix Replicator menu updates (OMPE-50286)
- WritePrimAttribute updates an Xform attribute if it exists (OMPE-41691)
- Fix bug where scatte2d and scatter3d nodes get initialized with a seed of `0` instead of global seed when seed isn't specified (OMPE-50359)
- Fix bug where writers attached to multiple render products would fail to detach entirely. (OMPE-50439)
- Fix possible infinite loop when calling `orchestrator.wait_until_complete()` (OMPE-48265)
- ShadedSegmentation (used in CosmosWriter) matches segmentation mapping colours when provided (OMPE-50401)
- Fix bug in segmentation annotators that occured when the background was fully occluded and which resulted in missing labels and artifacts in the segmentation output (OMPE-50401)

### CHANGED
- CosmosWriter `instance_segmentation` output changed to `segmentation` to match with Transfer1 nomenclature

## 1.12.10 - 2025-05-29
### FIXED
- Avoid dangling annotators that could occur when detaching a shared annotators before detaching the annotator that depends on it.
- Raise error when attaching a render product to an invalid sensor prim. (OMPE-49873)

## 1.12.9 - 2025-05-27
### FIXED
- Fix issue where a writer attached after the timeline had started would capture every frame even with `capture_on_play=False`. (OMPE-48413)
- DepthSensor annotators make use of the applied schema to enable the depth sensor.

### ADDED
- Add output_dir parameter to Cosmos writer (OMPE-48414)

## 1.12.8 - 2025-05-22
### FIXED
- Fix schema application and attribute creation for omni_radar and omni_lidar sensor creation

### CHANGED
- Rename lidar sensors to `omni_lidar` and radar sensors to `omni_radar` across modules for consistency
- Change `OgnInstanceSegmentation`'s dependency on the Bounding Box 2D data, improving performance.
- Revert `OgnBoundingBox2D`'s support for tiled bbox 2d when multiple tiles view the same prim

## 1.12.7 - 2025-05-16
### FIXED
- Fix `OgnSemanticSegmentation` `outputs:ids` to have 1D array data.
- Fix bug in canny edge augmentation that could cause a crash.
- Fix bug in `CosmosWriter` where the optional mapping was incorrectly applied to segmentation. (OMPE-48417)
- Fix skeleton annotator failure when skeletons are animated with Fabric (OMPE-45895)

## 1.12.6 - 2025-05-14
### ADDED
- Add support for cameras to scatter 2d and 3d randomizers.

### FIXED
- Fix issue where `rep.modify.look_at` applied the incorrect rotation to a camera when its direction is co-linear with a Z-up stage. (OMPE-45290)
- Fix incorrect AOV name for `DepthSensorImager` annotator.
- Ensure CosmosWriter works as expected without an on_time trigger.

### CHANGED
- Add `on_attach_callback` to depth sensor annotators to automatically enable depth sensor settings.
- `annotators.AnnotatorRegistry.register_annotator_from_aov()` now takes a `on_attach_callback` argument.
- Renamed annotator `DepthSensorLeftImager` to `DepthSensorImager`.
- Update node attributes to USD to avoid issues on graph reset (OMPE-37817)

## 1.12.5 - 2025-05-05
### FIXED
- Fix issue where `rep.modify.look_at` applied the incorrect rotation to a camera when its direction is co-linear with a Z-up stage.

## 1.12.4 - 2025-05-04
### CHANGED
- `functional.physics` functions now take `prims` instead of `prim`, allowing for multiple prims to be specified.
- Improve `CosmosWriter` functionality when producing multiple clips.
- Allow `rep.create.render_product` to accept a list of any render vars.

### FIXED
- Fix issue where scatter 3d raise an error if `volume_excl_prims` was unspecified.
- Fix issue applying collider with `sdf` approximation.
- Fix issue where the first frame would fail to be written when attaching a writer on a played timeline. (OMPE-37212)

## 1.12.3 - 2025-04-25
### FIXED
- Fix issue where physics simulate node's `time` attribute could incorrectly be connected. (OMPE-25616)
- Functional `get` module functions returns a list of prims instead of paths.
- `rep.create.render_product` supports passing camera as a prim.
- Fix `rep.utils.sequential` to work with nested sequences, particularly when using `rep.modify.pose`
- Fix type for OmniLidar and OmniRadar creation
- Squeeze warp array annotator output to match numpy squeeze behavior. (OMPE-45288)
- Fix `look_at` to work with cameras when using Z-up axis. (OMPE-45290)
- Fix issue where `rep.orchestrator.step_async()` could incorrectly step the timeline when `capture_on_play=True` (OMPE-45296)

### ADDED
- Add `ColorizeNormals` augmentation
- Add `ColorizeDepth` augmentation
- Add `Sobel` augmentation
- Add `Canny` augmentation
- Add `shaded_instance_segmentation` annotator
- Add `shaded_instance_id_segmentation` annotator
- Add `CosmosWriter` writer (OMREQ-2047)
- Add `rep.settings.get_physx_timestep()` function to get the current physx timestep

### CHANGED
- Switch to new UsdSemantics schema. The legacy Semantics schema remains backwards compatible.

## 1.12.2 - 2025-04-17
### FIXED
- Fix Linux binaries being published in Windows extension

## 1.12.1 - 2025-04-15
### CHANGED
- Use Events 2.0 for orchestrator event handling

### ADDED
- Add support for 6th order fisheye distortion polynomial (DRIVE-22781)
- Add support for 4 depth AOVs: DepthSensorDistance, DepthSensorPointCloudPosition, DepthSensorPointCloudColor, DepthSensorLeftImager
- Add functional `create`
- Add functional `create_batch`
- Add functional `modify`
- Add functional `randomizer`
- Add creation for omni_lidar
- Add creation for omni_radar

## 1.12.0 - 2025-03-19
### CHANGED
- Support for ABI=1

## 1.11.36 - 2025-02-18
### FIXED
- Improve support for Kit 107.0 (OMPE-36502)

## 1.11.35 - 2025-01-16
### FIXED
- Improved performance of `create_prim` for mesh shapes

### CHANGED
- `OgnPerAxisPose` now repeats a single input sample if applied against multiple prims instead of raising an error (ISIM-2414)

## 1.11.34 - 2024-12-30
### CHANGED
- Support per-annotator semanticTypes filtering for bounding box annotators (OMPE-28827)

### FIXED
- Fix issue where orchestrator would incorrectly set totalSPP to `1` when running multiple `orchestrator.run()` loops (OMPE-32546)

## 1.11.33 - 2024-12-12
### FIXED
- `create.projection_material` proxy prims transform changes now update the projected material (OMPE-29525)
- Detaching an annotator that was initialized with `semanticTypes` will restore the global semantic filter (OMPE-28827)

### CHANGED
- `create.render_product_tiled` now supports varying view tile resolutions per render product (OMPE-28778)

## 1.11.32 - 2024-12-11
### ADDED
- Add register from aov support for `GenericModelOutput`. (OMPE-26763)

### FIXED
- Fix issue where `send_og_event()` triggers the `on_custom_event` trigger with a frame delay in standalone mode (OMPE-30430)
- Fix skeleton annotator error when mixing different skeleton topologies in the same scene (METROPERF-524)

### CHANGED
- Change `stageAtTimeInterval` to `stageReaderWriter` in `OgnFabricReader.cpp` to support FSD. This will affect the `Attribute` annotator. (OMPE-26763)
- InstanceID Segmentation annotator now returns IDs when no semantics are applied (OMPE-28530)

## 1.11.31 - 2024-11-22
### FIXED
- Return instance segmentation (instance, instance_id) in correct data format and shape when `colorize=True` (OMPE-27821)
- Support `writer.augment_annotator` when writer annotators are specified as strings (OMPE-29018)

## 1.11.30 - 2024-11-14
### ADDED
- Add `simulate` functionality to simulate physics without rendering
- Add functional physics API (`omni.replicator.core.functional.physics`)

### CHANGED
- Decrease startup time from ~600 ms to ~170 ms (OMPE-25769)
- Move annotator, augmentaton and writer registrations to `on_startup()`

## 1.11.29 - 2024-11-11
### FIXED
- Fix material config setup causing custom material nodes to not be visible (OMPE-20602)

## 1.11.28 - 2024-10-27
### FIXED
- Fix OgnSampleChoicePrim not working when connecting to a downstream node.
- Fix rotation overwriting orientation, causing physics to fail. (OMPE-23079)
- Add rtx::neuraylib::NeurayLib as a carb plugin dependency (OMPE-20602)

## 1.11.27 - 2024-10-20
### FIXED
- Pathtracing only renders one subframe when SPP and TotalSPP are equal.

## 1.11.26 - 2024-10-17
### FIXED
- Fix issue writing entropy node attribute when in Standalone mode (OMPE-25552)

## 1.11.25 - 2024-10-11
### FIXED
- Fix call to refresh Replicator menu (OMPE-23910)
- Fix import of UsdMdl Python modules (OMPE-24952)

## 1.11.24 - 2024-10-04
### FIXED
- Disable non-critical tests from ETM (OMPE-24143)

## 1.11.23 - 2024-10-03
### FIXED
- Reduce test times (OMPE-21639)

## 1.11.22 - 2024-10-01
### FIXED
- Fix crash that could occur when using scatter randomizers with collision checking

### CHANGED
- Orchestrator no longer sets `/rtx/pathtracing/maxSamplesPerLaunch` automatically when specifying high SPP.

## 1.11.21 - 2024-10-01
### FIXED
- Update for compatibility with kit 106.2+ (OMPE-21017, OMPE-21639)
- stage update in collision init causing issues (OMREQ-1314, ISIM-1571)

### CHANGED
- Remove deprecated camera models: (fisheyeOrthographic, fisheyeEquidistant, fisheyeEquisolid)

## 1.11.20 - 2024-09-05
### FIXED
- Fix issue where first frame could fail to return annotated data.
- Fix possible crash in certain scenarios with `PathTracing` render mode (OMPE-18353)
- Fix skeleton annotator issue caused by encountering an unanimated skeleton (METROPERF-294)
- Fix skeleton annotator issue where number of occlusions in output could be inconsistent with number of joints

### ADDED
- Add `mapping` argument to `semantic_segmentation` annotator

### CHANGED
- skeleton_annotator specifies `"N/A"` as the `occlusion_type` when encountering a skeleton without semantics
- `create.render_product_tiled` supports `force_new` argument to force a new render product to be created
- `create.render_product_tiled` supports non-perfect-square number of cameras

## 1.11.19 - 2024-08-23
### ADDED
- Add new `create.render_product_tiled` function for creating tiled render products (replaces `create.tiled_sensor`)

## FIXED
- Add a check to `create.from_usd()` for file existence

## 1.11.18 - 2024-08-19
### FIXED
- Fix missing connection `bufferSize` between instance and semantic segmentation nodes that could lead to a crash (OMPE-18338)

### CHANGED
- Deprecate `omni.sensors.tiled`.
- Support scatter_2d randomizer checking collision with non-leaf prims.

## 1.11.17 - 2024-08-08
### FIXED
- Fix error creating Replicator graph when encountering an unknown omnigraph node in the stage
- Avoid posting of Sdf syntax errors warnings when passing string lists to distribution samplers.
- Fix issue with semantic segmentation and pointcloud annotators when running on Multi-GPU systems
- Updated docstrings for 3d bbox annotator to fix confusion (ISIM-1742)

### ADDED
- Add support for reading skeleton data when using omni.anim.graph animated characters
- Add support for RTX tiled rendering through `create.render_product_tiled`

### CHANGED
- `distribution.sequence` now takes a 'stride' parameter to chunk multiple values per sample

## 1.11.16 - 2024-07-31
### CHANGED
- Removed unused extension dependencies

## 1.11.15 - 2024-07-30
### FIXED
- Restore render settings on replicator stop
- Fix issue where stereo cameras are incorrectly rotated when `rotation` or `look_at`` specified on creation. (METROPERF-353)
- Fix parsing attributes as lists that should be tuples
- Improve performance of CUDA annoators
- Fix slowdown when creating certain graph structures

### CHANGED
- Avoid re-using render product if specified name does not match an existing render product
- Initialization will wait until all assets and materials are loaded before Replicator data generation commences (OMPE-16024)

### ADDED
- Add support for `/exts/omni.kit.hydra_texture/renderProduct/path/prefix` render product prefix setting
- Add `on_time_end` trigger to activate on the last frame of a simulation (OMPE-15811)


## 1.11.14 - 2024-07-18
### FIXED
- Fix issue that can occur with pointcloud annotator with a multi-GPU system (ISIM-1547)

## 1.11.13 - 2024-07-16
### FIXED
- Fix issue where detaching a specific NodeWriter instance would detach all node writers of the same type (ISIM-1538)
- Fix error when applying `randomizer.rotation` on prims with opOrders that don't already include `rotateXYZ` (ISIM-1479)
- Fix bug restricting GPU augmentations from correctly returning a different data type than input
- Fix augmentation error when providing a name that wasn't registered

## 1.11.12 - 2024-07-04
### FIXED
- Fix bug causing error when writing to attributes of dtype=float4
- Fix errow when applying `randomizer.rotation` on prims with opOrders that don't already include `rotateXYZ` (ISIM-1479)

### CHANGED
- Improved pointcloud annotator performance (OMREQ-905)

## 1.11.11 - 2024-06-28
### FIXED
- Address projection material issue (OMPE-12973)
- Fix issue with semantic segmentation not resolving hierarchical semantics more than 1 layer deep
- Fix bug causing instance segmentation to return only background IDs when no semantic prim is visible

### CHANGED
- Improved pointcloud annotator performance (OMREQ-905)
- Improved semantic segmentation annotator performance

## 1.11.10 - 2024-06-25
### CHANGED
- Support Kit 106.0.1

## 1.11.9 - 2024-06-14
### FIXED
- Fix error raised when specifying `rest_offset` and/or `contact_offset` in `physics.rigid_body` and `physics.collider`
- Fix `on_condition` trigger to default to `rt_subframes=1` instead of `16`
- Fix BasicWriter writing to both S3 and local disk when specifying S3 parameters (ISIM-1340)

### ADDED
- Add `rt_subframe` argument to `on_condition` trigger
- Add `backend` argument to BasicWriter to allow optional backends to be passed directly to the writer

### CHANGED
- BasicWriter's `output_dir` argument is optional if a backend is passed in instead
- Improve performance when scenes have many graph nodes.

## 1.11.8 - 2024-05-28
### FIXED
- Fix SPP not accumulate because of fixed clampSpp. (ISIM-1249)
- Avoid endless `step skipped` if stop is hit within a step loop (ISIM-1244)

## 1.11.7 - 2024-05-23
### FIXED
- Better workaround for RTX related crash with tests, tickets ISIM-974, ISIM-1180, ISIM-1206, ISIM-1212, METROPERF-207, OMREQ-907

## 1.11.6 - 2024-05-22
### FIXED
- Added in missing bits to orchestrator.step from step_async that should have been there - these broke standalone ISIM-972 and ISIM-973
- Fix motion blur not working in ray tracing mode. (ISIM-1116)
- Fix SdRenderVarPtr missing valid input renderVar RtxSensorCpu, but test_writers test for it does not work yet (commented) (OM-124604)
- Fix crash caused by setting clampSpp to zero and ensure it is < 416, which also crashes unless /rtx/pathtracing/maxSamplesPerLaunch is very high (OM-1180)

## 1.11.5 - 2024-05-10
### FIXED
- Fix warning showing as error when re-initializing an attached annotator (ISIM-994)
- Fix issue causing crash when creating physics scene during orchestrator.step() in standalone mode (ISIM-950)
- Enable switching from real-time render mode to pathtracing with motion blur during generation (ISIM-972)
- Fix pathtraced motion blur breaking timeline advancement (ISIM-973)
- Fix pathtraced motion blur ignoring SPP setting (ISIM-974)

### ADDED
- Add support for multiple instances of fabric Reader Annotator, where each of them reads different attributes.
- Add `CocoWriter` to output in the MS-COCO format

### CHANGED
- Removed unused backround_rand from `BasicWriter`

## 1.11.4 - 2024-04-29
### FIXED
- Fix rep.randomizer.scatter_2d failing to update surface-prim position (OM-118953)
- Fix rep.randomizer.scatter_3d failing to update volume_prim position (OM-118953)
- Fix issue where multiple `get` nodes are not grouped together when used as inputs to randomizers (OM-123915)
- Disable `/rtx-transient/post/aa/limitedOps` when selecting RT AA mode other than `DLSS` or `DLAA`
- Fix frame not written when `num_frame=1` and `capture_on_play=True` (ISIM-943)
- Fix writers failing to attach when also attaching stand-alone annotators (ISIM-942)

### CHANGED
- ``create.group`` now connects to ReplicatorItem inputs (OM-123915)

### ADDED
- Add ``path_match`` to ``get`` sub-methods to match ``get.prims``

## 1.11.3 - 2024-04-18
### FIXED
- Fix bug in colorize_depth option of BasicWriter
- Fix issue with physics and animation timestep not being in sync (OM-121967)
- Fix issue with setting timeline when render mode is not pathtracing and we have motion blur, update test to reflect it (OM-122147)

### CHANGED
- ``rt_subframe`` values now take effect for any render mode.
- `camera` and `resolution` default metadata values from `OgnWriter` moved to `<render product>: {camera: ..., resolution: ...}`
  and `"camera": <render product>: ...`, `"resolution": <render product>: ...` for dataStructure modes `renderProduct` and
  `annotator`, respectively.
- Annotator `.attach()` method will raise an error if attempting to initialize an annotator with multiple render products. (OM-120713)

### ADDED
- Add `semantics` to rep.randomizer.instantiate (OM-56048)
- Add annotator to allow user to read custom data from fabric. (DRIVE-11414)
- Add user warning when specified delta time is greater than the physx timestep, and added setting to let the user alter this


## 1.11.2 - 2024-04-12
### FIXED
- Fix endpoint_url key in S3 backend
- Fix bucket creation in S3 backend
- Fix scatter crash upon upgrade to kit 106 caused by using wrong cpp API call
- Fix bug in glass blur causing flaky test
- Fix orchestrator incorrectly stepping timeline on step if `pause_timeline=True` (OM-117977)
- Fix bug in `AdjustSigmoid` augmentation
- Fix physx error when try to apply rigid body api on prim which has child prim that already has a rigid body api. (OM-84462)
- Fix issue with annotator failure if render product is toggled off after annotator is attached (OM-121249)
- Fix bug in look_at when passing in distributions of coordinates

### ADDED
- Add `mapping_dict` to KittiWriter to take a Python dictionary of `label:color` mappings
- Add `data_structure` attribute to `rep.writers.Writer` base class
- Add `use_legacy_structure` argument to `rep.Annotator.get_data`
- Add `use_common_output_dir` argument to `BasicWriter` (OM-92619)
- Add `colorize_depth` parameter to `BasicWriter`

### CHANGED
- Update docstring for `get_annotator()` method
- Modify `BasicWriter`` data structure to use new `annotator` data structure
- Update LookAt node to remove obsolete `targetPrimPath` input

## 1.11.1 - 2024-02-29
### FIXED
- Fix modify.semantics `mode` input not set when `semantics` is a `ReplicatorItem``
- Fix setting sequential value when connected to a non-list input
- Fix modify.material modifying multiple prims with a sampled material distribution
- Fix BindMaterial node to correctly modify prims with material per prim
- Fix randomizer.materials to avoid duplicating materials when defined using MDL paths
- Fix `create.render_product` error after updating kit. (OM-120321)

### CHANGED
- randomizer.materials now takes a `max_cached_materials` to limit number of cached materials stored in the scene.
- Update to Kit 106.0 Release (formerly 105.2)

### ADDED
- Add RGB output support for tiled sensor.
- Add `delta_time` in `step/step_async` in `orchestrator.py` to control the step size of timeline when motion blur is enabled in path tracing mode. (OM-119511)
- Add `/omni/replicator/pathTracedMotionBlurSubSamples` to modify the number of sub samples to render when motion blur is enabled in path tracing mode. (OM-119511)
- Add support for modifying annotator node's attributes even if it has been activated. (OM-119779)
- Added a name parameter to methods that create an OmniGraph node

## 1.11.0 - 2024-01-22
### CHANGED
- Update to Kit 105.2

### ADDED
- Add `create.tiled_renderer_sensor` to support tiled RTX Sensor.
- Add `RtxSensorGpu` and `RtxSensorCpu` annotator that output data from tiled RTX Sensor.
- Add rep.open_stage() method to open a new stage
- Add mesh decal creation using Warp (OM-83118)

## 1.10.20 - 2023-12-14
### FIXED
- Don't evaluate orchestrator graphs if they don't exist

## 1.10.19 - 2023-12-14
### FIXED
- Fix orchestrator graph failing to be found

## 1.10.18 - 2023-12-14
### FIXED
- Fix incorrect id_to_labels for semantic segmentation when there is no prim in the scene. (OM-116911)
- Fix S3 compatibility of BasicWriter and KittiWriter (OM-116532)
- Restore DiskBackend default to overwrite existing directories (``overwrite=True``)
- Prevent orchestrator from evaluating non-replicator graphs

### CHANGED
- Backends can be initialized with `.initialize(...)` or `.get(<name>, init_params={...})`
- BackendGroup is registered as a default backend, enabling multiple backends to be grouped together

## 1.10.17 - 2023-12-07
### FIXED
- Fix incorrect buffersize reported by pointcloud annotator under Windows
- Fix `io_funcions.write_np` error when passing in warp data (OM-116596)

## 1.10.16 - 2023-12-07
### FIXED
- Protect against graph reset clearing annotator device attribute causing data retrieval error (OM-116164)

## 1.10.15 - 2023-12-06
### FIXED
- Fix `pointcloud` annotator semgmentation output returning as incorrect datatype (OM-115434)

## 1.10.14 - 2023-12-05
### FIXED
- Fix array datatype reduced to 1 when width and height are both 1 (OM-116189)

## 1.10.13 - 2023-12-05
### FIXED
- Return support for dynamically changing render product resolution
- Fix incorrect array shape when format is unspecified and array height == 1 (OM-116189)

## 1.10.12 - 2023-12-01
### CHANGED
- /Replicator/Orchestrator graph moved to /Orchestrator in the session layer (OM-107606)
- Default writer scheduling graphs moved to session layer (OM-107606)
- Revert python directory structure for backward compatibility.

### FIXED
- Fix error raised when attaching writer in the context of another layer (OM-107606)
- Fix issue when creating randomization graph in certain situation resulting in deltas occurring in the SessionLayer (OM-107877)

## 1.10.11 - 2023-11-30
### CHANGED
- Scene instance + reference sampling for scatter nodes 40% faster
- Point instance sampling for scatter nodes 70% faster
- No-collision prims extra arg in scatter now accepts point and scene instances
- Fast voxel sampling visualization in scatter3d
- Move node `OgnCount` to C++ for better performance
- Exposed sample population custom name argument (OM-112221)
- Extend list of valid item types for `randomizer.instantiate` `path` argument
- Replicator graph changed to SIMULATION

### FIXED
- Fix typo in OgnSamplePopulation node (OM-112221)
- Fix how some usda files have set translate from issue with incompatible xformable in scatter nodes (OM-103181)
- Fix incorrect element count of returned arrays when using certain resolutions with DirectX (Windows) (OM-113849)
- Fix bug affecting determinism of OgnSamplePopulation (rep.randomizer.instantiate) node
- Fix error raised on annotators returning an array of size 1 (OM-114654)
- Fix trigger argument not being passed to attach_async for writers
- Fix endless scroll issue in script editor (OM-114249)
- Fix error raised on annotators returning an array of size 1
- Fix user being able to name prims with invalid Usd names (OM-115472)
- Fix Replicator failing to restart after `num_frames` has been reached (OM-112257)
- Fix instantiate node failing to create populations when populated by prims
- Fix crash on Preview in certain scenarios (OM-104917)

## 1.10.10 - 2023-10-04
### CHANGED
- Revert projection material offset vertices calculation for correctness at the cost of performance
- `db.outputs.exec` is set to `og.ExecutionAttributeState.ENABLED` for some nodes if the input is empty to prevent downstream node from stopping running. (OM-111243)

### FIXED
- Fix missing first frame when `on_time` trigger used together with `/omni/replicator/RTSubframes` set to > 1
- Fix issue resulting in numpy data buffer potentially being overwritten before dispatcher write when using a CPU device annotator (OM-111243)

## 1.10.9 - 2023-09-27
### FIXED
- Fix bug when retrieving multiple annotator arrays of differing and unspecified shapes

## 1.10.8 - 2023-09-26
### FIXED
- Fix error reporting annotator attributes with `Data` suffix

## 1.10.7 - 2023-09-25
### FIXED
- Fix error when using `Type` annotator attribute output (OM-110164)
- Fix typo causing `<anno>Width` to be unused
- Fix error raised when dispatch sync gate is not connected to downstream node (OM-110166)
- Fix bug which could result in invalid annotator parameters being cached
- Fix crash due to incorrect cuda buffer shape when using single channel arrays
- Fix extra axis in output array shape when retrieving warp arrays
- Fix error retrieving annotator parameters with certain AOVs
- Fix custom render product name when stereo cameras are attached.
- Fix bug causing writers to fail to reattach to more than one render product after being detached
- Fix bug with warp augmentations with 2D output arrays calculating incorrect kernel dimensions

### CHANGED
- AugmentCPU data input/output can support additional array datatypes
- Support `paths` arg of type `ReplicatorItem` which has output type `target` to `randomizer.instantiate`.

## 1.10.6 - 2023-09-20
### FIXED
- Fix incorrect RefTime annotator denominator value (OM-106926)

## 1.10.5 - 2023-09-20
### ADDED
- Add create.xform & cleaned-up _create_prim method
- Add `get_annotators`, `get_annotator`, `add_annotator`, `augment_annotator` methods to `Writer` class. (OM-97635)
- Add `name` argument to augmentation functions to specify augmented annotator name.
- Add capability for annotators to output multiple `Ptr` type arrays

### FIXED
- Fix orchestrator typo (omni.kit.app.get_app().next_update() to omni.kit.app.get_app().update())
- Fix incorrect `GlassBlur` augmentation
- Fix identical semantics being applied to prims multiple times (OM-108397)
- Fix automatic attribute creation when calling modify.attribute with a datatype if the input prim is a material (OM-108408)
- Fix missing first frame when attaching a writer to replicator when already in `STARTED` mode. (OM-109114)
- Fix broken attribute_mappings when specifying a node annotator
- Fix return type in function signature of `register_annotator_from_node` (OM-105208)
- Fix error raised when detaching writers tied to multiple render products in certain scenarios (OM-108036)

### CHANGED
- Warp augmentation now maintain source AOV data on the GPU to improve performance
- Register default augmentations
- `modify.visibility` can now take a single bool and apply it to multiple meshes
- Augmented annotators now take the source annotator's name by default. (OM-97635)
- Cache annotator params that change infrequently when retrieving data for better performance

## 1.10.4 - 2023-08-30
### ADDED
- Add `ReferenceTime` annotator that provides the time corresponding with the render and associated annotators.
- Add `pointInstance` to `info` of the pointcloud annotator with instance segmentation array, to be alongside `pointSemantic`, a semantic segmentation array.

### FIXED
- Fix bug in RefTimeGate that could result in a crash
- Fix broken KittiWriter instance segmentation colorize option (OM-106180)

### CHANGED
- `create.render_product()` no longer re-uses render products assigned to the `/OmniverseKit_Persp` camera. (OM-107105)
- `create.render_product()` will set `force_new=True` when naming a new render product

## 1.10.3 - 2023-08-29
### ADDED
- Add `parent` parameter to prim creation
- Add `create.xform`

## 1.10.3 - 2023-08-29
### FIXED
- Fix standalone orchestrator calls (`wait_until_complete`, `start`, `initialize`) (OM-105046)
- Fix `num_frames` argument being incorrectly reset on scenario restart (OM-105046)
- Fix validation of synchronous orchestrator functions to prevent calling them from within Kit
- Fix KittiWriter semantic segmentation writing when using multiple render products.
- Fix `wait_until_complete` and `wait_until_complete_async` incorrectly stopping a playing timeline (OM-105032, OM-105046, OM-103399)
- Fix validation of synchronous orchestrator functions to prevent calling them from within Kit
- Fix `<writer>.trigger()` call to schedule current simulation frame rather than write current writer payload (OM-105077)
- Fix `step_async(rt_subframe)` getting overwritten by subframe input of replicator triggers (OM-107103)

### CHANGED
- When calling `rep.create.render_product`, if the input cameras are a stereo camera pair, the render product name will have a `L` or `R` suffix.
- `wait_until_complete` and `wait_until_complete_async` no longer stop replicator (OM-105032, OM-105046)
- Change `<writer>.trigger()` to `<writer>.schedule_write` for better clarify of function.
- Change `rep.writer.get()` to take `render_products` and `trigger` arguments for convenience.
- Disallow parenting to gprims

## 1.10.2 - 2023-08-12
### FIXED
- Update WritePrimAttributes node to automatically add `inputs:` prefix when required.

## 1.10.1 - 2023-08-08
### ADDED
- Add `rep.modify.variant` for modifying prims variants (OM-102987)
- Add `modify.pose_orbit` function to position objects in terms of orbits around a point. This is particularly useful
    for positioning cameras.
### FIXED
- Fix annotators and writers not capturing data if attached on a playing scene with `Capture On Play` enabled
### CHANGED
- `rep.create.render_product` now returns a `HydraTexture` object which can be destroyed using `.destroy()`. `.path` will return the prim path per previous behaviour. (OM-87164)

## 1.10.0 - 2023-07-31
### FIXED
- Fix for `OgnPerAxisPose`, where same value will apply to all prims inside a group using a `distribution` node. (OM-97739)
- Replicator will not run if no replicator component exists in the scene
- Fix support for ReplicatorItem objects as input to `rep.modify.semantics`
- Fix bug in `rep.modify.material` when randomizing across materials
- Fix bug in camera relative node when using certain camera paths
- Improve `rep.settings` documentation
- Improve performance by removing `commands` calls that decreased performance over time
- Fix crash on MGPU systems when AOVs are assigned to device > 0 and using AOV annotators
- Fix global_translations data error in skeleton_data annotator (DHS-372)
- Fix occlusion index out of range error (OM-89639)
- Fixed URLs for Documentation
- Fix `OgnWritePrimAttribute`, where bool type is wrapped by numpy. (OM-102647)
- Fix `create.stereo_camera` where if the stage's up axis is Z axis, the two camreas will be created along the X axis. (OM-100414)
- Fix issue where `create.stereo_camera`'s `look_at` does not work if the up axis is Z.

### CHANGED
- OnFrame trigger subframe attribute changed from `rt_subframes` to `rtSubframes` for consistency
- OnTime trigger subframe attribute changed from `rt_subframes` to `rtSubframes` for consistency
- Adding a rigid body (`rep.physics.rigid_body`) no longer sets timeline to `play`
- Samples per pixels (spp) no longer set to 1 on replicator start unless `/omni/replicator/captureMotionBlur` is set to `True`
- Timeline is no longer controlled by replicator during replicator start unless `/omni/replicator/captureMotionBlur` is set to `True`
- Deprecate `pause_timeline` argument from `step` and `step_async` functions, timeline is no longer paused by default on step.
- `rep.modify.projection_material` now supports non-mesh prims and assets composed for multiple meshes.
- `rep.randomizer.scatter_2d` now supports non-mesh prims as surface prims.
- `SampleOmniPBR` now automatically disables scene instances in order to correctly propagate material assignments.
- `rep.trigger.on_frame` argument `num_frames` will be deprecated. It is now replaced with `max_execs` for consistency and clarity.
- `rep.trigger.on_time` argument `num` will be deprecated. It is now replaced with `max_execs` for consistency and clarity.
- `create.render_product` now takes a `name` argument enabling custom names of new Render Products (OM-87165)
- `rep.modify.projection_material` now takes a `texture_group` argument to handle randomized groups of material types. (OM-101053)

### ADDED
- Add `/omni/replicator/captureMotionBlur` bool flag to control whether to capture motion blur (both RealTime and PathTracing modes supported)
- Add `reset_physics` argument to `OnTime` trigger to control whether to restart physics simulation on trigger activation
- Add exposed metallic argument when modifying projection material
- Add some usage telemetry (OM-94206)
- Add `/omni/replicator/asyncRendering` setting to enable async rendering during replicator start
- Add trigger.on_condition trigger which can be activated by evaluating a python function (OM-95126)
- Add `modifier` argument to `rep.trigger.on_key_press` to allow combining keys with modifiers.
- `rep.modify.semantics` now takes a `mode` argument allowing adding to, replacing or clearing existing semantics. Defaults to `add`.
- Add `trigger` argument to writer attach method. Writers will by default continue to be activated by an on-frame trigger
    but can now also be triggered by any trigger or condition (ie. a Python function returning a bool) (OM-95127)
- Support specifying device index (eg. "cuda:1") when initializing an AOV annotator such as `LdrColor`
- Add a new argument `fn_name` in `randomizer.register` to allow user to custom registered function name. (OM-100409)
- Add a `get_file_group` utility to get groups of files based on the suffixes and group by the prefix (OM-101053)

## 1.9.8 - 2023-06-07
### FIXED
- Increase scheduling robustness for nodes depending on multiple upstream prims (OM-61696)
- Fix named outputs missing from payload

### CHANGED
- Compute GetPrims and GetPrimAtPath nodes on attribute change
- Refactored projection material node functionality (OM-95568)

## 1.9.7 - 2023-06-01
### FIXED
- Improve documentation
- Fix incorrect occlusion values reported when a labelled asset has multiple unlabelled or semantically filtered child prims.
- Fix issue where point instancer selects new prototypes as they're pulled from cache
- Fix AOV lifetime bug which resulted in incorrect frame data written to disk in certain circumstances (OM-95907)
- Fix material binding in OgnMaterialSampler failing on first frame
- Fix incorrect autograph connection when using OgnGetPrimAtPath
- Fix issue correctly scheduling nodes with multiple ReplicatorItem connections
- Fix scheduling issue when using Sdf Paths as attribute inputs (OM-61696)

### CHANGED
- Switch from `bundle` to `target` attribute type for all prim relationship node attributes
- Remove warmup period (ie. preview frames) on first Replicator step (OM-96084)
- Reset RNG on replicator `initialize` command rather than on `start` for better reliability
- `distribution.sequence` and `distribution.choice` now support sampling from [`Sdf.Path`, `Usd.Prim`, `ReplicatorItem`] (OM-61696)

### ADDED
- ReplicatorItem class provides additional methods: get_inputs, get_outputs, get_input_value, get_output_value
    and set_input_value which provides an easier way with which to retrieve and modify node values. (OM-94465)
- Add `get_registered_annotators` to `annotators` module and `AnnotatorRegistry` class that exposes available annotators (OM-94465)
- Add documentation to each default annotator, accessible through `rep.annotators.get(<annotator_name>).docs` (OM-94465)
- Add convenience methods to `ReplicatorItem` class: `get_prims`, `get_input`, `get_output`, `get_inputs`, `get_outputs`, `set_input` (OM-94465, OM-62718)
- Add `OgnSampleChoicePrim` and `OgnSampleSequencePrim` for sampling prims (OM-61696)

## 1.9.6 - 2023-05-15
### FIXED
- Fix warp error when data array is empty.
- `instantiate` with mode `point_instancer` no longer re-generates prototypes unnecessarily (OM-94390)
- Fix issue with skeleton data output handling empty data (OM-83739)
### CHANGED
- Remove the pip dependencies to use `omni.pip.compute` extension.

## 1.9.5 - 2023-05-05
### FIXED
- Fix "apply material" warnings
- Fix crash printing from OmniGraph (OM-93494)

## 1.9.4 - 2023-05-02
### FIXED
- Fix bug in cutmix augmentation node caused by using warp 0.8.2 on ETM (previously only tested 0.7.2). Updated code so works on both.
### CHANGED
- No longer specify exact warp version in extcache.kit

## 1.9.3 - 2023-05-01
### FIXED
- Fix a bug in `orchestrator.py`'s `step` function.
- Fix bug in scatter2d where it used local vertex transform for offset normal computation as well as for pruning bounds. now it is global and both are fixed.
- Fix bug in scatter3d where sometimes the triangle mesh extended over the newly partitioned voxel space.
### ADDED
- Add 360 degree bounding box annotator (DRIVE-11803)

## 1.9.2 - 2023-04-26
### ADDED
- Add annotator type to the basic writer so augmented rgb images could be saved (OM-89827)
- Add Replicator MDLs and register them in material preferences (OM-87755)
- Add projection material to objects and update via proxy prims (OM-88170)
- Can now specify additional prims to scatter nodes that contain meshes to prevent collisions with (OM-89697, OM-76055)
- Add 8 tests for no_coll_prims feature for both variants of prim type (point instance/scene instance), collision true/false, and node type (2D/3D). (OM-89697, OM-76055)
- Update voxelization method for Scatter3D node to cast voxels in global space to prevent double sampling up upon overlap - preventing is default but the user can switch it off (OM-90830)
- Add test for Scatter3D to confirm that there is no doubling up upon overlap (OM-90830)
- Add a feature for specifying volume exclusion based on prims in (Scatter3D only) - volume_excl_prims. This is more sample efficient but less accurate. (OM-90948, OM-76055)
- Add test for volume_excl_prims feature. (OM-90948, OM-76055)
- Add min and max sampling extents for scatter nodes implemented with rejection sampling (OM-85756 and OM-85757)
- Add efficient pruning of triangle meshes based (Scatter2D) and efficient pruning of voxel grids (Scatter3D) for sample extents. Does so conservatively and rejection sampling cleans up the rest (OM-85756 and OM-85757)
- Add tests for min and max sampling extents in scatter nodes (OM-85756 and OM-85757)
- Add S3 backend to KITTI writer (OM-90092)
### CHANGED
- Remove `OgnGroup` node since it is replaced by `omni.graph.nodes.ReadPrimsBundle`.
### FIXED
- Experimental replicator data augmentation nodes had random numpy seed set improperly (OM-89827)
- Some instances of `create.from_usd` resulted in transform not being set properly, cleared xoporder to fix bug (OM-89583)
- Fix `get.prims` and `get.prim_at_path`'s nodes are not scheduled properly. (OM-92211)

## 1.9.1 - 2023-04-21
- DriveSim only release

## 1.9.0 - 2023-04-12
### ADDED
- Add function to create MDL graphs from JSON (OM-79358)
- Add `orchestrator.register_status_callback` to allow registering callbacks on orchestrator status changed (OM-77512)
### CHANGED
- Migrate to Kit 105.0 (OM-89289)
- Changed `swhFrameNumber` to use `simTimeNumerator` and `simTimeDenominator` (OM-89289)
### FIXED
- Fix incorrect KITTI semantic segmentation directory name.
- Improve KITTI writer to better match spec.

## 1.8.1 - 2023-03-24
### ADDED
- `rep.randomizer.materials` can now take a list of materials created by Replicator (OM-79560)

## 1.8.0 - 2023-03-22
### ADDED
- Add `path_match` to `get.prims()` for faster string matching
- Add OgnWriter output of all named node attributes through `data["named_outputs"]` (OM-82915)
- Add support for OnFrame trigger through `data["trigger_outputs"]` (OM-82915)
- Capability in `OgnAugment.py` to register warp kernels as nodes that have input 1D and 2D arrays (besides just 3D) (OM-90135)
- 9 ogn/py data augmentation nodes flagged "Exp" for experimental - we will move these to less cumbersom functions later (OM-90135)
- 7 data augmentation nodes implemented as warp kernels in `augmentations_default.py` (OM-90135)
- `wp_utils.py` file that has warp utility functions in it - currently for importing filler images for augmentation nodes and zooming to size (OM-90135)
- Tests for all data augmentation nodes. Tests check if image data can be passed to and output from the nodes. (OM-90135)
- A few images used in data augmentation tests (OM-90135)
- Add `write_exr` to `dispatcher.py` and corresponding backends. (OM-84024)

### FIXED
- Fix bug forcing getting children of Xforms when sampling materials (OM-83611)

## 1.7.12 - 2023-03-08
### FIXED
- Fix PathTracing sample accumulation bug when CaptureOnPlay is turned on

## 1.7.11 - 2023-03-07
### FIXED
- Ensure annotator attributes remain on session layer (OM-85212)
- Correctly catch `/omni/replicator/captureOnPlay` setting on startup (OM-85259)

## 1.7.10 - 2023-03-07
### FIXED
- Fix incorrect KITTI semantic segmentation directory name

## 1.7.9 - 2023-03-06
### CHANGED
- Change KITTI writer to output semantic segmentation consistent with spec: 8-bit image containing per-pixel semantic ID
- Change KITTI writer to offer `use_kitti_dir_names` option to use standard KITTI directory naming structure
- Disable Replicator when timeline playing by default (OM-77526)
- Replicator capture controlled by timeline controls when set to `capture_on_play` (OM-77526)

## 1.7.8 - 2023-02-28
### FIXED
- Fix replicator bug when using Movie Capture together with a playing timeline (OM-83863)

## 1.7.7 - 2023-02-27
### FIXED
- Fix KittiWriter's instance segmentation output format to align with KITTI specs
- Fix KittiWriter sky labelling
- Fix skeleton data errors when no semantically labelled skeleton is in the scene (OM-83739)
- Fix skeleton data output to have correct data shape for translations and rotations

### CHANGED
- Handle spaces in semantic values (spaces in semantic types remain disallowed)
- Change backend write threads setting to `"/omni/replicator/backend/writeThreads"` (OM-77793)
- Allow control of maximum backend queue size with `"/omni/replicator/backend/queueSize"` (OM-77793)
- Orchestrator status will now only read `STOPPED` when all rendering and writing has completed (OM-82465)

## 1.7.6 - 2023-02-16
### FIXED
- Fix `pointcloud` annotator outputting incorrect data when one unlabelled prim and one labelled prim are in the scene. (OM-81230)
- Fix `contactOffset` and `collisionOffset` increases as the `MetersPerUnit` of the scene increases. (OM-73794)
- Fix issue preventing RGB from writing data with skeleton_data enabled and no skeletons in stage. (OM-75395)
- Address error raised when modifying pose of a prim containing a `transform` or `orient` xformOp/ (OM-81273)

### ADDED
- Add `includeUnlabelled` attribute to `pointcloud` annotator to allow user to capture unlabelled prims. (OM-81230)
- Add `modify.material` functionality (OM-79552)

## 1.7.5 - 2023-02-13
### FIXED
- Fix issue preventing detaching node writers (OM-80503)

### CHANGED
- Changed `skeleton_data` output from single output JSON (deprecated) to individual outputs. (OM-77982)

## 1.7.4 - 2023-02-09
### FIXED
- Fix node execution scheduling when depending on OgnSamplePopulation (instance) node (OM-61629)
- Ensure distribution.sequence node is reset on replicator start (OM-79831)
- Fix CUDA error crash when running the example in Custom Writer Tutorial.
- Remove dependency on `omni.kit.widget.viewport` when using Viewport 2.0
- Fix error creating render products when `/Render` prim doesn't exist
- Fix node execution scheduling when a node is depending on the upstream node by attribute.

## 1.7.3 - 2023-02-06
### FIXED
- Fix `_add_auto_sync_gate` where it doesn't apply recursively to all upstream nodes before. (OM-80757)
- Ensure visualizers are always available (OM-78426)
- Fix `on_final_frame` being fired before all data is written (OM-80252)

### ADDED
- Add `modify.animation` functionality (OM-80095)
- Add `get.skelanimation`
- Add `get.skeleton`
- Add `wait_until_complete` and `wait_until_complete_async` functions (OM-79660)

## 1.7.2 - 2023-02-01
### ADDED
- Add `fisheyeKannalaBrandtK3` and `fisheyeRadTanThinPrism` as new camera types. (OM-74691)
- Add support for per axis randomization of position and rotation. (OM-62719)
- Add an argument to `orchestrator.run` to optionally start the timeline (OM-80096)

### FIXED
- Fix joint projection when using pinhole camera (OM-77757)
- Fix setting the correct resolved type of `physics.colliders`. (OM-76074)
- Pass `num_frames` argument in `run_async` function. (OM-79750)

## 1.7.1 - 2023-01-19
### FIXED
- Fix orchestrator hang when scene FPS is set to 0.0 (OM-77223)
- Fix orchestrator stepping time when timeline is not playing
- Fix orchestrator double step through timeline in certain setups (OM-77526)

## 1.7.0 - 2023-01-17
### FIXED
- Fix `occlusionRatio` data in `bounding_box` annotator. (OM-77094)
- Fix bug that broke collision checking in scatter2d
- Fix index of geomsubset in test_geomsubset to reflect ordering in Kit 104.2+release.30.e51bf939
- Fix nodes handling uninitialized state better. (OM-73680)
- Fix checking `inputs:numSamples` attribute exists before accessing it. (OM-73680)

### ADDED
- Add async versions of common functions: `run_async`, `stop_async`, `preview_async`, `writer.attach_async` (OM-73566)
- Add fast collision method for point instances in scatter2d and scatter3d nodes
- Add option of using skelJoints after retargetting for skeleton joints info (OM-72731)
- Add `num_frames` argument to `orchestrator.run()` to specify maximum number of frames to capture (OM-73565)

## 1.6.4 - 2022-12-14
### FIXED
- Fix `distribution.combine` where input is a numerical value (OM-76074).
- Fix physics properties failing to be set to a static value for more than one prim
- Fix error when detaching a writer that contains an annotator defined as a NodeConnectionTemplate

### CHANGED
- Re-use render products created under `with rep.new_layer()` on script re-run (OM-52410)
- Added argument to orchestrator.step to let user specify if it should pause timeline

## 1.6.3 - 2022-12-13
### FIXED
- Fix an issue where cached assets would be added under the same parent Xform (OM-52410)

## 1.6.2 - 2022-12-12
### FIXED
- Add `InstanceSegmentationLegacy` and `InstanceIdSegmentationLegacy` nodes to keep backward compatibility.
- Pause playing simulation during RT Subframe rendering
- Disable FrameGate while simulation is playing (capture every frame)
- Writer and gates now correctly authored in session layer
- Auto connect execution attributes of augmentation nodes
- Fix issues with reattaching writer (OM-65028)
- Fixed point and scene instancer bugs -- now they work for use with instantiate, scatter2d, and scatter3d. Scene instancers work with fast collision in scatter nodes.
- Fix bug where node attribute `__device` may be applied twice
- Fix omnigraph category warnings on startup

### ADDED
- Add `_unregister_status_callback` to cleanly unregister callbacks

### CHANGED
- Instantiate cached assets no longer set to instanceable

## 1.6.1 - 2022-12-06
### FIXED
- Fix bug in semantic segmentation annotator that could lead to a crash
- Fix typo error that computes wrong bbox 2D area in `kitti.py`.
- Fix `contactOffset` and `restOffset` when `meters_per_unit` is too small, resulting inaccurate physics behavior.
- Fix `uniform`, `log_uniform` and `normal` distribution nodes to support save/reload functionality.
- Fix bug when specifying render product indices during writer initialization that resulted in incorrect node connections

### ADDED
- Add `contact_offset` and `rest_offset` as optional args to `physics.collider` and `physics.rigid_body`.
- Add ability to use "cuda" device when getting an annotator
- Add `HdrColor` annotator

### CHANGED
- Improve speed of collision checking for Scatter3D by 20X+
- Improve performance when annotator data remains on the GPU

## 1.6.0 - 2022-11-21
### ADDED
- Add a way to modify timeline by frame or time (OM-54198)
- Add `ReplicatorItem` support for `num_samples` input in `uniform`, `log_uniform` and `normal` distribution nodes.
- Add `ordered` arg to `sequence` distribution node to allow sample items with or without order.
- Add `numSamples` output attribute to distribution nodes.
- Add occlusion output along with the `BoundingBoxAnnotator` when labelled asset is composed of a single mesh.
- Add Augmentation class, allowing custom augmentations to be applied to annotators

### FIXED
- Fix issue whereby operations reused across triggers were reassigned rather than copied to the new trigger
- Fix rep.randomizer.colors to correctly treat lists of colors as input
- Fix function call in SkeletonData node causing `Ill-Formed Sdf.Path` warnings
- Fix `xformOpOrder` enforcement in `OgnWritePrimAttribute`.
- Fix check for visibility attribute before applying (OM-72567)
- Fix function calls in SkeletonData node causing `Ill-Formed Sdf.Path` warnings (OM-67752)
- Fix randomization with point instancers (OM-72137)
- Fix `distribution.combine`'s num_samples when connect to a downstream node.
- Fix `OgnWritePhysics` when passing a single static input value.
- Fix `get_type` in `OgnWritePrimAttribute` to be align with `Sdf`'s API.
- Fix `population` when path is a `Sdf.Path`.
- Fix `OgnSizeToScale` when input prim list is empty.
- Fix bug where annotators could be linked to additional render products when specifying render product indices (OM-75216)

### CHANGED
- Improve performance of Bounding Box Annotator node
- Improve performance of instance id segmentation annotator
- Improve performance of instance segmentation annotator
- Provide additional output parameters to CameraParams annotator including focal length and aperture
- Remove concept of a WriterTemplate class and replace with an expanded Writer class

## 1.5.3 - 2022-11-06
### ADDED
- Add helper methods to replicator.get for different Usd types
- Add ability to render `N` subframes to remove artifacts in RTX RealTime render mode (OM-70205)
- Add support for list of `Sdf.Path` as input to `choice` distribution node (OM-61287)

### FIXED
- Fix error in Semantic Segmentation annotator when scene is empty (OM-70189)
- Fix broken `input_prims` parameters in modify operations (OM-67555)
- Fix inconsistent look-at sequencing when combined with other operations (OM-67554, OM-61293)
- Fix error in `create.camera` when `count > 1` (OM-57265)
- Fix issue with `OgnSetPivot` when setting the pivot on prims with origin non-centred. （OM-64820）
- Fix skeleton annotations working again with fisheye_polynomial camera type (OM-67834)
- Fix skeleton annotations match animated skeletons (OM-67834)
- Fix getting attached writer/writers (OM-70733)

### CHANGED
- get.prims now takes flag for case-insensitivity in path matching
- Add flag for case-insensitivity in get.prims path matching
- Add 'name' argument to `rep.create` methods
- `randomizer.instantiate` changed to utilize `distribution.choice` node for default sampler
- Better skeleton "in_view" check (OM-67834)

## 1.5.2 - 2022-10-17
### FIXED
- Catch exception in skeleton joint 2D translations when view matrix is zero

## 1.5.1 - 2022-10-11
### ADDED
- Allow custom endpoint URLs for S3 backend

## 1.5.0 - 2022-10-11
### ADDED
- Compatibility with Kit 104+
- Documentation for missing module members
- Add `get.prim_at_path` function
### CHANGED
- Disable semantic inheritance by default in bounding box annotators
- Removed compatibility with Kit < 104.0

### FIXED
- Fix bounding box 3D annotator definition when running with Kit 104
- Fix issue with colliding path names for writer SyncGate when running with multiple writers
- Filter out invalid 3D bounding boxes within annotator
- Fix `look_at` when the `look_at` axis isalign with `up_axis` of the stage.

## 1.4.7 - 2022-09-08
### FIXED
- Fix incorrect skeleton joint image-space projections
- Fix crash occurring on stage close - OM-62083

## 1.4.6 - 2022-09-07
### CHANGED
- Backend dispatcher now supports for writing data to AWS S3 buckets
- BasicWriter can now be configured to write to AWS S3 buckets

## 1.4.5 - 2022-09-06
### FIXED
- Fix `cam_local_to_world` in `OgnPointCloudGenerator.py`.  Previous behaviour used the inverse transform which resulted in incorrect point projections.

## 1.4.4 - 2022-08-30
### CHANGED
- `look_at` can now take `choice` and `sequence` distributions as input.
- KittiWriter supports semantic segmentation and instance segmentation
- Use HydraTextures when creating render products when available

## 1.4.3 - 2022-08-18
### CHANGED
- Default camera rotation on Z-up scenes modified to use more intuitive rotations - OM-60423

## 1.4.2 - 2022-08-17
### CHANGED
- Remove use of deprecated og.ContextHelper module
### FIXED
- Automatic camera rotation in z-up scenes moved to parent xform to avoid issues with look-at - OM-59090

## 1.4.1 - 2022-08-17
### CHANGED
- Support for internal reference of instantiate

### FIXED
- Fix bug causing incorrect node connections when using instantiate
- Fix instance segmentation where the prim has invalid id
- Fix error randomizer.instantiate where path and size are both replicator item

## 1.4.0 - 2022-08-17
### ADDED
- Add support for attaching multiple product renders to a writer
- Add multi-render-product support for BasicWriter and KittiWriter
- Add `get_data()` function to annotators
- Add texture scale and rotate for `randomizer.texture`.
- Add support for combining different distribution nodes.
- Add Node that converts object's size to scale.
- Add xform as parent of new prims for easier modification with pivot.
- Add function that allow users to modify the translation, rotation and scale pivot of a prim.
- Add Node that converts object's desired size to scale op.
- Add camera relative positioning for prims.
- Automatically arrange in sequence nodes of the same type under the same trigger referring to a common prim group
- Add create stereo camera pair
- Add a sequential sampling node
- Add pointcloud annotator that generates pointcloud for the given scene.
- Add log uniform distribution
- Add parsed instance segmentation annotator.
- Add `up_axis` support in `modify.py`'s `look_at` function.
- Add support for size to be a `ReplicatorItem` in `randomizer.instantiate`.
- Add support for internal reference in `randomizer.instantiate`.
- rep.modify.attribute can now support static values

### CHANGED
- cameraParams annotator types that were transform[4] changed to matrixd[4] due to deprecation
- Distribution nodes no longer output a bundle.
- Changed `modify.attribute` to modify the child prim of the Xform
- `instance_segmentation` annotator now outputs "parsed" instances. Original behaviour moved to
    `instance_id_segmentation` annotator.
- `distribution.choice` node can now takes a `ReplicatorItem` to `num_samples`.
- BasicWriter now supports sequence naming when using an on_time trigger.

### FIXED
- `randomizer.instantiate` now takes `ReplicatorItem` as input.
- skeleton annotator data now follows standard directory formatting in basicwriter.
- Fix `modify.attribute` with empty `attribute_type`.
- Fix `OgnWritePrimAtrribute` which it fails to handle list of strings
- Fix `create.light` where it fails to handle texture.
- Fix resolved type for distribution nodes.
- Fix `distribution.choice` where it will error out when input is a mix of int and float.
- `randomizer.materials` now can take a choice distribution node as input.
- Fix size attribute to maintain asset aspect ratio.

## 1.3.2 - 2022-07-08
### FIXED
- Split debug and release package for omni.replicator.core

## 1.3.1 - 2022-07-06
### FIXED
- Address compatibility issues with older writers missing backend
- Ensure new viewports are in focus in OV Code UI
- Fix compatibility issues with stop/run toggles in Omniverse Code

## 1.3.0 - 2022-06-30
### ADDED
- Add skeleton annotator nodes (OgnGetSkeletonPrims and OgnGetSkeletonData)
- Add support for C++ nodes in replicator

## 1.2.4 - 2022-06-28
### FIXED
- Fix incorrect `bbox_tight` and `bbox_loose` indexing in `kitti.py`
- Fixed semanic segmentation and bounding box where there is no semantic entities in the viewport.
- Fixed instance segmentation when there is no instances in the viewport.
- Fix bounding box to support Kit 104.0

## 1.2.3 - 2022-06-15
### FIXED
- Publish platform specific versions of the extension

## 1.2.2 - 2022-06-08
### FIXED
- Fix incorrect `trigger.on_time()` behaviour causing intervals to effectively increase with each execution.

## 1.2.1 - 2022-06-07
### FIXED
- Use pre-bundled pip packages

## 1.2.0 - 2022-06-02
### FIXED
- Fix semantic and instance segmentation error when colorize is set to False
- Fix issue preventing writing data after re-running a script using `rep.new_layer`

### ADDED
- Add `primPaths` and `bboxIds` to bounding box 2D/3D output
- Add colorize option to basicwriter segmentation output

### CHANGED
- Remove "UNLABELLED" label from instance segmentation mapping output
- `image_output_format` only affects RGB image output

## 1.2.0-drivesim - 2022-06-01
### FIXED
- Fix semantic and instance segmentation error when colorize is set to False

### ADDED
- Add `primPaths` and `bboxIds` to bounding box 2D/3D output
- Add colorize option to basicwriter segmentation output

### CHANGED
- Remove "UNLABELLED" label from instance segmentation mapping output
- `image_output_format` only affects RGB image output

## 1.1.1 - 2022-05-30
### FIXED
- Fix incorrect semantic labels in bbox incorrectly reporting "UNLABELLED" in certain circumstances

## 1.1.0 - 2022-05-27
### FIXED
- Revert choice distribution default behaviour to `with_replacements=True`
- Allow for multiple tokens of the same class
- Semantic Segmentation mapping now labels unlabelled pixels from "UNLABELLED: " to "class: UNLABELLED"
- Semantic Segmentation no longer duplicates ids/colors for a given semantic mapping

### ADDED
- Improve configuration capabilities in KITTI writer defaults
- Added option to set root directory for relative paths passed to disk backend.

### CHANGED
- Allow setting up get.prims() with a single tuple for `semantics` and `semantics_exclusion`

## 1.1.0-drivesim - 2022-05-20
### FIXED
- Revert choice distribution default behaviour to `with_replacements=True`
- Allow for multiple tokens of the same class
- Semantic Segmentation mapping now labels unlabelled pixels from "UNLABELLED: " to "class: UNLABELLED"

### ADDED
- Improve configuration capabilities in KITTI writer defaults

## 1.0.1 - 2022-05-20
### FIXED
- Fix bug in semantic segmentation annotator returning incorrect labels

## 1.0.0 - 2022-05-18
### FIXED
- Fix camera params annotator
- Fix viewport hiding when setting camera to Perspective camera
- Reset timeline when on_time trigger fires

### ADDED
- Add project_uvw option to texture randomizer
- Improve performance of segmentation annotators
- Add camera name to KITTI writer output path for multi-camera rigs

## 0.0.11-isaac - 2022-05-17
- Add project_uvw option to texture randomizer
- Fix orchestrator for DriveSim

## 0.0.11-drivesim - 2022-05-18
- Fix orchestrator for DriveSim
- Add camera name to output to writer
- Improve KITTI writer

## 0.0.11 - 2022-05-03
- Clean up dispatcher logging
- Fix on-time trigger
- Fix bounding box output format

## 0.0.10 - 2022-04-25
- Rename omni.replicator to omni.replicator.core
- Update README
- Fix semantic segmentation bug

## 0.0.9 - 2022-04-25
- Update Kit
- Fix headless operation within OV Code
- Support autonode exec label mapping

## 0.0.8 - 2022-04-13
- Update Kit
- Increase recursive speed of get_usd_files
- Add exit on complete
- Add mdl input support to materials randomizer

## 0.0.7 - 2022-04-07
- Ensure correct number of frames are produced
- Ensure first frame has been randomized
- Minimize cases where materials are not loaded, including dome light textures

## 0.0.6 - 2022-04-07
- OmniPBR fix
- Collider fix

## 0.0.5 - 2022-04-07
- Fix shutdown error

## 0.0.4 - 2022-04-07
- BasicWriter added
- Many minor bug fixes and improvements

## 0.0.3 - 2022-04-01

### Added
- Physics tests

### Changed
- Documentation
- "Look At" fix

### Removed
- Tests that fail (temporarily)

## 0.0.2 - UNPUBLISHED

## 0.0.1 - UNPUBLISHED
