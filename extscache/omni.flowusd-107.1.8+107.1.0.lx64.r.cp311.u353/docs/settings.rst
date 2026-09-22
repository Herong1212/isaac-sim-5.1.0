.. |flow_short| replace:: Flow

Flow Settings
-----------------------

.. contents::
   :depth: 2
   :local:

Simulate Properties
++++++++++++++++++++++++

=========================== ===========================================================================================================================
Property                    Result
=========================== ===========================================================================================================================
blockMinLifetime            | Minimum lifetime of any allocate block. Avoids premature deactivation caused by GPU readback delay.
densityCellSize             | Size of density cells in world units. By default velocity cell size is twice density cell size.
enableLowPrecisionDensity   | Use 8-bit channels for temperature, fuel, burn, smoke
enableLowPrecisionVelocity  | Use 8-bit channels for velocity, divergence
enableSmallBlocks           | Use 16x8x8 density cell blocks instead of the default 32x16x16
enableVariableTimeStep      | Take step every frame. Can cause inconsistent simulation behavior for highly variable time step values, but useful when frame time is fixed already.
forceClear                  | Kills all active block allocations in this layer
forceDisableCoreSimulation  | Disable most simulation components. Emitters still function.
forceDisableEmitters        | Disable all emitters in this layer
forceSimulate               | Force simulate, even if timeline is paused.
interpolateTimeSteps        | Useful for motion blur in movie capture. Produces sub-frames between full simulation steps.
layer                       | See Layer section above.
maxStepsPerSimulate         | Limit on steps per frame to avoid excessive steps when application is running slow.
physicsCollisionEnabled     | If true, enable collision for prims using the USD physics collision applied schema.
physicsConvexCollision      | If true, use the PhysX convex collision hulls for |flow_short| collision. Requires PhysX to be actively simulating.
simulateWhenPaused          | Run simulation even if deltaTime is 0.0.
stepsPerSecond              | Simulation update rate
timeScale                   | Scales input time. Useful for slomo.
velocitySubSteps            | Higher values improve behavior with high speed effects, at the cost of performance.
advection                   | See Advection_ section.
vorticity                   | See Vorticity_ section.
pressure                    | See Pressure_ section.
summaryAllocate             | See SummaryAllocate_ section.
nanoVdbExport               | See NanoVdbExport_ section.
=========================== ===========================================================================================================================

.. _Advection:

Advection
####################

======================= ===========================================================================================================================
Property                Result
======================= ===========================================================================================================================
buoyancyMaxSmoke        | Smoke clamp value applied before computing smoke buoyancy, default 1.0
buoyancyPerSmoke        | Buoyant force per unit smoke, default 0.0
buoyancyPerTemp         | Upward force relative to temperature. Higher values help produce mushroom effects.
burnPerTemp             | Rate of burn relative to temperature. Higher burn values affect fuel consumption and
                        | divergence (expansion) terms.
combustionEnabled       | If false, only buoyancyMaxSmoke and buoyancyPerSmoke are active
coolingRate             | Temperature fade, applied on a per cell level. (Not conduction/convection.)
divergencePerBurn       | Expansion relative to burn amount. Units comparable to velocity in terms of scale.
                        | Higher values produce visible expansion, but can remove detail.
downsampleEnabled       | Boolean to enable/disable downsample. Downsample needed for SummaryAllocate_
enabled                 | Boolean to enable/disable advection.
forceFadeEnabled        | If true, fade will be applied even if advection is disabled
fuelPerBurn             | Fuel consumed relative to burn amount. Lower values will make a given amount of fuel
                        | last longer.
globalFetch             | Improves advection quality for high velocities, with some increase in runtime cost.
                        | (Can remove some banding artifacts)
gravity                 | Used to determine the 'up' direction for buoyancy.
ignitionTemp            | Minimum temperature for combustion.
smokePerBurn            | Smoke increase relative to burn amount.
tempPerBurn             | Temperature increase relative to burn amount.
smoke                   | See :ref:`Advection Channel <AdvectionChannel>` section.
velocity                | See :ref:`Advection Channel <AdvectionChannel>` section.
divergence              | See :ref:`Advection Channel <AdvectionChannel>` section.
temperature             | See :ref:`Advection Channel <AdvectionChannel>` section.
fuel                    | See :ref:`Advection Channel <AdvectionChannel>` section.
burn                    | See :ref:`Advection Channel <AdvectionChannel>` section.
======================= ===========================================================================================================================

.. _AdvectionChannel:

Advection Channel
*****************

========================= ===========================================================================================================================
Property                  Result
========================= ===========================================================================================================================
damping                   | Reduce channel proportional to current value. Valid range is 0 to 1, where 1
                          | takes the value to 0 immediately.
fade                      | Reduce channel at a constant rate per second. Valid range is 0 to infinity
                          | effectively.
secondOrderBlendFactor    | Second order correction factor. Value range is 0.0 to 1.0. 0.5 is generally a
                          | safe default. Higher values increase the sharpness, but comes with potentially
                          | banding artifacts. Use extra caution with velocity, where effects are even
                          | more pronounced.
secondOrderBlendThreshold | Minimum value to apply second order correction. Reduces simulation cost for cells
                          | near zero, with minimal/zero visual artifacts.
========================= ===========================================================================================================================

.. _Vorticity:

Vorticity
####################

========================= ===========================================================================================================================
Property                  Result
========================= ===========================================================================================================================
burnMask                  | Allows force to be applied relative to burn value in grid.
constantMask              | Allows force to be applied without respect to local velocity.
densityMask               | Allows force to be applied relative to divergence (Parameter name
                          | should be fixed).
enabled                   | Boolean to enable/disable vorticity confinement.
forceScale                | Control intensity of effect
fuelMask                  | Allows force to be applied relative to fuel value in grid.
smokeMask                 | Allows force to be applied relative to smoke value in grid.
temperatureMask           | Allows force to be applied relative to temperature value in grid.
velocityLinearMask        | Makes force directly proportional to local velocity
                          | Math: velocityLinearMask * speed
velocityLogScale          | This primarily exists to allow rescaling of |flow_short| effects to different
                          | coordinate systems.
velocityMask              | Velocity log mask, works together with velocityLogScale. Makes local linear
                          | velocity a requirement for forces to be applied. The log part makes the force
                          | applied with respect to velocity a diminishing return to avoid instability.
========================= ===========================================================================================================================

Pressure
####################

========================= ===========================================================================================================================
Property                  Result
========================= ===========================================================================================================================
enabled                   | Boolean to enable/disable the pressure solver.
========================= ===========================================================================================================================

.. _SummaryAllocate:

SummaryAllocate
########################

========================= ===========================================================================================================================
Property                  Result
========================= ===========================================================================================================================
enableNeighborAllocation  | If false, SummaryAllocate preserves active blocks, but does not attempt allocation of new blocks.
smokeThreshold            | Minimum smoke to keep a block active.
speedThreshold            | Minimum speed to keep a block active, given
                          | speedThresholdMinSmoke is satisfied.
speedThresholdMinSmoke    | Minimum smoke value for speedThreshold to apply.
========================= ===========================================================================================================================

.. _NanoVdbExport:

NanoVdbExport
########################

NanoVDB export allows |flow_short| grid data to be cached out to disk. This caching also allows |flow_short| data to feed RTX PT non-uniform volumes.

========================= ===========================================================================================================================
Property                  Result
========================= ===========================================================================================================================
burnEnabled               | If true, enables export of burn channel to NanoVDB.
divergenceEnabled         | If true, enables export of divergence channel to NanoVDB.
enabled                   | If true, enables NanoVDB export. If false, zero NanoVDB export will occur.
fuelEnabled               | If true, enables export of fuel channel to NanoVDB.
readbackClearOnStart      | If true, readbackDirectory will be cleared of |flow_short| VDB files at start of simulation.
readbackClearOnStop       | If true, readbackDirectory will be cleared of |flow_short| VDB files at stop of simulation.
readbackDirectory         | Target directory for VDB files.
readbackEnabled           | If true, copy VDBs back to CPU. If false, VDBs will be GPU access only.
readbackMaterial          | Optional path to an OmniVolumeDensity material. Will automatically configure USD timeSamples necessary to play cache.
readbackOpenVDB           | If true, convert NanoVDB to OpenVDB format for storage on disk.
smokeEnabled              | If true, enables export of smoke channel to NanoVDB.
statisticsEnabled         | If true, compute min/max/ave values on exported VDBs.
temperatureEnabled        | If true, enables export of temperature channel to NanoVDB.
velocityEnabled           | If true, enables export of velocity channel to NanoVDB.
========================= ===========================================================================================================================

Offscreen Properties
++++++++++++++++++++++++

========================= ===========================================================================================================================
Property                  Result
========================= ===========================================================================================================================
layer                     | Layer ID to apply these settings to
colormap                  | See Colormap_ section.
shadow                    | See Shadow_ section.
debugVolume               | See DebugVolume_ section.
========================= ===========================================================================================================================

.. _Colormap:

Colormap
#################

========================= ===========================================================================================================================
Property                  Result
========================= ===========================================================================================================================
colorScale                | Multiplier applied to RGB components.
resolution                | Number of texels in colormap.
rgabPoints                | RGBA values of control points, RGB can be over 1.0 for HDR effects.
xPoints                   | X coordinates of control points, maps to temperature. Valid over 0 to 1.
colorScalePoints          | Multipliers of control points applied to RGB component in control point.
========================= ===========================================================================================================================

.. _Shadow:

Shadow
#############

========================= ===========================================================================================================================
Property                  Result
========================= ===========================================================================================================================
attenuation               | Rate of light blockage. Higher values increase self shadow effect.
coarsePropagate           | Compute shadows at 2x2x2 coarser grid. Provides good
                          | quality at a much lower runtime cost.
enabled                   | Boolean to enable/disable self shadowing.
isPointLight              | If true, point light, else directional light.
lightDirection            | Directional light. Points to light.
lightPosition             | Point light position.
minIntensity              | Provide ambient level
numSteps                  | Number of steps per self shadow ray, divide by 2 when
                          | coarsePropagate is enabled.
stepOffsetScale           | Ray march offset to avoid a cell shadowing itself.
stepSizeScale             | Ray march step size relative to cell size. Higher values increase
                          | quality and performance cost.
========================= ===========================================================================================================================

.. _DebugVolume:

DebugVolume
###################

========================= ===========================================================================================================================
Property                  Result
========================= ===========================================================================================================================
enableSpeedAsTemperature  | Write speed value to temperature channel, to visualize in ray march.
enableVelocityAsDensity   | Write abs() of velocity channels to density xyz to visualize in ray march.
velocityScale             | Scale applied to velocity to control brightness for ray march result.
========================= ===========================================================================================================================

Render Properties
++++++++++++++++++++++++

========================= ===========================================================================================================================
Property                  Result
========================= ===========================================================================================================================
layer                     | Layer ID to apply these settings to
rayMarch                  | See RayMarch_ section
========================= ===========================================================================================================================

.. _RayMarch:

RayMarch
#####################

========================= ===========================================================================================================================
Property                  Result
========================= ===========================================================================================================================
attenuation               | Rate of light blockage. Higher values make the volume look more opaque
colorScale                | Multiplier applied to RGB values during ray march
enableBlockWireframe      | Visualizes active blocks for debug purposes
enableRawMode             | If true, do not apply colormap, pass raw density xyzw as color
shadowFactor              | The degree to which the z shadow channel scales the RGB channels from
                          | the colormap. 1.0 is default. 0.0 disables self shadowing effectively.
stepSizeScale             | Ray march step size relative to cell size. Higher values increase
                          | quality and performance cost.
cloud                     | See RayMarchCloud_ section.
========================= ===========================================================================================================================

.. _RayMarchCloud:

RayMarchCloud
#####################

========================= ===========================================================================================================================
Property                  Result
========================= ===========================================================================================================================
ambientColor              | Color in shadowed regions.
ambientMultiplier         | Scale to adjust brightness of ambient color.
attenuationMultiplier     | Controls how fast cloud shadows go dark.
densityMultiplier         | Scales input density.
enableCloudMode           | If true, default ray march is disabled, these settings are used instead.
numShadowSteps            | More steps can improve quality, but add performance cost.
shadowStepMultiplier      | Larger steps cover more of world space, at risk of artifacts.
sunDirection              | Direction to sun.
volumeBaseColor           | Base color for scattering.
volumeColorMultiplier     | Scale to adjust brightness of volume base color.
========================= ===========================================================================================================================


Emitter Properties
++++++++++++++++++++++++

Emitter Sphere
########################

Sphere emitters are the simplest emitter type. Defined by a position and radius.

========================= ===========================================================================================================================
Property                  Result
========================= ===========================================================================================================================
allocationScale           | 1.0 allocates blocks needed to contain sphere. 0.0 disables allocation.
                          | Values higher than 1.0 can be used to add additional padding.
applyPostPressure         | If true, apply velocity after pressure solve. This is useful
                          | for collision, as it allows hard enforcement of velocity inside
                          | moving bodies.
burn                      | Target burn value.
coupleRateBurn            | Couple rate for burn channel.
coupleRateDivergence      | Couple rate for divergence channel.
coupleRateFuel            | Couple rate for the fuel channel.
coupleRateSmoke           | Couple rate for the smoke channel.
coupleRateTemperature     | Couple rate for the temperature channel.
coupleRateVelocity        | Couple rate for the velocity channel.
divergence                | Target divergence value.
enabled                   | Boolean to enable/disable emitter
fuel                      | Target fuel value.
layer                     | Layer ID of simulation this emitter effects
multisample               | Test sphere overlap at 8 locations instead of 1
numSubSteps               | Substeps per simulation update. More steps produce a smoother result with moving emitters.
physicsVelocityScale      | If set to 1.0, the body velocity will be added to the target velocity.
                          | This is useful for collision effects, where the body velocity
                          | and grid cell velocity should align.
position                  | Position of sphere
radius                    | World space radius of sphere
radiusIsWorldSpace        | If true, do not apply xform scale to radius
smoke                     | Target smoke value.
temperature               | Target temperature value.
velocity                  | Target velocity value.
velocityIsWorldSpace      | If true, do not rotate velocity by xform
========================= ===========================================================================================================================

Emitter Box
#####################

Box emitters support emission from an oriented box. Clipping planes can also be added to support convex hulls.

========================= ===========================================================================================================================
Property                  Result
========================= ===========================================================================================================================
allocationScale           | 1.0 allocates blocks needed to contain box. 0.0 disables allocation.
                          | Values higher than 1.0 can be used to add additional padding.
applyPostPressure         | If true, apply velocity after pressure solve. This is useful for
                          | collision, as it allows hard enforcement of velocity inside moving bodies.
burn                      | Target burn value.
clippingPlanes            | List of clipping planes in local space.
coupleRateBurn            | Couple rate for burn channel.
coupleRateDivergence      | Couple rate for divergence channel.
coupleRateFuel            | Couple rate for the fuel channel.
coupleRateSmoke           | Couple rate for the smoke channel.
coupleRateTemperature     | Couple rate for the temperature channel.
coupleRateVelocity        | Couple rate for the velocity channel.
divergence                | Target divergence value.
enabled                   | Boolean to enable/disable emitter
fuel                      | Target fuel value.
halfSize                  | Half of box width/height/depth in local units
layer                     | Layer integer. See *Layer* section.
multisample               | Test sphere overlap at 8 locations instead of 1
physicsVelocityScale      | If set to 1.0, the body velocity will be added to the target velocity.
                          | This is useful for collision effects, where
                          | the body velocity and grid cell velocity should align.
smoke                     | Target smoke value.
temperature               | Target temperature value.
velocity                  | Target velocity value.
velocityIsWorldSpace      | If true, do not rotate velocity by xform
========================= ===========================================================================================================================

Emitter Point
#########################

Point emitters allow simple arrays to define points that are splatted to the simulation.

=========================== ===========================================================================================================================
Property                    Result
=========================== ===========================================================================================================================
allocateMask                | Default allocation behavior. If true and allocateMasks is empty, all points will trigger allocation.
applyPostPressure           | If true, apply velocity after pressure solve.
                            | This is useful for collision, as it allows hard enforcement of velocity inside moving bodies.
burn                        | Default target burn value.
burnScale                   | Multiplier for burn and pointBurns.
colorIsSrgb                 | If true, perform color correction on temperature, fuel, burn channels
coupleRateBurn              | Default couple rate for burn channel.
coupleRateDivergence        | Default couple rate for divergence channel.
coupleRateFuel              | Default couple rate for fuel channel.
coupleRateSmoke             | Default couple rate for smoke channel.
coupleRateTemperature       | Default couple rate for temperature channel.
coupleRateVelocity          | Default couple rate for velocity channel.
divergence                  | Default target divergence value.
divergenceScale             | Multiplier for divergence and pointDivergences.
enabled                     | Boolean to enable/disable emitter
enableStreaming             | If true, only apply streamingBatchSize per frame
fuel                        | Default target fuel value.
fuelScale                   | Multiplier for fuel and pointFuels
layer                       | Layer integer. See *Layer* section.
numSubSteps                 | If numSubSteps > 1, Interpolates point position using velocity
pointAllocateMasks          | Optional array of allocate settings per point.
pointBurns                  | Array of target burn values for each position.
pointColors                 | Array of temperature, fuel, burn values, used for color with ray march in raw mode.
pointCoupleRateBurns        | Array of burn couple rates for each position.
pointCoupleRateDivergences  | Array of divergence couple rates for each position.
pointCoupleRateFuels        | Array of fuel couple rate for each position.
pointCoupleRateSmokes       | Array of smoke couple rates for each position.
pointCoupleRateTemperatures | Array of temperature couple rates for each position.
pointCoupleRateVelocities   | Array of velocity couple rates for each position.
pointDivergences            | Array of target divergence values for each position.
pointFuels                  | Array of target fuel values for each position
pointPositions              | Array of local space positions. Determines total point count.
pointSmokes                 | Array of target smoke values for each position
pointsPrim                  | Optional relationship to UsdGeomPoint, to source arrays
pointTemperatures           | Array of target temperature values for each position.
pointVelocities             | Array of target velocity values for each position.
smoke                       | Default target smoke value.
smokeScale                  | Multiplier for smoke and pointSmokes
streamClearAtStart          | If true, clears entire layer when streaming start
streamOnce                  | If true, apply each point to the grid only once
temperature                 | Default target temperature value.
temperatureScale            | Multiplier for temperature and pointTemperatures
updateCoarseDensity         | If true, update coarse density for the block covered by this emitter
velocity                    | Default target velocity value.
velocityIsWorldSpace        | If true, do not rotate velocity by xform
velocityScale               | Multiplier for velocity and pointVelocities
=========================== ===========================================================================================================================

Emitter Mesh
#########################

Mesh emitters rasterize meshes to the |flow_short| grid. Can connect to UsdGeomMesh prims to use existing meshes in stage.

Experimental feature.

=========================== ===========================================================================================================================
Property                    Result
=========================== ===========================================================================================================================
allocateMask                | Default allocation behavior. If true and allocateMasks is empty, all points will trigger allocation.
applyPostPressure           | If true, apply velocity after pressure solve.
                            | This is useful for collision, as it allows hard enforcement of velocity inside moving bodies.
burn                        | Default target burn value.
burnScale                   | Multiplier for burn and pointBurns.
colorIsSrgb                 | If true, perform color correction on temperature, fuel, burn channels
coupleRateBurn              | Default couple rate for burn channel.
coupleRateDivergence        | Default couple rate for divergence channel.
coupleRateFuel              | Default couple rate for fuel channel.
coupleRateSmoke             | Default couple rate for smoke channel.
coupleRateTemperature       | Default couple rate for temperature channel.
coupleRateVelocity          | Default couple rate for velocity channel.
divergence                  | Default target divergence value.
divergenceScale             | Multiplier for divergence and pointDivergences.
enabled                     | Boolean to enable/disable emitter
fuel                        | Default target fuel value.
fuelScale                   | Multiplier for fuel and pointFuels
layer                       | Layer integer. See *Layer* section.
maxDistance                 | Max distance from surface to emit.
meshBurns                   | Array of target burn values for each face index.
meshColors                  | Array of temperature, fuel, burn values, used for color with ray march in raw mode.
meshCoupleRateBurns         | Array of burn couple rates for each face index.
meshCoupleRateDivergences   | Array of divergence couple rates for each face index.
meshCoupleRateFuels         | Array of fuel couple rate for each face index.
meshCoupleRateSmokes        | Array of smoke couple rates for each face index.
meshCoupleRateTemperatures  | Array of temperature couple rates for each face index.
meshCoupleRateVelocities    | Array of velocity couple rates for each position.
meshDivergences             | Array of target divergence values for each face index.
meshFaceVertexCounts        | Array of vertex counts for each polygon face
meshFaceVertexIndices       | Array of indices for each face pointing to position indices.
meshFuels                   | Array of target fuel values for each position
meshPositions               | Array of local space positions. Determines total point count.
meshPrim                    | Optional relationship to UsdGeomMesh, to source arrays
meshSmokes                  | Array of target smoke values for each position
meshSubsetEnableds          | Reserved for future use.
meshSubsetFaceCounts        | Reserved for future use.
meshSubsetLayers            | Reserved for future use.
meshTemperatures            | Array of target temperature values for each position.
meshVelocities              | Array of target velocity values for each position.
minDistance                 | Min distance from surface to emit.
numSubSteps                 | If numSubSteps > 1, Interpolates point position using velocity
orientationLeftHanded       | If true, assume left winding direction of face polygons.
physicsVelocityScale        | If set to 1.0, the body velocity will be added to the target velocity.
smoke                       | Default target smoke value.
smokeScale                  | Multiplier for smoke and pointSmokes
temperature                 | Default target temperature value.
temperatureScale            | Multiplier for temperature and pointTemperatures
velocity                    | Default target velocity value.
velocityIsWorldSpace        | If true, do not rotate velocity by xform
velocityScale               | Multiplier for velocity and pointVelocities
=========================== ===========================================================================================================================


Emitter Texture
########################

Texture emitters allow simple arrays to define dense 3D grids of values.

.. note::
    Mapping of Array Index to Texel:
    arrayIndex = (texelIndex.z * textureHeight + texelIndex.y) * textureWidth + texelIndex.x

    textureName:assetPath and textureName:channel enable the use of standard image file formats as input to the texture emitter.
    Current channel values supported are red, green, blue, alpha, redSrgb, greenSrgb, blueSrgb, alphaSrgb, redSnorm, greenSnorm, blueSnorm, alphaSnorm.
    For Vec3 velocity, a red channel value will use red, green, blue to drive x, y, z.

============================= ===========================================================================================================================
Property                      Result
============================= ===========================================================================================================================
allocationScale               | 1.0 allocates blocks needed to contain box defined by halfSize/position. 0.0 disables allocation. Values higher than 1.0 can be used to add
                              | additional padding.
applyPostPressure             | If true, apply velocity after pressure solve.
                              | This is useful for collision, as it allows hard enforcement of velocity inside moving bodies.
burn                          | Default target burn value.
burnScale                     | Multiplier for burn and textureBurns
colorIsSrgb                   | If true, perform color correction on temperature, fuel, burn channels
coupleRateBurn                | Default couple rate for burn channel.
coupleRateDivergence          | Default couple rate for divergence channel.
coupleRateFuel                | Default couple rate for fuel channel.
coupleRateSmoke               | Default couple rate for smoke channel.
coupleRateRateTemperature     | Default couple rate for temperature channel.
coupleRateVelocity            | Default couple rate for velocity channel.
divergence                    | Default target divergence value.
divergenceScale               | Multiplier for divergence and textureDivergences
enabled                       | Boolean to enable/disable emitter.
fuel                          | Default target fuel value.
fuelScale                     | Multiplier for fuel and textureFuels
halfSize                      | Half of box width/height/depth in world units.
layer                         | Layer integer. See *Layer* section.
position                      | World space position.
smoke                         | Default target smoke value.
smokeScale                    | Multiplier for smoke and textureSmokes
temperature                   | Default target temperature value.
temperatureScale              | Multiplier for temperature and temperatureScale
textureBurns                  | Array of target burn values for each texel.
textureCoupleRateBurns        | Array of burn couple rates for each texel.
textureCoupleRateDivergences  | Array of divergence couple rates for each texel.
textureCoupleRateFuels        | Array of fuel couple rate for each texel.
textureCoupleRateSmokes       | Array of smoke couple rates for each texel.
textureCoupleRateTemperatures | Array of temperature couple rates for each texel.
textureCoupleRateVelocities   | Array of velocity couple rates for each texel.
textureDepth                  | Depth in texels of texture data.
textureDivergences            | Array of target divergence values for each texel.
textureFirstElement           | Array index offset applied for all arrays. Useful for animation.
textureFuels                  | Array of target fuel values for each texel.
textureHeight                 | Height in texels of texture data.
textureSmokes                 | Array of target smoke values for each texel.
textureTemperatures           | Array of target temperature values for each texel.
textureVelocities             | Array of target velocity values for each texel.
textureWidth                  | Width in texels of texture data.
velocity                      | Default target velocity value.
velocityIsWorldSpace          | If true, do not rotate velocity by xform
velocityScale                 | Multiplier for velocity and textureVelocities
============================= ===========================================================================================================================

Emitter NanoVDB
########################

NanoVDB emitters allow sparse voxel data structures to define emitter shapes/values.

========================================= ===========================================================================================================================
Property                                  Result
========================================= ===========================================================================================================================
allocateActiveLeaves                      | If true, finer allocation granularity is used. (Adds some CPU overhead.)
allocationScale                           | 1.0 allocates blocks needed to contain NanoVDB. 0.0 disables allocation. Values higher than 1.0 can be used to add
                                          | additional padding.
applyPostPressure                         | If true, apply velocity after pressure solve.
                                          | This is useful for collision, as it allows hard enforcement of velocity inside moving bodies.
burn                                      | Default target burn value.
burnScale                                 | Multiplier for burn and nanoVdbBurns.
colorIsSrgb                               | If true, perform color correction on temperature, fuel, burn channels
coupleRateBurn                            | Default couple rate for burn channel.
coupleRateDivergence                      | Default couple rate for divergence channel.
coupleRateFuel                            | Default couple rate for fuel channel.
coupleRateSmoke                           | Default couple rate for smoke channel.
coupleRateTemperature                     | Default couple rate for temperature channel.
coupleRateVelocity                        | Default couple rate for velocity channel.
divergence                                | Default target divergence value.
divergenceScale                           | Multiplier for divergence and nanoVdbDivergences
enabled                                   | Boolean to enable/disable emitter
fuel                                      | Default target fuel value.
fuelScale                                 | Multiplier for fuel and nanoVdbFuels
layer                                     | Layer integer. See *Layer* section.
maxDistance                               | Maximum distance for emitter active region. Used with nanoVdbDistances.
minDistance                               | Minimum distance for emitter active region. Used with nanoVdbDistances.
nanoVdbBurnFirstElement                   | Burn channel. Word offset applied when reading nanoVdbBurns array.
nanoVdbBurns                              | Burn channel. Word array containing NanoVDB data structure
nanoVdbBurns::assetPath                   | Burn channel. Optional path to OpenVDB/NanoVDB asset to use. Overrides nanoVdbBurns.
nanoVdbBurns::gridName                    | Burn channel. Grid name to search for in NanoVDB data structure.
nanoVdbCoupleRateBurnFirstElement         | Burn couple rate channel. Word offset applied when reading nanoVdbCoupleRateBurns array.
nanoVdbCoupleRateBurns                    | Burn couple rate channel. Word array containing NanoVDB data structure
nanoVdbCoupleRateBurns::assetPath         | Burn couple rate channel. Optional path to OpenVDB/NanoVDB asset to use. Overrides nanoVdbCoupleRateBurns.
nanoVdbCoupleRateBurns::gridName          | Burn couple rate channel. Grid name to search for in NanoVDB data structure.
nanoVdbCoupleRateDivergenceFirstElement   | Divergence couple rate channel. Word offset applied when reading nanoVdbCoupleRateDivergences array.
nanoVdbCoupleRateDivergences              | Divergence couple rate channel. Word array containing NanoVDB data structure
nanoVdbCoupleRateDivergences::assetPath   | Divergence couple rate channel. Optional path to OpenVDB/NanoVDB asset to use. Overrides nanoVdbCoupleRateDivergences.
nanoVdbCoupleRateDivergences::gridName    | Divergence couple rate channel. Grid name to search for in NanoVDB data structure.
nanoVdbCoupleRateFuelFirstElement         | Fuel couple rate channel. Word offset applied when reading nanoVdbCoupleRateFuels array.
nanoVdbCoupleRateFuels                    | Fuel couple rate channel. Word array containing NanoVDB data structure
nanoVdbCoupleRateFuels::assetPath         | Fuel couple rate channel. Optional path to OpenVDB/NanoVDB asset to use. Overrides nanoVdbCoupleRateFuels.
nanoVdbCoupleRateFuels::gridName          | Fuel couple rate channel. Grid name to search for in NanoVDB data structure.
nanoVdbCoupleRateSmokeFirstElement        | Smoke couple rate channel. Word offset applied when reading nanoVdbCoupleRateSmokes array.
nanoVdbCoupleRateSmokes                   | Smoke couple rate channel. Word array containing NanoVDB data structure
nanoVdbCoupleRateSmokes::assetPath        | Smoke couple rate channel. Optional path to OpenVDB/NanoVDB asset to use. Overrides nanoVdbCoupleRateSmokes.
nanoVdbCoupleRateSmoke::gridName          | Smoke couple rate channel. Grid name to search for in NanoVDB data structure.
nanoVdbCoupleRateTemperatureFirstElement  | Temperature couple rate channel. Word offset applied when reading nanoVdbCoupleRateTemperatures array.
nanoVdbCoupleRateTemperatures             | Temperature couple rate channel. Word array containing NanoVDB data structure
nanoVdbCoupleRateTemperatures::assetPath  | Temperature couple rate channel. Optional path to OpenVDB/NanoVDB asset to use. Overrides nanoVdbCoupleRateTemperatures.
nanoVdbCoupleRateTemperature::gridName    | Temperature couple rate channel. Grid name to search for in NanoVDB data structure.
nanoVdbCoupleRateVelocities               | Velocity couple rate channel. Word array containing NanoVDB data structure
nanoVdbCoupleRateVelocities::assetPath    | Velocity couple rate channel. Optional path to OpenVDB/NanoVDB asset to use. Overrides nanoVdbCoupleRateVelocities.
nanoVdbCoupleRateVelocities::gridName     | Velocity couple rate channel. Grid name to search for in NanoVDB data structure.
nanoVdbCoupleRateVelocityFirstElement     | Velocity couple rate channel. Word offset applied when reading nanoVdbCoupleRateVelocities array.
nanoVdbDistanceFirstElement               | Distance channel. Word offset applied when reading nanoVdbDistances array.
nanoVdbDistances                          | Distance channel. Word array containing NanoVDB data structure
nanoVdbDistances::assetPath               | Distance channel. Optional path to OpenVDB/NanoVDB asset to use. Overrides nanoVdbDistances.
nanoVdbDistances::gridName                | Distance channel. Grid name to search for in NanoVDB data structure.
nanoVdbDivergenceFirstElement             | Divergence channel. Word offset applied when reading nanoVdbDivergences array.
nanoVdbDivergences                        | Divergence channel. Word array containing NanoVDB data structure
nanoVdbDivergences::assetPath             | Divergence channel. Optional path to OpenVDB/NanoVDB asset to use. Overrides nanoVdbDivergences.
nanoVdbDivergences::gridName              | Divergence channel. Grid name to search for in NanoVDB data structure.
nanoVdbFuelFirstElement                   | Fuel channel. Word offset applied when reading nanoVdbFuels array.
nanoVdbFuels                              | Fuel channel. Word array containing NanoVDB data structure
nanoVdbFuels::assetPath                   | Fuel channel. Optional path to OpenVDB/NanoVDB asset to use. Overrides nanoVdbFuels.
nanoVdbFuels::gridName                    | Fuel channel. Grid name to search for in NanoVDB data structure.
nanoVdbSmokeFirstElement                  | Smoke channel. Word offset applied when reading nanoVdbSmokes array.
nanoVdbSmokes                             | Smoke channel. Word array containing NanoVDB data structure
nanoVdbSmokes::assetPath                  | Smoke channel. Optional path to OpenVDB/NanoVDB asset to use. Overrides nanoVdbSmokes.
nanoVdbSmokes::gridName                   | Smoke channel. Grid name to search for in NanoVDB data structure.
nanoVdbTemperatureFirstElement            | Temperature channel. Word offset applied when reading nanoVdbTemperatures array.
nanoVdbTemperatures                       | Temperature channel. Word array containing NanoVDB data structure
nanoVdbTemperatures::assetPath            | Temperature channel. Optional path to OpenVDB/NanoVDB asset to use. Overrides nanoVdbTemperatures.
nanoVdbTemperatures::gridName             | Temperature channel. Grid name to search for in NanoVDB data structure.
nanoVdbVelocities                         | Velocity channel. Word array containing NanoVDB data structure
nanoVdbVelocities::assetPath              | Velocity channel. Optional path to OpenVDB/NanoVDB asset to use. Overrides nanoVdbVelocities.
nanoVdbVelocities::gridName               | Velocity channel. Grid name to search for in NanoVDB data structure.
nanoVdbVelocityFirstElement               | Velocity channel. Word offset applied when reading nanoVdbVelocities array.
smoke                                     | Default target smoke value.
smokeScale                                | Multiplier for smoke and nanoVdbSmokes
temperature                               | Default target temperature value.
temperatureScale                          | Multiplier for temperature and nanoVdbTemperatures
velocity                                  | Default target velocity value.
velocityIsWorldSpace                      | If true, do not rotate velocity by xform
velocityScale                             | Multiplier for velocity and nanoVdbVelocities
========================================= ===========================================================================================================================
