.. _omni_genproc_core_ResampleCurves_1:

.. _omni_genproc_core_ResampleCurves:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Resample Curves
    :keywords: lang-en omnigraph node curve core resample-curves


Resample Curves
===============

.. <description>

Resample curves to use a smaller number of segments. Note that currently only cubic bezier curves are considered when resampling.

.. </description>


Installation
------------

To use this node enable :ref:`omni.genproc.core<ext_omni_genproc_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Avoid Sharp Turns (*inputs:avoidSharpTurns*)", "``bool``", "Experimental setting to fit a resampled curve with equal and opposite tangents on either side of each control point", "False"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Transform Bundle (*inputs:curvesBundle*)", "``bundle``", "Bundle containing curves data", "None"
    "Mode (*inputs:mode*)", "``int``", "Resampling mode (0 - resample by number of segments, 1 - resample by step)", "0"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Number of Points (*inputs:numberOfSegments*)", "``int``", "When resampling by number of segments, this value specifies the number of segments in the resampled curve", "10"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Step (*inputs:step*)", "``float``", "When resampling by Step, the number of resampled segments will be the length of the curve divided by this value", "1.0"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Verbose (*inputs:verbose*)", "``bool``", "print verbose information", "False"
    "", "Metadata", "*displayGroup* = parameters", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Curve Bundle (*outputs:curvesBundle*)", "``bundle``", "Bundle containing curves data", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prev Avoid Sharp Turns (*state:prevAvoidSharpTurns*)", "``bool``", "Previous avoidSharpTurns value for recompute test", "None"
    "Prev Mode (*state:prevMode*)", "``int``", "Previous mode value for recompute test", "None"
    "Prev Number Of Segments (*state:prevNumberOfSegments*)", "``int``", "Previous numberOfSegments value for recompute test", "None"
    "Prev Step (*state:prevStep*)", "``float``", "Previous step value for recompute test", "None"
    "Prev Verbose (*state:prevVerbose*)", "``bool``", "Previous verbose value for recompute test", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.genproc.core.ResampleCurves"
    "Version", "1"
    "Extension", "omni.genproc.core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Resample Curves"
    "__tokens", "{""points"": ""points"", ""curveVertexCounts"": ""curveVertexCounts"", ""basis"": ""basis"", ""bezier"": ""bezier"", ""bspline"": ""bspline"", ""catmullRom"": ""catmullRom"", ""wrap"": ""wrap"", ""pinned"": ""pinned"", ""periodic"": ""periodic"", ""nonperiodic"": ""nonperiodic"", ""type"": ""type"", ""cubic"": ""cubic"", ""linear"": ""linear"", ""transform"": ""transform""}"
    "Categories", "curve"
    "Generated Class Name", "OgnResampleCurvesDatabase"
    "Python Module", "omni.genproc.core"

