.. _omni_genproc_core_ScatterPointsGroup_1:

.. _omni_genproc_core_ScatterPointsGroup:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: scatter points group
    :keywords: lang-en omnigraph node core scatter-points-group


scatter points group
====================

.. <description>

Scatters points from grouped sources.

.. </description>


Installation
------------

To use this node enable :ref:`omni.genproc.core<ext_omni_genproc_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Active (*inputs:active*)", "``bool``", "Is the Scatter Points Group node currently active?", "True"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Bases (*inputs:bases*)", "``bundle``", "Scatter base meshes.", "None"
    "Camera (*inputs:camera*)", "``bundle``", "Camera to filter the scattered points.", "None"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Curve Sources (*inputs:curveSources*)", "``bundle``", "Scatter curve sources.", "None"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Curve Steps Per Segment (*inputs:curveStepsPerSegment*)", "``uint64``", "Steps per segment for curve tessellation.", "10"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Filter Using Camera (*inputs:filterUsingCamera*)", "``bool``", "If true, the scattered points will be discarded if they are outside the viewing frustum of the provided cameras.", "False"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Frustum Offset (*inputs:frustumOffset*)", "``double``", "Offset to enlarge the frustum filtering the points.", "0"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Groups (*inputs:groups*)", "``bundle``", "Scatter groups.", "None"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Object Indices Ramp Interpolations (*inputs:objectIndicesRampInterpolations*)", "``int[]``", "Interpolation method between keys. Linear creates a flat curve from point to point. Smooth creates an ease in or ease out curve from point to point.", "[]"
    "Object Indices Ramp Positions (*inputs:objectIndicesRampPositions*)", "``float[]``", "Positions over the normalized elevation of the base meshes from 0 to 1.", "[]"
    "Object Indices Ramp Tags (*inputs:objectIndicesRampTags*)", "``token[]``", "Possible tag values for ramp", "[]"
    "Object Indices Ramp Values (*inputs:objectIndicesRampValues*)", "``float[]``", "Values of the object indices ramp at the corresponding positions", "[]"
    "Playback Evaluation (*inputs:playbackEvaluation*)", "``bool``", "If this is true, time for the simulation is from the timeline, not real time.", "False"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Playback Start Frame (*inputs:playbackStartFrame*)", "``int``", "If 'playbackEvaluation' is true, this is the frame after which the simulation will start.", "0"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Prototypes (*inputs:prototypes*)", "``bundle``", "The Paths of the prototypes.", "None"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Random Seed (*inputs:randomSeed*)", "``uint64``", "Random seed.", "0"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Texture Filters (*inputs:textureFilters*)", "``bundle``", "Configuration of texture filters", "None"
    "Textures (*inputs:textures*)", "``bundle``", "Textures can be used to filter the scattered points for each bases", "None"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Time (*inputs:time*)", "``double``", "Either the running clock or the timeline time or timeline time, depending on playbackEvaluation.", "0"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Usd Timecode (*inputs:usdTimecode*)", "``double``", "The USD timecode at the current playback point (timeline time * timecodes/sec).", "0"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Volume Sources (*inputs:volumeSources*)", "``bundle``", "Scatter volume sources.", "None"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Weights Ramp Interpolations (*inputs:weightsRampInterpolations*)", "``int[]``", "Interpolation method between keys. Linear creates a flat curve from point to point. Smooth creates an ease in or ease out curve from point to point.", "[]"
    "Weights Ramp Positions (*inputs:weightsRampPositions*)", "``float[]``", "Positions over the normalized elevation of the base meshes from 0 to 1.", "[]"
    "Weights Ramp Values (*inputs:weightsRampValues*)", "``float[]``", "Values of the weights ramp at the corresponding positions", "[]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bundle (*outputs:bundle*)", "``bundle``", "output bundle of points data", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Cached Base Meshes (*state:cachedBaseMeshes*)", "``bundle``", "Cached base meshes", "None"
    "Cached Curve Sources (*state:cachedCurveSources*)", "``bundle``", "Cached curve sources", "None"
    "Cached Volume Sources (*state:cachedVolumeSources*)", "``bundle``", "Cached volume sources", "None"
    "Prev Active (*state:prevActive*)", "``bool``", "Previous active value for recompute test", "None"
    "Prev Curve Steps Per Segment (*state:prevCurveStepsPerSegment*)", "``uint64``", "Previous curve steps per segment value for recompute test", "None"
    "Prev Filter Using Camera (*state:prevFilterUsingCamera*)", "``bool``", "Previous filter using camera value for recompute test", "None"
    "Prev Frustum Offset (*state:prevFrustumOffset*)", "``double``", "Previous frustum offset value for recompute test", "None"
    "Prev Object Indices Ramp Interpolations (*state:prevObjectIndicesRampInterpolations*)", "``int[]``", "Previous object indices ramp interpolations for recompute test", "None"
    "Prev Object Indices Ramp Positions (*state:prevObjectIndicesRampPositions*)", "``float[]``", "Previous object indices ramp positions values for recompute test", "None"
    "Prev Object Indices Ramp Values (*state:prevObjectIndicesRampValues*)", "``float[]``", "Previous object indices ramp values for recompute test", "None"
    "Prev Playback Evaluation (*state:prevPlaybackEvaluation*)", "``bool``", "Previous playbackEvaluation value for recompute test", "None"
    "Prev Playback Start Frame (*state:prevPlaybackStartFrame*)", "``int``", "Previous playbackStartFrame value for recompute test", "None"
    "Prev Random Seed (*state:prevRandomSeed*)", "``uint64``", "Previous randomSeed value for recompute test", "None"
    "Prev Time (*state:prevTime*)", "``double``", "Previous time value for recompute test", "None"
    "Prev Usd Timecode (*state:prevUsdTimecode*)", "``double``", "Previous usdTimecode value for recompute test", "None"
    "Prev Weights Ramp Interpolations (*state:prevWeightsRampInterpolations*)", "``int[]``", "Previous weights ramp interpolations for recompute test", "None"
    "Prev Weights Ramp Positions (*state:prevWeightsRampPositions*)", "``float[]``", "Previous weights ramp positions values for recompute test", "None"
    "Prev Weights Ramp Values (*state:prevWeightsRampValues*)", "``float[]``", "Previous weights ramp values for recompute test", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.genproc.core.ScatterPointsGroup"
    "Version", "1"
    "Extension", "omni.genproc.core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "scatter points group"
    "__tokens", "{""additive"": ""additive"", ""basis"": ""basis"", ""bezier"": ""bezier"", ""binormals"": ""binormals"", ""bspline"": ""bspline"", ""catmullRom"": ""catmullRom"", ""curveVertexCounts"": ""curveVertexCounts"", ""curvePathRegion"": ""curvePathRegion"", ""curvePathWidth"": ""curvePathWidth"", ""curvePathWidthRampPositions"": ""curvePathWidthRampPositions"", ""curvePathWidthRampValues"": ""curvePathWidthRampValues"", ""curvePathWidthRampInterpolations"": ""curvePathWidthRampInterpolations"", ""curvePathWidthTags"": ""curvePathWidthTags"", ""density"": ""density"", ""desiredPoints"": ""desiredPoints"", ""dirtyID"": ""dirtyID"", ""filteredTris"": ""filteredTris"", ""groupName"": ""groupName"", ""noiseModulation"": ""noiseModulation"", ""noiseExponential"": ""noiseExponential"", ""nonperiodic"": ""nonperiodic"", ""normals"": ""normals"", ""normalUpVectorBias"": ""normalUpVectorBias"", ""objectIndex"": ""objectIndex"", ""objectIndices"": ""objectIndices"", ""offset"": ""offset"", ""offsetRandom"": ""offsetRandom"", ""primvars_objectIndices"": ""primvars:objectIndices"", ""periodic"": ""periodic"", ""pinned"": ""pinned"", ""points"": ""points"", ""primvars_scatterWeights"": ""primvars:scatterWeights"", ""prototypes"": ""prototypes"", ""prototypePercents"": ""prototypePercents"", ""pruneCollision"": ""pruneCollision"", ""randomSeed"": ""randomSeed"", ""rotation"": ""rotation"", ""rotationRandom"": ""rotationRandom"", ""rotations"": ""rotations"", ""scale"": ""scale"", ""scaleRandom"": ""scaleRandom"", ""scales"": ""scales"", ""scatterMethod"": ""scatterMethod"", ""scatterWeights"": ""scatterWeights"", ""settingsOverride"": ""settingsOverride"", ""subtractive"": ""subtractive"", ""slopeMask"": ""slopeMask"", ""tangents"": ""tangents"", ""transform"": ""transform"", ""triIndices"": ""triIndices"", ""visible"": ""visible"", ""wrap"": ""wrap"", ""zoneSign"": ""zoneSign"", ""BasisCurves"": ""BasisCurves"", ""Mesh"": ""Mesh"", ""width"": ""width"", ""height"": ""height"", ""bitDepth"": ""bitDepth"", ""componentCount"": ""componentCount"", ""valid"": ""valid"", ""data"": ""data"", ""baseIndex"": ""baseIndex"", ""channel"": ""channel"", ""textureIndex"": ""textureIndex"", ""r"": ""r"", ""g"": ""g"", ""b"": ""b"", ""a"": ""a""}"
    "Generated Class Name", "OgnScatterPointsGroupDatabase"
    "Python Module", "omni.genproc.core"

