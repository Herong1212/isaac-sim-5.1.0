.. _omni_graph_nodes_CurveTubePositions_1:

.. _omni_graph_nodes_CurveTubePositions:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Curve Tube Positions
    :keywords: lang-en omnigraph node geometry:generator threadsafe nodes curve-tube-positions


Curve Tube Positions
====================

.. <description>

Take the points on a curve and a subset of vertex ranges and generate point geometry corresponding to a tube that follows the curve positions. Imagine a curve that is the center of a straw. The tube is constructed by inflating subsections of the curve.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Columns (*inputs:cols*)", "``int[]``", "Index along the curve where the tube is to be constructed.", "[]"
    "Curve Points (*inputs:curvePoints*)", "``float[3][]``", "Points on the curve from which the tubes are to be constructed.", "[]"
    "Curve Vertex Counts (*inputs:curveVertexCounts*)", "``int[]``", "Vertex counts for each curve frame. Must have the same number of elements as 'Curve Vertex Starts'.", "[]"
    "Curve Vertex Starts (*inputs:curveVertexStarts*)", "``int[]``", "Vertex index starting points for each curve frame. Must have the same number of elements as 'Curve Vertex Counts'.", "[]"
    "Out Vectors (*inputs:out*)", "``float[3][]``", "Out vector directions on the constructed tube.", "[]"
    "Tube Point Starts (*inputs:tubePointStarts*)", "``int[]``", "Tube starting point index values. Must have the same number of elements as 'Columns'.", "[]"
    "Up Vectors (*inputs:up*)", "``float[3][]``", "Up vectors on the constructed tube.", "[]"
    "Tube Widths (*inputs:width*)", "``float[]``", "Width of the constructed tube.", "[]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Points (*outputs:points*)", "``float[3][]``", "Points on the tube that was constructed.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.CurveTubePositions"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Curve Tube Positions"
    "Categories", "geometry:generator"
    "Generated Class Name", "OgnCurveTubePositionsDatabase"
    "Python Module", "omni.graph.nodes"

