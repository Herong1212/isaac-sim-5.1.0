.. _omni_graph_nodes_GetLocationAtDistanceOnCurve2_1:

.. _omni_graph_nodes_GetLocationAtDistanceOnCurve2:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Locations At Distances On Curve
    :keywords: lang-en omnigraph node internal threadsafe nodes get-location-at-distance-on-curve2


Get Locations At Distances On Curve
===================================

.. <description>

Given a set of curve points and a normalized distance between 0-1.0, return the location on a closed curve. 0 is the first point on the curve, 1.0 is also the first point because the is an implicit segment connecting the first and last points. Values outside the range 0-1.0 will be wrapped to that range, for example -0.4 is equivalent to 0.6 and 1.3 is equivalent to 0.3. This is a simplistic curve-following node, intended for curves in a plane, for prototyping purposes.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Curve (*inputs:curve*)", "``pointd[3][]``", "The vertex values of the curve to be examined.", "[]"
    "Distance (*inputs:distance*)", "``double``", "The distance along the curve, normalized to the range 0-1.0.", "0.0"
    "Forward (*inputs:forwardAxis*)", "``token``", "The direction vector from which the returned rotation is relative. The legal values are 'X', 'Y', or 'Z'.", "X"
    "Up (*inputs:upAxis*)", "``token``", "The world Up vector, the curve should be in a plane perpendicular with this. The legal values are 'X', 'Y', or 'Z'.", "Y"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Location on curve at the given distance in world space. (*outputs:location*)", "``pointd[3]``", "Location", "None"
    "World space orientation of the curve at the given distance. It may not be smooth for some curves. (*outputs:orientation*)", "``quatf[4]``", "Orientation", "None"
    "World space rotation of the curve at the given distance. It may not be smooth for some curves. (*outputs:rotateXYZ*)", "``vectord[3]``", "Rotations", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.GetLocationAtDistanceOnCurve2"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "hidden", "true"
    "uiName", "Get Locations At Distances On Curve"
    "__tokens", "[""x"", ""y"", ""z"", ""X"", ""Y"", ""Z""]"
    "Categories", "internal"
    "Generated Class Name", "OgnGetLocationAtDistanceOnCurve2Database"
    "Python Module", "omni.graph.nodes"

