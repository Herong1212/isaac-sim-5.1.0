.. _omni_graph_nodes_CurveToFrame_1:

.. _omni_graph_nodes_CurveToFrame:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Create Curve From Frame
    :keywords: lang-en omnigraph node examples,geometry:generator threadsafe nodes curve-to-frame


Create Curve From Frame
=======================

.. <description>

Create a frame object based on a curve description. The frame object is a combination of normal, up, and tangent vector. A frame object is generated for every subset of 'Curve Points' whose vertex ranges are based on the 'Curve Vertex Starts' and 'Curve Vertex Counts'.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Curve Points (*inputs:curvePoints*)", "``float[3][]``", "Points on the curve to be framed.", "[]"
    "Curve Vertex Counts (*inputs:curveVertexCounts*)", "``int[]``", "Vertex counts for each curve frame. Must have the same number of elements as 'Curve Vertex Starts'.", "[]"
    "Curve Vertex Starts (*inputs:curveVertexStarts*)", "``int[]``", "Vertex index starting points for each curve frame. Must have the same number of elements as 'Curve Vertex Counts'.", "[]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Out Vectors (*outputs:out*)", "``float[3][]``", "Out vector directions on the curve frame.", "None"
    "Tangents (*outputs:tangent*)", "``float[3][]``", "Tangents on the curve frame.", "None"
    "Up Vectors (*outputs:up*)", "``float[3][]``", "Up vectors on the curve frame.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.CurveToFrame"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Create Curve From Frame"
    "Categories", "examples,geometry:generator"
    "Generated Class Name", "OgnCurveFrameDatabase"
    "Python Module", "omni.graph.nodes"

