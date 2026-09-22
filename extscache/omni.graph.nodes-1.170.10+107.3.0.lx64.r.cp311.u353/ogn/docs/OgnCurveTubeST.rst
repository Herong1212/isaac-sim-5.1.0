.. _omni_graph_nodes_CurveTubeST_1:

.. _omni_graph_nodes_CurveTubeST:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Curve Tube ST
    :keywords: lang-en omnigraph node geometry:generator threadsafe nodes curve-tube-s-t


Curve Tube ST
=============

.. <description>

Compute curve tube ST values. S and T refer to the parameters in the 2-dimensional surface space of the tube.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Columns (*inputs:cols*)", "``int[]``", "Columns of the tubes.", "[]"
    "Curve Vertex Counts (*inputs:curveVertexCounts*)", "``int[]``", "Vertex counts for each curve frame. Must have the same number of elements as 'Curve Vertex Starts'.", "[]"
    "Curve Vertex Starts (*inputs:curveVertexStarts*)", "``int[]``", "Vertex index starting points for each curve frame. Must have the same number of elements as 'Curve Vertex Counts'.", "[]"
    "Scale T Like S (*inputs:scaleTLikeS*)", "``bool``", "If true then scale T the same as S.", "False"
    "T Values (*inputs:t*)", "``float[]``", "T values of the tubes.", "[]"
    "Tube Quad Starts (*inputs:tubeQuadStarts*)", "``int[]``", "Vertex index values for the tube quad starting points.", "[]"
    "Tube ST Starts (*inputs:tubeSTStarts*)", "``int[]``", "Vertex index values for the tube ST starting points.", "[]"
    "Tube Widths (*inputs:width*)", "``float[]``", "Width of tube positions, if scaling T like S.", "[]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "ST Values (*outputs:primvars:st*)", "``float[2][]``", "Array of computed ST values.", "None"
    "ST Indices (*outputs:primvars:st:indices*)", "``int[]``", "Array of computed ST indices.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.CurveTubeST"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Curve Tube ST"
    "Categories", "geometry:generator"
    "Generated Class Name", "OgnCurveTubeSTDatabase"
    "Python Module", "omni.graph.nodes"

