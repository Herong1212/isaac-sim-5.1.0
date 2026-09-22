.. _omni_graph_nodes_SourceIndices_1:

.. _omni_graph_nodes_SourceIndices:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Extract Source Index Array
    :keywords: lang-en omnigraph node math:operator threadsafe nodes source-indices


Extract Source Index Array
==========================

.. <description>

Takes an input array of index values in 'sourceStartsInTarget' encoded as the list of index values at which the output array value will be incremented, starting at the second entry, and with the last entry into the array being the desired sized of the output array 'sourceIndices'. For example the input [1,2,3,5,6,6] would generate an output array of size 5 (last index) consisting of the values [0,0,2,3,3,3]:
    - the first two 0s to fill the output array up to index input[1]=2
    - the first two 0s to fill the output array up to index input[1]=2
    - the 2 to fill the output array up to index input[2]=3
    - the three 3s to fill the output array up to index input[3]=6

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Source Starts In Target (*inputs:sourceStartsInTarget*)", "``int[]``", "List of index values encoding the increments for the output array values.", "[]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Source Indices (*outputs:sourceIndices*)", "``int[]``", "Decoded list of index values as described by the node algorithm.", "[]"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.SourceIndices"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Extract Source Index Array"
    "Categories", "math:operator"
    "Generated Class Name", "OgnSourceIndicesDatabase"
    "Python Module", "omni.graph.nodes_core"

