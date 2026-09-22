.. _omni_genproc_core_PointsOnCurve_1:

.. _omni_genproc_core_PointsOnCurve:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Points on Curve
    :keywords: lang-en omnigraph node curve core points-on-curve


Points on Curve
===============

.. <description>

Given a bundle containing curve data and a u-value (between zero and one),  get a point on the curve and the curve tangent at that point.  Note that if multiple curves are present in the bundle, only the first one will be used.

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
    "Number of Points (*inputs:numberOfPoints*)", "``int``", "Number of points to randomly sample on the curve (if nothing is connected to the uValue input)", "10"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Random Seed (*inputs:randomSeed*)", "``int``", "Seed for random number generator for u-value distribution (if nothing is connected to the uValue input)", "0"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Sampling Mode (*inputs:samplingMode*)", "``int``", "Sampling mode: 0 -- sample from an input array connect to the uValues input, 1 -- sample from a random distribution generated using the timeBasedSeed, randomSeed, and numberOfPoints inputs", "0"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Vary Randomness Over Time (*inputs:timeBasedSeed*)", "``bool``", "If true, random seed will vary with time; if false random numbers will be the same each frame.", "False"
    "", "Metadata", "*displayGroup* = parameters", ""
    "U-Values (*inputs:uValues*)", "``float[]``", "Parametric values from zero to one at which to sample points on the curve", "[]"
    "", "Metadata", "*displayGroup* = parameters", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Point on Curve (*outputs:points*)", "``float[3][]``", "Point on input curve", "None"
    "Tangent at Point (*outputs:tangents*)", "``float[3][]``", "Curve tangent at point", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prev Number Of Points (*state:prevNumberOfPoints*)", "``int``", "Previous numberOfPoints value for recompute test", "None"
    "Prev Random Seed (*state:prevRandomSeed*)", "``int``", "Previous randomSeed value for recompute test", "None"
    "Prev Sampling Mode (*state:prevSamplingMode*)", "``int``", "Previous samplingMode value for recompute test", "None"
    "Prev Time Based Seed (*state:prevTimeBasedSeed*)", "``bool``", "Previous timeBasedSeed value for recompute test", "None"
    "Prev U Values (*state:prevUValues*)", "``float[]``", "Previous uValues value for recompute test", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.genproc.core.PointsOnCurve"
    "Version", "1"
    "Extension", "omni.genproc.core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Points on Curve"
    "Categories", "curve"
    "Generated Class Name", "OgnPointsOnCurveDatabase"
    "Python Module", "omni.genproc.core"

