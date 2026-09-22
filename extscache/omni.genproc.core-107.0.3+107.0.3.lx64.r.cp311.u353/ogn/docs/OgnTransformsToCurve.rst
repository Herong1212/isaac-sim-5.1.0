.. _omni_genproc_core_TransformsToCurve_1:

.. _omni_genproc_core_TransformsToCurve:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Transforms to Curve
    :keywords: lang-en omnigraph node curve core transforms-to-curve


Transforms to Curve
===================

.. <description>

Given a bundle of prims, use the transforms of those prims to create a spline curve.

.. </description>


Installation
------------

To use this node enable :ref:`omni.genproc.core<ext_omni_genproc_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Basis (*inputs:basis*)", "``int``", "Curve basis (0 - Bezier, 1 - BSpline, 2 - Catmull-Rom)", "0"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Tangent Length (*inputs:tangentLength*)", "``float``", "Scale factor applied to curve tangents (note that tangents are also scaled by the scale of the transformable prims in the transform bundle)", "1.0"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Transform Bundle (*inputs:transformBundle*)", "``bundle``", "Bundle containing transform data", "None"
    "Type (*inputs:type*)", "``int``", "Curve type (0 - linear, 1 - cubic)", "1"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Wrap (*inputs:wrap*)", "``int``", "Curve wrap setting (0 - nonperiodic, 1 - periodic, 2 - pinned)", "0"
    "", "Metadata", "*displayGroup* = parameters", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Curve Bundle (*outputs:curveBundle*)", "``bundle``", "Bundle containing curves data", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prev Basis (*state:prevBasis*)", "``int``", "Previous basis value for recompute test", "None"
    "Prev Tangent Length (*state:prevTangentLength*)", "``float``", "Previous tangentLength value for recompute test", "None"
    "Prev Type (*state:prevType*)", "``int``", "Previous type value for recompute test", "None"
    "Prev Wrap (*state:prevWrap*)", "``int``", "Previous wrap value for recompute test", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.genproc.core.TransformsToCurve"
    "Version", "1"
    "Extension", "omni.genproc.core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Transforms to Curve"
    "__tokens", "{""points"": ""points"", ""curveVertexCounts"": ""curveVertexCounts"", ""basis"": ""basis"", ""bezier"": ""bezier"", ""bspline"": ""bspline"", ""catmullRom"": ""catmullRom"", ""wrap"": ""wrap"", ""pinned"": ""pinned"", ""periodic"": ""periodic"", ""nonperiodic"": ""nonperiodic"", ""type"": ""type"", ""cubic"": ""cubic"", ""linear"": ""linear"", ""travelling"": ""travelling""}"
    "Categories", "curve"
    "Generated Class Name", "OgnTransformsToCurveDatabase"
    "Python Module", "omni.genproc.core"

