.. _omni_genproc_core_GetCurveData_1:

.. _omni_genproc_core_GetCurveData:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Curve Data
    :keywords: lang-en omnigraph node curve core get-curve-data


Get Curve Data
==============

.. <description>

Extract curve data from the first curve found in the input bundle.  If the input bundle contains ramp and tag data, e.g. from an upstream TagPrimsFromRamp  node, the ramp will be evaluated and used to add a tag corresponding to each point.

.. </description>


Installation
------------

To use this node enable :ref:`omni.genproc.core<ext_omni_genproc_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Curves Bundle (*inputs:curvesBundle*)", "``bundle``", "Bundle containing curves data", "None"
    "Ramp Interpolations Name (*inputs:rampInterpolationsName*)", "``token``", "Name of bundle attribute containing ramp interpolations.  If no such attribute exists, the tags output will be empty.", "ramp_interpolations"
    "Ramp Positions Name (*inputs:rampPositionsName*)", "``token``", "Name of bundle attribute containing ramp positions.  If no such attribute exists, the tags output will be empty.", "ramp_positions"
    "Ramp Tags Name (*inputs:rampTagsName*)", "``token``", "Name of bundle attribute containing ramp tags.  If no such attribute exists, the tags output will be empty.", "tags"
    "Ramp Values Name (*inputs:rampValuesName*)", "``token``", "Name of bundle attribute containing ramp values.  If no such attribute exists, the tags output will be empty.", "ramp_values"
    "Samples per Segment (*inputs:samplesPerSegment*)", "``int``", "Number of points in each curve segment's tessellation", "100"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Points (*outputs:points*)", "``float[3][]``", "Vertices along the curve", "None"
    "Tags (*outputs:tags*)", "``token[]``", "Per-point tag value, provided only if valid ramp data is provided in the input bundle", "None"
    "Tangents (*outputs:tangents*)", "``float[3][]``", "Curve tangents at each vertex", "None"
    "U Values (*outputs:uValues*)", "``float[]``", "Parametric value from zero to one along the curve for each vertex", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prev Ramp Interpolations Name (*state:prevRampInterpolationsName*)", "``token``", "Previous rampInterpolationsName value for recompute test", "None"
    "Prev Ramp Positions Name (*state:prevRampPositionsName*)", "``token``", "Previous rampPositionsName value for recompute test", "None"
    "Prev Ramp Tags Name (*state:prevRampTagsName*)", "``token``", "Previous rampTagsName value for recompute test", "None"
    "Prev Ramp Values Name (*state:prevRampValuesName*)", "``token``", "Previous rampValuesName value for recompute test", "None"
    "Prev Samples Per Segment (*state:prevSamplesPerSegment*)", "``int``", "Previous samplesPerSegment value for recompute test", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.genproc.core.GetCurveData"
    "Version", "1"
    "Extension", "omni.genproc.core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Get Curve Data"
    "__tokens", "{""points"": ""points"", ""curveVertexCounts"": ""curveVertexCounts"", ""basis"": ""basis"", ""bezier"": ""bezier"", ""bspline"": ""bspline"", ""catmullRom"": ""catmullRom"", ""wrap"": ""wrap"", ""pinned"": ""pinned"", ""periodic"": ""periodic"", ""nonperiodic"": ""nonperiodic"", ""type"": ""type"", ""cubic"": ""cubic"", ""linear"": ""linear"", ""transform"": ""transform""}"
    "Categories", "curve"
    "Generated Class Name", "OgnGetCurveDataDatabase"
    "Python Module", "omni.genproc.core"

