.. _omni_genproc_core_PointOnCurve_1:

.. _omni_genproc_core_PointOnCurve:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Point on Curve
    :keywords: lang-en omnigraph node curve core point-on-curve


Point on Curve
==============

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
    "U Value (*inputs:uValue*)", "``float``", "Value from zero to one along curve at which we want to get a point", "None"
    "", "Metadata", "*displayGroup* = parameters", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Point on Curve (*outputs:point*)", "``float[3]``", "Point on input curve", "None"
    "Tangent at Point (*outputs:tangent*)", "``float[3]``", "Curve tangent at point", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prev U Value (*state:prevUValue*)", "``float``", "Previous uValue value for recompute test", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.genproc.core.PointOnCurve"
    "Version", "1"
    "Extension", "omni.genproc.core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Point on Curve"
    "Categories", "curve"
    "Generated Class Name", "OgnPointOnCurveDatabase"
    "Python Module", "omni.genproc.core"

