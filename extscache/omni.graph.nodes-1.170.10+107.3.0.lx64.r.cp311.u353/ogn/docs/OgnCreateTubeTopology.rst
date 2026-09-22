.. _omni_graph_nodes_CreateTubeTopology_1:

.. _omni_graph_nodes_CreateTubeTopology:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Create Tube Topology
    :keywords: lang-en omnigraph node geometry:generator threadsafe nodes create-tube-topology


Create Tube Topology
====================

.. <description>

Creates the face vertex counts and indices describing a tube topology with the given number of rows and columns.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Column Array (*inputs:cols*)", "``int[]``", "Array of columns in the topology to be generated", "[]"
    "Row Array (*inputs:rows*)", "``int[]``", "Array of rows in the topology to be generated", "[]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Face Vertex Counts (*outputs:faceVertexCounts*)", "``int[]``", "Array of vertex counts for each face in the tube topology", "None"
    "Face Vertex Indices (*outputs:faceVertexIndices*)", "``int[]``", "Array of vertex indices for each face in the tube topology", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.CreateTubeTopology"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Create Tube Topology"
    "Categories", "geometry:generator"
    "Generated Class Name", "OgnCreateTubeTopologyDatabase"
    "Python Module", "omni.graph.nodes"

