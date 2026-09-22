.. _omni_genproc_core_ScatterPoints_1:

.. _omni_genproc_core_ScatterPoints:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: scatter points
    :keywords: lang-en omnigraph node core scatter-points


scatter points
==============

.. <description>

Scatters points on the input geometry with optional curve regions

.. </description>


Installation
------------

To use this node enable :ref:`omni.genproc.core<ext_omni_genproc_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Active (*inputs:active*)", "``bool``", "Is the Scatter Points node currently active?", "True"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Binormals (*inputs:binormals*)", "``bool``", "If this is true, it output the object indices.", "True"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Camera Prim (*inputs:cameraPrim*)", "``bundle``", "Camera prim", "None"
    "Curve Tessellation (*inputs:curveTessellation*)", "``int``", "curve tessellation factor", "10"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Curves Bundle (*inputs:curvesBundle*)", "``bundle``", "Input curve data", "None"
    "Debug Draw (*inputs:debugDraw*)", "``bool``", "", "False"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Debug Draw Curve Triangulation (*inputs:debugDrawCurveTriangulation*)", "``bool``", "", "False"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Exclusive (*inputs:exclusive*)", "``bool``", "If this is true, it outputs the point cloud prim and the input bundles, otherwise only the point cloud prim", "True"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Filter Using Camera (*inputs:filterUsingCamera*)", "``bool``", "If true, scattered points will be discarded if they are occluded by scattering geometry or are outside the viewing frustum of the provided camera prim.", "False"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Normals (*inputs:normals*)", "``bool``", "If this is true, it output the object indices.", "True"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Num Desired Points (*inputs:numDesiredPoints*)", "``int``", "The number of generated points desired.", "100"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Object Index (*inputs:objectIndex*)", "``int``", "Object index is valid if you have multiple sources to output. this number corresponds with the order you imported your sources.", "0"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Object Index Random (*inputs:objectIndexRandom*)", "``int``", "Randomly pick an 'Object Index' source in a range.", "0"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Object Indices (*inputs:objectIndices*)", "``bool``", "If this is true, it output the object indices.", "True"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Occlusion Prim (*inputs:occlusionPrim*)", "``bundle``", "Geometry to use for occlusion test", "None"
    "Playback Evaluation (*inputs:playbackEvaluation*)", "``bool``", "If this is true, time for the simulation is from the timeline, not real time.", "False"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Playback Start Frame (*inputs:playbackStartFrame*)", "``int``", "If 'playbackEvaluation' is true, this is the frame after which the simulation will start.", "0"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Prim (*inputs:prim*)", "``bundle``", "Mesh geometry to use for point scattering", "None"
    "Random Seed (*inputs:randomSeed*)", "``uint64``", "", "0"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Rotation (*inputs:rotation*)", "``float[3]``", "Rotate the point in x,y,z. ", "[0, 0, 0]"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Rotation Random (*inputs:rotationRandom*)", "``float[3]``", "Randomly rotate the particle in x,y,z along a range. ", "[0, 0, 0]"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Rotations (*inputs:rotations*)", "``bool``", "If this is true, it output the rotations.", "True"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Scale (*inputs:scale*)", "``float[3]``", "Change the size of the point in x,y,z. ", "[5, 5, 5]"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Scale Random (*inputs:scaleRandom*)", "``float``", "Randomly change the size of the point in x,y,z.", "0.0"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Scales (*inputs:scales*)", "``bool``", "If this is true, it output the scales.", "True"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Scatter Across Points (*inputs:scatterAcrossPoints*)", "``bool``", "If this is true, points will be generated at the vertices of the input mesh(es).", "True"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Scatter Inside Volume (*inputs:scatterInsideVolume*)", "``bool``", "If this is true, points will be generated inside the input mesh(es).", "True"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Scatter On Surface (*inputs:scatterOnSurface*)", "``bool``", "If this is true, points will be generated on the surface of the input mesh(es).", "True"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Tangents (*inputs:tangents*)", "``bool``", "If this is true, it output the object indices.", "True"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Time (*inputs:time*)", "``double``", "Either the running clock or the timeline time or timeline time, depending on playbackEvaluation", "0"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Usd Timecode (*inputs:usdTimecode*)", "``double``", "The USD timecode at the current playback point (timeline time * timecodes/sec)", "0"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Use Scatter Geometry As Occlusion Geometry (*inputs:useScatterGeometryAsOcclusionGeometry*)", "``bool``", "If true, prims connected to the 'prim' input of this node will also be used to occlude points when  filtering using a camera. Otherwise, prims connected to the 'occlusionPrim' input will be used.", "True"
    "", "Metadata", "*displayGroup* = parameters", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bundle (*outputs:bundle*)", "``bundle``", "output bundle of points data", "None"
    "Projected Points (*outputs:projectedPoints*)", "``float[2][]``", "If a camera prim is provided, this collection will be populated with points projected into the camera's screen space in the range [-1, 1].  If no camera prim is provided, this will be empty.", "[]"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Cached Bundle (*state:cachedBundle*)", "``bundle``", "cached curve triangulation", "None"
    "Prev Active (*state:prevActive*)", "``bool``", "Previous active value for recompute test", "None"
    "Prev Binormals (*state:prevBinormals*)", "``bool``", "Previous normals value for recompute test", "None"
    "Prev Curve Tessellation (*state:prevCurveTessellation*)", "``int``", "Previous curveTessellation value for recompute test", "None"
    "Prev Exclusive (*state:prevExclusive*)", "``bool``", "Previous exclusive value for recompute test", "None"
    "Prev Filter Using Camera (*state:prevFilterUsingCamera*)", "``bool``", "Previous filterUsingCamera value for recompute test", "None"
    "Prev Normals (*state:prevNormals*)", "``bool``", "Previous normals value for recompute test", "None"
    "Prev Num Desired Points (*state:prevNumDesiredPoints*)", "``int``", "Previous numDesiredPoints value for recompute test", "None"
    "Prev Object Index (*state:prevObjectIndex*)", "``int``", "Previous objectIndex value for recompute test", "None"
    "Prev Object Index Random (*state:prevObjectIndexRandom*)", "``int``", "Previous objectIndexRandom value for recompute test", "None"
    "Prev Object Indices (*state:prevObjectIndices*)", "``bool``", "Previous objectIndices value for recompute test", "None"
    "Prev Playback Evaluation (*state:prevPlaybackEvaluation*)", "``bool``", "Previous playbackEvaluation value for recompute test", "None"
    "Prev Playback Start Frame (*state:prevPlaybackStartFrame*)", "``int``", "Previous playbackStartFrame value for recompute test", "None"
    "Prev Random Seed (*state:prevRandomSeed*)", "``uint64``", "Previous randomSeed value for recompute test", "None"
    "Prev Rotation (*state:prevRotation*)", "``float[3]``", "Previous rotation value for recompute test", "None"
    "Prev Rotation Random (*state:prevRotationRandom*)", "``float[3]``", "Previous rotation random value for recompute test", "None"
    "Prev Rotations (*state:prevRotations*)", "``bool``", "Previous rotations value for recompute test", "None"
    "Prev Scale (*state:prevScale*)", "``float[3]``", "Previous scale value for recompute test", "None"
    "Prev Scale Random (*state:prevScaleRandom*)", "``float``", "Previous scale random value for recompute test", "None"
    "Prev Scales (*state:prevScales*)", "``bool``", "Previous scales value for recompute test", "None"
    "Prev Scatter Across Points (*state:prevScatterAcrossPoints*)", "``bool``", "Previous scatterAcrossPoints value for recompute test", "None"
    "Prev Scatter Inside Volume (*state:prevScatterInsideVolume*)", "``bool``", "Previous scatterInsideVolume value for recompute test", "None"
    "Prev Scatter On Surface (*state:prevScatterOnSurface*)", "``bool``", "Previous scatterOnSurface value for recompute test", "None"
    "Prev Tangents (*state:prevTangents*)", "``bool``", "Previous tangents value for recompute test", "None"
    "Prev Time (*state:prevTime*)", "``double``", "Previous time value for recompute test", "None"
    "Prev Usd Timecode (*state:prevUsdTimecode*)", "``double``", "Previous usdTimecode value for recompute test", "None"
    "Prev Use Scatter Geometry As Occlusion Geometry (*state:prevUseScatterGeometryAsOcclusionGeometry*)", "``bool``", "Previous UseScatterGeometryAsOcclusionGeometry value for recompute test", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.genproc.core.ScatterPoints"
    "Version", "1"
    "Extension", "omni.genproc.core"
    "Icon", "ogn/icons/omni.genproc.core.ScatterPoints.svg"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "scatter points"
    "__tokens", "{""points"": ""points"", ""curveVertexCounts"": ""curveVertexCounts"", ""basis"": ""basis"", ""bezier"": ""bezier"", ""bspline"": ""bspline"", ""catmullRom"": ""catmullRom"", ""wrap"": ""wrap"", ""pinned"": ""pinned"", ""periodic"": ""periodic"", ""nonperiodic"": ""nonperiodic"", ""transform"": ""transform"", ""curveTessellation"": ""curveTessellation"", ""curveTriangulation"": ""curveTriangulation"", ""trigDebugIndices"": ""trigDebugIndices"", ""zoneSign"": ""zoneSign"", ""additive"": ""additive"", ""subtractive"": ""subtractive"", ""rotations"": ""rotations"", ""scales"": ""scales"", ""objectIndices"": ""objectIndices"", ""normals"": ""normals"", ""tangents"": ""tangents"", ""binormals"": ""binormals""}"
    "Generated Class Name", "OgnScatterPointsDatabase"
    "Python Module", "omni.genproc.core"

