.. _omni_graph_examples_cpp_Adjacency_1:

.. _omni_graph_examples_cpp_Adjacency:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Example Node: Adjacency
    :keywords: lang-en omnigraph node cpp adjacency


Example Node: Adjacency
=======================

.. <description>

Computes chosen adjacency information from specified input mesh topology data.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.examples.cpp<ext_omni_graph_examples_cpp>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Compute Distances (*inputs:computeDistances*)", "``bool``", "When enabled, the distances from each point to its neighbors is computed and stored in a 'float[]' attribute in 'output' as specified by 'nameOfDistancesOutputAttribute'.", "False"
    "Compute Neighbor Counts (*inputs:computeNeighborCounts*)", "``bool``", "When enabled, the number of neighbors of each point is computed and all are stored in an 'int[]' attribute in 'output' as specified by 'nameOfNeighborCountsOutputAttribute'.", "False"
    "Compute Neighbor Starts (*inputs:computeNeighborStarts*)", "``bool``", "When enabled, the beginning index of neighbors of each point within the arrays computed by either 'computeNeighbors' or 'computeDistances' is computed and all, plus an additional integer to indicate the end of the array, are stored in an 'int[]' attribute in 'output' as specified by 'nameOfNeighborStartsOutputAttribute'.  The extra integer at the end allows for easy computing of the number of neighbors of any single point, by subtracting the value in the array corresponding with the point, from the following value in the array.", "True"
    "Compute Neighbors (*inputs:computeNeighbors*)", "``bool``", "When enabled, the neighbors of each point are computed and stored contiguously in an 'int[]' attribute in 'output' as specified by 'nameOfNeighborsOutputAttribute'.", "True"
    "Mesh (*inputs:mesh*)", "``bundle``", "Bundle containing topology data to be analysed", "None"
    "Name Of Distances Output Attribute (*inputs:nameOfDistancesOutputAttribute*)", "``token``", "Name of the 'float[]' attribute to be created in 'output' to contain the computed distances to each neighbor.  This is only used if 'computeDistances' is true.", "distances"
    "Name Of Neighbor Counts Output Attribute (*inputs:nameOfNeighborCountsOutputAttribute*)", "``token``", "Name of the 'int[]' attribute to be created in 'output' to contain the number of neighbors of each point.  This is only used if 'computeNeighborCounts' is true.  A running sum of this array can be computed using 'computeNeighborStarts'.  The neighbors themselves can be computed using 'computeNeighbors'.", "neighborCounts"
    "Name Of Neighbor Starts Output Attribute (*inputs:nameOfNeighborStartsOutputAttribute*)", "``token``", "Name of the 'int[]' attribute to be created in 'output' to contain the beginning index of neighbors of each point in the arrays computed by either 'computeNeighbors' or 'computeDistances'.  This is only used if 'computeNeighborStarts' is true.", "neighborStarts"
    "Name Of Neighbors Output Attribute (*inputs:nameOfNeighborsOutputAttribute*)", "``token``", "Name of the 'int[]' attribute to be created in 'output' to contain the neighbors of all points.  This is only used if 'computeNeighbors' is true.  The beginnings of each point's neighbors within this array can be computed using 'computeNeighborStarts'.  The number of neighbors of each point can be computed using 'computeNeighborCounts'.", "neighbors"
    "Name Of Positions Input Attribute (*inputs:nameOfPositionsInputAttribute*)", "``token``", "Name of the 'point3f[]' attribute in 'mesh' containing the positions of each point.  This is only used if 'computeDistances' is true.  The element count of this array overrides 'pointCount', when used.", "points"
    "Name Of Vertex Counts Input Attribute (*inputs:nameOfVertexCountsInputAttribute*)", "``token``", "Name of the 'int[]' attribute in 'mesh' containing the vertex counts of each face", "faceVertexCounts"
    "Name Of Vertex Indices Input Attribute (*inputs:nameOfVertexIndicesInputAttribute*)", "``token``", "Name of the 'int[]' attribute in 'mesh' containing the vertex indices of each face", "faceVertexIndices"
    "Point Count (*inputs:pointCount*)", "``int``", "Number of points being referred to in the vertex indices attribute.  This is only used if 'computeDistances' is false, otherwise this is overridden by the element count of the attribute specified by 'nameOfPositionsInputAttribute'.", "0"
    "Remove Duplicates (*inputs:removeDuplicates*)", "``bool``", "When enabled, each neighbor of a point will be counted only once, instead of once per edge that connects the point to the neighbor.", "True"
    "Treat Edges As One Way (*inputs:treatEdgesAsOneWay*)", "``bool``", "When enabled, if a face has an edge from A to B, B will be considered a neighbor of A, but A will not be considered a neighbor of B.  This can be useful as part of identifying unshared edges or inconsistent face winding order.", "False"
    "Treat Faces As Curves (*inputs:treatFacesAsCurves*)", "``bool``", "When enabled, the input faces will be treated as curves, instead of closed polygons, i.e. no edge from the last vertex of each face to the first vertex of that face will be counted.", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Mesh (*outputs:mesh*)", "``bundle``", "A copy of the input 'mesh' with the computed attributes added, as specified above.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.examples.cpp.Adjacency"
    "Version", "1"
    "Extension", "omni.graph.examples.cpp"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Example Node: Adjacency"
    "Generated Class Name", "OgnExampleAdjacencyDatabase"
    "Python Module", "omni.graph.examples.cpp"

