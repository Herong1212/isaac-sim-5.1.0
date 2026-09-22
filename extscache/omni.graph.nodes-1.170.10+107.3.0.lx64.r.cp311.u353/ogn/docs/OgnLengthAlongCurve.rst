.. _omni_graph_nodes_LengthAlongCurve_1:

.. _omni_graph_nodes_LengthAlongCurve:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Length Along Curve
    :keywords: lang-en omnigraph node geometry:analysis threadsafe nodes length-along-curve


Length Along Curve
==================

.. <description>

Find the length along the curve of a subset of points on the curve.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Curve Points (*inputs:curvePoints*)", "``float[3][]``", "Points on the curve for which the lengths are to be computed.", "[]"
    "Curve Vertex Counts (*inputs:curveVertexCounts*)", "``int[]``", "Vertex counts for each curve subsection whose length is to be computed. Must have the same number of elements as 'Curve Vertex Starts'.", "[]"
    "Curve Vertex Starts (*inputs:curveVertexStarts*)", "``int[]``", "Vertex index starting points for each curve subsection whose length is to be computed. Must have the same number of elements as 'Curve Vertex Counts'.", "[]"
    "Normalize (*inputs:normalize*)", "``bool``", "If true then normalize the curve length to a 0, 1 range.", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Length (*outputs:length*)", "``float[]``", "List of lengths along the curve corresponding to the input point specifications.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.LengthAlongCurve"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Length Along Curve"
    "Categories", "geometry:analysis"
    "Generated Class Name", "OgnLengthAlongCurveDatabase"
    "Python Module", "omni.graph.nodes"

