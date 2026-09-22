.. _omni_genproc_core_ClosestPointOnCurve_1:

.. _omni_genproc_core_ClosestPointOnCurve:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Closest Point on Curve
    :keywords: lang-en omnigraph node curve core closest-point-on-curve


Closest Point on Curve
======================

.. <description>

Given a reference point and a bundle containing curve data, get the closest point on the curve to  the reference point along with the curve tangent and u-value (between zero and one) at that point.  Note that if multiple curves are present in the bundle, only the first one will be used.

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
    "Point (*inputs:point*)", "``float[3]``", "Reference point for which we want to find the closest point on the input curve(s)", "[0.0, 0.0, 0.0]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Point on Curve (*outputs:point*)", "``float[3]``", "Closest point on input curve(s) to specified reference point", "None"
    "Tangent at Point (*outputs:tangent*)", "``float[3]``", "Curve tangent at closest point on curve", "None"
    "U Value (*outputs:uValue*)", "``float``", "Parametric value of closest pont on curve", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Cache Bundle (*state:cacheBundle*)", "``bundle``", "cached compute state", "None"
    "Prev Point (*state:prevPoint*)", "``float[3]``", "Previous point value for recompute test", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.genproc.core.ClosestPointOnCurve"
    "Version", "1"
    "Extension", "omni.genproc.core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Closest Point on Curve"
    "__tokens", "{""points"": ""points"", ""curveVertexCounts"": ""curveVertexCounts"", ""basis"": ""basis"", ""bezier"": ""bezier"", ""bspline"": ""bspline"", ""catmullRom"": ""catmullRom"", ""wrap"": ""wrap"", ""pinned"": ""pinned"", ""periodic"": ""periodic"", ""nonperiodic"": ""nonperiodic"", ""type"": ""type"", ""cubic"": ""cubic"", ""linear"": ""linear"", ""transform"": ""transform"", ""tangents"": ""tangents"", ""distances"": ""distances"", ""curveSegmentCounts"": ""curveSegmentCounts""}"
    "Categories", "curve"
    "Generated Class Name", "OgnClosestPointOnCurveDatabase"
    "Python Module", "omni.genproc.core"

