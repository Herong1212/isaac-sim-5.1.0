.. _omni_graph_nodes_GetLocationAtDistanceOnCurve_1:

.. _omni_graph_nodes_GetLocationAtDistanceOnCurve:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Locations At Distances On Curve
    :keywords: lang-en omnigraph node internal threadsafe nodes get-location-at-distance-on-curve


Get Locations At Distances On Curve
===================================

.. <description>

DEPRECATED: Use GetLocationAtDistanceOnCurve2

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Curve (*inputs:curve*)", "``pointd[3][]``", "The curve to be examined", "[]"
    "Distances (*inputs:distance*)", "``double[]``", "The distances along the curve, wrapped to the range 0-1.0", "[]"
    "Forward (*inputs:forwardAxis*)", "``token``", "The direction vector from which the returned rotation is relative, one of X, Y, Z", "X"
    "Up (*inputs:upAxis*)", "``token``", "The world Up vector, the curve should be in a plane perpendicular with this - one of X, Y, Z", "Y"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Locations on curve at the given distances in world space (*outputs:location*)", "``pointd[3][]``", "Locations", "None"
    "World space orientations of the curve at the given distances, may not be smooth for some curves (*outputs:orientation*)", "``quatf[4][]``", "Orientations", "None"
    "World space rotations of the curve at the given distances, may not be smooth for some curves (*outputs:rotateXYZ*)", "``vectord[3][]``", "Rotations", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.GetLocationAtDistanceOnCurve"
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
    "Generated Class Name", "OgnGetLocationAtDistanceOnCurveDatabase"
    "Python Module", "omni.graph.nodes"

