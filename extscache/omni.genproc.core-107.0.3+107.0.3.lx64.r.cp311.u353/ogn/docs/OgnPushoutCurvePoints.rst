.. _omni_genproc_core_PushoutCurvePoints_1:

.. _omni_genproc_core_PushoutCurvePoints:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: curves: pushout curve points
    :keywords: lang-en omnigraph node curve core pushout-curve-points


curves: pushout curve points
============================

.. <description>

Sample points along curves in the input curvesBundle. When a range of these points falls within the  bounding sphere / box of the prims within the collisionBundle, this node attempts to push those subsections  of points outside the bounding volume in some reasonable way.  This node outputs two bundles: a pointsBundle that contains one prim per polyline containing the  displaced points of that polyline, and a curvesBundle that contains curve prims fit to those  displaced points.

.. </description>


Installation
------------

To use this node enable :ref:`omni.genproc.core<ext_omni_genproc_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Transform Bundle (*inputs:collisionBundle*)", "``bundle``", "Input meshes. The bounding spheres / boxes of each of these meshes will be used as the pushout volumes.", "None"
    "Collision Proxy (*inputs:collisionProxy*)", "``int``", "0 = Sphere, 1 = Axis-Oriented Box", "0"
    "Transform Bundle (*inputs:curvesBundle*)", "``bundle``", "Bundle containing curves data", "None"
    "Number of Segments (*inputs:numberOfSegments*)", "``int``", "Number of segments per curve for each output curve. If this value is not positive,  the number of segments in the corresponding input curve will be used.", "0"
    "Push Out Horizontally (*inputs:pushoutHorizontally*)", "``bool``", "If true, pushout will not modify any particle's vertical position (as defined by the specified up vector)", "False"
    "Samples per Segment (*inputs:samplesPerSegment*)", "``int``", "Number of points in each curve segment's tessellation", "20"
    "Up Axis (*inputs:upAxis*)", "``float[3]``", "Up axis to be used when 'Node UpAxis' is specified as the up axis source.", "[0, 1, 0]"
    "Up Axis Source (*inputs:upAxisSource*)", "``int``", "0 = Use Scene Up, 1 = Use Node UpAxis", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Transform Bundle (*outputs:curvesBundle*)", "``bundle``", "Bundle containing curves fit to displaced points", "None"
    "Points Bundle (*outputs:pointsBundle*)", "``bundle``", "Bundle containing displaced points data sampled from curves", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prev Collision Proxy (*state:prevCollisionProxy*)", "``int``", "Previous collisionProxy value for recompute test", "None"
    "Prev Number Of Segments (*state:prevNumberOfSegments*)", "``int``", "Previous numberOfSegments value for recompute test", "None"
    "Prev Pushout Horizontally (*state:prevPushoutHorizontally*)", "``bool``", "Previous pushoutHorizontally value for recompute test", "None"
    "Prev Samples Per Segment (*state:prevSamplesPerSegment*)", "``int``", "Previous samplesPerSegment value for recompute test", "None"
    "Prev Up Axis (*state:prevUpAxis*)", "``float[3]``", "Previous upAxis value for recompute test", "None"
    "Prev Up Axis Source (*state:prevUpAxisSource*)", "``int``", "Previous upAxisSource value for recompute test", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.genproc.core.PushoutCurvePoints"
    "Version", "1"
    "Extension", "omni.genproc.core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "curves: pushout curve points"
    "__tokens", "{""points"": ""points"", ""curveVertexCounts"": ""curveVertexCounts"", ""basis"": ""basis"", ""bezier"": ""bezier"", ""bspline"": ""bspline"", ""catmullRom"": ""catmullRom"", ""wrap"": ""wrap"", ""pinned"": ""pinned"", ""periodic"": ""periodic"", ""nonperiodic"": ""nonperiodic"", ""type"": ""type"", ""cubic"": ""cubic"", ""linear"": ""linear"", ""transform"": ""transform""}"
    "Categories", "curve"
    "Generated Class Name", "OgnPushoutCurvePointsDatabase"
    "Python Module", "omni.genproc.core"

